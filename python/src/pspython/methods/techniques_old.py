from __future__ import annotations

from . import techniques


def cyclic_voltammetry(**kwargs):
    """Alias for backwards compatibility."""
    cv = techniques.CyclicVoltammetryParameters(**kwargs)
    return cv.to_psmethod()


def linear_sweep_voltammetry(**kwargs):
    """Alias for backwards compatibility."""
    method = techniques.LinearSweepParameters(**kwargs)
    return method.to_psmethod()


def square_wave_voltammetry(**kwargs):
    """Alias for backwards compatibility."""
    method = techniques.SquareWaveParameters(**kwargs)
    return method.to_psmethod()


def differential_pulse_voltammetry(**kwargs):
    """Alias for backwards compatibility."""
    method = techniques.DifferentialPulseParameters(**kwargs)
    return method.to_psmethod()


def chronoamperometry(**kwargs):
    """Alias for backwards compatibility."""
    method = techniques.ChronoAmperometryParameters(**kwargs)
    return method.to_psmethod()


def multi_step_amperometry(**kwargs):
    """Alias for backwards compatibility."""
    method = techniques.MultiStepAmperometryParameters(**kwargs)
    return method.to_psmethod()


def open_circuit_potentiometry(**kwargs):
    """Alias for backwards compatibility."""
    method = techniques.OpenCircuitPotentiometryParameters(**kwargs)
    return method.to_psmethod()


def chronopotentiometry(**kwargs):
    """Alias for backwards compatibility."""
    method = techniques.ChronopotentiometryParameters(**kwargs)
    return method.to_psmethod()


def electrochemical_impedance_spectroscopy(**kwargs):
    """Alias for backwards compatibility."""
    method = techniques.ElectrochemicalImpedanceSpectroscopyParameters(**kwargs)
    return method.to_psmethod()


def galvanostatic_impedance_spectroscopy(**kwargs):
    """Alias for backwards compatibility."""
    method = techniques.GalvanostaticImpedanceSpectroscopyParameters(**kwargs)
    return method.to_psmethod()


def method_script_sandbox(**kwargs):
    """Alias for backwards compatibility."""
    method = techniques.MethodScriptParameters(**kwargs)
    return method.to_psmethod()
