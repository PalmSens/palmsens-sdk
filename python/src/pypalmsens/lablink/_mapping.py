from . import _model
from ._public import InstrumentInfo, LablinkInfo, MeasurementInfo


class TranslationError(Exception):
    """Raised when the hub returned data that cannot be mapped."""


def _to_lablink_info(m: _model.LablinkInfoResult) -> LablinkInfo:
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


def _to_instrument_info(inner: dict) -> InstrumentInfo:
    """Map a raw instrument dict to an InstrumentInfo."""
    return InstrumentInfo(
        custom_name=inner['CustomInstrumentName'] or None,
        default_name=inner['DefaultInstrumentName'],
        is_claimed=inner['IsClaimed'],
        claim_owner=inner['ClaimOwnerUsername'] or None,
        is_in_error=inner['IsInErrorState'],
        is_measuring=inner['IsMeasuring'],
        model=inner['Model'],
        multichannel_id=inner['MultiChannelId'],
        multichannel_index=inner['MultiChannelIndex'],
        in_multichannel_group=inner['BelongsToMultiChannelInstrument'],
    )


def _to_measurement_info(inner: dict) -> MeasurementInfo:
    return MeasurementInfo()
