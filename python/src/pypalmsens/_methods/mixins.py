from __future__ import annotations

from pydantic import Field, field_validator

from . import settings
from ._shared import (
    AllowedCurrentRanges,
    AllowedPotentialRanges,
)
from .base_model import BaseModel


class CurrentRangeMixin(BaseModel):
    current_range: settings.CurrentRange = Field(default_factory=settings.CurrentRange)
    """Set the autoranging current."""

    @field_validator('current_range', mode='before')
    @classmethod
    def current_converter(
        cls, value: AllowedCurrentRanges | settings.CurrentRange
    ) -> settings.CurrentRange:
        if isinstance(value, str):
            return settings.CurrentRange(min=value, max=value, start=value)
        return value


class PotentialRangeMixin(BaseModel):
    potential_range: settings.PotentialRange = Field(default_factory=settings.PotentialRange)
    """Set the autoranging potential."""

    @field_validator('potential_range', mode='before')
    @classmethod
    def potential_converter(
        cls, value: AllowedPotentialRanges | settings.PotentialRange
    ) -> settings.PotentialRange:
        if isinstance(value, str):
            return settings.PotentialRange(min=value, max=value, start=value)
        return value


class PretreatmentMixin(BaseModel):
    pretreatment: settings.Pretreatment = Field(default_factory=settings.Pretreatment)
    """Set the pretreatment settings."""


class VersusOCPMixin(BaseModel):
    versus_ocp: settings.VersusOCP = Field(default_factory=settings.VersusOCP)
    """Set the versus OCP settings."""


class BiPotMixin(BaseModel):
    bipot: settings.BiPot = Field(default_factory=settings.BiPot)
    """Set the bipot settings."""


class PostMeasurementMixin(BaseModel):
    post_measurement: settings.PostMeasurement = Field(default_factory=settings.PostMeasurement)
    """Set the post measurement settings."""


class CurrentLimitsMixin(BaseModel):
    current_limits: settings.CurrentLimits = Field(default_factory=settings.CurrentLimits)
    """Set the current limit settings."""


class PotentialLimitsMixin(BaseModel):
    potential_limits: settings.PotentialLimits = Field(default_factory=settings.PotentialLimits)
    """Set the potential limit settings."""


class ChargeLimitsMixin(BaseModel):
    charge_limits: settings.ChargeLimits = Field(default_factory=settings.ChargeLimits)
    """Set the charge limit settings."""


class IrDropCompensationMixin(BaseModel):
    ir_drop_compensation: settings.IrDropCompensation = Field(
        default_factory=settings.IrDropCompensation
    )
    """Set the iR drop compensation settings."""


class EquilibrationTriggersMixin(BaseModel):
    equilibrion_triggers: settings.EquilibrationTriggers = Field(
        default_factory=settings.EquilibrationTriggers
    )
    """Set the trigger at equilibration settings."""


class MeasurementTriggersMixin(BaseModel):
    measurement_triggers: settings.MeasurementTriggers = Field(
        default_factory=settings.MeasurementTriggers
    )
    """Set the trigger at measurement settings."""


class DelayTriggersMixin(BaseModel):
    delay_triggers: settings.DelayTriggers = Field(default_factory=settings.DelayTriggers)
    """Set the delayed trigger at measurement settings."""


class MultiplexerMixin(BaseModel):
    multiplexer: settings.Multiplexer = Field(default_factory=settings.Multiplexer)
    """Set the multiplexer settings."""


class DataProcessingMixin(BaseModel):
    data_processing: settings.DataProcessing = Field(default_factory=settings.DataProcessing)
    """Set the data processing settings."""


class GeneralMixin(BaseModel):
    general: settings.General = Field(default_factory=settings.General)
    """Sets general/other settings."""
