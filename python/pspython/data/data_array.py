from collections.abc import Sequence

import numpy as np

from ._shared import ArrayType


class DataArray(Sequence):
    def __init__(self, *, dotnet_data_array):
        self.dotnet_data_array = dotnet_data_array

    def __repr__(self):
        return f'{self.__class__.__name__}(name={self.name!r}, quantity={self.quantity}, units={self.unit})'

    def __getitem__(self, index):
        if isinstance(index, int):
            if index >= len(self) or index < -len(self):
                raise IndexError('list index out of range')
            index = index % len(self)
            return self.dotnet_data_array[index].Value

        return self.to_list()[index]

    def __len__(self):
        return len(self.dotnet_data_array)

    def min(self) -> float:
        """Return min value."""
        return self.dotnet_data_array.MinValue

    def max(self) -> float:
        """Return max value."""
        return self.dotnet_data_array.MaxValue

    @property
    def name(self):
        """Name of the array."""
        return self.dotnet_data_array.Description

    def to_numpy(self) -> np.ndarray:
        """Export data array to numpy."""
        return np.array(self.dotnet_data_array.GetValues())

    def to_list(self) -> list[float]:
        """Export data array to list."""
        return list(self.dotnet_data_array.GetValues())

    @property
    def type(self) -> ArrayType:
        """ArrayType enum."""
        return ArrayType(self.dotnet_data_array.ArrayType)

    @property
    def unit(self) -> str:
        """Unit for array."""
        return self.dotnet_data_array.Unit.ToString()

    @property
    def quantity(self) -> str:
        """Quantity for array."""
        return self.dotnet_data_array.Unit.Quantity

    @property
    def ocp_value(self) -> float:
        """OCP Value."""
        return self.dotnet_data_array.OCPValue
