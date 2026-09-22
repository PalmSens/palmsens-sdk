"""Connect, manage, and start measurements on Lablink instances."""

from __future__ import annotations

_supported = True

try:
    import PalmSens.Sdk  # noqa
except (ImportError, ModuleNotFoundError):
    _supported = False
finally:
    IS_SUPPORTED = _supported

if IS_SUPPORTED:
    from ._data import Dataset
    from ._instance import Instance, discover
    from ._instrument import InstrumentClaim, InstrumentRef
    from ._measurement import Measurement, MeasurementJob, MeasurementRef
    from ._session import Session

    __all__ = [
        'Dataset',
        'Instance',
        'InstrumentClaim',
        'InstrumentRef',
        'Measurement',
        'MeasurementJob',
        'MeasurementRef',
        'Session',
        'discover',
    ]
