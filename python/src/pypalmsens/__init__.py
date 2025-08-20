from __future__ import annotations

import sys

# Load dotnet platform dependencies and init SDK
if sys.platform == 'win32':
    from ._lib.windows import sdk_version
else:
    from ._lib.mono import sdk_version

__version__ = '0.0.1'
__sdk_version__ = sdk_version

from . import config, data, models
from ._instruments._instrument_manager import (
    InstrumentManager,
    connect,
    discover,
)
from ._instruments._instrument_manager_async import (
    InstrumentManagerAsync,
    connect_async,
    discover_async,
)
from ._io import load_method_file, load_session_file, save_method_file, save_session_file
from .methods.techniques import (
    ChronoAmperometry,
    ChronoPotentiometry,
    CyclicVoltammetry,
    DifferentialPulseVoltammetry,
    ElectrochemicalImpedanceSpectroscopy,
    GalvanostaticImpedanceSpectroscopy,
    LinearSweepVoltammetry,
    MethodScript,
    MultiStepAmperometry,
    OpenCircuitPotentiometry,
    SquareWaveVoltammetry,
)

__all__ = [
    'config',
    'data',
    'models',
    'connect',
    'connect_async',
    'discover',
    'discover_async',
    'load_method_file',
    'load_session_file',
    'save_method_file',
    'save_session_file',
    'InstrumentManager',
    'InstrumentManagerAsync',
    'ChronoAmperometry',
    'ChronoPotentiometry',
    'CyclicVoltammetry',
    'DifferentialPulseVoltammetry',
    'ElectrochemicalImpedanceSpectroscopy',
    'GalvanostaticImpedanceSpectroscopy',
    'LinearSweepVoltammetry',
    'MethodScript',
    'MultiStepAmperometry',
    'OpenCircuitPotentiometry',
    'SquareWaveVoltammetry',
]
