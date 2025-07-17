from PalmSens.Techniques import SquareWave as PSSquareWave

from ._shared import (
    get_current_range,
    set_autoranging_current,
    set_bipot_settings,
    set_extra_value_mask,
    set_filter_settings,
    set_ir_drop_compensation,
    set_multiplexer_settings,
    set_post_measurement_settings,
    set_pretreatment,
    set_trigger_at_equilibration_settings,
    set_trigger_at_measurement_settings,
    set_versus_ocp,
)
from .potential_method import PotentialMethod


class SquareWave(PotentialMethod): ...


def square_wave_voltammetry(**kwargs):
    """Create a square wave voltammetry method object.

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
    * begin_potential : float --
        Begin potential in V (default: -0.5)
    * end_potential : float --
        End potential in V (default: 0.5)
    * step_potential : float --
        Step potential in V (default: 0.1)
    * frequency : float --
        Frequency in Hz (default: 10.0)
    * amplitude : float --
        Amplitude in V (default: 0.05) [half peak to peak]
    * record_forward_and_reverse_currents : bool --
        Record forward and reverse currents (default: False)
    * versus_ocp_mode : int --
        0 = disable versus OCP, 1 = begin potential, 2 = end potential, 3 = begin & end potential (default: 0)
    * versus_ocp_max_ocp_time : float --
        Maximum OCP time in s (default: 20.0)
    * versus_ocp_stability_criterion : float --
        Stability criterion in mV/s (default: 0.0) [0 = no stability criterion, > 0 is stability threshold potential/time (mV/s)]
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
    * trigger_at_equilibration : bool --
        Trigger at equilibration (default: False)
    * trigger_at_equilibration_lines : list --
        Trigger at equilibration lines (default: [False, False, False, False]) [d0 high, d1 high, d2 high, d3 high]
    * trigger_at_measurement : bool --
        Trigger at measurement (default: False)
    * trigger_at_measurement_lines : list --
        Trigger at measurement lines (default: [False, False, False, False]) [d0 high, d1 high, d2 high, d3 high]
    * dc_mains_filter : int --
        DC mains filter (default: 50) [set to 50 Hz or 60 Hz (50 Hz is default)]
    * default_curve_post_processing_filter : int --
        Default curve post processing filter (default: 0) [-1 = no filter, 0 = spike rejection, 1 = spike rejection + Savitsky-golay window 5, 2 = spike rejection + Savitsky-golay window 9, 3 = spike rejection + Savitsky-golay window 15, 4 = spike rejection + Savitsky-golay window 25]
    * set_mux_mode : int --
        Set multiplexer mode (default: -1) [-1 = disable, 0 = sequentially]
    * set_mux_channels : list --
        Set multiplexer channels (default: [False, False, False, False, False, False, False, False]) [a list of bools for each channel (channel 1, channel 2, ..., channel 128).]
    * set_mux8r2_settings : PalmSens.Method.MuxSettings --
        Initialize the settings for the MUX8R2 multiplexer (default: None) [use get_mux8r2_settings() to create the settings]
    * save_on_internal_storage : bool --
        Save on internal storage (default: False)
    """
    square_wave_voltammetry = PSSquareWave()

    # (auto)ranging
    current_range_max = kwargs.get('current_range_max', get_current_range(8))
    current_range_min = kwargs.get('current_range_min', get_current_range(4))
    current_range_start = kwargs.get('current_range_start', get_current_range(6))
    set_autoranging_current(
        square_wave_voltammetry, current_range_max, current_range_min, current_range_start
    )

    # pretreatment
    deposition_potential = kwargs.get('deposition_potential', 0.0)
    deposition_time = kwargs.get('deposition_time', 0.0)
    conditioning_potential = kwargs.get('conditioning_potential', 0.0)
    conditioning_time = kwargs.get('conditioning_time', 0.0)
    set_pretreatment(
        square_wave_voltammetry,
        deposition_potential,
        deposition_time,
        conditioning_potential,
        conditioning_time,
    )

    # square wave voltammetry settings
    equilibration_time = kwargs.get('equilibration_time', 0.0)  # Time (s)
    begin_potential = kwargs.get('begin_potential', -0.5)  # potential (V)
    end_potential = kwargs.get('end_potential', 0.5)  # potential (V)
    step_potential = kwargs.get('step_potential', 0.1)  # potential (V)
    frequency = kwargs.get('frequency', 10.0)  # frequency (Hz)
    amplitude = kwargs.get('amplitude', 0.05)  # amplitude (V) [half peak to peak]
    record_forward_and_reverse_currents = kwargs.get(
        'record_forward_and_reverse_currents', False
    )  # record forward and reverse currents (default: False)
    square_wave_voltammetry.EquilibrationTime = equilibration_time
    square_wave_voltammetry.BeginPotential = begin_potential
    square_wave_voltammetry.EndPotential = end_potential
    square_wave_voltammetry.StepPotential = step_potential
    square_wave_voltammetry.Frequency = frequency
    square_wave_voltammetry.PulseAmplitude = amplitude

    # advanced settings
    # versus OCP settings
    versus_ocp_mode = kwargs.get(
        'versus_ocp_mode', 0
    )  # 0 = disable versus OCP, 1 = begin potential, 2 = end potential, 3 = begin & end potential
    versus_ocp_max_ocp_time = kwargs.get('versus_ocp_max_ocp_time', 20)  # Time (s)
    versus_ocp_stability_criterion = kwargs.get(
        'versus_ocp_stability_criterion', 0
    )  # 0 = no stability criterion, > 0 is stability threshold potential/time (mV/s)
    set_versus_ocp(
        square_wave_voltammetry,
        versus_ocp_mode,
        versus_ocp_max_ocp_time,
        versus_ocp_stability_criterion,
    )

    # bipot settings
    enable_bipot_current = kwargs.get('enable_bipot_current', False)
    bipot_mode = kwargs.get('bipot_mode', 0)  # 0 = constant, 1 = offset
    bipot_potential = kwargs.get('bipot_potential', 0.0)  # in V
    bipot_current_range_max = kwargs.get('bipot_current_range_max', get_current_range(8))
    bipot_current_range_min = kwargs.get('bipot_current_range_min', get_current_range(4))
    bipot_current_range_start = kwargs.get('bipot_current_range_start', get_current_range(6))
    set_bipot_settings(
        square_wave_voltammetry,
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
        square_wave_voltammetry,
        enable_bipot_current=enable_bipot_current,
        record_auxiliary_input=record_auxiliary_input,
        record_cell_potential=record_cell_potential,
        record_we_potential=record_we_potential,
        record_forward_and_reverse_currents=record_forward_and_reverse_currents,
    )

    # post measurement settings
    cell_on_after_measurement = kwargs.get('cell_on_after_measurement', False)
    cell_on_after_measurement_potential = kwargs.get(
        'cell_on_after_measurement_potential', 0.0
    )  # in V
    set_post_measurement_settings(
        square_wave_voltammetry, cell_on_after_measurement, cell_on_after_measurement_potential
    )

    # iR compensation settings
    use_ir_compensation = kwargs.get('use_ir_compensation', False)
    ir_compensation = kwargs.get('ir_compensation', 0.0)  # IR compensation in Ω
    set_ir_drop_compensation(square_wave_voltammetry, use_ir_compensation, ir_compensation)

    # set trigger settings
    trigger_at_equilibration = kwargs.get('trigger_at_equilibration', False)
    trigger_at_equilibration_lines = kwargs.get(
        'trigger_at_equilibration_lines', [False, False, False, False]
    )  # d0 high, d1 high, d2 high, d3 high
    trigger_at_measurement = kwargs.get('trigger_at_measurement', False)
    trigger_at_measurement_lines = kwargs.get(
        'trigger_at_measurement_lines', [False, False, False, False]
    )  # d0 high, d1 high, d2 high, d3 high
    set_trigger_at_equilibration_settings(
        square_wave_voltammetry, trigger_at_equilibration, trigger_at_equilibration_lines
    )
    set_trigger_at_measurement_settings(
        square_wave_voltammetry, trigger_at_measurement, trigger_at_measurement_lines
    )

    # set filter settings
    dc_mains_filter = kwargs.get(
        'dc_mains_filter', 50
    )  # set to 50 Hz or 60 Hz (50 Hz is default)
    default_curve_post_processing_filter = kwargs.get(
        'default_curve_post_processing_filter', 0
    )  # -1 = no filter, 0 = spike rejection, 1 = spike rejection + Savitsky-golay window 5, 2 = spike rejection + Savitsky-golay window 9, 3 = spike rejection + Savitsky-golay window 15, 4 = spike rejection + Savitsky-golay window 25
    set_filter_settings(
        square_wave_voltammetry, dc_mains_filter, default_curve_post_processing_filter
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
        square_wave_voltammetry, set_mux_mode, set_mux_channels, set_mux8r2_settings
    )

    # internal storage
    save_on_internal_storage = kwargs.get('save_on_internal_storage', False)
    square_wave_voltammetry.SaveOnDevice = save_on_internal_storage

    # use hardware synchronization with other channels/instruments
    use_hardware_sync = kwargs.get('use_hardware_sync', False)
    square_wave_voltammetry.UseHWSync = use_hardware_sync

    return square_wave_voltammetry
