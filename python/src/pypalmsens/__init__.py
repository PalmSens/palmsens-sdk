from __future__ import annotations

from . import _libpalmsens

__sdk_version__ = _libpalmsens.load()
__version__ = '1.3.3'

from . import (
    data,
    fitting,
    mixed_mode,
    settings,
)
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
from ._instruments.instrument_pool import InstrumentPool
from ._instruments.instrument_pool_async import InstrumentPoolAsync
from ._io import load_method_file, load_session_file, save_method_file, save_session_file
from ._methods.techniques import (
    ACVoltammetry,
    ChronoAmperometry,
    ChronoCoulometry,
    ChronoPotentiometry,
    CyclicVoltammetry,
    DifferentialPulseVoltammetry,
    ElectrochemicalImpedanceSpectroscopy,
    FastAmperometry,
    FastCyclicVoltammetry,
    FastGalvanostaticImpedanceSpectroscopy,
    FastImpedanceSpectroscopy,
    GalvanostaticImpedanceSpectroscopy,
    LinearSweepPotentiometry,
    LinearSweepVoltammetry,
    MethodScript,
    MultiplePulseAmperometry,
    MultiStepAmperometry,
    MultiStepPotentiometry,
    NormalPulseVoltammetry,
    OpenCircuitPotentiometry,
    PulsedAmperometricDetection,
    SquareWaveVoltammetry,
    StrippingChronoPotentiometry,
)

__all__ = [
    'settings',
    'data',
    'fitting',
    'mixed_mode',
    'connect',
    'connect_async',
    'discover',
    'discover_async',
    'load_method_file',
    'load_session_file',
    'save_method_file',
    'save_session_file',
    'InstrumentManager',
    'FastAmperometry',
    'InstrumentManagerAsync',
    'InstrumentPool',
    'InstrumentPoolAsync',
    'ACVoltammetry',
    'ChronoAmperometry',
    'ChronoCoulometry',
    'ChronoPotentiometry',
    'CyclicVoltammetry',
    'DifferentialPulseVoltammetry',
    'ElectrochemicalImpedanceSpectroscopy',
    'FastCyclicVoltammetry',
    'FastGalvanostaticImpedanceSpectroscopy',
    'FastImpedanceSpectroscopy',
    'GalvanostaticImpedanceSpectroscopy',
    'LinearSweepPotentiometry',
    'LinearSweepVoltammetry',
    'MethodScript',
    'MultiplePulseAmperometry',
    'MultiStepAmperometry',
    'MultiStepPotentiometry',
    'NormalPulseVoltammetry',
    'OpenCircuitPotentiometry',
    'PulsedAmperometricDetection',
    'SquareWaveVoltammetry',
    'StrippingChronoPotentiometry',
]
