from . import _model
from ._public import LablinkInfo


class TranslationError(Exception):
    """Raised when the hub returned data that cannot be mapped."""


def _to_info(m: _model.LablinkInfoResult) -> LablinkInfo:
    """Translate a `LablinkInfoResult` wire model to the public `LablinkInfo`."""
    if m is None:
        raise TranslationError('no info payload returned')

    if m.Name is None:
        raise TranslationError("payload is missing 'Name'")

    if m.Version is None:
        raise TranslationError("payload is missing 'Version'")

    return LablinkInfo(
        name=m.Name,
        version=m.Version,
        special_version=m.SpecialVersion or '',
        os_version=m.OsVersion or '',
        model=m.LablinkModel or '',
        serial_number=(m.Serial.Serial if m.Serial and m.Serial.Serial else ''),
        is_measuring=m.IsMeasuring or False,
    )
