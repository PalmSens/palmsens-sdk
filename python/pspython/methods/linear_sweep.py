from dataclasses import dataclass

from PalmSens.Techniques import LinearSweep as PSLinearSweep

from .potential_method import PotentialMethodParameters


@dataclass
class LinearSweepParameters(PotentialMethodParameters):
    """Create linear sweep method parameters.

    Attributes
    ----------
    begin_potential : float
        Begin potential in V (default: -0.5)
    end_potential : float
        End potential in V (default: 0.5)
    step_potential : float
        Step potential in V (default: 0.1)
    scanrate : float
        Scan rate in V/s (default: 1.0)
    """

    # linear sweep voltammetry settings
    begin_potential: float = -0.5  # potential (V)
    end_potential: float = 0.5  # potential (V)
    step_potential: float = 0.1  # potential (V)
    scanrate: float = 1.0  # potential/time (V/s)

    def update_dotnet_method(self, *, dotnet_method):
        """Update method with linear sweep settings."""
        super().update_dotnet_method(dotnet_method=dotnet_method)

        dotnet_method.BeginPotential = self.begin_potential
        dotnet_method.EndPotential = self.end_potential
        dotnet_method.StepPotential = self.step_potential
        dotnet_method.Scanrate = self.scanrate

    def to_dotnet_method(self):
        """Convert parameters to dotnet method."""
        obj = PSLinearSweep()

        self.update_dotnet_method(dotnet_method=obj)

        return obj


def linear_sweep_voltammetry(**kwargs):
    """Alias for LinearSweep for backwards compatibility"""
    lsv = LinearSweepParameters(**kwargs)
    return lsv.to_dotnet_method()
