from dataclasses import dataclass, field
from typing import Any, Optional

import PalmSens
from PalmSens import Method as PSMethod
from PalmSens import MuxMethod as PSMuxMethod

from ._shared import (
    get_current_range,
)


def method_ids() -> list[str]:
    """Return list of all possible method ids."""
    return list(PSMethod.MethodIds)


def method_ids_by_technique_id() -> dict[int, list[str]]:
    """Unique id for method."""

    return {k: list(v) for k, v in dict(PSMethod.MethodIdsByTechniqueId).items()}


class BaseParameters:
    def update_dotnet_method(self, *, dotnet_method: PSMethod): ...

    def to_dotnet_method(self) -> Any: ...

    @classmethod
    def from_dotnet_method(cls, dotnet_method: PSMethod) -> Any: ...


@dataclass
class MethodParameters(BaseParameters):
    """Create a general method parameters.

    Attributes
    ----------
    current_range_max: int
        Maximum current range (default: 10 mA).
        Use `get_current_range()` to get the range.
    current_range_min: int
        Minimum current range (default: 1 µA).
        Use `get_current_range()` to get the range.
    current_range_start: int
         Start current range (default: 100 µA).
         Use `get_current_range()` to get the range.

    deposition_potential: float
        Deposition potential in V (default: 0.0)
    deposition_time: float
        Deposition time in s (default: 0.0)
    conditioning_potential: float
        Conditioning potential in V (default: 0.0)
    conditioning_time: float
        Conditioning time in s (default: 0.0)

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

    # post measurement settings
    cell_on_after_measurement: bool = False
    cell_on_after_measurement_potential: float = 0.0  # V

    # set trigger settings
    trigger_at_measurement: bool = False
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

    def update_dotnet_method(self, *, dotnet_method):
        obj = dotnet_method

        # Set the autoranging current for a given method
        obj.Ranging.MaximumCurrentRange = self.current_range_max
        obj.Ranging.MinimumCurrentRange = self.current_range_min
        obj.Ranging.StartCurrentRange = self.current_range_start

        # Set the pretreatment settings for a given method
        obj.DepositionPotential = self.deposition_potential
        obj.DepositionTime = self.deposition_time
        obj.ConditioningPotential = self.conditioning_potential
        obj.ConditioningTime = self.conditioning_time

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

    def to_dotnet_method(self):
        """Convert parameters to dotnet method."""
        raise NotImplementedError


class Method:
    def __init__(self, *, dotnet_method):
        self.dotnet_method = dotnet_method

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(name={self.name!r}, id={self.id!r})'

    def to_parameters(self) -> BaseParameters:
        """Return method parameters."""
        raise NotImplementedError

    @classmethod
    def from_parameters(cls, *, parameters: BaseParameters) -> 'Method':
        """Create instance of Method from parameters"""
        obj = parameters.to_dotnet_method()
        return cls(dotnet_method=obj)

    @property
    def id(self) -> str:
        """Unique id for method."""
        return self.dotnet_method.MethodID

    @property
    def name(self) -> str:
        """Name for the technique."""
        return self.dotnet_method.Name

    @property
    def short_name(self) -> str:
        """Short name for the technique."""
        return self.dotnet_method.ShortName

    @property
    def technique(self) -> int:
        """
        The technique number used in the firmware
        """
        return self.dotnet_method.Technique

    @property
    def notes(self) -> str:
        """
        Some user notes for use with this method
        """
        return self.dotnet_method.Notes

    @property
    def standby_potential(self) -> float:
        """
        Standby Potential (for use with cell on after
        measurement)
        """
        return self.dotnet_method.StandbyPotential

    @property
    def standby_time(self) -> float:
        """
        Standby time (for use with cell on after measurement)
        """
        return self.dotnet_method.StandbyTime

    @property
    def cell_on_after_measurement(self) -> bool:
        """
        Enable/disable cell after measurement
        """
        return self.dotnet_method.CellOnAfterMeasurement

    @property
    def min_peak_height(self) -> float:
        """
        Determines the minimum peak height in ┬ÁA. Peaks lower than this value are neglected.
        """
        return self.dotnet_method.MinPeakHeight

    @property
    def min_peak_width(self) -> float:
        """
        The minimum peak width, in the unit of the curves X axis. Peaks narrower than this value are neglected.
        """
        return self.dotnet_method.MinPeakWidth

    @property
    def smooth_level(self) -> int:
        """
        The smoothlevel to be used. `-1` = none, 0 = no smooth (spike rejection only), `1` = 5 points, `2` = 9 points, `3` = 15 points, `4` = 25 points
        """
        return self.dotnet_method.SmoothLevel

    @property
    def ranging(self) -> PalmSens.Method.Ranging:
        """
        Ranging information, settings defining the minimum/maximum/starting current range
        """
        return self.dotnet_method.Ranging

    @property
    def power_freq(self) -> int:
        """
        Adjusts sampling on instrument to account for mains frequency. It accepts two values: 50 for 50Hz 60 for 60Hz
        """
        return self.dotnet_method.PowerFreq

    def to_dict(self) -> dict[str, Any]:
        """Return dictionary with method properties."""
        obj = self.dotnet_method
        return {
            'analyte_name': list(obj.AnalyteName),
            'analyte_peak_autodetect': list(obj.AnalytePeakAutodetect),
            'area': obj.Area,
            'ba': obj.Ba,
            'bandwidth': obj.Bandwidth,
            'bc': obj.Bc,
            'begin_potential': obj.BeginPotential,
            'bipot_cr': str(obj.BiPotCR),
            'bipot_potential': obj.BiPotPotential,
            'bipot_mode_ps': str(obj.BipotModePS),
            'bipot_ranging': obj.BipotRanging,  # object
            'blank_type': str(obj.BlankType),
            'cell_on_after_measurement': obj.CellOnAfterMeasurement,
            'cell_volume': obj.CellVolume,
            'concentration_unit': obj.ConcentrationUnit,
            'conditioning_potential': obj.ConditioningPotential,
            'conditioning_time': obj.ConditioningTime,
            'default_bandwidth': obj.DefaultBandwidth,
            'default_x_array_type_bipot_potential': str(obj.DefaultXArrayTypeBipotPotential),
            'default_x_axis': str(obj.DefaultXAxis),
            'default_x_unit': str(obj.DefaultXUnit),
            'default_y_axis': str(obj.DefaultYAxis),
            'default_y_unit': str(obj.DefaultYUnit),
            'density': obj.Density,
            'deposition_potential': obj.DepositionPotential,
            'deposition_time': obj.DepositionTime,
            'determination': str(obj.Determination),
            'e_peak_left': list(obj.EPeakLeft),
            'e_peak_right': list(obj.EPeakRight),
            'e_peaks': list(obj.EPeaks),
            'e_pretreat': list(obj.EPretreat),
            'end_potential': obj.EndPotential,
            'equilibration_time': obj.EquilibrationTime,
            'extra_value_msk': str(obj.ExtraValueMsk),
            'ir_drop_comp_res': obj.IRDropCompRes,
            'is_main_we': obj.IsMainWE,
            'is_versus_ocp': obj.IsVersusOCP,
            'limit_max_value': obj.LimitMaxValue,
            'limit_min_value': obj.LimitMinValue,
            'max_mux_channel_selected': obj.MaxMuxChannelSelected,
            'method_filename': obj.MethodFilename,
            'method_id': obj.MethodID,
            'method_is_galvanostatic': obj.MethodIsGalvanostatic,
            'min_peak_height': obj.MinPeakHeight,
            'min_peak_width': obj.MinPeakWidth,
            'multiplex_cycles': obj.MultiplexCycles,
            'mux_method': str(obj.MuxMethod),
            'mux_no_time_reset_for_next_channel': obj.MuxNoTimeResetForNextChannel,
            'mux_settings': str(obj.MuxSett),  # object
            'name': obj.Name,
            'note': obj.Notes,
            'ocp_max_ocp_time': obj.OCPMaxOCPTime,
            'ocp_stability_criterion': obj.OCPStabilityCriterion,
            'ocp_mode': obj.OCPmode,
            'override_bandwidth': obj.OverrideBandwidth,
            'override_pg_stat_mode': obj.OverridePGStatMode,
            'override_potential_range': obj.OverridePotentialRange,
            'override_potential_range_max': obj.OverridePotentialRangeMax,
            'override_potential_range_min': obj.OverridePotentialRangeMin,
            'override': obj.Overrides,
            'pg_stat_mode': str(obj.PGStatMode),
            'peak_overlap': obj.PeakOverlap,
            'peak_value': str(obj.PeakValue),
            'peak_window': obj.PeakWindow,
            'poly_em_stat': obj.PolyEmStat,  # object
            'poly_stat_mode': str(obj.PolyStatMode),
            'power_freq': obj.PowerFreq,
            'power_line_period': obj.PowerLinePeriod,
            'pret_limit_max_value': obj.PretLimitMaxValue,
            'pret_limit_min_value': obj.PretLimitMinValue,
            'pretreatment_duration': obj.PretreatmentDuration,
            'ranging': obj.Ranging,  # object
            'ranging_potential': obj.RangingPotential,  # object
            'ranging_type': str(obj.RangingType),
            'record_ce': obj.RecordCE,
            'reference_electrode_name': obj.ReferenceElectrodeName,
            'reference_electrode_offset': obj.ReferenceElectrodeOffset,
            'se_2_extra_value_channel_names': {
                row.Key: row.Value for row in obj.SE2ExtraValueChannelNames
            },
            'se_2_versus_x_channel_names': {
                row.Key: row.Value for row in obj.SE2VersusXChannelNames
            },
            'se_2_vs_x_channel': str(obj.SE2vsXChannel),
            'sample_volume': obj.SampleVolume,
            'scanrate': obj.Scanrate,
            'selected_potentiostat_channel': str(obj.SelectedPotentiostatChannel),
            'short_name': obj.ShortName,
            'smooth_level': obj.SmoothLevel,
            'solution_nr': list(obj.SolutionNr),
            'standard_concentration': list(obj.StandardConcentration),
            'standards_values': str(obj.StandardsValues),
            'standby_potential': obj.StandbyPotential,
            'standby_time': obj.StandbyTime,
            'step_potential': obj.StepPotential,
            'supports_corrosion': obj.SupportsCorrosion,
            'supports_determination': obj.SupportsDetermination,
            'supports_hold_during_measurement': obj.SupportsHoldDuringMeasurement,
            'supports_ir_drop_comp': obj.SupportsIRDropComp,
            'technique_number': obj.TechniqueNumber,
            'trigger_delay_period': obj.TriggerDelayPeriod,
            'trigger_value_on_delay': obj.TriggerValueOnDelay,
            'trigger_value_on_equil': obj.TriggerValueOnEquil,
            'trigger_value_on_start': obj.TriggerValueOnStart,
            # 'use_alternative_signal_train': obj.UseAlternativeSignalTrain,  # not availabe for CV
            'use_hw_sync': obj.UseHWSync,
            'use_ir_drop_comp': obj.UseIRDropComp,
            'use_limit_max_value': obj.UseLimitMaxValue,
            'use_limit_min_value': obj.UseLimitMinValue,
            'use_mux_channel': list(obj.UseMuxChannel),
            'use_pret_limit_max_value': obj.UsePretLimitMaxValue,
            'use_pret_limit_min_value': obj.UsePretLimitMinValue,
            'use_stirrer': obj.UseStirrer,
            'use_trigger_on_delay': obj.UseTriggerOnDelay,
            'use_trigger_on_equil': obj.UseTriggerOnEquil,
            'use_trigger_on_start': obj.UseTriggerOnStart,
            'versus_ocp_begin_potential': obj.VersusOCPBeginPotential,
            'versus_ocp_end_potential': obj.VersusOCPEndPotential,
            'versus_ocp_vtx_1_potential': obj.VersusOCPVtx1Potential,
            'versus_ocp_vtx_2_potential': obj.VersusOCPVtx2Potential,
            'view_bottom': obj.ViewBottom,
            'view_left': obj.ViewLeft,
            'view_right': obj.ViewRight,
            'view_top': obj.ViewTop,
            'volume_concentration': list(obj.VolumeConcentration),
            'vs_prev_ei': obj.VsPrevEI,
            'vtx_1_potential': obj.Vtx1Potential,
            'vtx_2_potential': obj.Vtx2Potential,
            'weight': obj.Weight,
            'x_direction': str(obj.XDirection),
            'x_left': obj.XLeft,
            'x_right': obj.XRight,
            'y_bottom': obj.YBottom,
            'y_direction': str(obj.YDirection),
            'y_top': obj.YTop,
            'n_avg_scans': obj.nAvgScans,
            'n_eq_scans': obj.nEqScans,
            'n_oc_pparameters': obj.nOCPparameters,
            'n_points': obj.nPoints,
            'n_scans': obj.nScans,
            't_pretreat': list(obj.tPretreat),
        }
