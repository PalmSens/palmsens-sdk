from __future__ import annotations

import sys

# Load dotnet platform dependencies and init SDK
if sys.platform == 'win32':
    from ._lib.windows import sdk_version
else:
    from ._lib.mono import sdk_version

__version__ = '1.0.0'
__sdk_version__ = sdk_version

from . import data, fitting, settings
from ._instruments.instrument_manager import (
    InstrumentManager,
    connect,
    discover,
)
from ._instruments.instrument_manager_async import (
    InstrumentManagerAsync,
    connect_async,
    discover_async,
)
from ._io import load_method_file, load_session_file, save_method_file, save_session_file
from ._methods.techniques import (
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
    'settings',
    'data',
    'fitting',
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
