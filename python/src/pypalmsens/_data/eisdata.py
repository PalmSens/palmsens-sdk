from __future__ import annotations

from enum import Enum

from .data_array import DataArray
from .dataset import DataSet


class EISValueType(Enum):
    X = 0
    """X values"""
    Freq = 1
    """FixedFrequency values"""
    Logf = 2
    """Log(F) values"""
    LogZ = 3
    """Log(Z) values"""
    Edc = 4
    """E DC values"""
    mEdc = 5
    """Mean E DC values"""
    Eac = 6
    """E AC values"""
    Time = 7
    """I values"""
    Idc = 8
    """E values"""
    Iac = 9
    """I AC values"""
    miDC = 10
    """measured I DC values"""
    ZRe = 11
    """Z' values"""
    ZIm = 12
    """-Z'' values"""
    Z = 13
    """Z values"""
    MinPhase = 14
    """-Phase values"""
    Rct = 15
    """RCT values"""
    LogY = 16
    """E or t values"""
    YRe = 17
    """Y' values"""
    YIm = 18
    """Y'' values"""
    Y = 19
    """Y (Admittance) values"""
    Cs = 20
    """Cs (Capacitance in Series) values"""
    CsRe = 21
    """Cs Real values"""
    CsIm = 22
    """-Cs imaginary values"""
    iDCinRange = 23
    AuxInput = 24
    """AuxInput values"""


class EISData:
    """Python wrapper for .NET EISdata class.

    Parameters
    ----------
    pseis
        Reference to .NET EISdata object.
    """

    def __init__(self, *, pseis):
        self._pseis = pseis

    def __repr__(self):
        data = [
            f'title={self.title}',
            f'n_points={self.n_points}',
            f'n_frequencies={self.n_frequencies}',
        ]
        if self.has_subscans:
            data.append(f'n_subscans={self.n_subscans}')

        s = ', '.join(data)
        return f'{self.__class__.__name__}({s})'

    @property
    def title(self) -> str:
        """Tite for EIS data."""
        return self._pseis.Title

    @property
    def frequency_type(self) -> str:
        """Frequency type."""
        return str(self._pseis.FreqType)

    @property
    def scan_type(self) -> str:
        """Scan type."""
        return str(self._pseis.ScanType)

    @property
    def dataset(self) -> DataSet:
        """Dataset which contains multiple arrays of values."""
        return DataSet(psdataset=self._pseis.EISDataSet)

    @property
    def subscans(self) -> list[EISData]:
        """Get list of subscans."""
        return [EISData(pseis=subscan) for subscan in self._pseis.GetSubScans()]

    @property
    def n_points(self) -> int:
        """Number of points (including subscans)."""
        return self._pseis.NPoints

    @property
    def n_frequencies(self) -> int:
        """Number of frequencies."""
        return self._pseis.NFrequencies

    @property
    def n_subscans(self) -> int:
        """Number of subscans."""
        return len(self._pseis.GetSubScans())

    @property
    def x_unit(self) -> str:
        """Unit for array."""
        return self._pseis.XUnit.ToString()

    @property
    def x_quantity(self) -> str:
        """Quantity for array."""
        return self._pseis.XUnit.Quantity

    @property
    def ocp_value(self) -> float:
        """OCP Value."""
        return self._pseis.OCPValue

    @property
    def has_subscans(self) -> bool:
        """Return True if data contains subscans."""
        return self._pseis.HasSubScans

    @property
    def mux_channel(self) -> int:
        """Mux channel."""
        return self._pseis.MuxChannel

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
            str(row.Key): DataArray(psarray=row.Value)
            for row in self._pseis.GetDataArrayVsX(frequency)
        }

    def arrays(self) -> list[DataArray]:
        """Complete list of data arrays."""
        return list(self.dataset.values())

    def current_range(self) -> list[str]:
        """Current ranges for the measurement."""
        return [self._pseis.GetCurrentRange(val).Description for val in range(self.n_points)]

    @property
    def cdc(self) -> str:
        """Gets the CDC circuit for fitting."""
        return self._pseis.CDC

    @property
    def cdc_values(self) -> list[float]:
        """Return values for circuit description code (CDC)."""
        return list(self._pseis.CDCValues)
