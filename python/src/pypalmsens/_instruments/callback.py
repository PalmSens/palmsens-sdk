from __future__ import annotations

from collections.abc import Generator
from dataclasses import dataclass, field
from typing import Literal, Protocol

import PalmSens
from PalmSens.Comm import StatusEventArgs
from typing_extensions import override

from .._data.data_array import DataArray
from .._data.dataset import DataSet
from .._methods.shared import cr_enum_to_string, pr_enum_to_string
from ..settings import (
    AllowedCurrentRanges,
    AllowedDeviceState,
    AllowedPotentialRanges,
    AllowedReadingStatus,
    AllowedTimingStatus,
)


@dataclass(slots=True)
class CallbackData:
    x_array: DataArray
    """Data array for the x variable."""

    y_array: DataArray
    """Data array for the y variable."""

    start: int
    """Start index for the new data."""

    @property
    def index(self) -> int:
        """Index of last point."""
        return len(self.x_array) - 1

    def last_datapoint(self) -> dict[str, float]:
        """Return last measured data point."""
        return {
            'index': self.index,
            'x': self.x_array[-1],
            'y': self.y_array[-1],
        }

    def new_datapoints(self) -> Generator[dict[str, float]]:
        """Return new data points since last callback."""
        for i in range(self.start, self.index):
            yield {
                'x': self.x_array[i],
                'y': self.y_array[i],
                'index': i,
            }

    @override
    def __str__(self):
        return str(self.last_datapoint())


@dataclass(slots=True)
class CallbackDataEIS:
    data: DataSet
    """EIS dataset."""

    start: int
    """Start index for the new data."""

    @property
    def index(self) -> int:
        """Index of last point."""
        return self.data.n_points - 1

    def last_datapoint(self) -> dict[str, float]:
        """Return last measured data point."""
        ret = {array.name: array[-1] for array in self.data.arrays()}
        ret['index'] = self.index
        return ret

    def new_datapoints(self) -> Generator[dict[str, float]]:
        """Return new data points since last callback."""
        for i in range(self.start, self.index):
            ret = {array.name: array[i] for array in self.data.arrays()}
            ret['index'] = i
            yield ret

    @override
    def __str__(self):
        return str(self.last_datapoint())


class Callback(Protocol):
    """Type signature for callback."""

    def __call__(self, data: CallbackData | CallbackDataEIS): ...


@dataclass(slots=True)
class PotentialReading:
    potential_range: AllowedPotentialRanges
    potential: float
    potential_in_range: float
    timing_status: AllowedTimingStatus
    reading_status: AllowedReadingStatus

    @override
    def __str__(self):
        return f'{self.potential:.3f} V'

    @classmethod
    def _from_psobject(cls, obj: PalmSens.Data.VoltageReading):
        return cls(
            potential_range=pr_enum_to_string(obj.Range),
            potential=obj.Value,
            potential_in_range=obj.ValueInRange,
            timing_status=str(obj.ReadingStatus),  # type: ignore
            reading_status=str(obj.TimingStatus),  # type: ignore
        )


@dataclass(slots=True)
class CurrentReading:
    current_range: AllowedCurrentRanges
    current: float
    current_in_range: float
    timing_status: AllowedTimingStatus
    reading_status: AllowedReadingStatus

    @override
    def __str__(self):
        return f'{self.current_in_range:.3f} * {self.current_range}'

    @classmethod
    def _from_psobject(cls, obj: PalmSens.Data.CurrentReading):
        return cls(
            current_range=cr_enum_to_string(obj.CurrentRange),
            current=obj.Value,
            current_in_range=obj.ValueInRange,
            timing_status=str(obj.ReadingStatus),  # type:ignore
            reading_status=str(obj.TimingStatus),  # type:ignore
        )


@dataclass(slots=True)
class Status:
    _status: PalmSens.Comm.Status = field(repr=False)
    device_state: AllowedDeviceState = 'Unknown'
    """Device state."""

    @classmethod
    def _from_event_args(cls, args: StatusEventArgs) -> Status:
        return cls(
            _status=args.GetStatus(),
            device_state=str(args.DeviceState),  # type:ignore
        )

    @override
    def __str__(self):
        return str(
            {'current': str(self.current_reading), 'potential': str(self.potential_reading)}
        )

    @property
    def pretreatment_phase(
        self,
    ) -> Literal['None', 'Conditioning', 'Depositing', 'Equilibrating']:
        """Pretreatment phase."""
        return str(self._status.PretreatmentPhase)  # type:ignore

    @property
    def potential(self) -> float:
        """Potential in V"""
        return self._status.PotentialReading.Value

    @property
    def potential_reading(self):
        """Potential reading dataclass."""
        return PotentialReading._from_psobject(self._status.PotentialReading)

    @property
    def current(self) -> float:
        """Current value in µA."""
        return self._status.CurrentReading.Value

    @property
    def current_reading(self):
        """Current reading dataclass."""
        return CurrentReading._from_psobject(self._status.CurrentReading)

    @property
    def current_we2(self) -> float:
        """Current WE2 value."""
        return self._status.CurrentReadingWE2.Value

    @property
    def current_reading_we2(self):
        """Current reading dataclass for WE2."""
        return CurrentReading._from_psobject(self._status.CurrentReadingWE2)

    @property
    def aux_input(self) -> float:
        """Raw aux input."""
        return self._status.AuxInput

    @property
    def aux_input_as_voltage(self) -> float:
        """Aux input as V."""
        return self._status.GetAuxInputAsVoltage()

    @property
    def corrected_bipot_current(self) -> float:
        """Corrected bipot current in the current range."""
        return self._status.GetCorrectedBipotCurrent()

    @property
    def noise(self) -> float:
        return self._status.Noise


class CallbackStatus(Protocol):
    """Type signature for idle status callback."""

    def __call__(self, status: Status): ...
