from dataclasses import dataclass

from PalmSens.Techniques import Potentiometry as PSPotentiometry

from ._shared import (
    get_current_range,
    get_potential_range,
    set_extra_value_mask,
)
from .time_method import TimeMethodParameters


@dataclass
class PotentiometryParameters(TimeMethodParameters):
    """Create potentiometry method parameters.

    Attributes
    ----------
    potential_range_max : PalmSens.PotentialRange
        Maximum potential range (default: 1 V).
        Use `get_potential_range()` to get the range.
    potential_range_min : PalmSens.PotentialRange
        Minimum potential range (default: 10 mV).
        Use `get_potential_range()` to get the range.
    potential_range_start : PalmSens.PotentialRange
        Start potential range (default: 1 V).
        Use `get_potential_range()` to get the range.

    current : float
        Current in applied current range (default: 0.0)
    applied_current_range : PalmSens.CurrentRange
        Applied current range (default: 100 µA).
        Use `get_current_range()` to get the range.
    interval_time : float
        Interval time in s (default: 0.1)
    run_time : float
        Run time in s (default: 1.0)

    record_auxiliary_input : bool
        Record auxiliary input (default: False)
    record_cell_potential : bool
        Record cell potential (default: False) [counter electrode vs ground]
    record_we_current : bool
        Record working electrode current (default: False)

    use_limit_potential_max : bool
        Use limit potential max (default: False)
    limit_potential_max : float
        Limit potential max in V (default: 0.0)
    use_limit_potential_min : bool
        Use limit potential min (default: False)
    limit_potential_min : float
        Limit potential min in V (default: 0.0)

    """

    # potential
    potential_range_max: int = get_potential_range(7)
    potential_range_min: int = get_potential_range(1)
    potential_range_start: int = get_potential_range(7)

    # chronopotentiometry settings
    current: float = 0.0  # in applied current range
    applied_current_range: int = get_current_range(6)  # in applied current range
    interval_time: float = 0.1  # Time (s)
    run_time: float = 1.0  # Time (s)

    # record extra value settings
    record_auxiliary_input: bool = False
    record_cell_potential: bool = False
    record_we_current: bool = False

    # limit settings
    use_limit_potential_max: bool = False
    limit_potential_max: float = 0.0  # in V
    use_limit_potential_min: bool = False
    limit_potential_min: float = 0.0  # in V

    def update_dotnet_method(self, *, dotnet_method):
        """Update method with potentiometry settings."""
        # Set the autoranging potential for a given method
        dotnet_method.RangingPotential.MaximumPotentialRange = self.potential_range_max
        dotnet_method.RangingPotential.MinimumPotentialRange = self.potential_range_min
        dotnet_method.RangingPotential.StartPotentialRange = self.potential_range_start

        # chronopotentiometry settings
        dotnet_method.Current = self.current
        dotnet_method.AppliedCurrentRange = self.applied_current_range
        dotnet_method.IntervalTime = self.interval_time
        dotnet_method.RunTime = self.run_time

        set_extra_value_mask(
            dotnet_method,
            record_auxiliary_input=self.record_auxiliary_input,
            record_cell_potential=self.record_cell_potential,
            record_we_current=self.record_we_current,
            record_we_current_range=self.applied_current_range,
        )

        # Set the limit settings for a given method
        dotnet_method.UseLimitMaxValue = self.use_limit_potential_max
        dotnet_method.LimitMaxValue = self.limit_potential_max
        dotnet_method.UseLimitMinValue = self.use_limit_potential_min
        dotnet_method.LimitMinValue = self.limit_potential_min

    def to_dotnet_method(self):
        """Convert parameters to dotnet method."""
        obj = PSPotentiometry()

        super().update_dotnet_method(dotnet_method=obj)
        self.update_dotnet_method(dotnet_method=obj)

        return obj


def chronopotentiometry(**kwargs):
    """Alias for Potentiometry for backwards compatibility"""
    cp = PotentiometryParameters(**kwargs)
    return cp.to_dotnet_method()
