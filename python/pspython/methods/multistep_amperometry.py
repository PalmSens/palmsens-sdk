from PalmSens.Techniques import (
    ELevel,
)
from PalmSens.Techniques import MultistepAmperometry as PSMultistepAmperometry

from ._shared import (
    get_current_range,
    set_autoranging_current,
    set_bipot_settings,
    set_extra_value_mask,
    set_filter_settings,
    set_ir_drop_compensation,
    set_limit_settings,
    set_multiplexer_settings,
    set_post_measurement_settings,
    set_pretreatment,
)
from .time_method import TimeMethod


class MultistepAmperometry(TimeMethod): ...


def multi_step_amperometry_level(**kwargs):
    """Create a multi-step amperometry level method object.

    :Keyword Arguments:
    * level : float --
        Level in V (default: 0.0)
    * duration : float --
        Duration in s (default: 1.0)
    * record : bool --
        Record the current (default: True)
    * use_limit_current_max : bool --
        Use limit current max (default: False)
    * limit_current_max : float --
        Limit current max in µA (default: 0.0)
    * use_limit_current_min : bool --
        Use limit current min (default: False)
    * limit_current_min : float --
        Limit current min in µA (default: 0.0)
    * trigger_at_level : bool --
        Use trigger at level (default: False)
    * trigger_at_level_lines : list --
        Trigger at level lines (default: [False, False, False, False]) [d0 high, d1 high, d2 high, d3 high]
    """
    multi_step_amperometry_level = ELevel()

    # level settings
    level = kwargs.get('level', 0.0)  # in V
    duration = kwargs.get('duration', 1.0)  # in s
    record = kwargs.get('record', True)  # record the current or not
    multi_step_amperometry_level.Level = level
    multi_step_amperometry_level.Duration = duration
    multi_step_amperometry_level.Record = record

    # limit settings
    use_limit_current_max = kwargs.get('use_limit_current_max', False)
    limit_current_max = kwargs.get('limit_current_max', 0.0)  # in µA
    use_limit_current_min = kwargs.get('use_limit_current_min', False)
    limit_current_min = kwargs.get('limit_current_min', 0.0)  # in µA
    multi_step_amperometry_level.UseMaxLimit = use_limit_current_max
    multi_step_amperometry_level.MaxLimit = limit_current_max
    multi_step_amperometry_level.UseMinLimit = use_limit_current_min
    multi_step_amperometry_level.MinLimit = limit_current_min

    # trigger settings
    trigger_at_level = kwargs.get('trigger_at_level', False)  # use trigger or not
    trigger_at_level_lines = kwargs.get(
        'trigger_at_level_lines', [False, False, False, False]
    )  # d0 high, d1 high, d2 high, d3 high
    multi_step_amperometry_level.UseTriggerOnStart = trigger_at_level
    multi_step_amperometry_level.TriggerValueOnStart = trigger_at_level_lines

    return multi_step_amperometry_level


def multi_step_amperometry(**kwargs):
    """Create a multi-step amperometry method object.

    :Keyword Arguments:
    * current_range_max : PalmSens.CurrentRange --
        Maximum current range (default: 10 mA) [use get_current_range() to get the range]
    * current_range_min : PalmSens.CurrentRange --
        Minimum current range (default: 1 µA) [use get_current_range() to get the range]
    * current_range_start : PalmSens.CurrentRange --
        Start current range (default: 100 µA) [use get_current_range() to get the range]
    * deposition_potential : float --
        Deposition potential in V (default: 0.0)
    * deposition_time : float --
        Deposition time in s (default: 0.0)
    * conditioning_potential : float --
        Conditioning potential in V (default: 0.0)
    * conditioning_time : float --
        Conditioning time in s (default: 0.0)
    * equilibration_time : float --
        Equilibration time in s (default: 0.0)
    * interval_time : float --
        Interval time in s (default: 0.1)
    * n_cycles : int --
        Number of cycles (default: 1)
    * levels : list --
        List of levels (default: [multi_step_amperometry_level()]) [use multi_step_amperometry_level() to create levels]
    * enable_bipot_current : bool --
        Enable bipot current (default: False)
    * bipot_mode : int --
        0 = constant, 1 = offset (default: 0)
    * bipot_potential : float --
        Bipotential in V (default: 0.0)
    * bipot_current_range_max : PalmSens.CurrentRange --
        Maximum bipot current range (default: 10 mA) [use get_current_range() to get the range]
    * bipot_current_range_min : PalmSens.CurrentRange --
        Minimum bipot current range (default: 1 µA) [use get_current_range() to get the range]
    * bipot_current_range_start : PalmSens.CurrentRange --
        Start bipot current range (default: 100 µA) [use get_current_range() to get the range]
    * record_auxiliary_input : bool --
        Record auxiliary input (default: False)
    * record_cell_potential : bool --
        Record cell potential (default: False) [counter electrode vs ground]
    * record_we_potential : bool --
        Record applied working electrode potential (default: False) [reference electrode vs ground]
    * cell_on_after_measurement : bool --
        Cell on after measurement (default: False)
    * cell_on_after_measurement_potential : float --
        Cell on after measurement potential in V (default: 0.0)
    * use_limit_current_max : bool --
        Use limit current max (default: False)
    * limit_current_max : float --
        Limit current max in µA (default: 0.0)
    * use_limit_current_min : bool --
        Use limit current min (default: False)
    * limit_current_min : float --
        Limit current min in µA (default: 0.0)
    * use_ir_compensation : bool --
        Use iR compensation (default: False)
    * ir_compensation : float --
        iR compensation in Ω (default: 0.0)
    * dc_mains_filter : int --
        DC mains filter (default: 50) [set to 50 Hz or 60 Hz (50 Hz is default)]
    * default_curve_post_processing_filter : int --
        Default curve post processing filter (default: 0) [-1 = no filter, 0 = spike rejection, 1 = spike rejection + Savitsky-golay window 5, 2 = spike rejection + Savitsky-golay window 9, 3 = spike rejection + Savitsky-golay window 15, 4 = spike rejection + Savitsky-golay window 25]
    * set_mux_mode : int --
        Set multiplexer mode (default: -1) [-1 = disable, 0 = sequentially]
    * set_mux_channels : list --
        Set multiplexer channels (default: [False, False, False, False, False, False, False, False]) [a list of bools for each channel (channel 1, channel 2, ..., channel 128).
    * set_mux8r2_settings : PalmSens.Method.MuxSettings --
        Initialize the settings for the MUX8R2 multiplexer (default: None) [use get_mux8r2_settings() to create the settings]
    * save_on_internal_storage : bool --
        Save on internal storage (default: False)
    """
    multi_step_amperometry = PSMultistepAmperometry()

    # (auto)ranging
    current_range_max = kwargs.get('current_range_max_range_max', get_current_range(8))
    currrent_range_min = kwargs.get('current_range_max_range_min', get_current_range(4))
    current_range_max_range_start = kwargs.get(
        'current_range_max_range_start', get_current_range(6)
    )
    set_autoranging_current(
        multi_step_amperometry,
        current_range_max,
        currrent_range_min,
        current_range_max_range_start,
    )

    # pretreatment
    deposition_potential = kwargs.get('deposition_potential', 0.0)
    deposition_time = kwargs.get('deposition_time', 0.0)
    conditioning_potential = kwargs.get('conditioning_potential', 0.0)
    conditioning_time = kwargs.get('conditioning_time', 0.0)
    set_pretreatment(
        multi_step_amperometry,
        deposition_potential,
        deposition_time,
        conditioning_potential,
        conditioning_time,
    )

    # multi-step amperometry settings
    equilibration_time = kwargs.get('equilibration_time', 0.0)  # Time (s)
    interval_time = kwargs.get('interval_time', 0.1)  # Time (s)
    n_cycles = kwargs.get('n_cycles', 1)  # Number of cycles
    levels = kwargs.get(
        'levels', [multi_step_amperometry_level()]
    )  # Levels [use multi_step_amperometry_level() to create levels]
    multi_step_amperometry.EquilibrationTime = equilibration_time
    multi_step_amperometry.IntervalTime = interval_time
    multi_step_amperometry.nCycles = n_cycles
    multi_step_amperometry.Levels.Clear()

    if len(levels) == 0:
        raise ValueError('At least one level must be specified.')

    use_partial_record = False
    use_level_limits = False

    for level in levels:
        if level.Record:
            use_partial_record = True
        if level.UseMaxLimit or level.UseMinLimit:
            use_level_limits = True

        multi_step_amperometry.Levels.Add(level)

    multi_step_amperometry.UseSelectiveRecord = use_partial_record
    multi_step_amperometry.UseLimits = use_level_limits

    # advanced settings
    # bipot settings
    enable_bipot_current = kwargs.get('enable_bipot_current', False)
    bipot_mode = kwargs.get('bipot_mode', 0)  # 0 = constant, 1 = offset
    bipot_potential = kwargs.get('bipot_potential', 0.0)  # in V
    bipot_current_range_max = kwargs.get('bipot_current_range_max', get_current_range(8))
    bipot_current_range_min = kwargs.get('bipot_current_range_min', get_current_range(4))
    bipot_current_range_start = kwargs.get('bipot_current_range_start', get_current_range(6))
    set_bipot_settings(
        multi_step_amperometry,
        bipot_mode,
        bipot_potential,
        bipot_current_range_max,
        bipot_current_range_min,
        bipot_current_range_start,
    )

    # record extra value settings
    record_auxiliary_input = kwargs.get('record_auxiliary_input', False)
    record_cell_potential = kwargs.get('record_cell_potential', False)
    record_we_potential = kwargs.get('record_we_potential', False)
    set_extra_value_mask(
        multi_step_amperometry,
        enable_bipot_current=enable_bipot_current,
        record_auxiliary_input=record_auxiliary_input,
        record_cell_potential=record_cell_potential,
        record_we_potential=record_we_potential,
    )

    # post measurement settings
    cell_on_after_measurement = kwargs.get('cell_on_after_measurement', False)
    cell_on_after_measurement_potential = kwargs.get(
        'cell_on_after_measurement_potential', 0.0
    )  # in V
    set_post_measurement_settings(
        multi_step_amperometry, cell_on_after_measurement, cell_on_after_measurement_potential
    )

    # gloabl limit settings
    use_limit_current_max = kwargs.get('use_limit_current_max', False)
    limit_current_max = kwargs.get('limit_current_max', 0.0)  # in µA
    use_limit_current_min = kwargs.get('use_limit_current_min', False)
    limit_current_min = kwargs.get('limit_current_min', 0.0)  # in µA
    set_limit_settings(
        multi_step_amperometry,
        use_limit_current_max,
        limit_current_max,
        use_limit_current_min,
        limit_current_min,
    )

    # iR compensation settings
    use_ir_compensation = kwargs.get('use_ir_compensation', False)
    ir_compensation = kwargs.get('ir_compensation', 0.0)  # IR compensation in Ω
    set_ir_drop_compensation(multi_step_amperometry, use_ir_compensation, ir_compensation)

    # set filter settings
    dc_mains_filter = kwargs.get(
        'dc_mains_filter', 50
    )  # set to 50 Hz or 60 Hz (50 Hz is default)
    default_curve_post_processing_filter = kwargs.get(
        'default_curve_post_processing_filter', 0
    )  # -1 = no filter, 0 = spike rejection, 1 = spike rejection + Savitsky-golay window 5, 2 = spike rejection + Savitsky-golay window 9, 3 = spike rejection + Savitsky-golay window 15, 4 = spike rejection + Savitsky-golay window 25
    set_filter_settings(
        multi_step_amperometry, dc_mains_filter, default_curve_post_processing_filter
    )

    # multiplexer settings
    set_mux_mode = kwargs.get(
        'set_mux_mode', -1
    )  # -1 = disable, 0 = sequentially, 1 = alternatingly
    set_mux_channels = kwargs.get(
        'set_mux_channels', [False, False, False, False, False, False, False, False]
    )  # a list of bools for each channel (channel 1, channel 2, ..., channel 128). In consequtive mode all selections are valid, in alternating mode the first channel must be selected and all other channels should be consequtive i.e. (channel 1, channel 2, channel 3 and so on).
    set_mux8r2_settings = kwargs.get(
        'set_mux8r2_settings', None
    )  # Initialize the settings for the MUX8R2 multiplexer, PalmSens.Method.MuxSettings, use get_mux8r2_settings() to create the settings
    set_multiplexer_settings(
        multi_step_amperometry, set_mux_mode, set_mux_channels, set_mux8r2_settings
    )

    # internal storage
    save_on_internal_storage = kwargs.get('save_on_internal_storage', False)
    multi_step_amperometry.SaveOnDevice = save_on_internal_storage

    # use hardware synchronization with other channels/instruments
    use_hardware_sync = kwargs.get('use_hardware_sync', False)
    multi_step_amperometry.UseHWSync = use_hardware_sync

    return multi_step_amperometry
