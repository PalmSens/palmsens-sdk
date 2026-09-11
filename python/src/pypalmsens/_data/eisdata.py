from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Literal, Self, final

from pydantic import TypeAdapter
from pydantic.dataclasses import dataclass as pydantic_dataclass
from typing_extensions import override

from .._converters import cr_enum_to_string
from .._types import AllowedCurrentRanges, AllowedFrequencyTypes, AllowedScanTypes
from .data_array import DataArray
from .dataset import DataSet

if TYPE_CHECKING:
    from PalmSens.Plottables import EISData as PSEISData


@pydantic_dataclass
class EISDataMetadata:
    title: str
    """Measurement title."""
    columns: list[str]
    """Names for data values."""
    units: list[str]
    """Units for data values."""
    quantities: list[str]
    """Quantities for data values."""
    n_frequencies: int
    """Number of frequencies (per subscan)."""
    frequency_type: AllowedFrequencyTypes
    """Frequency type."""
    scan_type: AllowedScanTypes
    """Scan type."""
    id: int
    """EIS Data identifier."""
    type: Literal['eis_data'] = 'eis_data'
    """Object type."""


@final
class EISData:
    """Dataset containing impedance measurement results.

    Notes
    -----
    Obtain internal instances via `_wrap`.
    """

    __slots__: ClassVar[tuple[str, ...]] = ('_internal',)
    _internal: PSEISData  # pyright: ignore[reportUninitializedInstanceVariable]

    def __init__(self):
        raise TypeError(
            'EISData cannot be instantiated directly. '
            'Obtain instances through measurements or io methods.'
        )

    @classmethod
    def _wrap(cls, pseis: PSEISData) -> Self:
        obj = cls.__new__(cls)
        obj._internal = pseis
        return obj

    @override
    def __repr__(self):
        data = [
            f'title={self.title}',
            f'n_points={self.n_points}',
            f'n_frequencies={self.n_frequencies}',
        ]
        if self.has_subscans:
            data.append(f'n_subscans={self.n_subscans}')

        s = ', '.join(data)
        return f'{type(self).__name__}({s})'

    @property
    def title(self) -> str:
        """Tite for EIS data."""
        return self._internal.Title

    @property
    def frequency_type(self) -> AllowedFrequencyTypes:
        """Frequency type."""
        return str(self._internal.FreqType).lower()  # type: ignore

    @property
    def scan_type(self) -> AllowedScanTypes:
        """Scan type."""
        value = str(self._internal.ScanType)
        mapping = {'TimeScan': 'time', 'PGScan': 'potential', 'Fixed': 'fixed'}
        return mapping[value]  # type: ignore

    @property
    def dataset(self) -> DataSet:
        """Dataset which contains multiple arrays of values."""
        return DataSet._wrap(self._internal.EISDataSet)

    @property
    def subscans(self) -> list[EISData]:
        """Get list of subscans."""
        return [EISData._wrap(subscan) for subscan in self._internal.GetSubScans()]

    @property
    def n_points(self) -> int:
        """Number of points (including subscans)."""
        return self._internal.NPoints

    @property
    def n_frequencies(self) -> int:
        """Number of frequencies."""
        return self._internal.NFrequencies

    @property
    def n_subscans(self) -> int:
        """Number of subscans."""
        return len(self._internal.GetSubScans())

    @property
    def x_unit(self) -> str:
        """Unit for array."""
        return self._internal.XUnit.ToString()

    @property
    def x_quantity(self) -> str:
        """Quantity for array."""
        return self._internal.XUnit.Quantity

    @property
    def ocp_value(self) -> float:
        """OCP Value."""
        return self._internal.OCPValue

    @property
    def has_subscans(self) -> bool:
        """Return True if data contains subscans."""
        return self._internal.HasSubScans

    @property
    def mux_channel(self) -> int:
        """Mux channel."""
        return self._internal.MuxChannel

    def get_data_for_frequency(self, frequency: int) -> dict[str, DataArray]:
        """Returns dictionary with data per frequency.

        Parameters
        ----------
        frequency : int
            Index of the frequency to retrieve the data for.

        Returns
        -------
        dict[str, DataArray]
            Data are returned as a dictionary keyed by the data type.
        """
        if not (0 <= frequency < self.n_frequencies):
            raise ValueError(f'Frequency must be between 0 and {self.n_frequencies}')

        return {
            str(row.Key): DataArray._wrap(row.Value)
            for row in self._internal.GetDataArrayVsX(frequency)
        }

    def arrays(self) -> list[DataArray]:
        """Complete list of data arrays."""
        return list(self.dataset.values())

    def current_range(self) -> list[AllowedCurrentRanges]:
        """Current ranges for the measurement."""
        return [
            cr_enum_to_string(self._internal.GetCurrentRange(val))
            for val in range(self.n_points)
        ]

    @property
    def cdc(self) -> str:
        """Gets the CDC circuit for fitting."""
        return self._internal.CDC

    @property
    def cdc_values(self) -> list[float]:
        """Return values for circuit description code (CDC)."""
        return list(self._internal.CDCValues)

    @property
    def id(self) -> int:
        """Unique identifier for curve object."""
        return self._internal.GetHashCode()

    def metadata(self) -> EISDataMetadata:
        """Return eis data metadata as dataclass"""
        arrays = [array for array in self.dataset.values() if not array.is_derived]
        return EISDataMetadata(
            title=self.title,
            columns=[array.name for array in arrays],
            units=[array.unit for array in arrays],
            quantities=[array.quantity for array in arrays],
            n_frequencies=self.n_frequencies,
            frequency_type=self.frequency_type,
            scan_type=self.scan_type,
            id=self.id,
        )

    def metadata_json(self) -> bytes:
        """Generate eis data metadata as json."""

        return TypeAdapter(EISDataMetadata).dump_json(self.metadata())
