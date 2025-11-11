from __future__ import annotations

from typing import Literal

import attrs
import PalmSens
from PalmSens import Method as PSMethod
from PalmSens import MuxMethod as PSMuxMethod
from typing_extensions import override

from .._shared import single_to_double
from ._shared import (
    CURRENT_RANGE,
    POTENTIAL_RANGE,
    convert_bools_to_int,
    convert_int_to_bools,
)
from .base import BaseSettings


@attrs.define
class CurrentRange(BaseSettings):
    """Set the autoranging current for a given method."""

    max: CURRENT_RANGE = CURRENT_RANGE.cr_10_mA
    """Maximum current range.

    Use `CURRENT_RANGE` to define the range."""

    min: CURRENT_RANGE = CURRENT_RANGE.cr_1_uA
    """Minimum current range.

    Use `CURRENT_RANGE` to define the range."""

    start: CURRENT_RANGE = CURRENT_RANGE.cr_100_uA
    """Start current range.

    Use `CURRENT_RANGE` to define the range."""

    @override
    def _update_psmethod(self, psmethod: PSMethod, /):
        psmethod.Ranging.MaximumCurrentRange = self.max._to_psobj()
        psmethod.Ranging.MinimumCurrentRange = self.min._to_psobj()
        psmethod.Ranging.StartCurrentRange = self.start._to_psobj()

    @override
    def _update_params(self, psmethod: PSMethod, /):
        self.max = CURRENT_RANGE._from_psobj(psmethod.Ranging.MaximumCurrentRange)
        self.min = CURRENT_RANGE._from_psobj(psmethod.Ranging.MinimumCurrentRange)
        self.start = CURRENT_RANGE._from_psobj(psmethod.Ranging.StartCurrentRange)


@attrs.define
class PotentialRange(BaseSettings):
    """Set the autoranging potential for a given method."""

    max: POTENTIAL_RANGE = POTENTIAL_RANGE.pr_1_V
    """Maximum potential range.

    Use `POTENTIAL_RANGE` to define the range."""

    min: POTENTIAL_RANGE = POTENTIAL_RANGE.pr_1_mV
    """Minimum potential range.

    Use `POTENTIAL_RANGE` to define the range."""

    start: POTENTIAL_RANGE = POTENTIAL_RANGE.pr_1_V
    """Start potential range.

    Use `POTENTIAL_RANGE` to define the range."""

    @override
    def _update_psmethod(self, psmethod: PSMethod, /):
        psmethod.RangingPotential.MaximumPotentialRange = self.max._to_psobj()
        psmethod.RangingPotential.MinimumPotentialRange = self.min._to_psobj()
        psmethod.RangingPotential.StartPotentialRange = self.start._to_psobj()

    @override
    def _update_params(self, psmethod: PSMethod, /):
        self.max = POTENTIAL_RANGE._from_psobj(psmethod.RangingPotential.MaximumPotentialRange)
        self.min = POTENTIAL_RANGE._from_psobj(psmethod.RangingPotential.MinimumPotentialRange)
        self.start = POTENTIAL_RANGE._from_psobj(psmethod.RangingPotential.StartPotentialRange)


@attrs.define
class Pretreatment(BaseSettings):
    """Set the pretreatment settings for a given method."""

    deposition_potential: float = 0.0
    """Deposition potential in V"""

    deposition_time: float = 0.0
    """Deposition time in s"""

    conditioning_potential: float = 0.0
    """Conditioning potential in V"""

    conditioning_time: float = 0.0
    """Conditioning time in s"""

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


@attrs.define
class VersusOCP(BaseSettings):
    """Set the versus OCP settings for a given method."""

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
    """Maximum OCP time in s"""

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


@attrs.define
class BiPot(BaseSettings):
    """Set the bipot settings for a given method."""

    _MODES: tuple[Literal['constant', 'offset'], ...] = ('constant', 'offset')

    mode: Literal['constant', 'offset'] = 'constant'
    """Set the bipotential mode.

    Possible values: `constant` or `offset`"""

    potential: float = 0.0
    """Set the bipotential in V"""

    current_range_max: CURRENT_RANGE = CURRENT_RANGE.cr_10_mA
    """Maximum bipotential current range in mA.

    Use `CURRENT_RANGE` to define the range."""

    current_range_min: CURRENT_RANGE = CURRENT_RANGE.cr_1_uA
    """Minimum bipotential current range.

    Use `CURRENT_RANGE` to define the range."""

    current_range_start: CURRENT_RANGE = CURRENT_RANGE.cr_100_uA
    """Start bipotential current range.

    Use `CURRENT_RANGE` to define the range."""

    @override
    def _update_psmethod(self, psmethod: PSMethod, /):
        bipot_num = self._MODES.index(self.mode)
        psmethod.BipotModePS = PalmSens.Method.EnumPalmSensBipotMode(bipot_num)
        psmethod.BiPotPotential = self.potential
        psmethod.BipotRanging.MaximumCurrentRange = self.current_range_max._to_psobj()
        psmethod.BipotRanging.MinimumCurrentRange = self.current_range_min._to_psobj()
        psmethod.BipotRanging.StartCurrentRange = self.current_range_start._to_psobj()

    @override
    def _update_params(self, psmethod: PSMethod, /):
        self.mode = self._MODES[int(psmethod.BipotModePS)]
        self.potential = single_to_double(psmethod.BiPotPotential)
        self.current_range_max = CURRENT_RANGE._from_psobj(
            psmethod.BipotRanging.MaximumCurrentRange
        )
        self.current_range_min = CURRENT_RANGE._from_psobj(
            psmethod.BipotRanging.MinimumCurrentRange
        )
        self.current_range_start = CURRENT_RANGE._from_psobj(
            psmethod.BipotRanging.StartCurrentRange
        )


@attrs.define
class PostMeasurement(BaseSettings):
    """Set the post measurement settings for a given method."""

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


@attrs.define
class CurrentLimits(BaseSettings):
    """Set the limit settings for a given method.

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


@attrs.define
class PotentialLimits(BaseSettings):
    """Set the limit settings for a given method.

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


@attrs.define
class ChargeLimits(BaseSettings):
    """Set the charge limit settings for a given method."""

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


@attrs.define
class IrDropCompensation(BaseSettings):
    """Set the iR drop compensation settings for a given method."""

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


@attrs.define
class EquilibrationTriggers(BaseSettings):
    """Set the trigger at equilibration settings for a given method.

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


@attrs.define
class MeasurementTriggers(BaseSettings):
    """Set the trigger at measurement settings for a given method.

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


@attrs.define
class DelayTriggers(BaseSettings):
    """Set the delayed trigger at measurement settings for a given method.

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


@attrs.define
class Multiplexer(BaseSettings):
    """Set the multiplexer settings for a given method."""

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

    channels: list[int] = attrs.field(factory=list)
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


@attrs.define
class DataProcessing(BaseSettings):
    """Set the data processing settings for a given method."""

    smooth_level: int = 0
    """Set the default curve post processing filter.

    Possible values:
    * -1 = no filter
    *  0 = spike rejection
    *  1 = spike rejection + Savitsky-golay window 5
    *  2 = spike rejection + Savitsky-golay window 9
    *  3 = spike rejection + Savitsky-golay window 15
    *  4 = spike rejection + Savitsky-golay window 25
    """

    min_height: float = 0.0
    """Determines the minimum peak height in µA for peak finding.

    Peaks lower than this value are neglected."""
    min_width: float = 0.1
    """The minimum peak width for peak finding.

    The value is in the unit of the curves X axis (V).
    Peaks narrower than this value are neglected (default: 0.1 V)."""

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


@attrs.define
class General(BaseSettings):
    """Sets general/other settings for a given method."""

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
