from typing import Any, Optional, Sequence

from PalmSens import (
    CurrentRange,
    CurrentRanges,
    ExtraValueMask,
    Method,
    MuxMethod,
    PotentialRange,
    PotentialRanges,
)
from PalmSens.Devices import PalmSens4Capabilities


def convert_bool_list_to_base2(lst: Sequence[bool]) -> int:
    """Convert e.g. [True, False, True, False] to 5."""

    lines = 0
    for i, set_high in enumerate(lst):
        if set_high:
            lines = lines | (1 << i)
    assert lines == int(''.join('01'[set_high] for set_high in reversed(lst)), base=2)
    return lines


def get_current_range(id: int) -> CurrentRange:
    """Get the current range for a given id.

    The id corresponds to the following ranges:
    * 100 pA = 0
    * 1 nA = 1
    * 10 nA = 2
    * 100 nA = 3
    * 1 uA = 4
    * 10 uA = 5
    * 100 uA = 6
    * 1 mA = 7
    * 10 mA = 8
    * 100 mA = 9
    * 2 uA = 10
    * 4 uA = 11
    * 8 uA = 12
    * 16 uA = 13
    * 32 uA = 14
    * 63 uA = 26
    * 125 uA = 17
    * 250 uA = 18
    * 500 uA = 19
    * 5 mA = 20
    * 6 uA = 21
    * 13 uA = 22
    * 25 uA = 23
    * 50 uA = 24
    * 200 uA = 25
    * 1 A = 30
    """
    if not 0 <= id <= 30:
        raise ValueError('Invalid id for current range. Valid ids are: 0-30')

    return CurrentRange(CurrentRanges(id))


def get_potential_range(id: int) -> PotentialRange:
    """Get the potential range for a given id.

    The id corresponds to the following ranges:
    * 1 mV = 0
    * 10 mV = 1
    * 20 mV = 2
    * 50 mV = 3
    * 100 mV = 4
    * 200 mV = 5
    * 500 mV = 6
    * 1 V = 7
    """
    if not 0 <= id <= 7:
        raise ValueError('Invalid id for potential range. Valid ids are: 0-7')

    ranges = [
        PotentialRanges.pr1mV,
        PotentialRanges.pr10mV,
        PotentialRanges.pr20mV,
        PotentialRanges.pr50mV,
        PotentialRanges.pr100mV,
        PotentialRanges.pr200mV,
        PotentialRanges.pr500mV,
        PotentialRanges.pr1V,
    ][id]
    return PotentialRange(ranges)


def set_autoranging_current(method, current_range_max, current_range_min, current_range_start):
    """Set the autoranging current for a given method."""
    method.Ranging.MaximumCurrentRange = current_range_max
    method.Ranging.MinimumCurrentRange = current_range_min
    method.Ranging.StartCurrentRange = current_range_start


def set_autoranging_bipot_current(
    method, bipot_current_range_max, bipot_current_range_min, bipot_current_range_start
):
    """Set the autoranging bipot current for a given method."""
    method.BipotRanging.MaximumCurrentRange = bipot_current_range_max
    method.BipotRanging.MinimumCurrentRange = bipot_current_range_min
    method.BipotRanging.StartCurrentRange = bipot_current_range_start


def set_autoranging_potential(
    method, potential_range_max, potential_range_min, potential_range_start
):
    """Set the autoranging potential for a given method."""
    method.RangingPotential.MaximumPotentialRange = potential_range_max
    method.RangingPotential.MinimumPotentialRange = potential_range_min
    method.RangingPotential.StartPotentialRange = potential_range_start


def set_pretreatment(
    method, deposition_potential, deposition_time, conditioning_potential, conditioning_time
):
    """Set the pretreatment settings for a given method."""
    method.DepositionPotential = deposition_potential
    method.DepositionTime = deposition_time
    method.ConditioningPotential = conditioning_potential
    method.ConditioningTime = conditioning_time


def set_versus_ocp(
    method, versus_ocp_mode, versus_ocp_max_ocp_time, versus_ocp_stability_criterion
):
    """Set the versus OCP settings for a given method."""
    method.OCPmode = versus_ocp_mode
    method.OCPMaxOCPTime = versus_ocp_max_ocp_time
    method.OCPStabilityCriterion = versus_ocp_stability_criterion


def set_bipot_settings(
    method,
    bipot_mode,
    bipot_potential,
    bipot_current_range_max,
    bipot_current_range_min,
    bipot_current_range_start,
):
    """Set the bipot settings for a given method."""
    method.BiPotModePS = Method.EnumPalmSensBipotMode(bipot_mode)
    method.BiPotPotential = bipot_potential
    set_autoranging_bipot_current(
        method,
        bipot_current_range_max,
        bipot_current_range_min,
        bipot_current_range_start,
    )


def set_extra_value_mask(
    method,
    *,
    enable_bipot_current: bool = False,
    record_auxiliary_input: bool = False,
    record_cell_potential: bool = False,
    record_we_potential: bool = False,
    record_forward_and_reverse_currents: bool = False,
    record_we_current: bool = False,
    record_we_current_range: Optional[Any] = None,
):
    """Set the extra value mask for a given method."""
    if record_we_current_range is None:
        record_we_current_range = get_current_range(4)

    extra_values = 0

    if enable_bipot_current:
        extra_values = extra_values | int(ExtraValueMask.BipotWE)
    if record_auxiliary_input:
        extra_values = extra_values | int(ExtraValueMask.AuxInput)
    if record_cell_potential:
        extra_values = extra_values | int(ExtraValueMask.CEPotential)
    if record_we_potential:
        extra_values = extra_values | int(ExtraValueMask.PotentialExtraRE)
    if record_forward_and_reverse_currents:
        extra_values = extra_values | int(ExtraValueMask.IForwardReverse)
    if record_we_current:
        extra_values = extra_values | int(ExtraValueMask.CurrentExtraWE)
        method.AppliedCurrentRange = record_we_current_range

    method.ExtraValueMsk = ExtraValueMask(extra_values)


def set_post_measurement_settings(
    method, cell_on_after_measurement, cell_on_after_measurement_potential
):
    """Set the post measurement settings for a given method."""
    method.CellOnAfterMeasurement = cell_on_after_measurement
    method.StandbyPotential = cell_on_after_measurement_potential


def set_limit_settings(method, use_limit_max, limit_max, use_limit_min, limit_min):
    """Set the limit settings for a given method."""
    method.UseLimitMaxValue = use_limit_max
    method.LimitMaxValue = limit_max
    method.UseLimitMinValue = use_limit_min
    method.LimitMinValue = limit_min


def set_charge_limit_settings(
    method, use_limit_charge_max, limit_charge_max, use_limit_charge_min, limit_charge_min
):
    """Set the charge limit settings for a given method."""
    method.UseChargeLimitMax = use_limit_charge_max
    method.ChargeLimitMax = limit_charge_max
    method.UseChargeLimitMin = use_limit_charge_min
    method.ChargeLimitMin = limit_charge_min


def set_ir_drop_compensation(method, use_ir_compensation, ir_compensation):
    """Set the iR drop compensation settings for a given method."""
    method.UseIRDropComp = use_ir_compensation
    method.IRDropCompRes = ir_compensation


def set_trigger_at_equilibration_settings(
    method, trigger_at_equilibration, trigger_at_equilibration_lines
):
    """Set the trigger at equilibration settings for a given method."""
    method.UseTriggerOnEquil = trigger_at_equilibration
    lines = 0
    for i, set_high in enumerate(trigger_at_equilibration_lines):
        if set_high:
            lines = lines | (1 << i)
    method.TriggerValueOnEquil = lines


def set_trigger_at_measurement_settings(
    method, trigger_at_measurement, trigger_at_measurement_lines
):
    """Set the trigger at measurement settings for a given method."""
    method.UseTriggerOnStart = trigger_at_measurement
    lines = 0
    for i, set_high in enumerate(trigger_at_measurement_lines):
        if set_high:
            lines = lines | (1 << i)
    method.TriggerValueOnStart = lines


def set_multiplexer_settings(
    method,
    set_mux_mode,
    set_mux_channels,
    set_mux8r2_settings,
):
    """Set the multiplexer settings for a given method."""
    method.MuxMethod = MuxMethod(set_mux_mode)
    # disable all mux channels
    for i in range(0, len(method.UseMuxChannel)):
        method.UseMuxChannel[i] = False
    # set the selected mux channels
    for i, use_channel in enumerate(set_mux_channels):
        method.UseMuxChannel[i] = use_channel
    # set the mux8r2 settings
    if set_mux8r2_settings is not None:
        method.MuxSett.ConnSEWE = set_mux8r2_settings.ConnSEWE
        method.MuxSett.ConnectCERE = set_mux8r2_settings.ConnectCERE
        method.MuxSett.CommonCERE = set_mux8r2_settings.CommonCERE
        method.MuxSett.UnselWE = set_mux8r2_settings.UnselWE


def get_mux8r2_settings(
    *,
    connect_sense_to_working_electrode: bool = False,
    combine_reference_and_counter_electrodes: bool = False,
    use_channel_1_reference_and_counter_electrodes: bool = False,
    set_unselected_channel_working_electrode: int = 0,
):
    """Create a mux8r2 multiplexer settings settings object.

    :Keyword Arguments:
        * connect_sense_to_working_electrode
            -- Connect the sense electrode to the working electrode. Default is False.
        * combine_reference_and_counter_electrodes
            -- Combine the reference and counter electrodes. Default is False.
        * use_channel_1_reference_and_counter_electrodes
            -- Use channel 1 reference and counter electrodes for all working electrodes. Default is False.
        * set_unselected_channel_working_electrode
            -- Set the unselected channel working electrode to 0 = Disconnected / floating, 1 = Ground, 2 = Standby potential. Default is 0.
    """

    mux_settings = Method.MuxSettings(False)
    mux_settings.ConnSEWE = connect_sense_to_working_electrode
    mux_settings.ConnectCERE = combine_reference_and_counter_electrodes
    mux_settings.CommonCERE = use_channel_1_reference_and_counter_electrodes
    mux_settings.UnselWE = Method.MuxSettings.UnselWESetting(
        set_unselected_channel_working_electrode
    )

    return mux_settings


def set_filter_settings(method, dc_mains_filter, default_curve_post_processing_filter):
    """Set the filter settings for a given method."""
    method.DCMainsFilter = dc_mains_filter
    method.DefaultCurvePostProcessingFilter = default_curve_post_processing_filter


def get_method_estimated_duration(method, *, instrument_manager=None):
    """Get the estimated duration of a given method.

    :Keyword Arguments:
        instrument_manager :
            -- Specifies the instrument manager to get the connected instruments capabilities from,
            if not specified it will use the PalmSens4 capabilities to determine the estimated duration.

    """
    if instrument_manager is None or instrument_manager.__comm is None:
        instrument_capabilities = PalmSens4Capabilities()
    else:
        instrument_capabilities = instrument_manager.__comm.Capabilities
    return method.GetMinimumEstimatedMeasurementDuration(instrument_capabilities)
