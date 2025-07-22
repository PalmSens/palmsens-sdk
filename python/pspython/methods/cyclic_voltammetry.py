from dataclasses import dataclass

from PalmSens import Method as PSMethod
from PalmSens.Techniques import CyclicVoltammetry as PSCyclicVoltammetry

from .potential_method import PotentialMethodParameters


@dataclass
class CyclicVoltammetryParameters(PotentialMethodParameters):
    """Create cyclic voltammetry method parameters.

    Attributes
    ----------
    equilibration_time : float
        Equilibration time in s (default: 0.0)
    begin_potential: float
        Begin potential in V (default: -0.5)
    vertex1_potential: float
        Vertex 1 potential in V (default: 0.5)
    vertex2_potential: float
        Vertex 2 potential in V (default: -0.5)
    step_potential: float
        Step potential in V (default: 0.1)
    scanrate: float
        Scan rate in V/s (default: 1.0)
    n_scans: float
        Number of scans (default: 1)
    """

    # cyclic voltammetry settings
    equilibration_time: float = 0.0  # Time (s)
    begin_potential: float = -0.5  # potential (V)
    vertex1_potential: float = 0.5  # potential (V)
    vertex2_potential: float = -0.5  # potential (V)
    step_potential: float = 0.1  # potential (V)
    scanrate: float = 1.0  # potential/time (V/s)
    n_scans: float = 1  # number of cycles

    def update_dotnet_method(self, *, dotnet_method):
        """Update method with cyclic voltammetry settings."""
        super().update_dotnet_method(dotnet_method=dotnet_method)

        dotnet_method.BeginPotential = self.begin_potential
        dotnet_method.Vtx1Potential = self.vertex1_potential
        dotnet_method.Vtx2Potential = self.vertex2_potential
        dotnet_method.StepPotential = self.step_potential
        dotnet_method.Scanrate = self.scanrate
        dotnet_method.nScans = self.n_scans

    def to_dotnet_method(self):
        """Convert parameters to dotnet method."""
        obj = PSCyclicVoltammetry()

        self.update_dotnet_method(dotnet_method=obj)

        return obj

    @classmethod
    def from_dotnet_method(cls, dotnet_method: PSMethod) -> 'CyclicVoltammetryParameters':
        """Generate parameters from dotnet method."""
        raise NotImplementedError


def cyclic_voltammetry(**kwargs):
    """Alias for CyclicVoltammetry for backwards compatibility"""
    cv = CyclicVoltammetryParameters(**kwargs)
    return cv.to_dotnet_method()
