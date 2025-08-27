from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Callable, Generator

import clr
from PalmSens.Data import CurrentReading
from PalmSens.Plottables import Curve as PSCurve

from ._shared import ArrayType
from .curve import Curve
from .data_array import DataArray

if TYPE_CHECKING:
    from PalmSens.Data import DataSet as PSDataSet


def _dataset_to_mapping_with_unique_keys(psdataset: PSDataSet, /) -> dict[str, DataArray]:
    """Suffix non-unique keys with integer. Keys are derived from the array type."""
    arrays = [array for array in psdataset.GetDataArrays()]
    array_types = [ArrayType(array.ArrayType).name for array in arrays]

    mapping = {}

    for array in arrays:
        array_type = ArrayType(array.ArrayType).name

        is_unique = array_types.count(array_type) == 1

        if not is_unique:
            i = 1
            while (key := f'{array_type}_{i}') in mapping:
                i += 1
        else:
            key = array_type

        mapping[key] = DataArray(psarray=array)

    return mapping


class DataSet(Mapping):
    """Python wrapper for .NET DataSet class.

    Parameters
    ----------
    psdataset : PalmSens.Data.DataSet
        Reference to .NET DataSet object.
    """

    def __init__(self, *, psdataset: PSDataSet):
        self._psdataset = psdataset
        self._mapping = _dataset_to_mapping_with_unique_keys(psdataset)

    def __repr__(self):
        return f'{self.__class__.__name__}({list(self.keys())})'

    def __getitem__(self, key: str):
        return self._mapping[key]

    def __iter__(self) -> Generator[str, None, None]:
        # Note that iterating over self.psdataset also returns the 'hidden' debug arrays
        # `.GetDataArrays()` excludes those.
        yield from self._mapping

    def __len__(self):
        return len(self._mapping)

    def _filter(self, key: Callable) -> list[DataArray]:
        """Filter array list based on callable.

        Callable takes dotnet DataArray as its only argument.
        """
        return [array for array in self._mapping.values() if key(array)]

    def _psarrays(self):
        """Return underlying PalmSens SDK objects."""
        return self._psdataset.GetDataArrays()

    def curve(self, x: str, y: str, title: str | None = None) -> Curve:
        """Construct a custom curve from x and y keys.

        Parameters
        ----------
        x : str
            Key identifying the x array
        y : str
            Key identifying the y array
        title : str
            Set the title. If None, use the $x-$y as title

        Returns
        -------
        curve : Curve
            New Curve with plotting x against y
        """
        xarray = self[x]
        yarray = self[y]

        if not title:
            title = f'{x}-{y}'

        pscurve = PSCurve(xarray._psarray, yarray._psarray, title=title)

        return Curve(pscurve=pscurve)

    def arrays(self) -> list[DataArray]:
        """Return list of all arrays. Alias for `.to_list()`"""
        return list(self.values())

    def hidden_arrays(self) -> list[DataArray]:
        """Return 'hidden' arrays used for debugging."""
        return [DataArray(psarray=psarray) for psarray in self._psdataset if psarray.Hidden]

    def arrays_by_name(self, name: str) -> list[DataArray]:
        """Get arrays by name.

        Parameters
        ----------
        name : str
            Name of the array.

        Returns
        -------
        arrays : list[DataArray]
        """
        return self._filter(key=lambda array: array.name == name)

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
        return self._filter(key=lambda array: array.quantity == quantity)

    def arrays_by_type(self, array_type: ArrayType) -> list[DataArray]:
        """Get arrays by data type.

        Parameters
        ----------
        array_type : str
            Type of the array.

        Returns
        -------
        arrays : list[DataArray]
        """
        return self._filter(key=lambda array: array.type == array_type)

    @property
    def array_types(self) -> set[ArrayType]:
        """Return unique set of array type (enum) for arrays in dataset."""
        return set(array.type for array in self.values())

    @property
    def array_names(self) -> set[str]:
        """Return unique set of names for arrays in dataset."""
        return set(array.name for array in self.values())

    @property
    def array_quantities(self) -> set[str]:
        """Return unique set of quantities for arrays in dataset."""
        return set(arr.quantity for arr in self.values())

    def current_arrays(self) -> list[DataArray]:
        """Return all Current arrays."""
        return self.arrays_by_type(ArrayType.Current)

    def potential_arrays(self) -> list[DataArray]:
        """Return all Potential arrays."""
        return self.arrays_by_type(ArrayType.Potential)

    def time_arrays(self) -> list[DataArray]:
        """Return all Time arrays."""
        return self.arrays_by_type(ArrayType.Time)

    def freq_arrays(self) -> list[DataArray]:
        """Return all Frequency arrays."""
        return self.arrays_by_type(ArrayType.Frequency)

    def zre_arrays(self) -> list[DataArray]:
        """Return all ZRe arrays."""
        return self.arrays_by_type(ArrayType.ZRe)

    def zim_arrays(self) -> list[DataArray]:
        """Return all ZIm arrays."""
        return self.arrays_by_type(ArrayType.ZIm)

    def aux_input_arrays(self) -> list[DataArray]:
        """Return all AuxInput arrays."""
        return self.arrays_by_type(ArrayType.AuxInput)

    def current_range(self) -> list[str]:
        """Return current range as list of strings."""
        array = self.current_arrays()[-1]

        clr_type = clr.GetClrType(CurrentReading)
        field_info = clr_type.GetField('CurrentRange')

        return [field_info.GetValue(val).ToString() for val in array._psarray]

    def reading_status(self) -> list[str]:
        """Return reading status as list of strings."""
        array = self.current_arrays()[-1]

        clr_type = clr.GetClrType(CurrentReading)
        field_info = clr_type.GetField('ReadingStatus')

        return [field_info.GetValue(val).ToString() for val in array._psarray]

    def timing_status(self) -> list[str]:
        """Return timing status as list of strings."""
        array = self.current_arrays()[-1]

        clr_type = clr.GetClrType(CurrentReading)
        field_info = clr_type.GetField('TimingStatus')

        return [field_info.GetValue(val).ToString() for val in array._psarray]

    def to_dataframe(self):
        """Return dataset as pandas dataframe."""
        import pandas as pd

        cols, arrays = zip(*[(key, arr.to_list()) for key, arr in self.items() if len(arr)])

        arrays = list(arrays)
        arrays.append(self.current_range())
        arrays.append(self.reading_status())

        cols = list(cols)
        cols.append('CR')
        cols.append('ReadingStatus')

        df = pd.DataFrame(arrays, index=cols).T

        return df
