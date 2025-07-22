from dataclasses import dataclass

from PalmSens import ExtraValueMask
from PalmSens.Techniques import SquareWave as PSSquareWave

from .potential_method import PotentialMethodParameters


@dataclass
class SquareWaveParameters(PotentialMethodParameters):
    """Create square wave method parameters.

    Attributes
    ----------
    equilibration_time : float
        Equilibration time in s (default: 0.0)
    begin_potential : float
        Begin potential in V (default: -0.5)
    end_potential : float
        End potential in V (default: 0.5)
    step_potential : float
        Step potential in V (default: 0.1)
    frequency : float
        Frequency in Hz (default: 10.0)
    amplitude : float
        Amplitude in V as half peak-to-peak value (default: 0.05).
    record_forward_and_reverse_currents : bool
        Record forward and reverse currents (default: False)
    """

    # square wave voltammetry settings
    equilibration_time: float = 0.0
    begin_potential: float = -0.5
    end_potential: float = 0.5
    step_potential: float = 0.1
    frequency: float = 10.0
    amplitude: float = 0.05
    record_forward_and_reverse_currents: bool = False

    def update_dotnet_method(self, *, dotnet_method):
        """Update method with linear sweep settings."""
        super().update_dotnet_method(dotnet_method=dotnet_method)

        dotnet_method.EquilibrationTime = self.equilibration_time
        dotnet_method.BeginPotential = self.begin_potential
        dotnet_method.EndPotential = self.end_potential
        dotnet_method.StepPotential = self.step_potential
        dotnet_method.Frequency = self.frequency
        dotnet_method.PulseAmplitude = self.amplitude

        if self.record_forward_and_reverse_currents:
            extra_values = int(dotnet_method.ExtraValueMsk) | int(
                ExtraValueMask.IForwardReverse
            )
            dotnet_method.ExtraValueMsk = ExtraValueMask(extra_values)

    def to_dotnet_method(self):
        """Convert parameters to dotnet method."""
        obj = PSSquareWave()

        self.update_dotnet_method(dotnet_method=obj)

        return obj


def square_wave_voltammetry(**kwargs) -> PSSquareWave:
    """Alias for LinearSweep for backwards compatibility"""
    swv = SquareWaveParameters(**kwargs)
    return swv.to_dotnet_method()
