from PalmSens import (  # type: ignore
    CurrentRange,
    CurrentRanges,
    ExtraValueMask,
    Method,
    MuxMethod,
    PotentialRange,
    PotentialRanges,
)
from PalmSens.Devices import PalmSens4Capabilities  # type: ignore
from PalmSens.Techniques import (  # type: ignore
    AmperometricDetection,
    CyclicVoltammetry,
    DifferentialPulse,
    ELevel,
    ImpedimetricGstatMethod,
    ImpedimetricMethod,
    LinearSweep,
    MethodScriptSandbox,
    MultistepAmperometry,
    OpenCircuitPotentiometry,
    Potentiometry,
    SquareWave,
)
from PalmSens.Techniques.Impedance import enumFrequencyType, enumScanType  # type: ignore


def linear_sweep_voltammetry(**kwargs):
    """Create a linear sweep voltammetry method object.

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
    * scanrate : float --
        Scan rate in V/s (default: 1.0)
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
    linear_sweep_voltammetry = LinearSweep()

    # (auto)ranging
    current_range_max = kwargs.get('current_range_max', get_current_range(8))
    current_range_min = kwargs.get('current_range_min', get_current_range(4))
    current_range_start = kwargs.get('current_range_start', get_current_range(6))
    set_autoranging_current(
        linear_sweep_voltammetry, current_range_max, current_range_min, current_range_start
    )

    # pretreatment
    deposition_potential = kwargs.get('deposition_potential', 0.0)
    deposition_time = kwargs.get('deposition_time', 0.0)
    conditioning_potential = kwargs.get('conditioning_potential', 0.0)
    conditioning_time = kwargs.get('conditioning_time', 0.0)
    set_pretreatment(
        linear_sweep_voltammetry,
        deposition_potential,
        deposition_time,
        conditioning_potential,
        conditioning_time,
    )

    # linear sweep voltammetry settings
    equilibration_time = kwargs.get('equilibration_time', 0.0)  # Time (s)
    begin_potential = kwargs.get('begin_potential', -0.5)  # potential (V)
    end_potential = kwargs.get('end_potential', 0.5)  # potential (V)
    step_potential = kwargs.get('step_potential', 0.1)  # potential (V)
    scanrate = kwargs.get('scanrate', 1.0)  # potential/time (V/s)
    linear_sweep_voltammetry.EquilibrationTime = equilibration_time
    linear_sweep_voltammetry.BeginPotential = begin_potential
    linear_sweep_voltammetry.EndPotential = end_potential
    linear_sweep_voltammetry.StepPotential = step_potential
    linear_sweep_voltammetry.Scanrate = scanrate

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
        linear_sweep_voltammetry,
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
        linear_sweep_voltammetry,
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
        linear_sweep_voltammetry,
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
        linear_sweep_voltammetry, cell_on_after_measurement, cell_on_after_measurement_potential
    )

    # limit settings
    use_limit_current_max = kwargs.get('use_limit_current_max', False)
    limit_current_max = kwargs.get('limit_current_max', 0.0)  # in µA
    use_limit_current_min = kwargs.get('use_limit_current_min', False)
    limit_current_min = kwargs.get('limit_current_min', 0.0)  # in µA
    set_limit_settings(
        linear_sweep_voltammetry,
        use_limit_current_max,
        limit_current_max,
        use_limit_current_min,
        limit_current_min,
    )

    # iR compensation settings
    use_ir_compensation = kwargs.get('use_ir_compensation', False)
    ir_compensation = kwargs.get('ir_compensation', 0.0)  # IR compensation in Ω
    set_ir_drop_compensation(linear_sweep_voltammetry, use_ir_compensation, ir_compensation)

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
        linear_sweep_voltammetry, trigger_at_equilibration, trigger_at_equilibration_lines
    )
    set_trigger_at_measurement_settings(
        linear_sweep_voltammetry, trigger_at_measurement, trigger_at_measurement_lines
    )

    # set filter settings
    dc_mains_filter = kwargs.get(
        'dc_mains_filter', 50
    )  # set to 50 Hz or 60 Hz (50 Hz is default)
    default_curve_post_processing_filter = kwargs.get(
        'default_curve_post_processing_filter', 0
    )  # -1 = no filter, 0 = spike rejection, 1 = spike rejection + Savitsky-golay window 5, 2 = spike rejection + Savitsky-golay window 9, 3 = spike rejection + Savitsky-golay window 15, 4 = spike rejection + Savitsky-golay window 25
    set_filter_settings(
        linear_sweep_voltammetry, dc_mains_filter, default_curve_post_processing_filter
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
        linear_sweep_voltammetry, set_mux_mode, set_mux_channels, set_mux8r2_settings
    )

    # internal storage
    save_on_internal_storage = kwargs.get('save_on_internal_storage', False)
    linear_sweep_voltammetry.SaveOnDevice = save_on_internal_storage

    # use hardware synchronization with other channels/instruments
    use_hardware_sync = kwargs.get('use_hardware_sync', False)
    linear_sweep_voltammetry.UseHWSync = use_hardware_sync

    return linear_sweep_voltammetry


def cyclic_voltammetry(**kwargs):
    """Create a cyclic voltammetry method object.

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
    * vertex1_potential : float --
        Vertex 1 potential in V (default: 0.5)
    * vertex2_potential : float --
        Vertex 2 potential in V (default: -0.5)
    * step_potential : float --
        Step potential in V (default: 0.1)
    * scanrate : float --
        Scan rate in V/s (default: 1.0)
    * n_cycles : int --
        Number of cycles (default: 1)
    * versus_ocp_mode : int --
        0 = disable versus OCP, 1 = vertex 1 potential, 2 = vertex 2 potential, 3 = vertex 1 & 2 potential, 4 = begin potential, 5 = begin & vertex 1 potential, 6 = begin & vertex 2 potential, 7 = begin & vertex 1 & 2 potential (default: 0)
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
        Use limit current max (default: False) [will reverse scan instead of aborting measurement]
    * limit_current_max : float --
        Limit current max in µA (default: 0.0)
    * use_limit_current_min : bool --
        Use limit current min (default: False) [will reverse scan instead of aborting measurement]
    * limit_current_min : float --
        Limit current min in µA (default: 0.0)
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
    cyclic_voltammetry = CyclicVoltammetry()

    # (auto)ranging
    current_range_max = kwargs.get('current_range_max', get_current_range(8))
    current_range_min = kwargs.get('current_range_min', get_current_range(4))
    current_range_start = kwargs.get('current_range_start', get_current_range(6))
    set_autoranging_current(
        cyclic_voltammetry, current_range_max, current_range_min, current_range_start
    )

    # pretreatment
    deposition_potential = kwargs.get('deposition_potential', 0.0)
    deposition_time = kwargs.get('deposition_time', 0.0)
    conditioning_potential = kwargs.get('conditioning_potential', 0.0)
    conditioning_time = kwargs.get('conditioning_time', 0.0)
    set_pretreatment(
        cyclic_voltammetry,
        deposition_potential,
        deposition_time,
        conditioning_potential,
        conditioning_time,
    )

    # cyclic voltammetry settings
    equilibration_time = kwargs.get('equilibration_time', 0.0)  # Time (s)
    begin_potential = kwargs.get('begin_potential', -0.5)  # potential (V)
    vertex1_potential = kwargs.get('vertex1_potential', 0.5)  # potential (V)
    vertex2_potential = kwargs.get('vertex2_potential', -0.5)  # potential (V)
    step_potential = kwargs.get('step_potential', 0.1)  # potential (V)
    scanrate = kwargs.get('scanrate', 1.0)  # potential/time (V/s)
    n_cycles = kwargs.get('n_cycles', 1)  # number of cycles (default: 1)
    cyclic_voltammetry.EquilibrationTime = equilibration_time
    cyclic_voltammetry.BeginPotential = begin_potential
    cyclic_voltammetry.Vtx1Potential = vertex1_potential
    cyclic_voltammetry.Vtx2Potential = vertex2_potential
    cyclic_voltammetry.StepPotential = step_potential
    cyclic_voltammetry.Scanrate = scanrate
    cyclic_voltammetry.nScans = n_cycles

    # advanced settings
    # versus OCP settings
    versus_ocp_mode = kwargs.get(
        'versus_ocp_mode', 0
    )  # 0 = disable versus OCP, 1 = vertex 1 potential, 2 = vertex 2 potential, 3 = vertex 1 & 2 potential, 4 = begin potential, 5 = begin & vertex 1 potential, 6 = begin & vertex 2 potential, 7 = begin & vertex 1 & 2 potential
    versus_ocp_max_ocp_time = kwargs.get('versus_ocp_max_ocp_time', 20)  # Time (s)
    versus_ocp_stability_criterion = kwargs.get(
        'versus_ocp_stability_criterion', 0
    )  # 0 = no stability criterion, > 0 is stability threshold potential/time (mV/s)
    set_versus_ocp(
        cyclic_voltammetry,
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
        cyclic_voltammetry,
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
        cyclic_voltammetry,
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
        cyclic_voltammetry, cell_on_after_measurement, cell_on_after_measurement_potential
    )

    # limit settings
    use_limit_current_max = kwargs.get('use_limit_current_max', False)
    limit_current_max = kwargs.get('limit_current_max', 0.0)  # in µA
    use_limit_current_min = kwargs.get('use_limit_current_min', False)
    limit_current_min = kwargs.get('limit_current_min', 0.0)  # in µA
    set_limit_settings(
        cyclic_voltammetry,
        use_limit_current_max,
        limit_current_max,
        use_limit_current_min,
        limit_current_min,
    )

    # iR compensation settings
    use_ir_compensation = kwargs.get('use_ir_compensation', False)
    ir_compensation = kwargs.get('ir_compensation', 0.0)  # IR compensation in Ω
    set_ir_drop_compensation(cyclic_voltammetry, use_ir_compensation, ir_compensation)

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
        cyclic_voltammetry, trigger_at_equilibration, trigger_at_equilibration_lines
    )
    set_trigger_at_measurement_settings(
        cyclic_voltammetry, trigger_at_measurement, trigger_at_measurement_lines
    )

    # set filter settings
    dc_mains_filter = kwargs.get(
        'dc_mains_filter', 50
    )  # set to 50 Hz or 60 Hz (50 Hz is default)
    default_curve_post_processing_filter = kwargs.get(
        'default_curve_post_processing_filter', 0
    )  # -1 = no filter, 0 = spike rejection, 1 = spike rejection + Savitsky-golay window 5, 2 = spike rejection + Savitsky-golay window 9, 3 = spike rejection + Savitsky-golay window 15, 4 = spike rejection + Savitsky-golay window 25
    set_filter_settings(
        cyclic_voltammetry, dc_mains_filter, default_curve_post_processing_filter
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
        cyclic_voltammetry, set_mux_mode, set_mux_channels, set_mux8r2_settings
    )

    # internal storage
    save_on_internal_storage = kwargs.get('save_on_internal_storage', False)
    cyclic_voltammetry.SaveOnDevice = save_on_internal_storage

    # use hardware synchronization with other channels/instruments
    use_hardware_sync = kwargs.get('use_hardware_sync', False)
    cyclic_voltammetry.UseHWSync = use_hardware_sync

    return cyclic_voltammetry


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
    square_wave_voltammetry = SquareWave()

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


def differential_pulse_voltammetry(**kwargs):
    """Create a differential pulse voltammetry method object.

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
    * pulse_potential : float --
        Pulse potential in V (default: 0.05)
    * pulse_time : float --
        Pulse time in s (default: 0.01)
    * scanrate : float --
        Scan rate in V/s (default: 1.0)
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
    * use_hardware_sync : bool --
        Use hardware synchronization with other channels/instruments (default: False)
    """
    differential_pulse_voltammetry = DifferentialPulse()

    # (auto)ranging
    current_range_max = kwargs.get('current_range_max', get_current_range(8))
    current_range_min = kwargs.get('current_range_min', get_current_range(4))
    current_range_start = kwargs.get('current_range_start', get_current_range(6))
    set_autoranging_current(
        differential_pulse_voltammetry,
        current_range_max,
        current_range_min,
        current_range_start,
    )

    # pretreatment
    deposition_potential = kwargs.get('deposition_potential', 0.0)
    deposition_time = kwargs.get('deposition_time', 0.0)
    conditioning_potential = kwargs.get('conditioning_potential', 0.0)
    conditioning_time = kwargs.get('conditioning_time', 0.0)
    set_pretreatment(
        differential_pulse_voltammetry,
        deposition_potential,
        deposition_time,
        conditioning_potential,
        conditioning_time,
    )

    # differential pulse voltammetry settings
    equilibration_time = kwargs.get('equilibration_time', 0.0)  # Time (s)
    begin_potential = kwargs.get('begin_potential', -0.5)  # potential (V)
    end_potential = kwargs.get('end_potential', 0.5)  # potential (V)
    step_potential = kwargs.get('step_potential', 0.1)  # potential (V)
    pulse_potential = kwargs.get('pulse_potential', 0.05)  # potential (V)
    pulse_time = kwargs.get('pulse_time', 0.01)  # time (s)
    scan_rate = kwargs.get('scanrate', 1.0)  # potential/time (V/s)
    differential_pulse_voltammetry.EquilibrationTime = equilibration_time
    differential_pulse_voltammetry.BeginPotential = begin_potential
    differential_pulse_voltammetry.EndPotential = end_potential
    differential_pulse_voltammetry.StepPotential = step_potential
    differential_pulse_voltammetry.PulsePotential = pulse_potential
    differential_pulse_voltammetry.PulseTime = pulse_time
    differential_pulse_voltammetry.Scanrate = scan_rate

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
        differential_pulse_voltammetry,
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
        differential_pulse_voltammetry,
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
        differential_pulse_voltammetry,
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
        differential_pulse_voltammetry,
        cell_on_after_measurement,
        cell_on_after_measurement_potential,
    )

    # iR compensation settings
    use_ir_compensation = kwargs.get('use_ir_compensation', False)
    ir_compensation = kwargs.get('ir_compensation', 0.0)  # IR compensation in Ω
    set_ir_drop_compensation(
        differential_pulse_voltammetry, use_ir_compensation, ir_compensation
    )

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
        differential_pulse_voltammetry, trigger_at_equilibration, trigger_at_equilibration_lines
    )
    set_trigger_at_measurement_settings(
        differential_pulse_voltammetry, trigger_at_measurement, trigger_at_measurement_lines
    )

    # set filter settings
    dc_mains_filter = kwargs.get(
        'dc_mains_filter', 50
    )  # set to 50 Hz or 60 Hz (50 Hz is default)
    default_curve_post_processing_filter = kwargs.get(
        'default_curve_post_processing_filter', 0
    )  # -1 = no filter, 0 = spike rejection, 1 = spike rejection + Savitsky-golay window 5, 2 = spike rejection + Savitsky-golay window 9, 3 = spike rejection + Savitsky-golay window 15, 4 = spike rejection + Savitsky-golay window 25
    set_filter_settings(
        differential_pulse_voltammetry, dc_mains_filter, default_curve_post_processing_filter
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
        differential_pulse_voltammetry, set_mux_mode, set_mux_channels, set_mux8r2_settings
    )

    # internal storage
    save_on_internal_storage = kwargs.get('save_on_internal_storage', False)
    differential_pulse_voltammetry.SaveOnDevice = save_on_internal_storage

    # use hardware synchronization with other channels/instruments
    use_hardware_sync = kwargs.get('use_hardware_sync', False)
    differential_pulse_voltammetry.UseHWSync = use_hardware_sync

    return differential_pulse_voltammetry


def chronoamperometry(**kwargs):
    """Create a chronoamperometry method object.

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
    * potential : float --
        Potential in V (default: 0.0)
    * run_time : float --
        Run time in s (default: 1.0)
    * versus_ocp_mode : int --
        0 = disable versus OCP, 1 = versus potential (default: 0)
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
    * use_limit_charge_max : bool --
        Use limit charge max (default: False)
    * limit_charge_max : float --
        Limit charge max in µC (default: 0.0)
    * use_limit_charge_min : bool --
        Use limit charge min (default: False)
    * limit_charge_min : float --
        Limit charge min in µC (default: 0.0)
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
        Set multiplexer mode (default: -1) [-1 = disable, 0 = sequentially, 1 = alternatingly]
    * set_mux_channels : list --
        Set multiplexer channels (default: [False, False, False, False, False, False, False, False]) [a list of bools for each channel (channel 1, channel 2, ..., channel 128). In consecutive mode all selections are valid, in alternating mode the first channel must be selected and all other channels should be consecutive i.e. (channel 1, channel 2, channel 3 and so on)]
    * set_mux8r2_settings : PalmSens.Method.MuxSettings --
        Initialize the settings for the MUX8R2 multiplexer (default: None) [use get_mux8r2_settings() to create the settings]
    * save_on_internal_storage : bool --
        Save on internal storage (default: False)
    * use_hardware_sync : bool --
        Use hardware synchronization with other channels/instruments (default: False)
    """
    chronoamperometry = AmperometricDetection()

    # (auto)ranging
    current_range_max = kwargs.get('current_range_max_range_max', get_current_range(8))
    currrent_range_min = kwargs.get('current_range_max_range_min', get_current_range(4))
    current_range_max_range_start = kwargs.get(
        'current_range_max_range_start', get_current_range(6)
    )
    set_autoranging_current(
        chronoamperometry, current_range_max, currrent_range_min, current_range_max_range_start
    )

    # pretreatment
    deposition_potential = kwargs.get('deposition_potential', 0.0)
    deposition_time = kwargs.get('deposition_time', 0.0)
    conditioning_potential = kwargs.get('conditioning_potential', 0.0)
    conditioning_time = kwargs.get('conditioning_time', 0.0)
    set_pretreatment(
        chronoamperometry,
        deposition_potential,
        deposition_time,
        conditioning_potential,
        conditioning_time,
    )

    # chronoamperometry settings
    equilibration_time = kwargs.get('equilibration_time', 0.0)
    interval_time = kwargs.get('interval_time', 0.1)
    potential = kwargs.get('e', 0.0)
    run_time = kwargs.get('run_time', 1.0)
    chronoamperometry.EquilibrationTime = equilibration_time
    chronoamperometry.IntervalTime = interval_time
    chronoamperometry.Potential = potential
    chronoamperometry.RunTime = run_time

    # advanced settings
    # versus OCP settings
    versus_ocp_mode = kwargs.get(
        'versus_ocp_mode', 0
    )  # 0 = disable versus OCP, 1 = versus potential
    versus_ocp_max_ocp_time = kwargs.get('versus_ocp_max_ocp_time', 20)  # Time (s)
    versus_ocp_stability_criterion = kwargs.get(
        'versus_ocp_stability_criterion', 0
    )  # 0 = no stability criterion, > 0 is stability threshold potential/time (mV/s)
    set_versus_ocp(
        chronoamperometry,
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
        chronoamperometry,
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
        chronoamperometry,
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
        chronoamperometry, cell_on_after_measurement, cell_on_after_measurement_potential
    )

    # limit settings
    use_limit_current_max = kwargs.get('use_limit_current_max', False)
    limit_current_max = kwargs.get('limit_current_max', 0.0)  # in µA
    use_limit_current_min = kwargs.get('use_limit_current_min', False)
    limit_current_min = kwargs.get('limit_current_min', 0.0)  # in µA
    set_limit_settings(
        chronoamperometry,
        use_limit_current_max,
        limit_current_max,
        use_limit_current_min,
        limit_current_min,
    )

    use_limit_charge_max = kwargs.get('use_limit_charge_max', False)
    limit_charge_max = kwargs.get('limit_charge_max', 0.0)  # in µC
    use_limit_charge_min = kwargs.get('use_limit_charge_min', False)
    limit_charge_min = kwargs.get('limit_charge_min', 0.0)  # in µC
    set_charge_limit_settings(
        chronoamperometry,
        use_limit_charge_max,
        limit_charge_max,
        use_limit_charge_min,
        limit_charge_min,
    )

    # iR compensation settings
    use_ir_compensation = kwargs.get('use_ir_compensation', False)
    ir_compensation = kwargs.get('ir_compensation', 0.0)  # IR compensation in Ω
    set_ir_drop_compensation(chronoamperometry, use_ir_compensation, ir_compensation)

    # trigger settings
    trigger_at_equilibration = kwargs.get('trigger_at_equilibration', False)
    trigger_at_equilibration_lines = kwargs.get(
        'trigger_at_equilibration_lines', [False, False, False, False]
    )  # d0 high, d1 high, d2 high, d3 high
    trigger_at_measurement = kwargs.get('trigger_at_measurement', False)
    trigger_at_measurement_lines = kwargs.get(
        'trigger_at_measurement_lines', [False, False, False, False]
    )  # d0 high, d1 high, d2 high, d3 high
    set_trigger_at_equilibration_settings(
        chronoamperometry, trigger_at_equilibration, trigger_at_equilibration_lines
    )
    set_trigger_at_measurement_settings(
        chronoamperometry, trigger_at_measurement, trigger_at_measurement_lines
    )

    # set filter settings
    dc_mains_filter = kwargs.get(
        'dc_mains_filter', 50
    )  # set to 50 Hz or 60 Hz (50 Hz is default)
    default_curve_post_processing_filter = kwargs.get(
        'default_curve_post_processing_filter', 0
    )  # -1 = no filter, 0 = spike rejection, 1 = spike rejection + Savitsky-golay window 5, 2 = spike rejection + Savitsky-golay window 9, 3 = spike rejection + Savitsky-golay window 15, 4 = spike rejection + Savitsky-golay window 25
    set_filter_settings(
        chronoamperometry, dc_mains_filter, default_curve_post_processing_filter
    )

    # set multiplexer settings
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
        chronoamperometry, set_mux_mode, set_mux_channels, set_mux8r2_settings
    )

    # internal storage
    save_on_internal_storage = kwargs.get('save_on_internal_storage', False)
    chronoamperometry.SaveOnDevice = save_on_internal_storage

    # use hardware synchronization with other channels/instruments
    use_hardware_sync = kwargs.get('use_hardware_sync', False)
    chronoamperometry.UseHWSync = use_hardware_sync

    return chronoamperometry


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
    multi_step_amperometry = MultistepAmperometry()

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


def open_circuit_potentiometry(**kwargs):
    """Create an open circuit potentiometry method object.

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
    * interval_time : float --
        Interval time in s (default: 0.1)
    * run_time : float --
        Run time in s (default: 1.0)
    * record_auxiliary_input : bool --
        Record auxiliary input (default: False)
    * record_we_current : bool --
        Record working electrode current (default: False)
    * record_we_current_range : PalmSens.CurrentRange --
        Record working electrode current range (default: 1 µA) [use get_current_range() to get the range]
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
    open_circuit_potentiometry = OpenCircuitPotentiometry()

    # (auto)ranging
    # current in pretreatment
    current_range_max = kwargs.get('current_range_max', get_current_range(8))
    current_range_min = kwargs.get('current_range_min', get_current_range(4))
    current_range_start = kwargs.get('current_range_start', get_current_range(6))
    set_autoranging_current(
        open_circuit_potentiometry, current_range_max, current_range_min, current_range_start
    )

    # potential
    potential_range_max = kwargs.get('potential_range_max', get_potential_range(7))
    potential_range_min = kwargs.get('potential_range_min', get_potential_range(1))
    potential_range_start = kwargs.get('potential_range_start', get_potential_range(7))
    set_autoranging_potential(
        open_circuit_potentiometry,
        potential_range_max,
        potential_range_min,
        potential_range_start,
    )

    # pretreatment
    deposition_potential = kwargs.get('deposition_potential', 0.0)
    deposition_time = kwargs.get('deposition_time', 0.0)
    conditioning_potential = kwargs.get('conditioning_potential', 0.0)
    conditioning_time = kwargs.get('conditioning_time', 0.0)
    set_pretreatment(
        open_circuit_potentiometry,
        deposition_potential,
        deposition_time,
        conditioning_potential,
        conditioning_time,
    )

    # open circuit potentiometry settings
    interval_time = kwargs.get('interval_time', 0.1)  # Time (s)
    run_time = kwargs.get('run_time', 1.0)  # Time (s)
    open_circuit_potentiometry.IntervalTime = interval_time
    open_circuit_potentiometry.RunTime = run_time

    # advanced settings
    # record extra value settings
    record_auxiliary_input = kwargs.get('record_auxiliary_input', False)
    record_we_current = kwargs.get('record_we_current', False)
    record_we_current_range = kwargs.get('record_we_current_range', get_current_range(4))
    set_extra_value_mask(
        open_circuit_potentiometry,
        record_auxiliary_input=record_auxiliary_input,
        record_we_current=record_we_current,
        record_we_current_range=record_we_current_range,
    )

    # post measurement settings
    cell_on_after_measurement = kwargs.get('cell_on_after_measurement', False)
    cell_on_after_measurement_potential = kwargs.get(
        'cell_on_after_measurement_potential', 0.0
    )  # in V
    set_post_measurement_settings(
        open_circuit_potentiometry,
        cell_on_after_measurement,
        cell_on_after_measurement_potential,
    )

    # limit settings
    use_limit_potential_max = kwargs.get('use_limit_potential_max', False)
    limit_potential_max = kwargs.get('limit_potential_max', 0.0)  # in V
    use_limit_potential_min = kwargs.get('use_limit_potential_min', False)
    limit_potential_min = kwargs.get('limit_potential_min', 0.0)  # in V
    set_limit_settings(
        open_circuit_potentiometry,
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
        open_circuit_potentiometry, trigger_at_measurement, trigger_at_measurement_lines
    )

    # set filter settings
    dc_mains_filter = kwargs.get(
        'dc_mains_filter', 50
    )  # set to 50 Hz or 60 Hz (50 Hz is default)
    default_curve_post_processing_filter = kwargs.get(
        'default_curve_post_processing_filter', 0
    )  # -1 = no filter, 0 = spike rejection, 1 = spike rejection + Savitsky-golay window 5, 2 = spike rejection + Savitsky-golay window 9, 3 = spike rejection + Savitsky-golay window 15, 4 = spike rejection + Savitsky-golay window 25
    set_filter_settings(
        open_circuit_potentiometry, dc_mains_filter, default_curve_post_processing_filter
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
        open_circuit_potentiometry, set_mux_mode, set_mux_channels, set_mux8r2_settings
    )

    # internal storage
    save_on_internal_storage = kwargs.get('save_on_internal_storage', False)
    open_circuit_potentiometry.SaveOnDevice = save_on_internal_storage

    # use hardware synchronization with other channels/instruments
    use_hardware_sync = kwargs.get('use_hardware_sync', False)
    open_circuit_potentiometry.UseHWSync = use_hardware_sync

    return open_circuit_potentiometry


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
    chronopotentiometry = Potentiometry()

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


def electrochemical_impedance_spectroscopy(**kwargs):
    """Create an electrochemical impedance spectroscopy method object.

    :Keyword Arguments:
    * current_range_max : PalmSens.CurrentRange --
        Maximum current range (default: 10 mA) [use get_current_range() to get the range]
    * current_range_min : PalmSens.CurrentRange --
        Minimum current range (default: 1 µA) [use get_current_range() to get the range]
    * potential_range_max : PalmSens.PotentialRange --
        Maximum potential range (default: 1 V) [use get_potential_range() to get the range]
    * potential_range_min : PalmSens.PotentialRange --
        Minimum potential range (default: 10 mV) [use get_potential_range() to get the range]
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
    * dc_potential : float --
        DC potential in V (default: 0.0)
    * ac_potential : float --
        AC potential in V RMS (default: 0.01)
    * n_frequencies : int --
        Number of frequencies (default: 11)
    * max_frequency : float --
        Maximum frequency in Hz (default: 1e5)
    * min_frequency : float --
        Minimum frequency in Hz (default: 1e3)
    * versus_ocp_mode : int --
        Versus OCP mode (default: 0) [0 = disable versus OCP, 1 = versus potential]
    * versus_ocp_max_ocp_time : float --
        Versus OCP max OCP time in s (default: 20.0)
    * versus_ocp_stability_criterion : float --
        Versus OCP stability criterion in mV/s (default: 0.0) [0 = no stability criterion, > 0 is stability threshold potential/time (mV/s)]
    * cell_on_after_measurement : bool --
        Cell on after measurement (default: False)
    * cell_on_after_measurement_potential : float --
        Cell on after measurement potential in V (default: 0.0)
    * trigger_at_equilibration : bool --
        Trigger at equilibration (default: False)
    * trigger_at_equilibration_lines : list --
        Trigger at equilibration lines (default: [False, False, False, False]) [d0 high, d1 high, d2 high, d3 high]
    * trigger_at_measurement : bool --
        Trigger at measurement (default: False)
    * trigger_at_measurement_lines : list --
        Trigger at measurement lines (default: [False, False, False, False]) [d0 high, d1 high, d2 high, d3 high]
    * set_mux_mode : int --
        Set multiplexer mode (default: -1) [-1 = disable, 0 = sequentially]
    * set_mux_channels : list --
        Set multiplexer channels (default: [False, False, False, False, False, False, False, False]) [a list of bools for each channel (channel 1, channel 2, ..., channel 128).
    * set_mux8r2_settings : PalmSens.Method.MuxSettings --
        Initialize the settings for the MUX8R2 multiplexer (default: None) [use get_mux8r2_settings() to create the settings]
    * save_on_internal_storage : bool --
        Save on internal storage (default: False)
    """
    electrochemical_impedance_spectroscopy = ImpedimetricMethod()

    # (auto)ranging
    current_range_max = kwargs.get('current_range_max', get_current_range(8))
    current_range_min = kwargs.get('current_range_min', get_current_range(4))
    potential_range_max = kwargs.get('potential_range_max', get_potential_range(7))
    potential_range_min = kwargs.get('potential_range_min', get_potential_range(1))
    set_autoranging_current(
        electrochemical_impedance_spectroscopy,
        current_range_max,
        current_range_min,
        current_range_max,
    )
    set_autoranging_potential(
        electrochemical_impedance_spectroscopy,
        potential_range_max,
        potential_range_min,
        potential_range_max,
    )

    # pretreatment
    deposition_potential = kwargs.get('deposition_potential', 0.0)
    deposition_time = kwargs.get('deposition_time', 0.0)
    conditioning_potential = kwargs.get('conditioning_potential', 0.0)
    conditioning_time = kwargs.get('conditioning_time', 0.0)
    set_pretreatment(
        electrochemical_impedance_spectroscopy,
        deposition_potential,
        deposition_time,
        conditioning_potential,
        conditioning_time,
    )

    # electrochemical impedance spectroscopy settings
    equilibration_time = kwargs.get('equilibration_time', 0.0)  # Time (s)
    dc_potential = kwargs.get('dc_potential', 0.0)  # in V
    ac_potential = kwargs.get('ac_potential', 0.01)  # in V RMS
    n_frequencies = kwargs.get('n_frequencies', 11)  # Number of frequencies
    max_frequency = kwargs.get('max_frequency', 1e5)  # in Hz
    min_frequency = kwargs.get('min_frequency', 1e3)  # in Hz
    electrochemical_impedance_spectroscopy.ScanType = enumScanType.Fixed
    electrochemical_impedance_spectroscopy.FreqType = enumFrequencyType.Scan
    electrochemical_impedance_spectroscopy.EquilibrationTime = equilibration_time
    electrochemical_impedance_spectroscopy.Potential = dc_potential
    electrochemical_impedance_spectroscopy.Eac = ac_potential
    electrochemical_impedance_spectroscopy.nFrequencies = n_frequencies
    electrochemical_impedance_spectroscopy.MaxFrequency = max_frequency
    electrochemical_impedance_spectroscopy.MinFrequency = min_frequency

    # advanced settings
    # versus OCP settings
    versus_ocp_mode = kwargs.get(
        'versus_ocp_mode', 0
    )  # 0 = disable versus OCP, 1 = versus potential
    versus_ocp_max_ocp_time = kwargs.get('versus_ocp_max_ocp_time', 20)  # Time (s)
    versus_ocp_stability_criterion = kwargs.get(
        'versus_ocp_stability_criterion', 0
    )  # 0 = no stability criterion, > 0 is stability threshold potential/time (mV/s)
    set_versus_ocp(
        electrochemical_impedance_spectroscopy,
        versus_ocp_mode,
        versus_ocp_max_ocp_time,
        versus_ocp_stability_criterion,
    )

    # post measurement settings
    cell_on_after_measurement = kwargs.get('cell_on_after_measurement', False)
    cell_on_after_measurement_potential = kwargs.get(
        'cell_on_after_measurement_potential', 0.0
    )  # in V
    set_post_measurement_settings(
        electrochemical_impedance_spectroscopy,
        cell_on_after_measurement,
        cell_on_after_measurement_potential,
    )

    # trigger settings
    trigger_at_equilibration = kwargs.get('trigger_at_equilibration', False)
    trigger_at_equilibration_lines = kwargs.get(
        'trigger_at_equilibration_lines', [False, False, False, False]
    )  # d0 high, d1 high, d2 high, d3 high
    trigger_at_measurement = kwargs.get('trigger_at_measurement', False)
    trigger_at_measurement_lines = kwargs.get(
        'trigger_at_measurement_lines', [False, False, False, False]
    )  # d0 high, d1 high, d2 high, d3 high
    set_trigger_at_equilibration_settings(
        electrochemical_impedance_spectroscopy,
        trigger_at_equilibration,
        trigger_at_equilibration_lines,
    )
    set_trigger_at_measurement_settings(
        electrochemical_impedance_spectroscopy,
        trigger_at_measurement,
        trigger_at_measurement_lines,
    )

    # set multiplexer settings
    set_mux_mode = kwargs.get('set_mux_mode', -1)  # -1 = disable, 0 = sequentially
    set_mux_channels = kwargs.get(
        'set_mux_channels', [False, False, False, False, False, False, False, False]
    )  # a list of bools for each channel (channel 1, channel 2, ..., channel 128).
    set_mux8r2_settings = kwargs.get(
        'set_mux8r2_settings', None
    )  # Initialize the settings for the MUX8R2 multiplexer, PalmSens.Method.MuxSettings, use get_mux8r2_settings() to create the settings
    set_multiplexer_settings(
        electrochemical_impedance_spectroscopy,
        set_mux_mode,
        set_mux_channels,
        set_mux8r2_settings,
    )

    # internal storage
    save_on_internal_storage = kwargs.get('save_on_internal_storage', False)
    electrochemical_impedance_spectroscopy.SaveOnDevice = save_on_internal_storage

    return electrochemical_impedance_spectroscopy


def galvanostatic_impedance_spectroscopy(**kwargs):
    """Create a galvanostatic impedance spectroscopy method object.

    :Keyword Arguments:
    * current_range_max : PalmSens.CurrentRange --
        Maximum current range (default: 10 mA) [use get_current_range() to get the range]
    * current_range_min : PalmSens.CurrentRange --
        Minimum current range (default: 1 µA) [use get_current_range() to get the range]
    * potential_range_max : PalmSens.PotentialRange --
        Maximum potential range (default: 1 V) [use get_potential_range() to get the range]
    * potential_range_min : PalmSens.PotentialRange --
        Minimum potential range (default: 10 mV) [use get_potential_range() to get the range]
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
    * applied_current_range : PalmSens.CurrentRange --
        Applied current range (default: 100 µA) [use get_current_range() to get the range]
    * ac_current : float --
        AC current in applied current range RMS (default: 0.01)
    * dc_current : float --
        DC current in applied current range (default: 0.0)
    * n_frequencies : int --
        Number of frequencies (default: 11)
    * max_frequency : float --
        Maximum frequency in Hz (default: 1e5)
    * min_frequency : float --
        Minimum frequency in Hz (default: 1e3)
    * cell_on_after_measurement : bool --
        Cell on after measurement (default: False)
    * cell_on_after_measurement_potential : float --
        Cell on after measurement potential in V (default: 0.0)
    * trigger_at_equilibration : bool --
        Trigger at equilibration (default: False)
    * trigger_at_equilibration_lines : list --
        Trigger at equilibration lines (default: [False, False, False, False]) [d0 high, d1 high, d2 high, d3 high]
    * trigger_at_measurement : bool --
        Trigger at measurement (default: False)
    * trigger_at_measurement_lines : list --
        Trigger at measurement lines (default: [False, False, False, False]) [d0 high, d1 high, d2 high, d3 high]
    * set_mux_mode : int --
        Set multiplexer mode (default: -1) [-1 = disable, 0 = sequentially]
    * set_mux_channels : list --
        Set multiplexer channels (default: [False, False, False, False, False, False, False, False]) [a list of bools for each channel (channel 1, channel 2, ..., channel 128).
    * set_mux8r2_settings : PalmSens.Method.MuxSettings --
        Initialize the settings for the MUX8R2 multiplexer (default: None) [use get_mux8r2_settings() to create the settings]
    * save_on_internal_storage : bool --
        Save on internal storage (default: False)
    """
    galvanostatic_impedance_spectroscopy = ImpedimetricGstatMethod()

    # (auto)ranging
    current_range_max = kwargs.get('current_range_max', get_current_range(8))
    current_range_min = kwargs.get('current_range_min', get_current_range(4))
    potential_range_max = kwargs.get('potential_range_max', get_potential_range(7))
    potential_range_min = kwargs.get('potential_range_min', get_potential_range(1))
    set_autoranging_current(
        galvanostatic_impedance_spectroscopy,
        current_range_max,
        current_range_min,
        current_range_max,
    )
    set_autoranging_potential(
        galvanostatic_impedance_spectroscopy,
        potential_range_max,
        potential_range_min,
        potential_range_max,
    )

    # pretreatment
    deposition_potential = kwargs.get('deposition_potential', 0.0)
    deposition_time = kwargs.get('deposition_time', 0.0)
    conditioning_potential = kwargs.get('conditioning_potential', 0.0)
    conditioning_time = kwargs.get('conditioning_time', 0.0)
    set_pretreatment(
        galvanostatic_impedance_spectroscopy,
        deposition_potential,
        deposition_time,
        conditioning_potential,
        conditioning_time,
    )

    # galvanostatic impedance spectroscopy settings
    applied_current_range = kwargs.get(
        'applied_current_range', get_current_range(6)
    )  # in applied current range
    equilibration_time = kwargs.get('equilibration_time', 0.0)  # Time (s)
    ac_current = kwargs.get('ac_current', 0.01)  # in applied current range RMS
    dc_current = kwargs.get('dc_current', 0.0)  # in applied current range
    n_frequencies = kwargs.get('n_frequencies', 11)  # Number of frequencies
    max_frequency = kwargs.get('max_frequency', 1e5)  # in Hz
    min_frequency = kwargs.get('min_frequency', 1e3)  # in Hz
    galvanostatic_impedance_spectroscopy.ScanType = enumScanType.Fixed
    galvanostatic_impedance_spectroscopy.FreqType = enumFrequencyType.Scan
    galvanostatic_impedance_spectroscopy.AppliedCurrentRange = applied_current_range
    galvanostatic_impedance_spectroscopy.EquilibrationTime = equilibration_time
    galvanostatic_impedance_spectroscopy.Iac = ac_current
    galvanostatic_impedance_spectroscopy.Idc = dc_current
    galvanostatic_impedance_spectroscopy.nFrequencies = n_frequencies
    galvanostatic_impedance_spectroscopy.MaxFrequency = max_frequency
    galvanostatic_impedance_spectroscopy.MinFrequency = min_frequency

    # advanced settings
    # post measurement settings
    cell_on_after_measurement = kwargs.get('cell_on_after_measurement', False)
    cell_on_after_measurement_potential = kwargs.get(
        'cell_on_after_measurement_potential', 0.0
    )  # in V
    set_post_measurement_settings(
        galvanostatic_impedance_spectroscopy,
        cell_on_after_measurement,
        cell_on_after_measurement_potential,
    )

    # trigger settings
    trigger_at_equilibration = kwargs.get('trigger_at_equilibration', False)
    trigger_at_equilibration_lines = kwargs.get(
        'trigger_at_equilibration_lines', [False, False, False, False]
    )  # d0 high, d1 high, d2 high, d3 high
    trigger_at_measurement = kwargs.get('trigger_at_measurement', False)
    trigger_at_measurement_lines = kwargs.get(
        'trigger_at_measurement_lines', [False, False, False, False]
    )  # d0 high, d1 high, d2 high, d3 high
    set_trigger_at_equilibration_settings(
        galvanostatic_impedance_spectroscopy,
        trigger_at_equilibration,
        trigger_at_equilibration_lines,
    )
    set_trigger_at_measurement_settings(
        galvanostatic_impedance_spectroscopy,
        trigger_at_measurement,
        trigger_at_measurement_lines,
    )

    # set multiplexer settings
    set_mux_mode = kwargs.get('set_mux_mode', -1)  # -1 = disable, 0 = sequentially
    set_mux_channels = kwargs.get(
        'set_mux_channels', [False, False, False, False, False, False, False, False]
    )  # a list of bools for each channel (channel 1, channel 2, ..., channel 128).
    set_mux8r2_settings = kwargs.get(
        'set_mux8r2_settings', None
    )  # Initialize the settings for the MUX8R2 multiplexer, PalmSens.Method.MuxSettings, use get_mux8r2_settings() to create the settings
    set_multiplexer_settings(
        galvanostatic_impedance_spectroscopy,
        set_mux_mode,
        set_mux_channels,
        set_mux8r2_settings,
    )

    # internal storage
    save_on_internal_storage = kwargs.get('save_on_internal_storage', False)
    galvanostatic_impedance_spectroscopy.SaveOnDevice = save_on_internal_storage

    return galvanostatic_impedance_spectroscopy


def method_script_sandbox(method_script):
    """Create a method script sandbox object.

    :Keyword Arguments:
    * method_script : str --
    """
    method_script_sandbox = MethodScriptSandbox()
    method_script_sandbox.MethodScript = method_script
    return method_script_sandbox


def get_current_range(id):
    """Get the current range for a given id.

    The id corresponds to the following ranges:
    * 100 pA = 0,
    * 1 nA = 1,
    * 10 nA = 2,
    * 100 nA = 3,
    * 1 uA = 4,
    * 10 uA = 5,
    * 100 uA = 6,
    * 1 mA = 7,
    * 10 mA = 8,
    * 100 mA = 9,
    * 2 uA = 10,
    * 4 uA = 11,
    * 8 uA = 12,
    * 16 uA = 13,
    * 32 uA = 14,
    * 63 uA = 26,
    * 125 uA = 17,
    * 250 uA = 18,
    * 500 uA = 19,
    * 5 mA = 20,
    * 6 uA = 21,
    * 13 uA = 22,
    * 25 uA = 23,
    * 50 uA = 24,
    * 200 uA = 25,
    * 1 A = 30
    """
    return CurrentRange(CurrentRanges(id))


def get_potential_range(id):
    """Get the potential range for a given id.

    The id corresponds to the following ranges:
    * 1 mV = 0,
    * 10 mV = 1,
    * 20 mV = 2,
    * 50 mV = 3,
    * 100 mV = 4,
    * 200 mV = 5,
    * 500 mV = 6,
    * 1 V = 7
    """
    if id == 0:
        return PotentialRange(PotentialRanges.pr1mV)
    elif id == 1:
        return PotentialRange(PotentialRanges.pr10mV)
    elif id == 2:
        return PotentialRange(PotentialRanges.pr20mV)
    elif id == 3:
        return PotentialRange(PotentialRanges.pr50mV)
    elif id == 4:
        return PotentialRange(PotentialRanges.pr100mV)
    elif id == 5:
        return PotentialRange(PotentialRanges.pr200mV)
    elif id == 6:
        return PotentialRange(PotentialRanges.pr500mV)
    elif id == 7:
        return PotentialRange(PotentialRanges.pr1V)
    else:
        raise ValueError(
            'Invalid id for potential range. Valid ids are: 0, 1, 2, 3, 4, 5, 6, 7'
        )


def set_autoranging_current(method, i_range_max, i_range_min, i_range_start):
    """Set the autoranging current for a given method."""
    method.Ranging.MaximumCurrentRange = i_range_max
    method.Ranging.MinimumCurrentRange = i_range_min
    method.Ranging.StartCurrentRange = i_range_start


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
        method, bipot_current_range_max, bipot_current_range_min, bipot_current_range_start
    )


def set_extra_value_mask(method, **kwargs):
    """Set the extra value mask for a given method."""
    enable_bipot_current = kwargs.get('enable_bipot_current', False)
    record_auxiliary_input = kwargs.get('record_auxiliary_input', False)
    record_cell_potential = kwargs.get('record_cell_potential', False)
    record_we_potential = kwargs.get('record_we_potential', False)
    record_forward_and_reverse_currents = kwargs.get(
        'record_forward_and_reverse_currents', False
    )
    record_we_current = kwargs.get('record_we_current', False)
    record_we_current_range = kwargs.get('record_we_current_range', get_current_range(4))

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


def set_ir_drop_compensation(method, use__ir_compensation, ir_compensation):
    """Set the iR drop compensation settings for a given method."""
    method.UseIRDropComp = use__ir_compensation
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


def set_multiplexer_settings(method, set_mux_mode, set_mux_channels, set_mux8r2_settings):
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


def get_mux8r2_settings(**kwargs):
    """Create a mux8r2 multiplexer settings settings object.

    :Keyword Arguments:
        * connect_sense_to_working_electrode
            -- Connect the sense electrode to the working electrode. Default is False.
        * combine_reference_and_counter_electrodes
            -- Combine the reference and counter electrodes. Default is False.
        * use_channel_1_reference_and_counter_electrodes
            -- Use channel 1 reference and counter electrodes for all working electrodes. Default is False.
        * set_unselected_channel_working_electrode
            -- Set the unselected channel working electrode to disconnected/floating (0), ground (1), or standby potential (2). Default is 0.
    """
    connect_sense_to_working_electrode = kwargs.get('connect_sense_to_working_electrode', False)
    combine_reference_and_counter_electrodes = kwargs.get(
        'combine_reference_and_counter_electrodes', False
    )
    use_channel_1_reference_and_counter_electrodes = kwargs.get(
        'use_channel_1_reference_and_counter_electrodes', False
    )
    set_unselected_channel_working_electrode = kwargs.get(
        'set_unselected_channel_working_electrode', 0
    )  # 0 = Disconnected / floating, 1 = Ground, 2 = Standby potential

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


def get_method_estimated_duration(method, **kwargs):
    """Get the estimated duration of a given method.

    :Keyword Arguments:
    """
    instrument_manager = kwargs.get(
        'instrument_manager', None
    )  # Specifies the instrument manager to get the connected instruments capabilities from, if not specified it will use the PalmSens4 capabilities to determine the estimated duration.

    if instrument_manager is None or instrument_manager.__comm is None:
        instrument_capabilities = PalmSens4Capabilities()
    else:
        instrument_capabilities = instrument_manager.__comm.Capabilities
    return method.GetMinimumEstimatedMeasurementDuration(instrument_capabilities)
