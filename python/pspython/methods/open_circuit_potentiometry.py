from PalmSens.Techniques import OpenCircuitPotentiometry as PSOpenCircuitPotentiometry

from ._shared import (
    get_current_range,
    set_extra_value_mask,
)
from .potentiometry import PotentiometryParameters


class OpenCircuitPotentiometryParameters(PotentiometryParameters):
    """Create open circuit potentiometry method parameters.

    Attributes
    ----------
    current : float
        Cannot be set, because it is always 0 for this technique.
    applied_current_range : PalmSens.CurrentRange
        Not used.
    interval_time : float
        Interval time in s (default: 0.1)
    run_time : float
        Run time in s (default: 1.0)

    record_we_current_range: int
        Record working electrode current range (default: 1 µA)
        Use `get_current_range()` to get the range.
    """

    # open circuit potentiometry settings
    current: float = 0.0  # not used
    applied_current_range: int = get_current_range(6)  # not used
    interval_time: float = 0.1  # Time (s)
    run_time: float = 1.0  # Time (s)

    # record extra value settings
    record_we_current_range: int = get_current_range(4)

    def update_dotnet_method(self, *, dotnet_method):
        """Update method with open circuit potentiometry settings."""
        super().update_dotnet_method(dotnet_method=dotnet_method)

        # chronopotentiometry settings
        dotnet_method.IntervalTime = self.interval_time
        dotnet_method.RunTime = self.run_time

        set_extra_value_mask(
            dotnet_method,
            record_auxiliary_input=self.record_auxiliary_input,
            record_cell_potential=self.record_cell_potential,
            record_we_current=self.record_we_current,
            record_we_current_range=self.record_we_current_range,
        )

    def to_dotnet_method(self):
        """Convert parameters to dotnet method."""
        obj = PSOpenCircuitPotentiometry()

        self.update_dotnet_method(dotnet_method=obj)

        return obj


def open_circuit_potentiometry(**kwargs):
    """Alias for Potentiometry for backwards compatibility"""
    cp = OpenCircuitPotentiometryParameters(**kwargs)
    return cp.to_dotnet_method()
