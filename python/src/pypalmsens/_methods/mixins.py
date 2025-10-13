from __future__ import annotations

import attrs

from . import settings
from ._shared import CURRENT_RANGE, POTENTIAL_RANGE


def current_converter(value: CURRENT_RANGE | settings.CurrentRange) -> settings.CurrentRange:
    if isinstance(value, CURRENT_RANGE):
        return settings.CurrentRange(min=value, max=value, start=value)
    return value


@attrs.define(slots=False)
class CurrentRangeMixin:
    current_range: settings.CurrentRange = attrs.field(
        factory=settings.CurrentRange, converter=current_converter
    )
    """Set the autoranging current."""


def potential_converter(
    value: POTENTIAL_RANGE | settings.PotentialRange,
) -> settings.PotentialRange:
    if isinstance(value, POTENTIAL_RANGE):
        return settings.PotentialRange(min=value, max=value, start=value)
    return value


@attrs.define(slots=False)
class PotentialRangeMixin:
    potential_range: settings.PotentialRange = attrs.field(
        factory=settings.PotentialRange, converter=potential_converter
    )
    """Set the autoranging potential."""


@attrs.define(slots=False)
class PretreatmentMixin:
    pretreatment: settings.Pretreatment = attrs.field(factory=settings.Pretreatment)
    """Set the pretreatment settings."""


@attrs.define(slots=False)
class VersusOCPMixin:
    versus_ocp: settings.VersusOCP = attrs.field(factory=settings.VersusOCP)
    """Set the versus OCP settings."""


@attrs.define(slots=False)
class BiPotMixin:
    bipot: settings.BiPot = attrs.field(factory=settings.BiPot)
    """Set the bipot settings"""


@attrs.define(slots=False)
class PostMeasurementMixin:
    post_measurement: settings.PostMeasurement = attrs.field(factory=settings.PostMeasurement)
    """Set the post measurement settings."""


@attrs.define(slots=False)
class CurrentLimitsMixin:
    current_limits: settings.CurrentLimits = attrs.field(factory=settings.CurrentLimits)
    """Set the current limit settings."""


@attrs.define(slots=False)
class PotentialLimitsMixin:
    potential_limits: settings.PotentialLimits = attrs.field(factory=settings.PotentialLimits)
    """Set the potential limit settings"""


@attrs.define(slots=False)
class ChargeLimitsMixin:
    charge_limits: settings.ChargeLimits = attrs.field(factory=settings.ChargeLimits)
    """Set the charge limit settings"""


@attrs.define(slots=False)
class IrDropCompensationMixin:
    ir_drop_compensation: settings.IrDropCompensation = attrs.field(
        factory=settings.IrDropCompensation
    )
    """Set the iR drop compensation settings."""


@attrs.define(slots=False)
class EquilibrationTriggersMixin:
    equilibrion_triggers: settings.EquilibrationTriggers = attrs.field(
        factory=settings.EquilibrationTriggers
    )
    """Set the trigger at equilibration settings."""


@attrs.define(slots=False)
class MeasurementTriggersMixin:
    measurement_triggers: settings.MeasurementTriggers = attrs.field(
        factory=settings.MeasurementTriggers
    )
    """Set the trigger at measurement settings."""


@attrs.define(slots=False)
class DelayTriggersMixin:
    delay_triggers: settings.DelayTriggers = attrs.field(factory=settings.DelayTriggers)
    """Set the delayed trigger at measurement settings."""


@attrs.define(slots=False)
class MultiplexerMixin:
    multiplexer: settings.Multiplexer = attrs.field(factory=settings.Multiplexer)
    """Set the multiplexer settings"""


@attrs.define(slots=False)
class DataProcessingMixin:
    data_processing: settings.DataProcessing = attrs.field(factory=settings.DataProcessing)
    """Set the data processing settings."""


@attrs.define(slots=False)
class GeneralMixin:
    general: settings.General = attrs.field(factory=settings.General)
    """Sets general/other settings."""
