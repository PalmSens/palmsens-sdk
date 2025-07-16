from collections.abc import Mapping
from typing import Callable, Generator

from ._shared import ArrayType
from .data_array import DataArray


class DataSet(Mapping):
    def __init__(self, *, dotnet_dataset):
        self.dotnet_dataset = dotnet_dataset

    def __repr__(self):
        return f'{self.__class__.__name__}({list(self.keys())})'

    def __getitem__(self, key: tuple[str, str]):
        if not (isinstance(key, tuple) and len(key) == 2):
            raise KeyError(f'Key must be a tuple with 2 values, got: {key}')
        name, quantity = key

        ret = self._filter(
            key=lambda array: array.Description == name and array.Unit.Quantity == quantity
        )

        if not ret:
            raise KeyError(f'{key}')
        if len(ret) > 1:
            raise KeyError(f'This should not happen, got multiple instances for key: {key}')
        return ret[0]

    def __iter__(self) -> Generator[tuple[str, str], None, None]:
        for array in self.dotnet_dataset:
            yield (array.Description, ArrayType(array.ArrayType).name)

    def __len__(self):
        return self.dotnet_dataset.Count

    def _filter(self, key: Callable) -> list[DataArray]:
        """Filter array list based on callable.

        Callable takes dotnet DataArray as its only argument.
        """
        return [
            DataArray(dotnet_data_array=dotnet_data_array)
            for dotnet_data_array in self.dotnet_dataset
            if key(dotnet_data_array)
        ]

    def to_dict(self) -> dict[tuple[str, str], DataArray]:
        """Return DataSet as dictionary."""
        return dict(self)

    def to_list(self) -> list[DataArray]:
        """Return list of arrays."""
        return list(self.values())

    def arrays_by_name(self, description: str) -> list[DataArray]:
        """Get arrays by description.

        Parameters
        ----------
        description : str
            Description of the array.

        Returns
        -------
        arrays : list[DataArray]
        """
        return self._filter(key=lambda array: array.Description == description)

    def arrays_by_quantity(self, quantity: str) -> list[DataArray]:
        """Get arrays by quantity.

        Parameters
        ----------
        quantity : str
            Quantity of the array.

        Returns
        -------
        arrays : list[DataArray]
        """
        return self._filter(key=lambda array: array.Unit.Quantity == quantity)

    def arrays_by_type(self, array_type: ArrayType) -> list[DataArray]:
        """Get arrays by data type.

        Parameters
        ----------
        description : str
            Description of the array.

        Returns
        -------
        arrays : list[DataArray]
        """
        return self._filter(key=lambda array: array.ArrayType == array_type.value)

    @property
    def array_types(self) -> set[ArrayType]:
        """Return unique set of array type (enum) for arrays in dataset."""
        return set(ArrayType(arr.ArrayType) for arr in self.dotnet_dataset)

    @property
    def array_names(self) -> set[str]:
        """Return unique set of names for arrays in dataset."""
        return set(arr.Description for arr in self.dotnet_dataset)

    @property
    def array_quantities(self) -> set[str]:
        """Return unique set of quantities for arrays in dataset."""
        return set(arr.Unit.Quantity for arr in self.dotnet_dataset)

    @property
    def arrays(self) -> list[DataArray]:
        """Return list of all arrays. Alias for `.to_list()`"""
        return self.to_list()

    @property
    def current_arrays(self) -> list[DataArray]:
        """Return all Current arrays."""
        return self.arrays_by_type(ArrayType.Current)

    @property
    def potential_arrays(self) -> list[DataArray]:
        """Return all Potential arrays."""
        return self.arrays_by_type(ArrayType.Potential)

    @property
    def time_arrays(self) -> list[DataArray]:
        """Return all Time arrays."""
        return self.arrays_by_type(ArrayType.Time)

    @property
    def freq_arrays(self) -> list[DataArray]:
        """Return all Frequency arrays."""
        return self.arrays_by_type(ArrayType.Frequency)

    @property
    def zre_arrays(self) -> list[DataArray]:
        """Return all ZRe arrays."""
        return self.arrays_by_type(ArrayType.ZRe)

    @property
    def zim_arrays(self) -> list[DataArray]:
        """Return all ZIm arrays."""
        return self.arrays_by_type(ArrayType.ZIm)

    @property
    def aux_input_arrays(self) -> list[DataArray]:
        """Return all AuxInput arrays."""
        return self.arrays_by_type(ArrayType.AuxInput)
