from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from ._shared import ArrayType


class DataArray(Sequence):
    """Python wrapper for .NET DataArray class.

    Parameters
    ----------
    psarray
        Reference to .NET DataArray object.
    """

    def __init__(self, *, psarray):
        self._psarray = psarray

    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'name={self.name}, '
            f'unit={self.unit}, '
            f'n_points={len(self)})'
        )

    def __getitem__(self, index):
        if isinstance(index, int):
            if index >= len(self) or index < -len(self):
                raise IndexError('list index out of range')
            index = index % len(self)
            return self._psarray[index].Value

        return self.to_list()[index]

    def __len__(self):
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
