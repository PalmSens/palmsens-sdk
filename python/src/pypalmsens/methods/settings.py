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
class BaseSettings(Protocol):
    """Protocol to provide generic methods for parameters."""

    def _update_psmethod(self, *, obj): ...
    def _update_params(self, *, obj): ...


@attrs.define
class CurrentRanges(BaseSettings):
    """Set the autoranging current for a given method.

    Attributes
    ----------
    max: int
        Maximum current range (default: 10 mA).
        Use `CURRENT_RANGE` to define the range.
    min: int
        Minimum current range (default: 1 µA).
        Use `CURRENT_RANGE` to define the range.
    start: int
         Start current range (default: 100 µA).
         Use `CURRENT_RANGE` to define the range.
    """

    max: CURRENT_RANGE = CURRENT_RANGE.cr_10_mA
    min: CURRENT_RANGE = CURRENT_RANGE.cr_1_uA
    start: CURRENT_RANGE = CURRENT_RANGE.cr_100_uA

    def _update_psmethod(self, *, obj):
        obj.Ranging.MaximumCurrentRange = self.max._to_psobj()
        obj.Ranging.MinimumCurrentRange = self.min._to_psobj()
        obj.Ranging.StartCurrentRange = self.start._to_psobj()

    def _update_params(self, *, obj):
        self.max = CURRENT_RANGE._from_psobj(obj.Ranging.MaximumCurrentRange)
        self.min = CURRENT_RANGE._from_psobj(obj.Ranging.MinimumCurrentRange)
        self.start = CURRENT_RANGE._from_psobj(obj.Ranging.StartCurrentRange)


@attrs.define
class PotentialRanges(BaseSettings):
    """Set the autoranging potential for a given method.

    Attributes
    ----------
    max: int
        Maximum potential range (default: 1V).
        Use `POTENTIAL_RANGE` to define the range.
    min: int
        Minimum potential range (default: 10mV).
        Use `POTENTIAL_RANGE` to define the range.
    start: int
        Start potential range (default: 1V).
        Use `POTENTIAL_RANGE` to define the range.
    """

    max: POTENTIAL_RANGE = POTENTIAL_RANGE.pr_1_V
    min: POTENTIAL_RANGE = POTENTIAL_RANGE.pr_1_mV
    start: POTENTIAL_RANGE = POTENTIAL_RANGE.pr_1_V

    def _update_psmethod(self, *, obj):
        obj.RangingPotential.MaximumPotentialRange = self.max._to_psobj()
        obj.RangingPotential.MinimumPotentialRange = self.min._to_psobj()
        obj.RangingPotential.StartPotentialRange = self.start._to_psobj()

    def _update_params(self, *, obj):
        self.max = POTENTIAL_RANGE._from_psobj(obj.RangingPotential.MaximumPotentialRange)
        self.min = POTENTIAL_RANGE._from_psobj(obj.RangingPotential.MinimumPotentialRange)
        self.start = POTENTIAL_RANGE._from_psobj(obj.RangingPotential.StartPotentialRange)


@attrs.define
class Pretreatment(BaseSettings):
    """Set the pretreatment settings for a given method.

    Attributes
    ----------
    deposition_potential: float
        Deposition potential in V (default: 0.0)
    deposition_time: float
        Deposition time in s (default: 0.0)
    conditioning_potential: float
        Conditioning potential in V (default: 0.0)
    conditioning_time: float
        Conditioning time in s (default: 0.0)
    """

    deposition_potential: float = 0.0
    deposition_time: float = 0.0
    conditioning_potential: float = 0.0
    conditioning_time: float = 0.0

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
class VersusOCP(BaseSettings):
    """Set the versus OCP settings for a given method.

    Attributes
    ----------
    versus_ocp_mode: int
        Set versus OCP mode.
            0 = disable versus OCP
            1 = vertex 1 potential
            2 = vertex 2 potential
            3 = vertex 1 & 2 potential
            4 = begin potential
            5 = begin & vertex 1 potential
            6 = begin & vertex 2 potential
            7 = begin & vertex 1 & 2 potential
    versus_ocp_max_ocp_time: int
        Maximum OCP time in s (default: 20.0)
    versus_ocp_stability_criterion: int = 0
        Stability criterion in mV/s (default: 0.0)
            0 = no stability criterion
            > 0 is stability threshold potential/time (mV/s)
    """

    mode: int = 0
    max_ocp_time: float = 20.0  # Time (s)
    stability_criterion: int = 0

    def _update_psmethod(self, *, obj):
        obj.OCPmode = self.mode
        obj.OCPMaxOCPTime = self.max_ocp_time
        obj.OCPStabilityCriterion = self.stability_criterion

    def _update_params(self, *, obj):
        self.mode = obj.OCPmode
        self.max_ocp_time = obj.OCPMaxOCPTime
        self.stability_criterion = obj.OCPStabilityCriterion


@attrs.define
class BiPot(BaseSettings):
    """Set the bipot settings for a given method.

    Attributes
    ----------
    mode: str
        Set the bipotential mode, 'constant' (default) or 'offset'
    potential: float
        Set the bipotential in V (default: 0.0)
    current_range_max: int
        Maximum bipotential current range (default: 10 mA).
        Use `CURRENT_RANGE` to define the range.
    current_range_min: int
        Minimum bipotential current range (default: 1 µA).
        Use `CURRENT_RANGE` to define the range.
    current_range_start: int
        Start bipotential current range (default: 100 µA).
        Use `CURRENT_RANGE` to define the range.
    """

    mode: Literal['constant', 'offset'] = 'constant'
    potential: float = 0.0  # V
    current_range_max: CURRENT_RANGE = CURRENT_RANGE.cr_10_mA
    current_range_min: CURRENT_RANGE = CURRENT_RANGE.cr_1_uA
    current_range_start: CURRENT_RANGE = CURRENT_RANGE.cr_100_uA

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
class PostMeasurement(BaseSettings):
    """Set the post measurement settings for a given method.

    Attributes
    ----------
    cell_on_after_measurement: bool
        Enable/disable cell after measurement (default: False)
    standby_potential: float
        Standby potential for use with cell on after measurement.
        Potential in V (default: 0.0)
    standby_time: float
        Standby time for use with cell on after measurement.
        Time in s (default)
    """

    cell_on_after_measurement: bool = False
    standby_potential: float = 0.0  # V
    standby_time: float = 0.0  # s

    def _update_psmethod(self, *, obj):
        obj.CellOnAfterMeasurement = self.cell_on_after_measurement
        obj.StandbyPotential = self.standby_potential
        obj.StandbyTime = self.standby_time

    def _update_params(self, *, obj):
        self.cell_on_after_measurement = obj.CellOnAfterMeasurement
        self.standby_potential = obj.StandbyPotential
        self.standby_time = obj.StandbyTime


@attrs.define
class CurrentLimits(BaseSettings):
    """Set the limit settings for a given method.

    Attributes
    ----------
    use_limit_max: bool
        Use limit current max (default: False).
        This will reverse the scan instead of aborting measurement
    limit_max: float
        Limit current max in µA (default: 0.0)
    use_limit_min: bool
        Use limit current min (default: False)
        This will reverse the scan instead of aborting measurement
    limit_min: float
        Limit current min in µA (default: 0.0)
    """

    use_limit_max: bool = False
    limit_max: float = 0.0  # µA
    use_limit_min: bool = False
    limit_min: float = 0.0  # µA

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
class PotentialLimits(BaseSettings):
    """Set the limit settings for a given method.

    Attributes
    ----------
    use_limit_max: bool
        Use limit potential max (default: False).
    limit_max: float
        Limit potential max in V (default: 0.0)
    use_limit_min: bool
        Use limit potential min (default: False)
    limit_min: float
        Limit potential min in V (default: 0.0)
    """

    use_limit_max: bool = False
    limit_max: float = 0.0  # V
    use_limit_min: bool = False
    limit_min: float = 0.0  # V

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
class ChargeLimits(BaseSettings):
    """Set the charge limit settings for a given method.

    Attributes
    ----------
    use_limit_max: bool
        Use limit charge max (default: False).
    limit_max: float
        Limit charge max in µC (default: 0.0)
    use_limit_min: bool
        Use limit charge min (default: False)
    limit_min: float
        Limit charge min in µC (default: 0.0)
    """

    use_limit_max: bool = False
    limit_max: float = 0.0  # in µC
    use_limit_min: bool = False
    limit_min: float = 0.0  # in µC

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
class IrDropCompensation(BaseSettings):
    """Set the iR drop compensation settings for a given method.

    Attributes
    ----------
    enable: bool
        Enable iR compensation
    ir_compensation: float
        Set the iR compensation in Ω (default: 0.0)
    """

    enable: bool = False
    ir_compensation: float = 0.0  # Ω

    def _update_psmethod(self, *, obj):
        obj.UseIRDropComp = self.enable
        obj.IRDropCompRes = self.ir_compensation

    def _update_params(self, *, obj):
        self.enable = obj.UseIRDropComp
        self.ir_compensation = obj.IRDropCompRes


@attrs.define
class EquilibrationTriggers(BaseSettings):
    """Set the trigger at equilibration settings for a given method.

    Attributes
    ----------
    enable: bool
        If enabled, set one or more digital outputs at the start of
        the equilibration period (default: False)
    d0: bool
        If True, enable trigger at d0 high
    d1: bool
        If True, enable trigger at d1 high
    d2: bool
        If True, enable trigger at d2 high
    d3: bool
        If True, enable trigger at d3 high
    """

    enable: bool = False
    d0: bool = False
    d1: bool = False
    d2: bool = False
    d3: bool = False

    def _update_psmethod(self, *, obj):
        obj.UseTriggerOnEquil = self.enable
        obj.TriggerValueOnEquil = convert_bools_to_int((self.d0, self.d1, self.d2, self.d3))

    def _update_params(self, *, obj):
        self.enable = obj.UseTriggerOnEquil
        self.d0, self.d1, self.d2, self.d3 = convert_int_to_bools(obj.TriggerValueOnEquil)


@attrs.define
class MeasurementTriggers(BaseSettings):
    """Set the trigger at measurement settings for a given method.

    Attributes
    ----------
    enable: bool
        If enabled, set one or more digital outputs at the start measurement,
        end of equilibration period (default: False)
    d0: bool
        If True, enable trigger at d0 high
    d1: bool
        If True, enable trigger at d1 high
    d2: bool
        If True, enable trigger at d2 high
    d3: bool
        If True, enable trigger at d3 high
    """

    enable: bool = False
    d0: bool = False
    d1: bool = False
    d2: bool = False
    d3: bool = False

    def _update_psmethod(self, *, obj):
        obj.UseTriggerOnStart = self.enable
        obj.TriggerValueOnStart = convert_bools_to_int((self.d0, self.d1, self.d2, self.d3))

    def _update_params(self, *, obj):
        self.enable = obj.UseTriggerOnStart
        self.d0, self.d1, self.d2, self.d3 = convert_int_to_bools(obj.TriggerValueOnStart)


@attrs.define
class Multiplexer(BaseSettings):
    """Set the multiplexer settings for a given method.

    Attributes
    ----------
    mode: int = -1
        Set multiplexer mode
           -1 = No multiplexer (disable)
            0 = Consecutive
            1 = Alternate
    channels: list[bool]
        Set multiplexer channels as a list of indexes for which channels to enable (max 128).
        For example, [0,3,7]. In consecutive mode all selections are valid.
        In alternating mode the first channel must be selected and all other
        channels should be consequtive i.e. (channel 1, channel 2, channel 3 and so on).
    connect_sense_to_working_electrode: bool
        Connect the sense electrode to the working electrode. Default is False.
    combine_reference_and_counter_electrodes: bool
        Combine the reference and counter electrodes. Default is False.
    use_channel_1_reference_and_counter_electrodes: bool
        Use channel 1 reference and counter electrodes for all working electrodes. Default is False.
    set_unselected_channel_working_electrode: int
        Set the unselected channel working electrode to 0 = Disconnected / floating, 1 = Ground, 2 = Standby potential. Default is 0.
    """

    mode: Literal['none', 'consecutive', 'alternate'] = 'none'
    channels: list[int] = attrs.field(factory=list)
    connect_sense_to_working_electrode: bool = False
    combine_reference_and_counter_electrodes: bool = False
    use_channel_1_reference_and_counter_electrodes: bool = False
    set_unselected_channel_working_electrode: int = 0

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
class DataProcessing(BaseSettings):
    """Set the data processing settings for a given method.

    Attributes
    ----------
    min_height: float
        Determines the minimum peak height in µA for peak finding.
        Peaks lower than this value are neglected (default: 0.0 uA).
    min_width: float
        The minimum peak width for peak finding,
        in the unit of the curves X axis (V).
        Peaks narrower than this value are neglected (default: 0.1 V).
    smooth_level: int
        Set the default curve post processing filter (default: 0)
           -1 = no filter
            0 = spike rejection
            1 = spike rejection + Savitsky-golay window 5
            2 = spike rejection + Savitsky-golay window 9
            3 = spike rejection + Savitsky-golay window 15
            4 = spike rejection + Savitsky-golay window 25
    """

    smooth_level: int = 0
    min_height: float = 0.0  # uA
    min_width: float = 0.1  # V

    def _update_psmethod(self, *, obj):
        obj.SmoothLevel = self.smooth_level
        obj.MinPeakHeight = self.min_height
        obj.MinPeakWidth = self.min_width

    def _update_params(self, *, obj):
        self.smooth_level = obj.SmoothLevel
        self.min_width = single_to_double(obj.MinPeakWidth)
        self.min_height = single_to_double(obj.MinPeakHeight)


@attrs.define
class General(BaseSettings):
    """Sets general/other settings for a given method.

    Attributes
    ----------
    notes : str
        Add some user notes for use with this technique
    save_on_internal_storage: bool
        Save on internal storage (default: False)
    use_hardware_sync: bool
        Use hardware synchronization with other channels/instruments (default: False)
    power_frequency: int
        Set the DC mains filter in Hz.
        Adjusts sampling on instrument to account for mains frequency.
        Set to 50 Hz or 60 Hz depending on your region (default: 50).
    """

    save_on_internal_storage: bool = False
    use_hardware_sync: bool = False
    notes: str = ''
    power_frequency: Literal[50, 60] = 50

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
