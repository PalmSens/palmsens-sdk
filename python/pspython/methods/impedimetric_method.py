from PalmSens.Techniques import ImpedimetricMethod as PSImpedimetricMethod
from PalmSens.Techniques.Impedance import enumFrequencyType, enumScanType

from ._shared import (
    get_current_range,
    get_potential_range,
    set_autoranging_current,
    set_autoranging_potential,
    set_multiplexer_settings,
    set_post_measurement_settings,
    set_pretreatment,
    set_trigger_at_equilibration_settings,
    set_trigger_at_measurement_settings,
    set_versus_ocp,
)
from .time_method import TimeMethod


class ImpedimetricMethod(TimeMethod): ...


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
    electrochemical_impedance_spectroscopy = PSImpedimetricMethod()

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
