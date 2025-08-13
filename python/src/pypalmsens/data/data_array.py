from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from ._shared import ArrayType


class DataArray(Sequence):
    def __init__(self, *, psarray):
        self.psarray = psarray

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
            return self.psarray[index].Value

        return self.to_list()[index]

    def __len__(self):
        return len(self.psarray)

    def min(self) -> float:
        """Return min value."""
        return self.psarray.MinValue

    def max(self) -> float:
        """Return max value."""
        return self.psarray.MaxValue

    @property
    def name(self) -> str:
        """Name of the array."""
        return self.psarray.Description

    def to_numpy(self) -> np.ndarray:
        """Export data array to numpy."""
        return np.array(self.psarray.GetValues())

    def to_list(self) -> list[float]:
        """Export data array to list."""
        return list(self.psarray.GetValues())

    @property
    def type(self) -> ArrayType:
        """ArrayType enum."""
        return ArrayType(self.psarray.ArrayType)

    @property
    def unit(self) -> str:
        """Unit for array."""
        return self.psarray.Unit.ToString()

    @property
    def quantity(self) -> str:
        """Quantity for array."""
        return self.psarray.Unit.Quantity

    @property
    def ocp_value(self) -> float:
        """OCP Value."""
        return self.psarray.OCPValue
