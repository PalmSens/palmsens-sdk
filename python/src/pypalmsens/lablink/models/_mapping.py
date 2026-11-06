from typing import Any

from . import _wire
from ._public import InstrumentInfo, LablinkInfo, MeasurementInfo


class TranslationError(Exception):
    """Raised when the hub returned data that cannot be mapped."""


def _to_lablink_info(data: _wire.LablinkInfoResult) -> LablinkInfo:
    """Translate a `LablinkInfoResult` wire model to the public `LablinkInfo`."""
    if data is None:
        raise TranslationError('no info payload returned')

    if data.Name is None:
        raise TranslationError("payload is missing 'Name'")

    if data.Version is None:
        raise TranslationError("payload is missing 'Version'")

    return LablinkInfo(
        name=data.Name,
        version=data.Version,
        special_version=data.SpecialVersion or '',
        os_version=data.OsVersion or '',
        model=data.LablinkModel or '',
        serial_number=(data.Serial.Serial if data.Serial and data.Serial.Serial else ''),
        is_measuring=data.IsMeasuring or False,
    )


def _to_instrument_info(data: dict[str, Any]) -> InstrumentInfo:
    """Map a raw instrument dict to an InstrumentInfo."""
    return InstrumentInfo(
        custom_name=data['CustomInstrumentName'] or None,
        default_name=data['DefaultInstrumentName'],
        is_claimed=data['IsClaimed'],
        claim_owner=data['ClaimOwnerUsername'] or None,
        is_in_error=data['IsInErrorState'],
        is_measuring=data['IsMeasuring'],
        model=data['Model'],
        multichannel_id=data['MultiChannelId'],
        multichannel_index=data['MultiChannelIndex'],
        in_multichannel_group=data['BelongsToMultiChannelInstrument'],
    )


def _to_measurement_info(data: dict[str, Any]) -> MeasurementInfo:
    return MeasurementInfo()
