from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

import PalmSens
from PalmSens import Method as PSMethod
from PalmSens import MuxMethod as PSMuxMethod

from ._shared import (
    CURRENT_RANGE,
    POTENTIAL_RANGE,
    convert_bools_to_int,
    convert_int_to_bools,
)


@dataclass
class AutorangingCurrentSettings:
    """Set the autoranging current for a given method.

    Attributes
    ----------
    current_range_max: int
        Maximum current range (default: 10 mA).
        Use `CURRENT_RANGE` to define the range.
    current_range_min: int
        Minimum current range (default: 1 µA).
        Use `CURRENT_RANGE` to define the range.
    current_range_start: int
         Start current range (default: 100 µA).
         Use `CURRENT_RANGE` to define the range.
    """

    current_range_max: CURRENT_RANGE = CURRENT_RANGE.cr_10_mA
    current_range_min: CURRENT_RANGE = CURRENT_RANGE.cr_1_uA
    current_range_start: CURRENT_RANGE = CURRENT_RANGE.cr_100_uA

    def update_psmethod(self, *, obj):
        obj.Ranging.MaximumCurrentRange = self.current_range_max.to_psobj()
        obj.Ranging.MinimumCurrentRange = self.current_range_min.to_psobj()
        obj.Ranging.StartCurrentRange = self.current_range_start.to_psobj()

    def update_params(self, *, obj):
        self.current_range_max = CURRENT_RANGE.from_psobj(obj.Ranging.MaximumCurrentRange)
        self.current_range_min = CURRENT_RANGE.from_psobj(obj.Ranging.MinimumCurrentRange)
        self.current_range_start = CURRENT_RANGE.from_psobj(obj.Ranging.StartCurrentRange)


@dataclass
class AutorangingPotentialSettings:
    """Set the autoranging potential for a given method.

    Attributes
    ----------
    potential_range_max: int
        Maximum potential range (default: 1V).
        Use `POTENTIAL_RANGE` to define the range.
    potential_range_min: int
        Minimum potential range (default: 10mV).
        Use `POTENTIAL_RANGE` to define the range.
    potential_range_start: int
        Start potential range (default: 1V).
        Use `POTENTIAL_RANGE` to define the range.
    """

    potential_range_max: POTENTIAL_RANGE = POTENTIAL_RANGE.pr_1_V
    potential_range_min: POTENTIAL_RANGE = POTENTIAL_RANGE.pr_1_mV
    potential_range_start: POTENTIAL_RANGE = POTENTIAL_RANGE.pr_1_V

    def update_psmethod(self, *, obj):
        obj.RangingPotential.MaximumPotentialRange = self.potential_range_max.to_psobj()
        obj.RangingPotential.MinimumPotentialRange = self.potential_range_min.to_psobj()
        obj.RangingPotential.StartPotentialRange = self.potential_range_start.to_psobj()

    def update_params(self, *, obj):
        self.potential_range_max = POTENTIAL_RANGE.from_psobj(
            obj.RangingPotential.MaximumPotentialRange
        )
        self.potential_range_min = POTENTIAL_RANGE.from_psobj(
            obj.RangingPotential.MinimumPotentialRange
        )
        self.potential_range_start = POTENTIAL_RANGE.from_psobj(
            obj.RangingPotential.StartPotentialRange
        )


@dataclass
class PretreatmentSettings:
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

    def update_psmethod(self, *, obj):
        obj.DepositionPotential = self.deposition_potential
        obj.DepositionTime = self.deposition_time
        obj.ConditioningPotential = self.conditioning_potential
        obj.ConditioningTime = self.conditioning_time

    def update_params(self, *, obj):
        self.deposition_potential = obj.DepositionPotential
        self.deposition_time = obj.DepositionTime
        self.conditioning_potential = obj.ConditioningPotential
        self.conditioning_time = obj.ConditioningTime


@dataclass
class VersusOcpSettings:
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

    versus_ocp_mode: int = 0
    versus_ocp_max_ocp_time: float = 20.0  # Time (s)
    versus_ocp_stability_criterion: int = 0

    def update_psmethod(self, *, obj):
        obj.OCPmode = self.versus_ocp_mode
        obj.OCPMaxOCPTime = self.versus_ocp_max_ocp_time
        obj.OCPStabilityCriterion = self.versus_ocp_stability_criterion

    def update_params(self, *, obj):
        self.versus_ocp_mode = obj.OCPmode
        self.versus_ocp_max_ocp_time = obj.OCPMaxOCPTime
        self.versus_ocp_stability_criterion = obj.OCPStabilityCriterion


@dataclass
class BipotSettings:
    """Set the bipot settings for a given method.

    Attributes
    ----------
    enable_bipot_current: bool
        Enable bipotential current (default: False)
    bipot_mode: int
        Set the bipotential mode, 0 = constant, 1 = offset (default: 0)
    bipot_potential: float
        Set the bipotential in V (default: 0.0)
    bipot_current_range_max: int
        Maximum bipotential current range (default: 10 mA).
        Use `CURRENT_RANGE` to define the range.
    bipot_current_range_min: int
        Minimum bipotential current range (default: 1 µA).
        Use `CURRENT_RANGE` to define the range.
    bipot_current_range_start: int
        Start bipotential current range (default: 100 µA).
        Use `CURRENT_RANGE` to define the range.
    """

    bipot_mode: int = 0
    bipot_potential: float = 0.0  # V
    bipot_current_range_max: CURRENT_RANGE = CURRENT_RANGE.cr_10_mA
    bipot_current_range_min: CURRENT_RANGE = CURRENT_RANGE.cr_1_uA
    bipot_current_range_start: CURRENT_RANGE = CURRENT_RANGE.cr_100_uA

    def update_psmethod(self, *, obj):
        obj.BipotModePS = PalmSens.Method.EnumPalmSensBipotMode(self.bipot_mode)
        obj.BiPotPotential = self.bipot_potential
        obj.BipotRanging.MaximumCurrentRange = self.bipot_current_range_max.to_psobj()
        obj.BipotRanging.MinimumCurrentRange = self.bipot_current_range_min.to_psobj()
        obj.BipotRanging.StartCurrentRange = self.bipot_current_range_start.to_psobj()

    def update_params(self, *, obj):
        self.bipot_mode = int(obj.BipotModePS)
        self.bipot_potential = obj.BiPotPotential
        self.bipot_current_range_max = CURRENT_RANGE.from_psobj(
            obj.BipotRanging.MaximumCurrentRange
        )
        self.bipot_current_range_min = CURRENT_RANGE.from_psobj(
            obj.BipotRanging.MinimumCurrentRange
        )
        self.bipot_current_range_start = CURRENT_RANGE.from_psobj(
            obj.BipotRanging.StartCurrentRange
        )


@dataclass
class PostMeasurementSettings:
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

    def update_psmethod(self, *, obj):
        obj.CellOnAfterMeasurement = self.cell_on_after_measurement
        obj.StandbyPotential = self.standby_potential
        obj.StandbyTime = self.standby_time

    def update_params(self, *, obj):
        self.cell_on_after_measurement = obj.CellOnAfterMeasurement
        self.standby_potential = obj.StandbyPotential
        self.standby_time = obj.StandbyTime


@dataclass
class CurrentLimitSettings:
    """Set the limit settings for a given method.

    Attributes
    ----------
    use_limit_current_max: bool
        Use limit current max (default: False).
        This will reverse the scan instead of aborting measurement
    limit_current_max: float
        Limit current max in µA (default: 0.0)
    use_limit_current_min: bool
        Use limit current min (default: False)
        This will reverse the scan instead of aborting measurement
    limit_current_min: float
        Limit current min in µA (default: 0.0)
    """

    use_limit_current_max: bool = False
    limit_current_max: float = 0.0  # µA
    use_limit_current_min: bool = False
    limit_current_min: float = 0.0  # µA

    def update_psmethod(self, *, obj):
        obj.UseLimitMaxValue = self.use_limit_current_max
        obj.LimitMaxValue = self.limit_current_max
        obj.UseLimitMinValue = self.use_limit_current_min
        obj.LimitMinValue = self.limit_current_min

    def update_params(self, *, obj):
        self.use_limit_current_max = obj.UseLimitMaxValue
        self.limit_current_max = obj.LimitMaxValue
        self.use_limit_current_min = obj.UseLimitMinValue
        self.limit_current_min = obj.LimitMinValue


@dataclass
class PotentialLimitSettings:
    """Set the limit settings for a given method.

    Attributes
    ----------
    use_limit_potential_max: bool
        Use limit potential max (default: False).
    limit_potential_max: float
        Limit potential max in V (default: 0.0)
    use_limit_potential_min: bool
        Use limit potential min (default: False)
    limit_potential_min: float
        Limit potential min in V (default: 0.0)
    """

    use_limit_potential_max: bool = False
    limit_potential_max: float = 0.0  # V
    use_limit_potential_min: bool = False
    limit_potential_min: float = 0.0  # V

    def update_psmethod(self, *, obj):
        obj.UseLimitMaxValue = self.use_limit_potential_max
        obj.LimitMaxValue = self.limit_potential_max
        obj.UseLimitMinValue = self.use_limit_potential_min
        obj.LimitMinValue = self.limit_potential_min

    def update_params(self, *, obj):
        self.use_limit_potential_max = obj.UseLimitMaxValue
        self.limit_potential_max = obj.LimitMaxValue
        self.use_limit_potential_min = obj.UseLimitMinValue
        self.limit_potential_min = obj.LimitMinValue


@dataclass
class ChargeLimitSettings:
    """Set the charge limit settings for a given method.

    Attributes
    ----------
    use_limit_charge_max: bool
        Use limit charge max (default: False).
    limit_charge_max: float
        Limit charge max in µC (default: 0.0)
    use_limit_charge_min: bool
        Use limit charge min (default: False)
    limit_charge_min: float
        Limit charge min in µC (default: 0.0)
    """

    use_limit_charge_max: bool = False
    limit_charge_max: float = 0.0  # in µC
    use_limit_charge_min: bool = False
    limit_charge_min: float = 0.0  # in µC

    def update_psmethod(self, *, obj):
        obj.UseChargeLimitMax = self.use_limit_charge_max
        obj.ChargeLimitMax = self.limit_charge_max
        obj.UseChargeLimitMin = self.use_limit_charge_min
        obj.ChargeLimitMin = self.limit_charge_min

    def update_params(self, *, obj):
        self.use_limit_charge_max = obj.UseChargeLimitMax
        self.limit_charge_max = obj.ChargeLimitMax
        self.use_limit_charge_min = obj.UseChargeLimitMin
        self.limit_charge_min = obj.ChargeLimitMin


@dataclass
class IrDropCompensationSettings:
    """Set the iR drop compensation settings for a given method.

    Attributes
    ----------
    use_ir_compensation: bool
        Enable iR compensation
    ir_compensation: float
        Set the iR compensation in Ω (default: 0.0)

    """

    use_ir_compensation: bool = False
    ir_compensation: float = 0.0  # Ω

    def update_psmethod(self, *, obj):
        obj.UseIRDropComp = self.use_ir_compensation
        obj.IRDropCompRes = self.ir_compensation

    def update_params(self, *, obj):
        self.use_ir_compensation = obj.UseIRDropComp
        self.ir_compensation = obj.IRDropCompRes


@dataclass
class TriggerAtEquilibrationSettings:
    """Set the trigger at equilibration settings for a given method.

    Attributes
    ----------
    trigger_at_equilibration: bool
        Enable trigger at equilibration (default: False)
    trigger_at_equilibration_lines: tuple[bool, bool, bool, bool]
        Enable trigger at equilibration lines (default: [False, False, False, False])
        Line order: d0 high, d1 high, d2 high, d3 high

    """

    trigger_at_equilibration: bool = False
    trigger_at_equilibration_lines: tuple[bool, bool, bool, bool] = (False, False, False, False)

    def update_psmethod(self, *, obj):
        obj.UseTriggerOnEquil = self.trigger_at_equilibration
        obj.TriggerValueOnEquil = convert_bools_to_int(self.trigger_at_equilibration_lines)

    def update_params(self, *, obj):
        self.trigger_at_equilibration = obj.UseTriggerOnEquil
        self.trigger_at_equilibration_lines = convert_int_to_bools(obj.TriggerValueOnEquil)


@dataclass
class TriggerAtMeasurementSettings:
    """Set the trigger at measurement settings for a given method.

    Attributes
    ----------
    trigger_at_measurement: bool
        Enable trigger at measurement (default: False)
    trigger_at_measurement_lines: tuple[bool, bool, bool, bool]
        Enable trigger at measurement lines (default: [False, False, False, False])
        Line order: d0 high, d1 high, d2 high, d3 high

    """

    trigger_at_measurement: bool = False
    trigger_at_measurement_lines: tuple[bool, bool, bool, bool] = (False, False, False, False)

    def update_psmethod(self, *, obj):
        obj.UseTriggerOnStart = self.trigger_at_measurement
        obj.TriggerValueOnStart = convert_bools_to_int(self.trigger_at_measurement_lines)

    def update_params(self, *, obj):
        self.trigger_at_measurement = obj.UseTriggerOnStart
        self.trigger_at_measurement_lines = convert_int_to_bools(obj.TriggerValueOnStart)


@dataclass
class MultiplexerSettings:
    """Set the multiplexer settings for a given method.

    Attributes
    ----------
    set_mux_mode: int = -1
        Set multiplexer mode
           -1 = No multiplexer (disable)
            0 = Consecutive
            1 = Alternate
    set_mux_channels: list[bool]
        Set multiplexer channels as a list of bools for each channel (channel 1, channel 2, ..., channel 128).
        In consecutive mode all selections are valid.
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

    set_mux_mode: int = -1
    set_mux_channels: list[bool] = field(
        default_factory=lambda: [False, False, False, False, False, False, False, False]
    )
    connect_sense_to_working_electrode: bool = False
    combine_reference_and_counter_electrodes: bool = False
    use_channel_1_reference_and_counter_electrodes: bool = False
    set_unselected_channel_working_electrode: int = 0

    def update_psmethod(self, *, obj):
        # Create a mux8r2 multiplexer settings settings object
        obj.MuxMethod = PSMuxMethod(self.set_mux_mode)

        # disable all mux channels
        for i in range(len(obj.UseMuxChannel)):
            obj.UseMuxChannel[i] = False

        # set the selected mux channels
        for i, use_channel in enumerate(self.set_mux_channels):
            obj.UseMuxChannel[i] = use_channel

        obj.MuxSett.ConnSEWE = self.connect_sense_to_working_electrode
        obj.MuxSett.ConnectCERE = self.combine_reference_and_counter_electrodes
        obj.MuxSett.CommonCERE = self.use_channel_1_reference_and_counter_electrodes
        obj.MuxSett.UnselWE = PSMethod.MuxSettings.UnselWESetting(
            self.set_unselected_channel_working_electrode
        )

    def update_params(self, *, obj):
        self.set_mux_mode = int(obj.MuxMethod)

        channels = [i for i in range(len(obj.UseMuxChannel)) if obj.UseMuxChannel[i]]

        n_channels = max(channels) + 1 if channels else 0

        self.set_mux_channels = [i in channels for i in range(n_channels)]

        self.connect_sense_to_working_electrode = obj.MuxSett.ConnSEWE
        self.combine_reference_and_counter_electrodes = obj.MuxSett.ConnectCERE
        self.use_channel_1_reference_and_counter_electrodes = obj.MuxSett.CommonCERE
        self.set_unselected_channel_working_electrode = int(obj.MuxSett.UnselWE)


@dataclass
class PeakSettings:
    """Set the filter settings for a given method.

    Attributes
    ----------
    min_peak_height: float
        Determines the minimum peak height in µA.
        Peaks lower than this value are neglected (default: 0.0 uA).
    min_peak_width: float
        The minimum peak width,
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
    min_peak_height: float = 0.0  # uA
    min_peak_width: float = 0.1  # V

    def update_psmethod(self, *, obj):
        obj.SmoothLevel = self.smooth_level
        obj.MinPeakHeight = self.min_peak_height
        obj.MinPeakWidth = self.min_peak_width

    def update_params(self, *, obj):
        self.smooth_level = obj.SmoothLevel
        self.min_peak_width = obj.MinPeakWidth
        self.min_peak_height = obj.MinPeakHeight


@dataclass
class CommonSettings:
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

    def update_psmethod(self, *, obj):
        obj.SaveOnDevice = self.save_on_internal_storage
        obj.UseHWSync = self.use_hardware_sync
        obj.Notes = self.notes
        obj.PowerFreq = self.power_frequency

    def update_params(self, *, obj):
        self.save_on_internal_storage = obj.SaveOnDevice
        self.use_hardware_sync = obj.UseHWSync
        self.notes = obj.Notes
        self.power_frequency = obj.PowerFreq
