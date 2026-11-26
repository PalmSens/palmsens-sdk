"""Connect, manage, and start measurements on Lablink instances."""

from __future__ import annotations

_supported = True

try:
    import PalmSens.Sdk  # noqa
except (ImportError, ModuleNotFoundError):
    _supported = False
finally:
    SDK_AVAILABLE = _supported

import importlib.util

_REQUIRED = ('packaging', 'pandas', 'signalrcore', 'xarray', 'zeroconf')
missing = [dep for dep in _REQUIRED if importlib.util.find_spec(dep) is None]
if missing:
    exc = ImportError(f'pypalmsens.lablink requires: {", ".join(missing)}')
    exc.add_note('\nInstall the extra: pip install "pypalmsens[lablink]"')
    raise exc

from ._errors import (
    LablinkApiError,
    LablinkClientError,
    LablinkServerError,
    NoActiveMeasurementError,
)
from ._instance import Instance
from ._instrument import Instrument, InstrumentClaim, InstrumentClaimBatch
from ._measurement import Measurement, MeasurementJob
from ._session import Session
from ._version import SUPPORTED

__all__ = [
    'SUPPORTED',
    'Instance',
    'Instrument',
    'InstrumentClaim',
    'InstrumentClaimBatch',
    'LablinkApiError',
    'LablinkClientError',
    'LablinkServerError',
    'Measurement',
    'MeasurementJob',
    'NoActiveMeasurementError',
    'Session',
    'discover',
]
