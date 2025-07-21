from dataclasses import dataclass, field
from typing import Optional

import PalmSens
from PalmSens import Method as PSMethod
from PalmSens import MuxMethod as PSMuxMethod
from PalmSens.Techniques import CyclicVoltammetry as PSCyclicVoltammetry

from ._shared import (
    convert_bool_list_to_base2,
    get_current_range,
    set_extra_value_mask,
)
from .method import BaseParameters


@dataclass
class CyclicVoltammetryParameters(BaseParameters):
    """Create a cyclic voltammetry method parameters.

    Attributes
    ----------
    current_range_max: int
        Maximum current range (default: 10 mA) [use get_current_range() to get the range]
    current_range_min: int
        Minimum current range (default: 1 µA) [use get_current_range() to get the range]
    current_range_start: int
         Start current range (default: 100 µA) [use get_current_range() to get the range]
    deposition_potential: float
        Deposition potential in V (default: 0.0)
    deposition_time: float
        Deposition time in s (default: 0.0)
    conditioning_potential: float
        Conditioning potential in V (default: 0.0)
    conditioning_time: float
        Conditioning time in s (default: 0.0)
    equilibration_time: float
        Equilibration time in s (default: 0.0)

    begin_potential: float
        Begin potential in V (default: -0.5)
    vertex1_potential: float
        Vertex 1 potential in V (default: 0.5)
    vertex2_potential: float
        Vertex 2 potential in V (default: -0.5)
    step_potential: float
        Step potential in V (default: 0.1)
    scanrate: float
        Scan rate in V/s (default: 1.0)
    n_scans: float
        Number of scans (default: 1)

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
    enable_bipot_current: bool
        Enable bipotential current (default: False)
    bipot_mode: int
        Set the bipotential mode, 0 = constant, 1 = offset (default: 0)
    bipot_potential: float
        Set the bipotential in V (default: 0.0)
    bipot_current_range_max: int
        Maximum bipotential current range (default: 10 mA) [use get_current_range() to get the range]
    bipot_current_range_min: int
        Minimum bipotential current range (default: 1 µA) [use get_current_range() to get the range]
    bipot_current_range_start: int
        Start bipotential current range (default: 100 µA) [use get_current_range() to get the range]

    record_auxiliary_input: bool
        Record auxiliary input (default: False)
    record_cell_potential: bool
        Record cell potential (default: False) [counter electrode vs ground]
    record_we_potential: bool
        Record applied working electrode potential (default: False) [reference electrode vs ground]

    cell_on_after_measurement: bool
        Cell on after measurement (default: False)
    cell_on_after_measurement_potential: float
        Cell on after measurement potential in V (default: 0.0)

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

    use_ir_compensation: bool
        Enable iR compensation
    ir_compensation: float
        Set the iR compensation in Ω (default: 0.0)

    trigger_at_equilibration: bool
        Enable trigger at equilibration (default: False)
    trigger_at_equilibration_lines: tuple[bool, bool, bool, bool]
        Enable trigger at equilibration lines (default: [False, False, False, False])
        Line order: d0 high, d1 high, d2 high, d3 high
    trigger_at_measurement: bool
        Enable trigger at measurement (default: False)
    trigger_at_measurement_lines: tuple[bool, bool, bool, bool]
        Enable trigger at measurement lines (default: [False, False, False, False])
        Line order: d0 high, d1 high, d2 high, d3 high

    dc_mains_filter: int
        Set the DC mains filter in Hz. Set to 50 Hz or 60 Hz depending on your region (default: 50).
    default_curve_post_processing_filter: int = 0
        Set the default curve post processing filter (default: 0)
           -1 = no filter
            0 = spike rejection
            1 = spike rejection + Savitsky-golay window 5
            2 = spike rejection + Savitsky-golay window 9
            3 = spike rejection + Savitsky-golay window 15
            4 = spike rejection + Savitsky-golay window 25

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
    set_mux8r2_settings: Optional[PalmSens.Method.MuxSettings]
        Initialize the settings for the MUX8R2 multiplexer (default: None).
        use get_mux8r2_settings() to create the settings.

    save_on_internal_storage: bool
        Save on internal storage (default: False)

    use_hardware_sync: bool
        Use hardware synchronization with other channels/instruments (default: False)
    """

    # autoranging
    current_range_max: int = get_current_range(8)
    current_range_min: int = get_current_range(4)
    current_range_start: int = get_current_range(6)

    # pretreatment
    deposition_potential: float = 0.0
    deposition_time: float = 0.0
    conditioning_potential: float = 0.0
    conditioning_time: float = 0.0
    equilibration_time: float = 0.0  # Time (s)

    # cyclic voltammetry settings
    begin_potential: float = -0.5  # potential (V)
    vertex1_potential: float = 0.5  # potential (V)
    vertex2_potential: float = -0.5  # potential (V)
    step_potential: float = 0.1  # potential (V)
    scanrate: float = 1.0  # potential/time (V/s)
    n_scans: float = 1  # number of cycles

    # advanced settings
    versus_ocp_mode: int = 0
    versus_ocp_max_ocp_time: float = 20.0  # Time (s)
    versus_ocp_stability_criterion: int = 0

    # bipot settings
    enable_bipot_current: bool = False
    bipot_mode: int = 0
    bipot_potential: float = 0.0  # V
    bipot_current_range_max: int = get_current_range(8)
    bipot_current_range_min: int = get_current_range(4)
    bipot_current_range_start: int = get_current_range(6)

    # record extra value settings
    record_auxiliary_input: bool = False
    record_cell_potential: bool = False
    record_we_potential: bool = False

    # post measurement settings
    cell_on_after_measurement: bool = False
    cell_on_after_measurement_potential: float = 0.0  # V

    # limit settings
    use_limit_current_max: bool = False
    limit_current_max: float = 0.0  # µA
    use_limit_current_min: bool = False
    limit_current_min: float = 0.0  # µA

    # iR compensation settings
    use_ir_compensation: bool = False
    ir_compensation: float = 0.0  # Ω

    # set trigger settings
    trigger_at_equilibration: bool = False
    # d0 high, d1 high, d2 high, d3 high
    trigger_at_equilibration_lines: tuple[bool, bool, bool, bool] = (False, False, False, False)
    trigger_at_measurement: bool = False
    # d0 high, d1 high, d2 high, d3 high
    trigger_at_measurement_lines: tuple[bool, bool, bool, bool] = (False, False, False, False)

    # set filter settings
    dc_mains_filter: int = 50  # Hz
    default_curve_post_processing_filter: int = 0

    # multiplexer settings
    set_mux_mode: int = -1
    set_mux_channels: list[bool] = field(
        default_factory=lambda: [False, False, False, False, False, False, False, False]
    )
    set_mux8r2_settings: Optional[PalmSens.Method.MuxSettings] = None

    # internal storage
    save_on_internal_storage: bool = False

    # use hardware synchronization with other channels/instruments
    use_hardware_sync: bool = False

    def to_dotnet_method(self):
        """Convert parameters to dotnet method."""
        obj = PSCyclicVoltammetry()

        # Set the autoranging current for a given method
        obj.Ranging.MaximumCurrentRange = self.current_range_max
        obj.Ranging.MinimumCurrentRange = self.current_range_min
        obj.Ranging.StartCurrentRange = self.current_range_start

        # Set the pretreatment settings for a given method
        obj.DepositionPotential = self.deposition_potential
        obj.DepositionTime = self.deposition_time
        obj.ConditioningPotential = self.conditioning_potential
        obj.ConditioningTime = self.conditioning_time

        obj.EquilibrationTime = self.equilibration_time

        # cyclic voltammetry settings
        obj.BeginPotential = self.begin_potential
        obj.Vtx1Potential = self.vertex1_potential
        obj.Vtx2Potential = self.vertex2_potential
        obj.StepPotential = self.step_potential
        obj.Scanrate = self.scanrate
        obj.nScans = self.n_scans

        # Set the versus OCP settings for a given method
        obj.OCPmode = self.versus_ocp_mode
        obj.OCPMaxOCPTime = self.versus_ocp_max_ocp_time
        obj.OCPStabilityCriterion = self.versus_ocp_stability_criterion

        # Set the bipot settings for a given method
        obj.BiPotModePS = PSMethod.EnumPalmSensBipotMode(self.bipot_mode)
        obj.BiPotPotential = self.bipot_potential

        # Set the autoranging bipot current for a given method
        obj.BipotRanging.MaximumCurrentRange = self.bipot_current_range_max
        obj.BipotRanging.MinimumCurrentRange = self.bipot_current_range_min
        obj.BipotRanging.StartCurrentRange = self.bipot_current_range_start

        set_extra_value_mask(
            obj,
            enable_bipot_current=self.enable_bipot_current,
            record_auxiliary_input=self.record_auxiliary_input,
            record_cell_potential=self.record_cell_potential,
            record_we_potential=self.record_we_potential,
        )

        # Set the post measurement settings for a given method
        obj.CellOnAfterMeasurement = self.cell_on_after_measurement
        obj.StandbyPotential = self.cell_on_after_measurement_potential

        # Set the limit settings for a given method
        obj.UseLimitMaxValue = self.use_limit_current_max
        obj.LimitMaxValue = self.limit_current_max
        obj.UseLimitMinValue = self.use_limit_current_min
        obj.LimitMinValue = self.limit_current_min

        # Set the iR drop compensation settings for a given method
        obj.UseIRDropComp = self.use_ir_compensation
        obj.IRDropCompRes = self.ir_compensation

        # Set the trigger at equilibration settings for a given method
        obj.UseTriggerOnEquil = self.trigger_at_equilibration
        obj.TriggerValueOnEquil = convert_bool_list_to_base2(
            self.trigger_at_equilibration_lines
        )

        # Set the trigger at measurement settings for a given method
        obj.UseTriggerOnStart = self.trigger_at_measurement
        obj.TriggerValueOnStart = convert_bool_list_to_base2(self.trigger_at_measurement_lines)

        # Set the filter settings for a given method
        obj.DCMainsFilter = self.dc_mains_filter
        obj.DefaultCurvePostProcessingFilter = self.default_curve_post_processing_filter

        # Create a mux8r2 multiplexer settings settings object
        obj.MuxMethod = PSMuxMethod(self.set_mux_mode)

        # disable all mux channels
        for i in range(len(obj.UseMuxChannel)):
            obj.UseMuxChannel[i] = False

        # set the selected mux channels
        for i, use_channel in enumerate(self.set_mux_channels):
            obj.UseMuxChannel[i] = use_channel

        if self.set_mux8r2_settings:
            obj.MuxSett.ConnSEWE = self.set_mux8r2_settings.ConnSEWE
            obj.MuxSett.ConnectCERE = self.set_mux8r2_settings.ConnectCERE
            obj.MuxSett.CommonCERE = self.set_mux8r2_settings.CommonCERE
            obj.MuxSett.UnselWE = self.set_mux8r2_settings.UnselWE

        # Other settings
        obj.SaveOnDevice = self.save_on_internal_storage
        obj.UseHWSync = self.use_hardware_sync

        return obj

    @classmethod
    def from_dotnet_method(cls, dotnet_method: PSMethod) -> 'CyclicVoltammetryParameters':
        """Generate parameters from dotnet method."""
        raise NotImplementedError


def cyclic_voltammetry(**kwargs):
    """Alias for CyclicVoltammetry for backwards compatibility"""
    cyclic_voltammetry = CyclicVoltammetryParameters(**kwargs)
    return cyclic_voltammetry.to_dotnet_method()
