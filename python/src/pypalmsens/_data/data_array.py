from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, overload

import numpy as np
from typing_extensions import override

from .._methods import cr_enum_to_string, pr_enum_to_string
from ..settings import (
    AllowedCurrentRanges,
    AllowedPotentialRanges,
    AllowedReadingStatus,
    AllowedTimingStatus,
)
from .data_value import CurrentReading, PotentialReading
from .shared import ArrayType

if TYPE_CHECKING:
    from PalmSens.Data import DataArray as PSDataArray


def implementation(interface):
    """Get implementation from interface."""
    # Use the new `__implementation__` or `__raw_implementation__` properties to
    # if you need to "downcast" to the implementation class.
    # https://github.com/pythonnet/pythonnet/blob/a404d6e4d2ef6182763bd626ab08e0de4400e621/CHANGELOG.md?plain=1#L73-L77
    return interface.__implementation__


class DataArray(Sequence[float]):
    """Python wrapper for .NET DataArray class.

    Parameters
    ----------
    psarray
        Reference to .NET DataArray object.
    """

    def __init__(self, *, psarray: PSDataArray):
        self._psarray: PSDataArray = psarray

    @override
    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'name={self.name}, '
            f'unit={self.unit}, '
            f'n_points={len(self)})'
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

    def copy(self) -> DataArray:
        """Return a copy of the array."""
        return DataArray(psarray=self._psarray.Clone())

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
    def type(self) -> ArrayType:
        """ArrayType enum."""
        return ArrayType(self._psarray.ArrayType)

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


class CurrentArray(DataArray):
    """Array of current values in μA.

    Note that for (m)IDC in EIS measurements the the array value
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
        if self.type is ArrayType.miDC:
            return self._current_in_range()
        return self.to_list()

    def _current_in_range(self) -> list[float]:
        return [implementation(val).ValueInRange for val in self._psarray]

    def current_in_range(self) -> list[float]:
        """Raw current value expressed in the active current range.

        `current` = `current_in_range` * CR, e.g. 0.2 * 100uA = 2.0 uA
        """
        # Work-around for mIDC bug
        if self.type is ArrayType.miDC:
            return self.to_list()
        return self._current_in_range()

    @override
    def to_list(self) -> list[float]:
        """Export data array to list."""
        # Override to work around bug in self._psarray.GetValues()
        # for current readings (PalmSens.Core 5.12.1114)
        # https://github.com/PalmSens/PalmSens_SDK/pull/279#issuecomment-3877662620
        return list(item.Value for item in self._psarray)

    @override
    def to_numpy(self) -> np.ndarray:
        """Export data array to numpy."""
        # Override to work around bug in self._psarray.GetValues()
        # for current readings (PalmSens.Core 5.12.1114)
        # https://github.com/PalmSens/PalmSens_SDK/pull/279#issuecomment-3877662620
        return np.array(self.to_list())

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
