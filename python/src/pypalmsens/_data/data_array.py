from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import TYPE_CHECKING, Any, ClassVar, Self, overload

import numpy as np
from PalmSens import Units as PSUnits
from PalmSens.Calculations import MathFunctions as PSMath
from PalmSens.Data import DataArray as PSDataArray
from PalmSens.Data import DataArrayCurrents as PSDataArrayCurrents
from PalmSens.Data import DataArrayPotentials as PSDataArrayPotentials
from typing_extensions import override

from .._converters import cr_enum_to_string, pr_enum_to_string
from .._types import (
    AllowedCurrentRanges,
    AllowedPotentialRanges,
    AllowedReadingStatus,
    AllowedTimingStatus,
)
from .data_value import CurrentReading, PotentialReading
from .types import AllowedArrayTypes, array_enum_to_str, array_str_to_enum

if TYPE_CHECKING:
    import pandas as pd


def implementation(interface):
    """Get implementation from interface."""
    # Use the new `__implementation__` or `__raw_implementation__` properties to
    # if you need to "downcast" to the implementation class.
    # https://github.com/pythonnet/pythonnet/blob/a404d6e4d2ef6182763bd626ab08e0de4400e621/CHANGELOG.md?plain=1#L73-L77
    return interface.__implementation__


DEFAULT_UNIT_MAPPING = {
    'Time': PSUnits.Time,
    'Potential': PSUnits.Volt,
    'Current': PSUnits.MicroAmpere,
    'Charge': PSUnits.MicroCoulomb,
    'Temperature': PSUnits.Temperature,
    'ExtraValue': PSUnits.Volt,
    'AuxInput': PSUnits.Volt,
    'ZRe': PSUnits.ZRe,
    'ZIm': PSUnits.ZIm,
    'Z': PSUnits.Z,
    'Y': PSUnits.Y,
    'YRe': PSUnits.YRe,
    'YIm': PSUnits.YIm,
    'Phase': PSUnits.Phase,
    'Frequency': PSUnits.Hertz,
    'Cs': PSUnits.Farad,
    'CsRe': PSUnits.FahradReal,
    'CsIm': PSUnits.FahradImaginary,
    'mEdc': PSUnits.Volt,
    'Eac': PSUnits.Volt,
    'Idc': PSUnits.MicroAmpere,
}


class DataArray(Sequence[float]):
    """Array of data values.

    A data array can be created from an iterable of values, or wrapped from an
    existing ``PSDataArray`` (see ``_wrap``).

    Parameters
    ----------
    values : Iterable[float]
        Values to store in the array.
        Any iterable (list, tuple, generator, etc.)
        of floats is accepted.
    array_type : AllowedArrayTypes, optional
        Type of the array. Defaults to `'Generic'`.
        Use e.g. `'Current'` or `'Potential'` when constructing
        arrays that represent measured quantities.
    name : str, optional
        Name of the array. Defaults to the value of `array_type` when not
        given. The name is used in `__repr__` and for identification.

    Notes
    -----
    Supports arithmetic between arrays of the same type.
    ``array_a + array_b``, ``array_a - array_b`` and
    ``array_a * factor`` return new arrays.
    """

    __slots__: ClassVar[tuple[str, ...]] = ('_inner',)
    _inner: PSDataArray
    _ps_cls: ClassVar[type[PSDataArray]] = PSDataArray

    def __init__(
        self,
        values: Iterable[float],
        *,
        array_type: AllowedArrayTypes = 'Generic',
        name: str | None = None,
    ):
        array_type_enum = array_str_to_enum(array_type)

        if name is None:
            name = array_type

        if isinstance(self, CurrentArray):
            inner = PSDataArrayCurrents(name, array_type_enum)
        elif isinstance(self, PotentialArray):
            inner = PSDataArrayPotentials(name, array_type_enum)
        else:
            try:
                unit = DEFAULT_UNIT_MAPPING[array_type]()
            except KeyError:
                unit = PSUnits.FixedUnit('Unknown', '', '')

            inner = self._ps_cls(name, unit, array_type_enum)

        inner.AddRange(values)

        self._inner = inner

    @classmethod
    def _wrap(cls, inner: PSDataArray) -> Self:
        obj = cls.__new__(cls)
        obj._inner = inner
        return obj

    @classmethod
    def _wrap_dispatched(
        cls, psarray: PSDataArray
    ) -> DataArray | CurrentArray | PotentialArray:
        if isinstance(psarray, PSDataArrayPotentials):
            return PotentialArray._wrap(psarray)
        if isinstance(psarray, PSDataArrayCurrents):
            return CurrentArray._wrap(psarray)

        return DataArray._wrap(psarray)

    @override
    def __repr__(self):
        return (
            f'{type(self).__name__}(name={self.name}, unit={self.unit}, n_points={len(self)})'
        )

    @overload
    def __getitem__(self, index: int) -> float: ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[float]: ...

    @override
    def __getitem__(self, index):
        if isinstance(index, int):
            if index >= len(self) or index < -len(self):
                raise IndexError('list index out of range')
            index = index % len(self)
            return self._inner[index].Value

        return self.to_list()[index]

    @override
    def __len__(self) -> int:
        return len(self._inner)

    def __add__(self, other: object) -> DataArray:
        if not isinstance(other, self.__class__):
            return NotImplemented

        operator = PSMath.enumOperator.Add
        new_array = PSMath.AddSubtractDataArrays(self._inner, other._inner, operator)

        return type(self)._wrap(new_array)

    def __radd__(self, other: object) -> DataArray:
        return self.__add__(other)

    def __sub__(self, other: object) -> DataArray:
        if not isinstance(other, self.__class__):
            return NotImplemented

        operator = PSMath.enumOperator.Subtract
        new_array = PSMath.AddSubtractDataArrays(self._inner, other._inner, operator)

        return type(self)._wrap(new_array)

    def __rsub__(self, other: object) -> DataArray:
        if not isinstance(other, self.__class__):
            return NotImplemented

        operator = PSMath.enumOperator.Subtract
        new_array = PSMath.AddSubtractDataArrays(other._inner, self._inner, operator)

        return type(self)._wrap(new_array)

    def __mul__(self, value: object) -> DataArray:
        if not isinstance(value, (int, float)):
            return NotImplemented

        new_values = PSMath.MultiplyDataArray(self._inner.GetValues(), value)

        new_array = PSDataArray(
            self._inner.Description, self._inner.Unit, self._inner.ArrayType
        )
        new_array.AddRange(new_values)

        return type(self)._wrap(new_array)

    def __rmul__(self, value: object) -> DataArray:
        return self.__mul__(value)

    def normalize(self) -> DataArray:
        """Normalize values in array to the 0 - 1 range.

        Values are scaled with ``(value - min) / (max - min)``,
        where min and max are the min and max values.

        The unit of the returned array is inherited from the source array.

        Returns
        -------
        new_array : DataArray
            Data array with normalized values.
        """
        new_values = PSMath.NormalizeArray(self._inner.GetValues(), self.min(), self.max())
        new_array = PSDataArray(
            self._inner.Description, self._inner.Unit, self._inner.ArrayType
        )
        new_array.AddRange(new_values)
        return type(self)._wrap(new_array)

    def copy(self) -> DataArray:
        """Return a copy of the array."""
        return DataArray._wrap(self._inner.Clone())

    def min(self) -> float:
        """Return min value."""
        return self._inner.MinValue

    def max(self) -> float:
        """Return max value."""
        return self._inner.MaxValue

    def savitsky_golay(self, window_size: int = 3) -> DataArray:
        """Smooth the array using a Savitsky-Golay filter with the window size.

        (i.e. window size 2 will filter points based on the values of the next/previous 2 points)

        Parameters
        ----------
        window_size : int
            Size of the window
        """
        new = self.copy()
        success = new._inner.Smooth(window_size, False)
        if not success:
            raise ValueError('Something went wrong.')
        return new

    @property
    def name(self) -> str:
        """Name of the array."""
        return self._inner.Description

    def to_numpy(self) -> np.ndarray:
        """Export data array to numpy."""
        return np.array(self._inner.GetValues())

    def to_list(self) -> list[float]:
        """Export data array to list."""
        return list(self._inner.GetValues())

    @property
    def type(self) -> AllowedArrayTypes:
        """Array type as str."""
        return array_enum_to_str(self._inner.ArrayType)

    @property
    def unit(self) -> str:
        """Unit for array."""
        return self._inner.Unit.ToString()

    @property
    def quantity(self) -> str:
        """Quantity for array."""
        return self._inner.Unit.Quantity

    @property
    def ocp_value(self) -> float:
        """OCP Value."""
        return self._inner.OCPValue

    @property
    def is_derived(self) -> bool:
        """Return True for derived data arrays."""
        return self.name in ('Y', 'YRe', 'YIm', 'Cs', 'CsRe', 'CsIm')


class CurrentArray(DataArray):
    """Array of current values in μA.

    Note that for (m)iDC in EIS measurements the array value
    is 'in range' instead of µA for backwards compatibility reasons.
    `current()` and `current_in_range()` return the correct values.

    Parameters
    ----------
    values : Iterable[float]
        Values to store in the array.
        Any iterable (list, tuple, generator, etc.)
        of floats is accepted.
    array_type : AllowedArrayTypes, optional
        Type of the array. Defaults to `'Generic'`.
        Use e.g. `'Current'` or `'Potential'` when constructing
        arrays that represent measured quantities.
    name : str, optional
        Name of the array. Defaults to the value of `array_type` when not
        given. The name is used in `__repr__` and for identification.
    """

    __slots__ = ()

    _ps_cls: ClassVar[type[PSDataArray]] = PSDataArrayCurrents

    def __init__(
        self,
        values: Iterable[float],
        *,
        name: str | None = None,
    ):
        super().__init__(values, array_type='Current', name=name)

    def current(self) -> list[float]:
        """Current in µA."""
        # Work-around for mIDC bug
        if self.type == 'miDC':
            return [implementation(val).Value for val in self._inner]
        return self.to_list()

    def current_in_range(self) -> list[float]:
        """Raw current value expressed in the active current range.

        `current` = `current_in_range` * CR, e.g. 0.2 * 100uA = 2.0 uA
        """
        return [implementation(val).ValueInRange for val in self._inner]

    def current_reading(self) -> list[CurrentReading]:
        """Return as list of potential reading objects."""
        return [CurrentReading._from_psobject(implementation(val)) for val in self._inner]

    def current_range(self) -> list[AllowedCurrentRanges]:
        """Return current range as list of strings."""
        return [cr_enum_to_string(implementation(val).CurrentRange) for val in self._inner]

    def reading_status(self) -> list[AllowedReadingStatus]:
        """Return reading status as list of strings."""
        return [str(implementation(val).ReadingStatus) for val in self._inner]  # type:ignore

    def timing_status(self) -> list[AllowedTimingStatus]:
        """Return timing status as list of strings."""
        return [str(implementation(val).TimingStatus) for val in self._inner]  # type:ignore

    def to_dict(self) -> dict[str, list[Any]]:
        """Return array as key/value mapping.

        The mapping can be used to create a pandas or polars dataframe.

        For example:

            array = measurement.dataset['Current']
            df = pd.DataFrame(array.to_dict())

        Returns
        -------
        dict[str, list[float | str]
            Dictionary with current readings
        """
        return {
            'Current': self.current(),
            'CurrentInRange': self.current_in_range(),
            'CR': self.current_range(),
            'TimingStatus': self.timing_status(),
            'ReadingStatus': self.reading_status(),
        }

    def to_dataframe(self) -> pd.DataFrame:
        """Return array as pandas DataFrome.

        Requires pandas to be installed.

        Returns
        -------
        df : pd.DataFrame
            Dataframe with current readings
        """
        import pandas as pd

        return pd.DataFrame(self.to_dict())


class PotentialArray(DataArray):
    """Array of potential values in V.

    Parameters
    ----------
    values : Iterable[float]
        Values to store in the array.
        Any iterable (list, tuple, generator, etc.)
        of floats is accepted.
    array_type : AllowedArrayTypes, optional
        Type of the array. Defaults to `'Generic'`.
        Use e.g. `'Current'` or `'Potential'` when constructing
        arrays that represent measured quantities.
    name : str, optional
        Name of the array. Defaults to the value of `array_type` when not
        given. The name is used in `__repr__` and for identification.
    """

    __slots__ = ()

    _ps_cls: ClassVar[type[PSDataArray]] = PSDataArrayPotentials

    def __init__(
        self,
        values: Iterable[float],
        *,
        name: str | None = None,
    ):
        super().__init__(values, array_type='Potential', name=name)

    def potential(self) -> list[float]:
        """Return list of potential values in V."""
        return self.to_list()

    def potential_in_range(self) -> list[float]:
        """Return list of raw potential values expressed in the active potential range.

        `potential` = `potential_in_range` * PR, e.g. 2.0 * 100mV = 0.2V
        """
        return [implementation(val).ValueInRange for val in self._inner]

    def potential_reading(self) -> list[PotentialReading]:
        """Return as list of potential reading objects."""
        return [PotentialReading._from_psobject(implementation(val)) for val in self._inner]

    def potential_range(self) -> list[AllowedPotentialRanges]:
        """Return potential range as list of strings."""
        return [pr_enum_to_string(implementation(val).Range) for val in self._inner]

    def reading_status(self) -> list[AllowedReadingStatus]:
        """Return reading status as list of strings."""
        return [str(implementation(val).ReadingStatus) for val in self._inner]  # type:ignore

    def timing_status(self) -> list[AllowedTimingStatus]:
        """Return timing status as list of strings."""
        return [str(implementation(val).TimingStatus) for val in self._inner]  # type:ignore

    def to_dict(self) -> dict[str, list[Any]]:
        """Return array as key/value mapping.

        The mapping can be used to create a pandas or polars dataframe.

        For example:

            array = measurement.dataset['Potential']
            df = pd.DataFrame(array.to_dict())

        Returns
        -------
        dict[str, list[float | str]
            Dictionary with potential readings
        """
        return {
            'Potential': self.potential(),
            'PotentialInRange': self.potential_in_range(),
            'CR': self.potential_range(),
            'TimingStatus': self.timing_status(),
            'ReadingStatus': self.reading_status(),
        }

    def to_dataframe(self) -> pd.DataFrame:
        """Return array as pandas DataFrome.

        Requires pandas to be installed.

        Returns
        -------
        df : pd.DataFrame
            Dataframe with potential readings
        """
        import pandas as pd

        return pd.DataFrame(self.to_dict())
