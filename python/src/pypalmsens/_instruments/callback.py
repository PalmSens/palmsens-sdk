from __future__ import annotations

from collections.abc import Generator
from dataclasses import dataclass, field
from typing import Literal, Protocol

import PalmSens
from PalmSens.Comm import StatusEventArgs
from typing_extensions import override

from .._data.data_array import DataArray
from .._data.data_value import CurrentReading, PotentialReading
from .._data.dataset import DataSet
from ..settings import (
    AllowedDeviceState,
)


@dataclass(slots=True)
class CallbackData:
    """Data returned by the new data callback."""

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
        for i in range(self.start, self.index + 1):
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
    """Data returned by the EIS new data callback."""

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
        for i in range(self.start, self.index + 1):
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
class Status:
    """Device Status class."""

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
    def potential_reading(self) -> PotentialReading:
        """Potential reading dataclass."""
        return PotentialReading._from_psobject(self._status.PotentialReading)

    @property
    def current(self) -> float:
        """Current value in µA."""
        return self._status.CurrentReading.Value

    @property
    def current_reading(self) -> CurrentReading:
        """Current reading dataclass."""
        return CurrentReading._from_psobject(self._status.CurrentReading)

    @property
    def current_we2(self) -> float:
        """Current WE2 value."""
        return self._status.CurrentReadingWE2.Value

    @property
    def current_reading_we2(self) -> CurrentReading:
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
        """Measured"""
        return self._status.Noise


class CallbackStatus(Protocol):
    """Type signature for idle status callback."""

    def __call__(self, status: Status): ...
