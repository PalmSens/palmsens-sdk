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

    def min(self) -> float:
        """Return min value."""
        return self._psarray.MinValue

    def max(self) -> float:
        """Return max value."""
        return self._psarray.MaxValue

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
