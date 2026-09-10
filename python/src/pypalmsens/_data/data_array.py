from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import TYPE_CHECKING, Any, Self, overload

import numpy as np
from PalmSens.Calculations import MathFunctions as PSMath
from PalmSens.Data import DataArray as PSDataArray
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


class DataArray(Sequence[float]):
    """Python wrapper for .NET DataArray class.

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

    __slots__ = ('_psarray',)

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

        unit = PSDataArray.GetDefaultUnit(array_type_enum)

        new_array = PSDataArray(name, unit, array_type_enum)
        new_array.AddRange(values)

        self._psarray = new_array

    @classmethod
    def _wrap(cls, psarray: PSDataArray) -> Self:
        obj = cls.__new__(cls)
        obj._psarray = psarray
        return obj

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
            return self._psarray[index].Value

        return self.to_list()[index]

    @override
    def __len__(self) -> int:
        return len(self._psarray)

    def __add__(self, other: object) -> Self:
        if not isinstance(other, self.__class__):
            return NotImplemented

        operator = PSMath.enumOperator.Add
        new_array = PSMath.AddSubtractDataArrays(self._psarray, other._psarray, operator)

        return type(self)._wrap(new_array)

    def __radd__(self, other: object) -> Self:
        return self.__add__(other)

    def __sub__(self, other: object) -> Self:
        if not isinstance(other, self.__class__):
            return NotImplemented

        operator = PSMath.enumOperator.Subtract
        new_array = PSMath.AddSubtractDataArrays(self._psarray, other._psarray, operator)

        return type(self)._wrap(new_array)

    def __rsub__(self, other: object) -> Self:
        if not isinstance(other, self.__class__):
            return NotImplemented

        operator = PSMath.enumOperator.Subtract
        new_array = PSMath.AddSubtractDataArrays(other._psarray, self._psarray, operator)

        return type(self)._wrap(new_array)

    def __mul__(self, value: object) -> Self:
        if not isinstance(value, (int, float)):
            return NotImplemented

        new_values = PSMath.MultiplyDataArray(self._psarray.GetValues(), value)

        new_array = PSDataArray(
            self._psarray.Description, self._psarray.Unit, self._psarray.ArrayType
        )
        new_array.AddRange(new_values)

        return type(self)._wrap(new_array)

    def __rmul__(self, value: object) -> Self:
        return self.__mul__(value)

    def normalize(self) -> Self:
        """Normalize values in array to the 0 - 1 range.

        Values are scaled with ``(value - min) / (max - min)``,
        where min and max are the min and max values.

        The unit of the returned array is inherited from the source array.

        Returns
        -------
        new_array : DataArray
            Data array with normalized values.
        """
        new_values = PSMath.NormalizeArray(self._psarray.GetValues(), self.min(), self.max())
        new_array = PSDataArray(
            self._psarray.Description, self._psarray.Unit, self._psarray.ArrayType
        )
        new_array.AddRange(new_values)
        return type(self)._wrap(new_array)

    def copy(self) -> DataArray:
        """Return a copy of the array."""
        return DataArray._wrap(self._psarray.Clone())

    def min(self) -> float:
        """Return min value."""
        return self._psarray.MinValue

    def max(self) -> float:
        """Return max value."""
        return self._psarray.MaxValue

    def savitsky_golay(self, window_size: int = 3) -> DataArray:
        """Smooth the array using a Savitsky-Golay filter with the window size.

        (i.e. window size 2 will filter points based on the values of the next/previous 2 points)

        Parameters
        ----------
        window_size : int
            Size of the window
        """
        new = self.copy()
        success = new._psarray.Smooth(window_size, False)
        if not success:
            raise ValueError('Something went wrong.')
        return new

    @property
    def name(self) -> str:
        """Name of the array."""
        return self._psarray.Description

    def to_numpy(self) -> np.ndarray:
        """Export data array to numpy."""
        return np.array(self._psarray.GetValues())

    def to_list(self) -> list[float]:
        """Export data array to list."""
        return list(self._psarray.GetValues())

    @property
    def type(self) -> AllowedArrayTypes:
        """Array type as str."""
        return array_enum_to_str(self._psarray.ArrayType)

    @property
    def unit(self) -> str:
        """Unit for array."""
        return self._psarray.Unit.ToString()

    @property
    def quantity(self) -> str:
        """Quantity for array."""
        return self._psarray.Unit.Quantity

    @property
    def ocp_value(self) -> float:
        """OCP Value."""
        return self._psarray.OCPValue

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
    psarray
        Reference to .NET DataArray object.
    """

    def current(self) -> list[float]:
        """Current in uA."""
        # Work-around for mIDC bug
        if self.type == 'miDC':
            return [implementation(val).Value for val in self._psarray]
        return self.to_list()

    def current_in_range(self) -> list[float]:
        """Raw current value expressed in the active current range.

        `current` = `current_in_range` * CR, e.g. 0.2 * 100uA = 2.0 uA
        """
        return [implementation(val).ValueInRange for val in self._psarray]

    def current_reading(self) -> list[CurrentReading]:
        """Return as list of potential reading objects."""
        return [CurrentReading._from_psobject(implementation(val)) for val in self._psarray]

    def current_range(self) -> list[AllowedCurrentRanges]:
        """Return current range as list of strings."""
        return [cr_enum_to_string(implementation(val).CurrentRange) for val in self._psarray]

    def reading_status(self) -> list[AllowedReadingStatus]:
        """Return reading status as list of strings."""
        return [str(implementation(val).ReadingStatus) for val in self._psarray]  # type:ignore

    def timing_status(self) -> list[AllowedTimingStatus]:
        """Return timing status as list of strings."""
        return [str(implementation(val).TimingStatus) for val in self._psarray]  # type:ignore

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
    psarray
        Reference to .NET DataArray object.
    """

    def potential(self) -> list[float]:
        """Return list of potential values in V."""
        return self.to_list()

    def potential_in_range(self) -> list[float]:
        """Return list of raw potential values expressed in the active potential range.

        `potential` = `potential_in_range` * PR, e.g. 2.0 * 100mV = 0.2V
        """
        return [implementation(val).ValueInRange for val in self._psarray]

    def potential_reading(self) -> list[PotentialReading]:
        """Return as list of potential reading objects."""
        return [PotentialReading._from_psobject(implementation(val)) for val in self._psarray]

    def potential_range(self) -> list[AllowedPotentialRanges]:
        """Return potential range as list of strings."""
        return [pr_enum_to_string(implementation(val).Range) for val in self._psarray]

    def reading_status(self) -> list[AllowedReadingStatus]:
        """Return reading status as list of strings."""
        return [str(implementation(val).ReadingStatus) for val in self._psarray]  # type:ignore

    def timing_status(self) -> list[AllowedTimingStatus]:
        """Return timing status as list of strings."""
        return [str(implementation(val).TimingStatus) for val in self._psarray]  # type:ignore

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
