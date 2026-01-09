from __future__ import annotations

from typing import Literal

import PalmSens
from PalmSens import Method as PSMethod
from PalmSens import MuxMethod as PSMuxMethod
from pydantic import Field
from typing_extensions import override

from .._helpers import single_to_double
from .base import BaseSettings
from .shared import (
    AllowedCurrentRanges,
    AllowedPotentialRanges,
    convert_bools_to_int,
    convert_int_to_bools,
    cr_enum_to_string,
    cr_string_to_enum,
    pr_enum_to_string,
    pr_string_to_enum,
)
from .base import BaseSettings
from .base_model import BaseModel


class CurrentRange(BaseSettings):
    """Set the autoranging current."""

    max: AllowedCurrentRanges = '10mA'
    """Maximum current range.

    See `pypalmsens.settings.AllowedCurrentRanges` for options."""

    min: AllowedCurrentRanges = '1uA'
    """Minimum current range.

    See `pypalmsens.settings.AllowedCurrentRanges` for options."""

    start: AllowedCurrentRanges = '100uA'
    """Start current range.

    See `pypalmsens.settings.AllowedCurrentRanges` for options."""

    @override
    def _update_psmethod(self, psmethod: PSMethod, /):
        psmethod.Ranging.MaximumCurrentRange = cr_string_to_enum(self.max)
        psmethod.Ranging.MinimumCurrentRange = cr_string_to_enum(self.min)
        psmethod.Ranging.StartCurrentRange = cr_string_to_enum(self.start)

    @override
    def _update_params(self, psmethod: PSMethod, /):
        self.max = cr_enum_to_string(psmethod.Ranging.MaximumCurrentRange)
        self.min = cr_enum_to_string(psmethod.Ranging.MinimumCurrentRange)
        self.start = cr_enum_to_string(psmethod.Ranging.StartCurrentRange)


class PotentialRange(BaseSettings):
    """Set the autoranging potential."""

    max: AllowedPotentialRanges = '1V'
    """Maximum potential range.

    See `pypalmsens.settings.AllowedPotentialRanges` for options."""

    min: AllowedPotentialRanges = '1mV'
    """Minimum potential range.

    See `pypalmsens.settings.AllowedPotentialRanges` for options."""

    start: AllowedPotentialRanges = '1V'
    """Start potential range.

    See `pypalmsens.settings.AllowedPotentialRanges` for options."""

    @override
    def _update_psmethod(self, psmethod: PSMethod, /):
        psmethod.RangingPotential.MaximumPotentialRange = pr_string_to_enum(self.max)
        psmethod.RangingPotential.MinimumPotentialRange = pr_string_to_enum(self.min)
        psmethod.RangingPotential.StartPotentialRange = pr_string_to_enum(self.start)

    @override
    def _update_params(self, psmethod: PSMethod, /):
        self.max = pr_enum_to_string(psmethod.RangingPotential.MaximumPotentialRange)
        self.min = pr_enum_to_string(psmethod.RangingPotential.MinimumPotentialRange)
        self.start = pr_enum_to_string(psmethod.RangingPotential.StartPotentialRange)


class Pretreatment(BaseSettings):
    """Set the measurement pretreatment settings."""

    deposition_potential: float = 0.0
    """Deposition potential in V."""

    deposition_time: float = 0.0
    """Deposition time in s."""

    conditioning_potential: float = 0.0
    """Conditioning potential in V."""

    conditioning_time: float = 0.0
    """Conditioning time in s."""

    @override
    def _update_psmethod(self, psmethod: PSMethod, /):
        psmethod.DepositionPotential = self.deposition_potential
        psmethod.DepositionTime = self.deposition_time
        psmethod.ConditioningPotential = self.conditioning_potential
        psmethod.ConditioningTime = self.conditioning_time

    @override
    def _update_params(self, psmethod: PSMethod, /):
        self.deposition_potential = single_to_double(psmethod.DepositionPotential)
        self.deposition_time = single_to_double(psmethod.DepositionTime)
        self.conditioning_potential = single_to_double(psmethod.ConditioningPotential)
        self.conditioning_time = single_to_double(psmethod.ConditioningTime)


class VersusOCP(BaseSettings):
    """Set the versus OCP settings."""

    mode: int = 0
    """Set versus OCP mode.

    Possible values:
    * 0 = disable versus OCP
    * 1 = vertex 1 potential
    * 2 = vertex 2 potential
    * 3 = vertex 1 & 2 potential
    * 4 = begin potential
    * 5 = begin & vertex 1 potential
    * 6 = begin & vertex 2 potential
    * 7 = begin & vertex 1 & 2 potential
    """

    max_ocp_time: float = 20.0
    """Maximum OCP time in s."""

    stability_criterion: float = 0.0
    """Stability criterion (potential/time) in mV/s.

    If equal to 0 means no stability criterion.
    If larger than 0, then the value is taken as the stability threshold.
    """

    @override
    def _update_psmethod(self, psmethod: PSMethod, /):
        psmethod.OCPmode = self.mode
        psmethod.OCPMaxOCPTime = self.max_ocp_time
        psmethod.OCPStabilityCriterion = self.stability_criterion

    @override
    def _update_params(self, psmethod: PSMethod, /):
        self.mode = psmethod.OCPmode
        self.max_ocp_time = single_to_double(psmethod.OCPMaxOCPTime)
        self.stability_criterion = single_to_double(psmethod.OCPStabilityCriterion)


class BiPotCurrentRange(BaseModel):
    """Set the BiPot auto ranging current."""

    max: AllowedCurrentRanges = '10mA'
    """Maximum current range.

    See `pypalmsens.settings.AllowedCurrentRanges` for options."""

    min: AllowedCurrentRanges = '1uA'
    """Minimum current range.

    See `pypalmsens.settings.AllowedCurrentRanges` for options."""

    start: AllowedCurrentRanges = '100uA'
    """Start current range.

    See `pypalmsens.settings.AllowedCurrentRanges` for options."""


class BiPot(BaseSettings):
    """Set the bipot settings."""

    _MODES: tuple[Literal['constant', 'offset'], ...] = ('constant', 'offset')

    mode: Literal['constant', 'offset'] = 'constant'
    """Set the bipotential mode.

    Possible values: `constant` or `offset`"""

    potential: float = 0.0
    """Set the bipotential in V."""

    current_range: AllowedCurrentRanges | BiPotCurrentRange = '1uA'
    """Set the bipotential current range.

    Can be a fixed current range or a ranging current. See the specifications for your instrument.
    Internally, a fixed current range is represented by an autoranging current with equal min/max ranges.

    See `pypalmsens.settings.AllowedCurrentRanges` for options."""

    @override
    def _update_psmethod(self, psmethod: PSMethod, /):
        bipot_num = self._MODES.index(self.mode)
        psmethod.BipotModePS = PalmSens.Method.EnumPalmSensBipotMode(bipot_num)
        psmethod.BiPotPotential = self.potential

        if isinstance(self.current_range, str):
            crmin = crmax = crstart = self.current_range
        else:
            crmax = self.current_range.max
            crmin = self.current_range.min
            crstart = self.current_range.start

        psmethod.BipotRanging.MaximumCurrentRange = cr_string_to_enum(crmax)
        psmethod.BipotRanging.MinimumCurrentRange = cr_string_to_enum(crmin)
        psmethod.BipotRanging.StartCurrentRange = cr_string_to_enum(crstart)

    @override
    def _update_params(self, psmethod: PSMethod, /):
        self.mode = self._MODES[int(psmethod.BipotModePS)]
        self.potential = single_to_double(psmethod.BiPotPotential)

        crmax = cr_enum_to_string(psmethod.BipotRanging.MaximumCurrentRange)
        crmin = cr_enum_to_string(psmethod.BipotRanging.MinimumCurrentRange)
        crstart = cr_enum_to_string(psmethod.BipotRanging.StartCurrentRange)

        if crmax == crmin == crstart:
            self.current_range = crmin
        else:
            self.current_range = BiPotCurrentRange(
                max=crmax,
                min=crmin,
                start=crstart,
            )


class PostMeasurement(BaseSettings):
    """Set the post measurement settings."""

    cell_on_after_measurement: bool = False
    """Enable/disable cell after measurement."""

    standby_potential: float = 0.0
    """Standby potential (V) for use with cell on after measurement."""

    standby_time: float = 0.0
    """Standby time (s) for use with cell on after measurement."""

    @override
    def _update_psmethod(self, psmethod: PSMethod, /):
        psmethod.CellOnAfterMeasurement = self.cell_on_after_measurement
        psmethod.StandbyPotential = self.standby_potential
        psmethod.StandbyTime = self.standby_time

    @override
    def _update_params(self, psmethod: PSMethod, /):
        self.cell_on_after_measurement = psmethod.CellOnAfterMeasurement
        self.standby_potential = single_to_double(psmethod.StandbyPotential)
        self.standby_time = single_to_double(psmethod.StandbyTime)


class CurrentLimits(BaseSettings):
    """Set the limit settings.

    Depending on the method, this will:
    - Abort the measurement
    - Reverse the scan instead (CV)
    - Proceed to the next stage (Mixed Mode)
    """

    max: None | float = None
    """Set limit current max in µA."""

    min: None | float = None
    """Set limit current min in µA."""

    @override
    def _update_psmethod(self, psmethod: PSMethod, /):
        if self.max is not None:
            psmethod.UseLimitMaxValue = True
            psmethod.LimitMaxValue = self.max
        else:
            psmethod.UseLimitMaxValue = False

        if self.min is not None:
            psmethod.UseLimitMinValue = True
            psmethod.LimitMinValue = self.min
        else:
            psmethod.UseLimitMinValue = False

    @override
    def _update_params(self, psmethod: PSMethod, /):
        if psmethod.UseLimitMaxValue:
            self.max = single_to_double(psmethod.LimitMaxValue)
        else:
            self.max = None

        if psmethod.UseLimitMinValue:
            self.min = single_to_double(psmethod.LimitMinValue)
        else:
            self.min = None


class PotentialLimits(BaseSettings):
    """Set the limit settings.

    Depending on the method, this will:
    - Abort the measurement
    - Proceed to the next stage (Mixed Mode)
    """

    max: None | float = None
    """Set limit potential max in V."""

    min: None | float = None
    """Set limit potential min in V."""

    @override
    def _update_psmethod(self, psmethod: PSMethod, /):
        if self.max is not None:
            psmethod.UseLimitMaxValue = True
            psmethod.LimitMaxValue = self.max
        else:
            psmethod.UseLimitMaxValue = False

        if self.min is not None:
            psmethod.UseLimitMinValue = True
            psmethod.LimitMinValue = self.min
        else:
            psmethod.UseLimitMinValue = False

    @override
    def _update_params(self, psmethod: PSMethod, /):
        if psmethod.UseLimitMaxValue:
            self.max = single_to_double(psmethod.LimitMaxValue)
        else:
            self.max = None

        if psmethod.UseLimitMinValue:
            self.min = single_to_double(psmethod.LimitMinValue)
        else:
            self.min = None


class ChargeLimits(BaseSettings):
    """Set the charge limit settings."""

    max: None | float = None
    """Set limit charge max in µC."""

    min: None | float = None
    """Set limit charge min in µC."""

    @override
    def _update_psmethod(self, psmethod: PSMethod, /):
        if self.max is not None:
            psmethod.UseChargeLimitMax = True
            psmethod.ChargeLimitMax = self.max
        else:
            psmethod.UseChargeLimitMax = False

        if self.min is not None:
            psmethod.UseChargeLimitMin = True
            psmethod.ChargeLimitMin = self.min
        else:
            psmethod.UseChargeLimitMin = False

    @override
    def _update_params(self, psmethod: PSMethod, /):
        if psmethod.UseChargeLimitMax:
            self.max = single_to_double(psmethod.ChargeLimitMax)
        else:
            self.max = None

        if psmethod.UseChargeLimitMin:
            self.min = single_to_double(psmethod.ChargeLimitMin)
        else:
            self.min = None


class IrDropCompensation(BaseSettings):
    """Set the iR drop compensation settings."""

    resistance: None | float = None
    """Set the iR compensation resistance in Ω"""

    @override
    def _update_psmethod(self, psmethod: PSMethod, /):
        if self.resistance:
            psmethod.UseIRDropComp = True
            psmethod.IRDropCompRes = self.resistance
        else:
            psmethod.UseIRDropComp = False

    @override
    def _update_params(self, psmethod: PSMethod, /):
        if psmethod.UseIRDropComp:
            self.resistance = single_to_double(psmethod.IRDropCompRes)
        else:
            self.resistance = None


class EquilibrationTriggers(BaseSettings):
    """Set the trigger at equilibration settings.

    If enabled, set one or more digital outputs at the start of
    the equilibration period.
    """

    d0: bool = False
    """If True, enable trigger at d0 high."""

    d1: bool = False
    """If True, enable trigger at d1 high."""

    d2: bool = False
    """If True, enable trigger at d2 high."""

    d3: bool = False
    """If True, enable trigger at d3 high."""

    @override
    def _update_psmethod(self, psmethod: PSMethod, /):
        if any((self.d0, self.d1, self.d2, self.d3)):
            psmethod.UseTriggerOnEquil = True
            psmethod.TriggerValueOnEquil = convert_bools_to_int(
                (self.d0, self.d1, self.d2, self.d3)
            )
        else:
            psmethod.UseTriggerOnEquil = False

    @override
    def _update_params(self, psmethod: PSMethod, /):
        if psmethod.UseTriggerOnEquil:
            self.d0, self.d1, self.d2, self.d3 = convert_int_to_bools(
                psmethod.TriggerValueOnEquil
            )
        else:
            self.d0 = False
            self.d1 = False
            self.d2 = False
            self.d3 = False


class MeasurementTriggers(BaseSettings):
    """Set the trigger at measurement settings.

    If enabled, set one or more digital outputs at the start measurement,
    """

    d0: bool = False
    """If True, enable trigger at d0 high."""

    d1: bool = False
    """If True, enable trigger at d1 high."""

    d2: bool = False
    """If True, enable trigger at d2 high."""

    d3: bool = False
    """If True, enable trigger at d3 high."""

    @override
    def _update_psmethod(self, psmethod: PSMethod, /):
        if any((self.d0, self.d1, self.d2, self.d3)):
            psmethod.UseTriggerOnStart = True
            psmethod.TriggerValueOnStart = convert_bools_to_int(
                (self.d0, self.d1, self.d2, self.d3)
            )
        else:
            psmethod.UseTriggerOnEquil = False

    @override
    def _update_params(self, psmethod: PSMethod, /):
        if psmethod.UseTriggerOnStart:
            self.d0, self.d1, self.d2, self.d3 = convert_int_to_bools(
                psmethod.TriggerValueOnStart
            )
        else:
            self.d0 = False
            self.d1 = False
            self.d2 = False
            self.d3 = False


class DelayTriggers(BaseSettings):
    """Set the delayed trigger at measurement settings.

    If enabled, set one or more digital outputs at the start measurement after a delay,
    """

    delay: float = 0.5
    """Delay in s after the measurement has started.

    The value will be rounded to interval time * number of data points.
    """

    d0: bool = False
    """If True, enable trigger at d0 high."""

    d1: bool = False
    """If True, enable trigger at d1 high."""

    d2: bool = False
    """If True, enable trigger at d2 high."""

    d3: bool = False
    """If True, enable trigger at d3 high."""

    @override
    def _update_psmethod(self, psmethod: PSMethod, /):
        psmethod.TriggerDelayPeriod = self.delay

        if any((self.d0, self.d1, self.d2, self.d3)):
            psmethod.UseTriggerOnDelay = True
            psmethod.TriggerValueOnDelay = convert_bools_to_int(
                (self.d0, self.d1, self.d2, self.d3)
            )
        else:
            psmethod.UseTriggerOnDelay = False

    @override
    def _update_params(self, psmethod: PSMethod, /):
        self.delay = single_to_double(psmethod.TriggerDelayPeriod)

        if psmethod.UseTriggerOnDelay:
            self.d0, self.d1, self.d2, self.d3 = convert_int_to_bools(
                psmethod.TriggerValueOnDelay
            )
        else:
            self.d0 = False
            self.d1 = False
            self.d2 = False
            self.d3 = False


class Multiplexer(BaseSettings):
    """Set the multiplexer settings."""

    _MODES: tuple[Literal['none', 'consecutive', 'alternate'], ...] = (
        'none',
        'consecutive',
        'alternate',
    )

    mode: Literal['none', 'consecutive', 'alternate'] = 'none'
    """Set multiplexer mode.

    Possible values:
    * 'none' = No multiplexer (disable)
    * 'consecutive
    * 'alternate
    """

    channels: list[int] = Field(default_factory=list)
    """Set multiplexer channels

    This is defined as a list of indexes for which channels to enable (max 128).
    For example, [0,3,7]. In consecutive mode all selections are valid.

    In alternating mode the first channel must be selected and all other
    channels should be consecutive i.e. (channel 1, channel 2, channel 3 and so on).
    """
    connect_sense_to_working_electrode: bool = False
    """Connect the sense electrode to the working electrode. Default is False."""

    combine_reference_and_counter_electrodes: bool = False
    """Combine the reference and counter electrodes. Default is False."""

    use_channel_1_reference_and_counter_electrodes: bool = False
    """Use channel 1 reference and counter electrodes for all working electrodes. Default is False."""

    set_unselected_channel_working_electrode: int = 0
    """Set the unselected channel working electrode to 0 = Disconnected / floating, 1 = Ground, 2 = Standby potential. Default is 0."""

    @override
    def _update_psmethod(self, psmethod: PSMethod, /):
        # Create a mux8r2 multiplexer settings settings object
        mux_mode = self._MODES.index(self.mode) - 1
        psmethod.MuxMethod = PSMuxMethod(mux_mode)

        # disable all mux channels (range 0-127)
        for i in range(len(psmethod.UseMuxChannel)):
            psmethod.UseMuxChannel[i] = False

        # set the selected mux channels
        for i in self.channels:
            psmethod.UseMuxChannel[i - 1] = True

        psmethod.MuxSett.ConnSEWE = self.connect_sense_to_working_electrode
        psmethod.MuxSett.ConnectCERE = self.combine_reference_and_counter_electrodes
        psmethod.MuxSett.CommonCERE = self.use_channel_1_reference_and_counter_electrodes
        psmethod.MuxSett.UnselWE = PSMethod.MuxSettings.UnselWESetting(
            self.set_unselected_channel_working_electrode
        )

    @override
    def _update_params(self, psmethod: PSMethod, /):
        self.mode = self._MODES[int(psmethod.MuxMethod) + 1]

        self.channels = [
            i + 1 for i in range(len(psmethod.UseMuxChannel)) if psmethod.UseMuxChannel[i]
        ]

        self.connect_sense_to_working_electrode = psmethod.MuxSett.ConnSEWE
        self.combine_reference_and_counter_electrodes = psmethod.MuxSett.ConnectCERE
        self.use_channel_1_reference_and_counter_electrodes = psmethod.MuxSett.CommonCERE
        self.set_unselected_channel_working_electrode = int(psmethod.MuxSett.UnselWE)


class DataProcessing(BaseSettings):
    """Set the data processing settings."""

    smooth_level: int = 0
    """Set the default curve post processing filter.

    Possible values:

    - -1: no filter
    - 0: spike rejection
    - 1: spike rejection + Savitsky-golay window 5
    - 2: spike rejection + Savitsky-golay window 9
    - 3: spike rejection + Savitsky-golay window 15
    - 4: spike rejection + Savitsky-golay window 25
    """

    min_height: float = 0.0
    """Determines the minimum peak height in µA for peak finding.

    Peaks lower than this value are rejected."""

    min_width: float = 0.1
    """The minimum peak width for peak finding.

    The value is in the unit of the curves X axis (V).
    Peaks narrower than this value are rejected (default: 0.1 V)."""

    @override
    def _update_psmethod(self, psmethod: PSMethod, /):
        psmethod.SmoothLevel = self.smooth_level
        psmethod.MinPeakHeight = self.min_height
        psmethod.MinPeakWidth = self.min_width

    @override
    def _update_params(self, psmethod: PSMethod, /):
        self.smooth_level = psmethod.SmoothLevel
        self.min_width = single_to_double(psmethod.MinPeakWidth)
        self.min_height = single_to_double(psmethod.MinPeakHeight)


class General(BaseSettings):
    """Sets general/other settings."""

    save_on_internal_storage: bool = False
    """Save on internal storage."""

    use_hardware_sync: bool = False
    """Use hardware synchronization with other channels/instruments."""

    notes: str = ''
    """Add some user notes for use with this technique."""

    power_frequency: Literal[50, 60] = 50
    """Set the DC mains filter in Hz.

    Adjusts sampling on instrument to account for mains frequency.
    Set to 50 Hz or 60 Hz depending on your region (default: 50)."""

    @override
    def _update_psmethod(self, psmethod: PSMethod, /):
        psmethod.SaveOnDevice = self.save_on_internal_storage
        psmethod.UseHWSync = self.use_hardware_sync
        psmethod.Notes = self.notes
        psmethod.PowerFreq = self.power_frequency

    @override
    def _update_params(self, psmethod: PSMethod, /):
        self.save_on_internal_storage = psmethod.SaveOnDevice
        self.use_hardware_sync = psmethod.UseHWSync
        self.notes = psmethod.Notes
        self.power_frequency = psmethod.PowerFreq
