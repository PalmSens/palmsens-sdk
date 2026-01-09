from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, overload

import clr
import numpy as np
from PalmSens.Data import CurrentReading
from typing_extensions import override

from .._methods import cr_enum_to_string
from ..settings import (
    AllowedCurrentRanges,
    AllowedReadingStatus,
    AllowedTimingStatus,
)
from .shared import ArrayType

if TYPE_CHECKING:
    from PalmSens.Data import DataArray as PSDataArray


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

    def as_current_range(self) -> list[AllowedCurrentRanges]:
        """Return current range as list of strings."""
        if self.type is not ArrayType.Current:
            raise ValueError(f'Invalid array type: {self.type}, expected: {ArrayType.Current}')

        clr_type = clr.GetClrType(CurrentReading)
        field_info = clr_type.GetField('CurrentRange')

        return [cr_enum_to_string(field_info.GetValue(val)) for val in self._psarray]

    def as_reading_status(self) -> list[AllowedReadingStatus]:
        """Return reading status as list of strings."""
        if self.type is not ArrayType.Current:
            raise ValueError(f'Invalid array type: {self.type}, expected: {ArrayType.Current}')

        clr_type = clr.GetClrType(CurrentReading)
        field_info = clr_type.GetField('ReadingStatus')

        return [field_info.GetValue(val).ToString() for val in self._psarray]

    def as_timing_status(self) -> list[AllowedTimingStatus]:
        """Return timing status as list of strings."""
        if self.type is not ArrayType.Current:
            raise ValueError(f'Invalid array type: {self.type}, expected: {ArrayType.Current}')

        clr_type = clr.GetClrType(CurrentReading)
        field_info = clr_type.GetField('TimingStatus')

        return [field_info.GetValue(val).ToString() for val in self._psarray]
