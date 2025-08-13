from __future__ import annotations

from ._shared import (
    CURRENT_RANGE,
    POTENTIAL_RANGE,
    get_method_estimated_duration,
    set_extra_value_mask,
)
from .techniques import (
    ChronoAmperometryParameters,
    ChronopotentiometryParameters,
    CyclicVoltammetryParameters,
    DifferentialPulseParameters,
    ElectrochemicalImpedanceSpectroscopyParameters,
    GalvanostaticImpedanceSpectroscopyParameters,
    LinearSweepParameters,
    MethodScriptParameters,
    MultiStepAmperometryParameters,
    OpenCircuitPotentiometryParameters,
    SquareWaveParameters,
)

__all__ = [
    'CURRENT_RANGE',
    'ChronoAmperometryParameters',
    'ChronopotentiometryParameters',
    'CyclicVoltammetryParameters',
    'DifferentialPulseParameters',
    'ElectrochemicalImpedanceSpectroscopyParameters',
    'GalvanostaticImpedanceSpectroscopyParameters',
    'LinearSweepParameters',
    'MethodScriptParameters',
    'MultiStepAmperometryParameters',
    'OpenCircuitPotentiometryParameters',
    'POTENTIAL_RANGE',
    'SquareWaveParameters',
    'get_method_estimated_duration',
    'set_extra_value_mask',
]
