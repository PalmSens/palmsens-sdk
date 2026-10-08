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
    # from ._data import Dataset
    from ._discover import discover
    from ._instance import Instance
    from ._instrument import InstrumentClaim, InstrumentRef
    from ._measurement import MeasurementJob, MeasurementRef
    from ._session import ClaimBatch, Session

    __all__ = [
        'ClaimBatch',
        'Instance',
        'InstrumentClaim',
        'InstrumentRef',
        'MeasurementJob',
        'MeasurementRef',
        'Session',
        'discover',
    ]
