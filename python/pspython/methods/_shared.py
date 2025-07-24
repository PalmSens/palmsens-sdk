from typing import Any, Optional, Sequence

from PalmSens import (
    CurrentRange,
    CurrentRanges,
    ExtraValueMask,
    Method,
    PotentialRange,
    PotentialRanges,
)
from PalmSens.Devices import PalmSens4Capabilities
from PalmSens.Techniques import ELevel


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


def set_extra_value_mask(
    obj,
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
        obj.AppliedCurrentRange = record_we_current_range

    obj.ExtraValueMsk = ExtraValueMask(extra_values)


def get_mux8r2_settings(
    *,
    connect_sense_to_working_electrode: bool = False,
    combine_reference_and_counter_electrodes: bool = False,
    use_channel_1_reference_and_counter_electrodes: bool = False,
    set_unselected_channel_working_electrode: int = 0,
):
    """Create a mux8r2 multiplexer settings settings object.

    Parameters
    ----------
    connect_sense_to_working_electrode: bool
        Connect the sense electrode to the working electrode. Default is False.
    combine_reference_and_counter_electrodes: bool
        Combine the reference and counter electrodes. Default is False.
    use_channel_1_reference_and_counter_electrodes: bool
        Use channel 1 reference and counter electrodes for all working electrodes. Default is False.
    set_unselected_channel_working_electrode: int
        Set the unselected channel working electrode to 0 = Disconnected / floating, 1 = Ground, 2 = Standby potential. Default is 0.
    """

    mux_settings = Method.MuxSettings(False)
    mux_settings.ConnSEWE = connect_sense_to_working_electrode
    mux_settings.ConnectCERE = combine_reference_and_counter_electrodes
    mux_settings.CommonCERE = use_channel_1_reference_and_counter_electrodes
    mux_settings.UnselWE = Method.MuxSettings.UnselWESetting(
        set_unselected_channel_working_electrode
    )

    return mux_settings


def get_method_estimated_duration(method, *, instrument_manager=None):
    """Get the estimated duration of a given method.

    Parameters
    ----------
    instrument_manager
        Specifies the instrument manager to get the connected instruments capabilities from,
        if not specified it will use the PalmSens4 capabilities to determine the estimated duration.

    """
    if instrument_manager is None or instrument_manager.__comm is None:
        instrument_capabilities = PalmSens4Capabilities()
    else:
        instrument_capabilities = instrument_manager.__comm.Capabilities
    return method.GetMinimumEstimatedMeasurementDuration(instrument_capabilities)


def multi_step_amperometry_level(
    level: float = 0.0,
    duration: float = 1.0,
    record: bool = True,
    use_limit_current_max: bool = False,
    limit_current_max: float = 0.0,
    use_limit_current_min: bool = False,
    limit_current_min: float = 0.0,
    trigger_at_level: bool = False,
    trigger_at_level_lines: tuple[bool, bool, bool, bool] = (False, False, False, False),
):
    """Create a multi-step amperometry level method object.

    Parameters
    ----------
    level : float
        Level in V (default: 0.0)
    duration : float
        Duration in s (default: 1.0)
    record : bool
        Record the current (default: True)
    use_limit_current_max : bool
        Use limit current max (default: False)
    limit_current_max : float
        Limit current max in µA (default: 0.0)
    use_limit_current_min : bool
        Use limit current min (default: False)
    limit_current_min : float
        Limit current min in µA (default: 0.0)
    trigger_at_level : bool
        Use trigger at level (default: False)
    trigger_at_level_lines : list
        Trigger at level lines (default: [False, False, False, False])
        [d0 high, d1 high, d2 high, d3 high]
    """
    multi_step_amperometry_level = ELevel()

    multi_step_amperometry_level.Level = level
    multi_step_amperometry_level.Duration = duration
    multi_step_amperometry_level.Record = record

    multi_step_amperometry_level.UseMaxLimit = use_limit_current_max
    multi_step_amperometry_level.MaxLimit = limit_current_max
    multi_step_amperometry_level.UseMinLimit = use_limit_current_min
    multi_step_amperometry_level.MinLimit = limit_current_min

    multi_step_amperometry_level.UseTriggerOnStart = trigger_at_level
    multi_step_amperometry_level.TriggerValueOnStart = convert_bool_list_to_base2(
        trigger_at_level_lines
    )

    return multi_step_amperometry_level
