from __future__ import annotations

from typing import Literal, Protocol, runtime_checkable

import attrs
import PalmSens
from PalmSens import Method as PSMethod
from PalmSens import MuxMethod as PSMuxMethod

from pypalmsens._shared import single_to_double

from ._shared import (
    CURRENT_RANGE,
    POTENTIAL_RANGE,
    convert_bools_to_int,
    convert_int_to_bools,
)


@runtime_checkable
class CommonSettings(Protocol):
    """Protocol to provide generic methods for parameters."""

    def _update_psmethod(self, *, obj): ...
    def _update_params(self, *, obj): ...


@attrs.define
class CurrentRange(CommonSettings):
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

    def _update_psmethod(self, *, obj):
        obj.Ranging.MaximumCurrentRange = self.max._to_psobj()
        obj.Ranging.MinimumCurrentRange = self.min._to_psobj()
        obj.Ranging.StartCurrentRange = self.start._to_psobj()

    def _update_params(self, *, obj):
        self.max = CURRENT_RANGE._from_psobj(obj.Ranging.MaximumCurrentRange)
        self.min = CURRENT_RANGE._from_psobj(obj.Ranging.MinimumCurrentRange)
        self.start = CURRENT_RANGE._from_psobj(obj.Ranging.StartCurrentRange)


@attrs.define
class PotentialRange(CommonSettings):
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

    def _update_psmethod(self, *, obj):
        obj.RangingPotential.MaximumPotentialRange = self.max._to_psobj()
        obj.RangingPotential.MinimumPotentialRange = self.min._to_psobj()
        obj.RangingPotential.StartPotentialRange = self.start._to_psobj()

    def _update_params(self, *, obj):
        self.max = POTENTIAL_RANGE._from_psobj(obj.RangingPotential.MaximumPotentialRange)
        self.min = POTENTIAL_RANGE._from_psobj(obj.RangingPotential.MinimumPotentialRange)
        self.start = POTENTIAL_RANGE._from_psobj(obj.RangingPotential.StartPotentialRange)


@attrs.define
class Pretreatment(CommonSettings):
    """Set the pretreatment settings for a given method."""

    deposition_potential: float = 0.0
    """Deposition potential in V"""

    deposition_time: float = 0.0
    """Deposition time in s"""

    conditioning_potential: float = 0.0
    """Conditioning potential in V"""

    conditioning_time: float = 0.0
    """Conditioning time in s"""

    def _update_psmethod(self, *, obj):
        obj.DepositionPotential = self.deposition_potential
        obj.DepositionTime = self.deposition_time
        obj.ConditioningPotential = self.conditioning_potential
        obj.ConditioningTime = self.conditioning_time

    def _update_params(self, *, obj):
        self.deposition_potential = obj.DepositionPotential
        self.deposition_time = obj.DepositionTime
        self.conditioning_potential = obj.ConditioningPotential
        self.conditioning_time = obj.ConditioningTime


@attrs.define
class VersusOCP(CommonSettings):
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

    stability_criterion: int = 0
    """Stability criterion (potential/time) in mV/s.

    If equal to 0 means no stability criterion.
    If larger than 0, then the value is taken as the stability threshold.
    """

    def _update_psmethod(self, *, obj):
        obj.OCPmode = self.mode
        obj.OCPMaxOCPTime = self.max_ocp_time
        obj.OCPStabilityCriterion = self.stability_criterion

    def _update_params(self, *, obj):
        self.mode = obj.OCPmode
        self.max_ocp_time = obj.OCPMaxOCPTime
        self.stability_criterion = obj.OCPStabilityCriterion


@attrs.define
class BiPot(CommonSettings):
    """Set the bipot settings for a given method."""

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

    _BIPOT_MODES = ('constant', 'offset')

    def _update_psmethod(self, *, obj):
        bipot_num = self._BIPOT_MODES.index(self.mode)
        obj.BipotModePS = PalmSens.Method.EnumPalmSensBipotMode(bipot_num)
        obj.BiPotPotential = self.potential
        obj.BipotRanging.MaximumCurrentRange = self.current_range_max._to_psobj()
        obj.BipotRanging.MinimumCurrentRange = self.current_range_min._to_psobj()
        obj.BipotRanging.StartCurrentRange = self.current_range_start._to_psobj()

    def _update_params(self, *, obj):
        self.mode = self._BIPOT_MODES[int(obj.BipotModePS)]
        self.potential = obj.BiPotPotential
        self.current_range_max = CURRENT_RANGE._from_psobj(obj.BipotRanging.MaximumCurrentRange)
        self.current_range_min = CURRENT_RANGE._from_psobj(obj.BipotRanging.MinimumCurrentRange)
        self.current_range_start = CURRENT_RANGE._from_psobj(obj.BipotRanging.StartCurrentRange)


@attrs.define
class PostMeasurement(CommonSettings):
    """Set the post measurement settings for a given method."""

    cell_on_after_measurement: bool = False
    """Enable/disable cell after measurement."""

    standby_potential: float = 0.0
    """Standby potential (V) for use with cell on after measurement."""

    standby_time: float = 0.0
    """Standby time (s) for use with cell on after measurement."""

    def _update_psmethod(self, *, obj):
        obj.CellOnAfterMeasurement = self.cell_on_after_measurement
        obj.StandbyPotential = self.standby_potential
        obj.StandbyTime = self.standby_time

    def _update_params(self, *, obj):
        self.cell_on_after_measurement = obj.CellOnAfterMeasurement
        self.standby_potential = obj.StandbyPotential
        self.standby_time = obj.StandbyTime


@attrs.define
class CurrentLimits(CommonSettings):
    """Set the limit settings for a given method."""

    use_limit_max: bool = False
    """Use limit current max.

    This will reverse the scan instead of aborting measurement."""

    limit_max: float = 0.0
    """Limit current max in µA."""

    use_limit_min: bool = False
    """Use limit current min.

    This will reverse the scan instead of aborting measurement."""

    limit_min: float = 0.0
    """Limit current min in µA."""

    def _update_psmethod(self, *, obj):
        obj.UseLimitMaxValue = self.use_limit_max
        obj.LimitMaxValue = self.limit_max
        obj.UseLimitMinValue = self.use_limit_min
        obj.LimitMinValue = self.limit_min

    def _update_params(self, *, obj):
        self.use_limit_max = obj.UseLimitMaxValue
        self.limit_max = obj.LimitMaxValue
        self.use_limit_min = obj.UseLimitMinValue
        self.limit_min = obj.LimitMinValue


@attrs.define
class PotentialLimits(CommonSettings):
    """Set the limit settings for a given method."""

    use_limit_max: bool = False
    """Use limit potential max."""

    limit_max: float = 0.0
    """Limit potential max in V."""

    use_limit_min: bool = False
    """Use limit potential min."""

    limit_min: float = 0.0
    """Limit potential min in V."""

    def _update_psmethod(self, *, obj):
        obj.UseLimitMaxValue = self.use_limit_max
        obj.LimitMaxValue = self.limit_max
        obj.UseLimitMinValue = self.use_limit_min
        obj.LimitMinValue = self.limit_min

    def _update_params(self, *, obj):
        self.use_limit_max = obj.UseLimitMaxValue
        self.limit_max = obj.LimitMaxValue
        self.use_limit_min = obj.UseLimitMinValue
        self.limit_min = obj.LimitMinValue


@attrs.define
class ChargeLimits(CommonSettings):
    """Set the charge limit settings for a given method."""

    use_limit_max: bool = False
    """Use limit charge max."""

    limit_max: float = 0.0
    """Limit charge max in µC."""

    use_limit_min: bool = False
    """Use limit charge min."""

    limit_min: float = 0.0
    """Limit charge min in µC."""

    def _update_psmethod(self, *, obj):
        obj.UseChargeLimitMax = self.use_limit_max
        obj.ChargeLimitMax = self.limit_max
        obj.UseChargeLimitMin = self.use_limit_min
        obj.ChargeLimitMin = self.limit_min

    def _update_params(self, *, obj):
        self.use_limit_max = obj.UseChargeLimitMax
        self.limit_max = obj.ChargeLimitMax
        self.use_limit_min = obj.UseChargeLimitMin
        self.limit_min = obj.ChargeLimitMin


@attrs.define
class IrDropCompensation(CommonSettings):
    """Set the iR drop compensation settings for a given method."""

    enable: bool = False
    """Enable iR compensation"""
    ir_compensation: float = 0.0
    """Set the iR compensation in Ω"""

    def _update_psmethod(self, *, obj):
        obj.UseIRDropComp = self.enable
        obj.IRDropCompRes = self.ir_compensation

    def _update_params(self, *, obj):
        self.enable = obj.UseIRDropComp
        self.ir_compensation = obj.IRDropCompRes


@attrs.define
class EquilibrationTriggers(CommonSettings):
    """Set the trigger at equilibration settings for a given method."""

    enable: bool = False
    """Enable equilibration triggers.

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

    def _update_psmethod(self, *, obj):
        obj.UseTriggerOnEquil = self.enable
        obj.TriggerValueOnEquil = convert_bools_to_int((self.d0, self.d1, self.d2, self.d3))

    def _update_params(self, *, obj):
        self.enable = obj.UseTriggerOnEquil
        self.d0, self.d1, self.d2, self.d3 = convert_int_to_bools(obj.TriggerValueOnEquil)


@attrs.define
class MeasurementTriggers(CommonSettings):
    """Set the trigger at measurement settings for a given method."""

    enable: bool = False
    """Enable measurement triggers.

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

    def _update_psmethod(self, *, obj):
        obj.UseTriggerOnStart = self.enable
        obj.TriggerValueOnStart = convert_bools_to_int((self.d0, self.d1, self.d2, self.d3))

    def _update_params(self, *, obj):
        self.enable = obj.UseTriggerOnStart
        self.d0, self.d1, self.d2, self.d3 = convert_int_to_bools(obj.TriggerValueOnStart)


@attrs.define
class Multiplexer(CommonSettings):
    """Set the multiplexer settings for a given method."""

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

    _MUX_MODES = ('none', 'consecutive', 'alternate')

    def _update_psmethod(self, *, obj):
        # Create a mux8r2 multiplexer settings settings object
        mux_mode = self._MUX_MODES.index(self.mode) - 1
        obj.MuxMethod = PSMuxMethod(mux_mode)

        # disable all mux channels (range 0-127)
        for i in range(len(obj.UseMuxChannel)):
            obj.UseMuxChannel[i] = False

        # set the selected mux channels
        for i in self.channels:
            obj.UseMuxChannel[i - 1] = True

        obj.MuxSett.ConnSEWE = self.connect_sense_to_working_electrode
        obj.MuxSett.ConnectCERE = self.combine_reference_and_counter_electrodes
        obj.MuxSett.CommonCERE = self.use_channel_1_reference_and_counter_electrodes
        obj.MuxSett.UnselWE = PSMethod.MuxSettings.UnselWESetting(
            self.set_unselected_channel_working_electrode
        )

    def _update_params(self, *, obj):
        self.mode = self._MUX_MODES[int(obj.MuxMethod) + 1]

        self.channels = [i + 1 for i in range(len(obj.UseMuxChannel)) if obj.UseMuxChannel[i]]

        self.connect_sense_to_working_electrode = obj.MuxSett.ConnSEWE
        self.combine_reference_and_counter_electrodes = obj.MuxSett.ConnectCERE
        self.use_channel_1_reference_and_counter_electrodes = obj.MuxSett.CommonCERE
        self.set_unselected_channel_working_electrode = int(obj.MuxSett.UnselWE)


@attrs.define
class DataProcessing(CommonSettings):
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

    def _update_psmethod(self, *, obj):
        obj.SmoothLevel = self.smooth_level
        obj.MinPeakHeight = self.min_height
        obj.MinPeakWidth = self.min_width

    def _update_params(self, *, obj):
        self.smooth_level = obj.SmoothLevel
        self.min_width = single_to_double(obj.MinPeakWidth)
        self.min_height = single_to_double(obj.MinPeakHeight)


@attrs.define
class General(CommonSettings):
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

    def _update_psmethod(self, *, obj):
        obj.SaveOnDevice = self.save_on_internal_storage
        obj.UseHWSync = self.use_hardware_sync
        obj.Notes = self.notes
        obj.PowerFreq = self.power_frequency

    def _update_params(self, *, obj):
        self.save_on_internal_storage = obj.SaveOnDevice
        self.use_hardware_sync = obj.UseHWSync
        self.notes = obj.Notes
        self.power_frequency = obj.PowerFreq
