"""
PyPalmSens: Take full control of your PalmSens instruments and automate electrochemistry experiments.

Provides an API to:

1. Discover, connect, and manage instruments
2. Configure and automate experiments
3. Read, write, and analyze measured data

Visit <https://dev.palmsens.com/python/latest/> for online documentation.
"""

from __future__ import annotations

from . import _libpalmsens

__sdk_version__: str = _libpalmsens.load()
__version__ = '1.11.0'

from . import (
    corrosion,
    data,
    energy,
    fitting,
    mixed_mode,  # deprecated, use stages
    settings,
    stages,
    types,
)
from ._instruments.comm_protocol import CommProtocol
from ._instruments.comm_protocol_async import CommProtocolAsync
from ._instruments.filesystem import DeviceFileSystem, DevicePath
from ._instruments.filesystem_async import DeviceFileSystemAsync
from ._instruments.instrument import Instrument, discover, discover_async
from ._instruments.instrument_manager import (
    InstrumentManager,
    connect,
    measure,
)
from ._instruments.instrument_manager_async import (
    InstrumentManagerAsync,
    connect_async,
    measure_async,
)
from ._instruments.instrument_pool import InstrumentPool
from ._instruments.instrument_pool_async import InstrumentPoolAsync
from ._io import (
    load_measurement,
    load_method_file,
    load_session_file,
    save_measurement,
    save_method_file,
    save_session_file,
)
from ._methods.mixed_mode import MixedMode
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
from ._stream import load_stream_file

__all__ = [
    'ACVoltammetry',
    'ChronoAmperometry',
    'ChronoCoulometry',
    'ChronoPotentiometry',
    'CommProtocol',
    'CommProtocolAsync',
    'CyclicVoltammetry',
    'DeviceFileSystem',
    'DeviceFileSystemAsync',
    'DevicePath',
    'DifferentialPulseVoltammetry',
    'ElectrochemicalImpedanceSpectroscopy',
    'FastAmperometry',
    'FastCyclicVoltammetry',
    'FastGalvanostaticImpedanceSpectroscopy',
    'FastImpedanceSpectroscopy',
    'GalvanostaticImpedanceSpectroscopy',
    'Instrument',
    'InstrumentManager',
    'InstrumentManagerAsync',
    'InstrumentPool',
    'InstrumentPoolAsync',
    'LinearSweepPotentiometry',
    'LinearSweepVoltammetry',
    'MethodScript',
    'MixedMode',
    'MultiStepAmperometry',
    'MultiStepPotentiometry',
    'MultiplePulseAmperometry',
    'NormalPulseVoltammetry',
    'OpenCircuitPotentiometry',
    'PulsedAmperometricDetection',
    'SquareWaveVoltammetry',
    'StrippingChronoPotentiometry',
    'connect',
    'connect_async',
    'corrosion',
    'data',
    'discover',
    'discover_async',
    'energy',
    'fitting',
    'load_measurement',
    'load_method_file',
    'load_session_file',
    'load_stream_file',
    'measure',
    'measure_async',
    'mixed_mode',
    'save_measurement',
    'save_method_file',
    'save_session_file',
    'settings',
    'stages',
    'types',
]
