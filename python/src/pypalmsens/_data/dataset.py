from __future__ import annotations

import warnings
from collections.abc import Generator, Mapping, Sequence
from typing import TYPE_CHECKING, Any, Callable, final

from PalmSens.Plottables import Curve as PSCurve
from typing_extensions import override

from .curve import Curve
from .data_array import CurrentArray, DataArray, PotentialArray
from .shared import AllowedArrayTypes, array_enum_to_str

if TYPE_CHECKING:
    import pandas as pd
    from PalmSens.Data import DataArray as PSDataArray
    from PalmSens.Data import DataSet as PSDataSet


def _dataset_to_mapping_with_unique_keys(psdataset: PSDataSet, /) -> dict[str, DataArray]:
    """Suffix non-unique keys with integer. Keys are derived from the array type."""
    CURRENT_TYPES = (
        'Current',
        'Iac',
        'miDC',
        'BipotCurrent',
        'ForwardCurrent',
        'ReverseCurrent',
        'CurrentExtraWE',
        'DCCurrent',
    )
    POTENTIAL_TYPES = (
        'Potential',
        'BipotPotential',
        'CEPotential',
        'SE2vsXPotential',
        'PotentialExtraRE',
    )

    arrays: list[PSDataArray] = [array for array in psdataset.GetDataArrays()]
    array_types = [array_enum_to_str(array.ArrayType) for array in arrays]

    mapping: dict[str, DataArray] = {}

    for array in arrays:
        array_type = array_enum_to_str(array.ArrayType)

        is_unique = array_types.count(array_type) == 1

        if not is_unique:
            i = 1
            while (key := f'{array_type}_{i}') in mapping:
                i += 1
        else:
            key = array_type

        if array_type in CURRENT_TYPES:
            cls = CurrentArray  # type: ignore
        elif array_type in POTENTIAL_TYPES:
            cls = PotentialArray  # type: ignore
        else:
            cls = DataArray  # type: ignore

        mapping[key] = cls(psarray=array)

    return mapping


@final
class DataSet(Mapping[str, DataArray]):
    """Python wrapper for .NET DataSet class.

    Parameters
    ----------
    psdataset : PalmSens.Data.DataSet
        Reference to .NET DataSet object.
    """

    def __init__(self, *, psdataset: PSDataSet):
        self._psdataset = psdataset
        self._mapping = _dataset_to_mapping_with_unique_keys(psdataset)

    @override
    def __repr__(self):
        return f'{self.__class__.__name__}({list(self.keys())})'

    @override
    def __getitem__(self, key: str):
        return self._mapping[key]

    @override
    def __iter__(self) -> Generator[str, None, None]:
        # Note that iterating over self.psdataset also returns the 'hidden' debug arrays
        # `.GetDataArrays()` excludes those.
        yield from self._mapping

    @override
    def __len__(self):
        return len(self._mapping)

    def _filter(self, key: Callable[[DataArray], bool]) -> list[DataArray]:
        """Filter array list based on callable.

        Callable takes dotnet DataArray as its only argument.
        """
        return [array for array in self._mapping.values() if key(array)]

    def _psarrays(self):
        """Return underlying PalmSens SDK objects."""
        return self._psdataset.GetDataArrays()

    @property
    def n_points(self) -> int:
        """Number of points in arrays."""
        return self._psdataset.NPoints

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

    def arrays(
        self,
        type: AllowedArrayTypes | None = None,
        name: str | None = None,
        quantity: str | None = None,
        hidden: bool = False,
    ) -> Sequence[DataArray]:
        """Return list of all arrays.

        By default, return all arrays.
        Only one filter can be active at the time.

        Parameters
        ----------
        type : str
            Get arrays by type of the array, e.g. 'Current', 'Frequency', 'AuxInput'.
            Use `.array_types()` to get a list of possible values.
        name : str
            Get arrays with given name, e.g. 'scan1', 'time'.
            Use `.array_names()` to get a list of possible values.
        quantity : str
            Get arrays by quantity, e.g. 'Charge', '-Phase'.
            Use `.array_quantities()` to get a list of possible values.
        hidden : bool
            Return hidden arrays used for debugging.

        Returns
        -------
        arrays : Sequence[DataArray]
            List of arrays.
        """
        if type:
            return self._filter(key=lambda array: array.type == type)
        elif name:
            return self._filter(key=lambda array: array.name == name)
        elif quantity:
            return self._filter(key=lambda array: array.quantity == quantity)
        elif hidden:
            return [DataArray(psarray=psarray) for psarray in self._psdataset if psarray.Hidden]
        else:
            return list(self.values())

    @property
    def array_types(self) -> set[AllowedArrayTypes]:
        """Return unique set of array types for arrays in dataset."""
        return set(array.type for array in self.values())

    @property
    def array_names(self) -> set[str]:
        """Return unique set of names for arrays in dataset."""
        return set(array.name for array in self.values())

    @property
    def array_quantities(self) -> set[str]:
        """Return unique set of quantities for arrays in dataset."""
        return set(arr.quantity for arr in self.values())

    def to_dict(self) -> dict[str, list[Any]]:
        """Return dataset as key/value mapping.

        The mapping can be used to create a pandas or polars dataframe.

        For example:

            df = pd.DataFrame(dataset.to_dict())

        Returns
        -------
        dct : dict[str, list[Any]]
            Dictionary with all arrays in dataset.
        """
        dct: dict[str, Any] = {key: arr.to_list() for key, arr in self.items() if len(arr)}

        current = self.arrays(type='Current')[-1]
        assert isinstance(current, CurrentArray)

        dct['CR'] = current.current_range()
        dct['ReadingStatus'] = current.reading_status()

        return dct

    def to_dataframe(self) -> pd.DataFrame:
        """Return dataset as pandas DataFrame.
        Requires pandas to be installed.

        Returns
        -------
        df : pd.DataFrame
            Dataframe with all arrays in dataset.
        """
        import pandas as pd

        dct = self.to_dict()
        return pd.DataFrame.from_dict(dct, orient='index').T

    def arrays_by_name(self, name: str) -> Sequence[DataArray]:
        warnings.warn(
            (f'This function has been deprecated, use `.arrays(name={name})` instead.'),
            DeprecationWarning,
        )
        return self.arrays(name=name)

    def arrays_by_quantity(self, quantity: str) -> Sequence[DataArray]:
        warnings.warn(
            (f'This function has been deprecated, use `.arrays(quantity={quantity})` instead.'),
            DeprecationWarning,
        )
        return self.arrays(quantity=quantity)

    def arrays_by_type(self, array_type: AllowedArrayTypes) -> Sequence[DataArray]:
        warnings.warn(
            (f'This function has been deprecated, use `.arrays(type={array_type})` instead.'),
            DeprecationWarning,
        )
        return self.arrays(type=array_type)
