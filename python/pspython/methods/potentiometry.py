from PalmSens.Techniques import Potentiometry as PSPotentiometry

from ._shared import (
    get_current_range,
    get_potential_range,
    set_autoranging_current,
    set_autoranging_potential,
    set_extra_value_mask,
    set_filter_settings,
    set_limit_settings,
    set_multiplexer_settings,
    set_post_measurement_settings,
    set_pretreatment,
    set_trigger_at_measurement_settings,
)
from .time_method import TimeMethodParameters


class PotentiometryParameters(TimeMethodParameters): ...


def chronopotentiometry(**kwargs):
    """Create a chronopotentiometry method object.

    :Keyword Arguments:
    * current_range_max : PalmSens.CurrentRange --
        Maximum current range (default: 10 mA) [use get_current_range() to get the range]
    * current_range_min : PalmSens.CurrentRange --
        Minimum current range (default: 1 µA) [use get_current_range() to get the range]
    * current_range_start : PalmSens.CurrentRange --
        Start current range (default: 100 µA) [use get_current_range() to get the range]
    * potential_range_max : PalmSens.PotentialRange --
        Maximum potential range (default: 1 V) [use get_potential_range() to get the range]
    * potential_range_min : PalmSens.PotentialRange --
        Minimum potential range (default: 10 mV) [use get_potential_range() to get the range]
    * potential_range_start : PalmSens.PotentialRange --
        Start potential range (default: 1 V) [use get_potential_range() to get the range]
    * deposition_potential : float --
        Deposition potential in V (default: 0.0)
    * deposition_time : float --
        Deposition time in s (default: 0.0)
    * conditioning_potential : float --
        Conditioning potential in V (default: 0.0)
    * conditioning_time : float --
        Conditioning time in s (default: 0.0)
    * current : float --
        Current in applied current range (default: 0.0)
    * applied_current_range : PalmSens.CurrentRange --
        Applied current range (default: 100 µA) [use get_current_range() to get the range]
    * interval_time : float --
        Interval time in s (default: 0.1)
    * run_time : float --
        Run time in s (default: 1.0)
    * record_auxiliary_input : bool --
        Record auxiliary input (default: False)
    * record_cell_potential : bool --
        Record cell potential (default: False) [counter electrode vs ground]
    * record_we_current : bool --
        Record working electrode current (default: False)
    * cell_on_after_measurement : bool --
        Cell on after measurement (default: False)
    * cell_on_after_measurement_potential : float --
        Cell on after measurement potential in V (default: 0.0)
    * use_limit_potential_max : bool --
        Use limit potential max (default: False)
    * limit_potential_max : float --
        Limit potential max in V (default: 0.0)
    * use_limit_potential_min : bool --
        Use limit potential min (default: False)
    * limit_potential_min : float --
        Limit potential min in V (default: 0.0)
    * trigger_at_measurement : bool --
        Trigger at measurement (default: False)
    * trigger_at_measurement_lines : list --
        Trigger at measurement lines (default: [False, False, False, False]) [d0 high, d1 high, d2 high, d3 high]
    * dc_mains_filter : int --
        DC mains filter (default: 50) [set to 50 Hz or 60 Hz (50 Hz is default)]
    * default_curve_post_processing_filter : int --
        Default curve post processing filter (default: 0) [-1 = no filter, 0 = spike rejection, 1 = spike rejection + Savitsky-golay window 5, 2 = spike rejection + Savitsky-golay window 9, 3 = spike rejection + Savitsky-golay window 15, 4 = spike rejection + Savitsky-golay window 25]
    * set_mux_mode : int --
        Set multiplexer mode (default: -1) [-1 = disable, 0 = sequentially, 1 = alternatingly]
    * set_mux_channels : list --
        Set multiplexer channels (default: [False, False, False, False, False, False, False, False]) [a list of bools for each channel (channel 1, channel 2, ..., channel 128). In consequtive mode all selections are valid, in alternating mode the first channel must be selected and all other channels should be consequtive i.e. (channel 1, channel 2, channel 3 and so on)]
    * set_mux8r2_settings : PalmSens.Method.MuxSettings --
        Initialize the settings for the MUX8R2 multiplexer (default: None) [use get_mux8r2_settings() to create the settings]
    * save_on_internal_storage : bool --
        Save on internal storage (default: False)
    * use_hardware_sync : bool --
        Use hardware synchronization with other channels/instruments (default: False)
    """
    chronopotentiometry = PSPotentiometry()

    # (auto)ranging
    # current in pretreatment
    current_range_max = kwargs.get('current_range_max', get_current_range(8))
    current_range_min = kwargs.get('current_range_min', get_current_range(4))
    current_range_start = kwargs.get('current_range_start', get_current_range(6))
    set_autoranging_current(
        chronopotentiometry, current_range_max, current_range_min, current_range_start
    )

    # potential
    potential_range_max = kwargs.get('potential_range_max', get_potential_range(7))
    potential_range_min = kwargs.get('potential_range_min', get_potential_range(1))
    potential_range_start = kwargs.get('potential_range_start', get_potential_range(7))
    set_autoranging_potential(
        chronopotentiometry, potential_range_max, potential_range_min, potential_range_start
    )

    # pretreatment
    deposition_potential = kwargs.get('deposition_potential', 0.0)
    deposition_time = kwargs.get('deposition_time', 0.0)
    conditioning_potential = kwargs.get('conditioning_potential', 0.0)
    conditioning_time = kwargs.get('conditioning_time', 0.0)
    set_pretreatment(
        chronopotentiometry,
        deposition_potential,
        deposition_time,
        conditioning_potential,
        conditioning_time,
    )

    # chronopotentiometry settings
    current = kwargs.get('current', 0.0)  # in applied current range
    applied_current_range = kwargs.get(
        'applied_current_range', get_current_range(6)
    )  # in applied current range
    interval_time = kwargs.get('interval_time', 0.1)  # Time (s)
    run_time = kwargs.get('run_time', 1.0)  # Time (s)
    chronopotentiometry.Current = current
    chronopotentiometry.AppliedCurrentRange = applied_current_range
    chronopotentiometry.IntervalTime = interval_time
    chronopotentiometry.RunTime = run_time

    # advanced settings
    # record extra value settings
    record_auxiliary_input = kwargs.get('record_auxiliary_input', False)
    record_cell_potential = kwargs.get('record_cell_potential', False)
    record_we_current = kwargs.get('record_we_current', False)
    set_extra_value_mask(
        chronopotentiometry,
        record_auxiliary_input=record_auxiliary_input,
        record_cell_potential=record_cell_potential,
        record_we_current=record_we_current,
        record_we_current_range=applied_current_range,
    )

    # post measurement settings
    cell_on_after_measurement = kwargs.get('cell_on_after_measurement', False)
    cell_on_after_measurement_potential = kwargs.get(
        'cell_on_after_measurement_potential', 0.0
    )  # in V
    set_post_measurement_settings(
        chronopotentiometry, cell_on_after_measurement, cell_on_after_measurement_potential
    )

    # limit settings
    use_limit_potential_max = kwargs.get('use_limit_potential_max', False)
    limit_potential_max = kwargs.get('limit_potential_max', 0.0)  # in V
    use_limit_potential_min = kwargs.get('use_limit_potential_min', False)
    limit_potential_min = kwargs.get('limit_potential_min', 0.0)  # in V
    set_limit_settings(
        chronopotentiometry,
        use_limit_potential_max,
        limit_potential_max,
        use_limit_potential_min,
        limit_potential_min,
    )

    # trigger settings
    trigger_at_measurement = kwargs.get('trigger_at_measurement', False)
    trigger_at_measurement_lines = kwargs.get(
        'trigger_at_measurement_lines', [False, False, False, False]
    )  # d0 high, d1 high, d2 high, d3 high
    set_trigger_at_measurement_settings(
        chronopotentiometry, trigger_at_measurement, trigger_at_measurement_lines
    )

    # set filter settings
    dc_mains_filter = kwargs.get(
        'dc_mains_filter', 50
    )  # set to 50 Hz or 60 Hz (50 Hz is default)
    default_curve_post_processing_filter = kwargs.get(
        'default_curve_post_processing_filter', 0
    )  # -1 = no filter, 0 = spike rejection, 1 = spike rejection + Savitsky-golay window 5, 2 = spike rejection + Savitsky-golay window 9, 3 = spike rejection + Savitsky-golay window 15, 4 = spike rejection + Savitsky-golay window 25
    set_filter_settings(
        chronopotentiometry, dc_mains_filter, default_curve_post_processing_filter
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
        chronopotentiometry, set_mux_mode, set_mux_channels, set_mux8r2_settings
    )

    # internal storage
    save_on_internal_storage = kwargs.get('save_on_internal_storage', False)
    chronopotentiometry.SaveOnDevice = save_on_internal_storage

    # use hardware synchronization with other channels/instruments
    use_hardware_sync = kwargs.get('use_hardware_sync', False)
    chronopotentiometry.UseHWSync = use_hardware_sync

    return chronopotentiometry
