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
    """Description of an EIS spectrum: what was measured, and in which units."""

    title: str
    """Measurement title."""
    columns: list[str]
    """Names of the measured data values; derived arrays are excluded."""
    units: list[str]
    """Units for data values."""
    quantities: list[str]
    """Quantities for data values."""
    n_frequencies: int
    """Number of frequencies (per subscan)."""
    frequency_type: AllowedFrequencyTypes
    """Whether a single frequency or frequency scan was applied."""
    scan_type: AllowedScanTypes
    """How the spectrum was scanned: fixed potential, potential scan, or time."""
    id: int
    """EIS Data identifier."""
    type: Literal['eis_data'] = 'eis_data'
    """Object type."""


@final
class EISData:
    """Dataset containing impedance measurement results.

    An EIS spectrum is the complex impedance `Z = Z' − jZ''` measured at each
    applied frequency, where `Z'` is the real part and `Z''` the imaginary part,
    at the angular frequency `ω = 2πf`.

    The columns of the spectrum are available as
    [DataArray][pypalmsens.data.DataArray] objects through
    [dataset][], each with its own name, quantity and unit.
    A method that repeats scans, i.e. `scan_type='potential'` or `'time'`, yields
    one spectrum per dc-potential level or per repetition, available through
    [subscans][].

    An equivalent circuit fitted to the spectrum is available as a circuit
    description code through [cdc][] with its parameter
    values in [cdc_values][], or as
    [FitResult][pypalmsens.fitting.FitResult] through
    [FitResult.from_eisdata][pypalmsens.fitting.FitResult.from_eisdata].

    EISData cannot be instantiated directly.
    Obtain instances through measurements or io methods.
    """

    __slots__: ClassVar[tuple[str, ...]] = ('_inner',)
    _inner: PSEISData  # pyright: ignore[reportUninitializedInstanceVariable]

    def __init__(self):
        raise TypeError(
            'EISData cannot be instantiated directly. '
            'Obtain instances through measurements or io methods.'
        )

    @classmethod
    def _wrap(cls, pseis: PSEISData) -> Self:
        obj = cls.__new__(cls)
        obj._inner = pseis
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
        """Title of the EIS data."""
        return self._inner.Title

    @property
    def frequency_type(self) -> AllowedFrequencyTypes:
        """Whether a single frequency or frequency scan was applied."""
        return str(self._inner.FreqType).lower()  # type: ignore

    @property
    def scan_type(self) -> AllowedScanTypes:
        """How the spectrum was scanned: fixed potential, potential scan, or time."""
        value = str(self._inner.ScanType)
        mapping = {'TimeScan': 'time', 'PGScan': 'potential', 'Fixed': 'fixed'}
        return mapping[value]  # type: ignore

    @property
    def dataset(self) -> DataSet:
        """Dataset with the arrays of this spectrum, keyed by array name."""
        return DataSet._wrap(self._inner.EISDataSet)

    @property
    def subscans(self) -> list[EISData]:
        """One spectrum per dc-potential level or per repetition of a time scan.

        Empty when the measurement only performed a single scan: see
        [has_subscans][]."""
        return [EISData._wrap(subscan) for subscan in self._inner.GetSubScans()]

    @property
    def n_points(self) -> int:
        """Number of points (including subscans)."""
        return self._inner.NPoints

    @property
    def n_frequencies(self) -> int:
        """Number of frequencies (per subscan)."""
        return self._inner.NFrequencies

    @property
    def n_subscans(self) -> int:
        """Number of subscans."""
        return len(self._inner.GetSubScans())

    @property
    def x_unit(self) -> str:
        """Unit of the x-axis array of the spectrum."""
        return self._inner.XUnit.ToString()

    @property
    def x_quantity(self) -> str:
        """Quantity of the x-axis array of the spectrum."""
        return self._inner.XUnit.Quantity

    @property
    def ocp_value(self) -> float:
        """Open circuit potential recorded with the spectrum in V.

        Determined before the measurement when the method measures versus OCP,
        and used as the reference for the applied dc-potentials."""
        return self._inner.OCPValue

    @property
    def has_subscans(self) -> bool:
        """Return True if data contains subscans, i.e. more than one frequency scan."""
        return self._inner.HasSubScans

    @property
    def mux_channel(self) -> int:
        """Multiplexer channel this data was measured on."""
        return self._inner.MuxChannel

    def get_data_for_frequency(self, frequency: int) -> dict[str, DataArray]:
        """Return the data measured at a single frequency.

        Parameters
        ----------
        frequency : int
            Index of the frequency to retrieve the data for, counting from 0 in
            the order the frequencies were measured.

        Returns
        -------
        dict[str, DataArray]
            Data are returned as a dictionary keyed by the data type.

        Raises
        ------
        ValueError
            If `frequency` is not a valid index for this spectrum.
        """
        if not (0 <= frequency < self.n_frequencies):
            raise ValueError(f'Frequency must be between 0 and {self.n_frequencies}')

        return {
            str(row.Key): DataArray._wrap(row.Value)
            for row in self._inner.GetDataArrayVsX(frequency)
        }

    def arrays(self) -> list[DataArray]:
        """Complete list of data arrays, including derived ones."""
        return list(self.dataset.values())

    def current_range(self) -> list[AllowedCurrentRanges]:
        """Current range the instrument used for each measured point, in point order."""
        return [
            cr_enum_to_string(self._inner.GetCurrentRange(val)) for val in range(self.n_points)
        ]

    @property
    def cdc(self) -> str:
        """Circuit description code (CDC) of the equivalent circuit fitted to this spectrum."""
        return self._inner.CDC

    @property
    def cdc_values(self) -> list[float]:
        """Fitted parameter values, in the order they appear in
        [cdc][]."""
        return list(self._inner.CDCValues)

    @property
    def id(self) -> int:
        """Unique identifier for this EIS data object."""
        return self._inner.GetHashCode()

    def metadata(self) -> EISDataMetadata:
        """Return eis data metadata as dataclass.

        Only non-derived arrays are listed in `columns`, `units` and `quantities`.
        """
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
        """Generate eis data metadata as JSON bytes."""

        return TypeAdapter(EISDataMetadata).dump_json(self.metadata())
