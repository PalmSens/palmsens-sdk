from __future__ import annotations

from enum import Enum

from .data_array import DataArray
from .dataset import DataSet


class EISValueType(Enum):
    X = 0
    Freq = 1
    Logf = 2
    LogZ = 3
    Edc = 4
    mEdc = 5
    Eac = 6
    Time = 7
    Idc = 8
    Iac = 9
    miDC = 10
    ZRe = 11
    ZIm = 12
    Z = 13
    MinPhase = 14
    Rct = 15
    LogY = 16
    YRe = 17
    YIm = 18
    Y = 19
    Cs = 20
    CsRe = 21
    CsIm = 22
    iDCinRange = 23
    AuxInput = 24


class EISData:
    def __init__(self, *, pseis):
        self.pseis = pseis

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
        return self.pseis.Title

    @property
    def frequency_type(self) -> str:
        """Frequency type."""
        return str(self.pseis.FreqType)

    @property
    def scan_type(self) -> str:
        """Scan type."""
        return str(self.pseis.ScanType)

    @property
    def dataset(self) -> DataSet:
        """Dataset which contains multiple arrays of values."""
        return DataSet(psdataset=self.pseis.EISDataSet)

    @property
    def subscans(self) -> list[EISData]:
        """Get list of subscans."""
        return [EISData(pseis=subscan) for subscan in self.pseis.GetSubScans()]

    @property
    def n_points(self) -> int:
        """Number of points (including subscans)."""
        return self.pseis.NPoints

    @property
    def n_frequencies(self) -> int:
        """Number of frequencies."""
        return self.pseis.NFrequencies

    @property
    def n_subscans(self) -> int:
        """Number of subscans."""
        return len(self.pseis.GetSubScans())

    @property
    def x_unit(self) -> str:
        """Unit for array."""
        return self.pseis.XUnit.ToString()

    @property
    def x_quantity(self) -> str:
        """Quantity for array."""
        return self.pseis.XUnit.Quantity

    @property
    def ocp_value(self) -> float:
        """OCP Value."""
        return self.pseis.OCPValue

    @property
    def has_subscans(self) -> bool:
        """Return True if data contains subscans."""
        return self.pseis.HasSubScans

    @property
    def mux_channel(self) -> int:
        """Mux channel."""
        return self.pseis.MuxChannel

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
            for row in self.pseis.GetDataArrayVsX(frequency)
        }

    def arrays(self) -> list[DataArray]:
        """Complete list of data arrays."""
        return list(self.dataset.values())

    def current_range(self) -> list[str]:
        """Current ranges for the measurement."""
        return [self.pseis.GetCurrentRange(val).Description for val in range(self.n_points)]

    def cdc(self) -> str:
        """Gets the CDC circuit for fitting."""
        return self.pseis.CDC

    def cdc_values(self) -> list[float]:
        """Return values for circuit description code (CDC)."""
        return list(self.pseis.CDCValues)
