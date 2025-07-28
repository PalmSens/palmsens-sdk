from dataclasses import dataclass
from typing import Any, Sequence

import numpy as np
from PalmSens import (
    CurrentRange,
    CurrentRanges,
    ExtraValueMask,
    Method,
    PotentialRange,
    PotentialRanges,
    Techniques,
)
from PalmSens.Devices import PalmSens4Capabilities


def single_to_double(val: float) -> float:
    """Cast single precision to double precision.

    Pythonnet returns System.Single, whereas python defaults to double precision.
    This leads to incorrect rounding, which makes comparing values difficult."""
    return float(str(np.float32(val)))


def convert_bools_to_int(lst: Sequence[bool]) -> int:
    """Convert e.g. [True, False, True, False] to 5."""
    return int(''.join('01'[set_high] for set_high in reversed(lst)), base=2)


def convert_int_to_bools(val) -> tuple[bool, bool, bool, bool]:
    """Convert e.g. 5 to [True, False, True, False]."""
    lst = tuple([bool(int(_)) for _ in reversed(f'{val:04b}')])
    assert len(lst) == 4  # specify length to make mypy happy
    return lst


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
):
    """Set the extra value mask for a given method."""
    extra_values = 0

    for flag, enum in (
        (enable_bipot_current, ExtraValueMask.BipotWE),
        (record_auxiliary_input, ExtraValueMask.AuxInput),
        (record_cell_potential, ExtraValueMask.CEPotential),
        (record_we_potential, ExtraValueMask.PotentialExtraRE),
        (record_forward_and_reverse_currents, ExtraValueMask.IForwardReverse),
        (record_we_current, ExtraValueMask.CurrentExtraWE),
    ):
        if flag:
            extra_values = extra_values | int(enum)

    obj.ExtraValueMsk = ExtraValueMask(extra_values)


def get_extra_value_mask(obj) -> dict[str, Any]:
    mask = obj.ExtraValueMsk

    ret = {
        'enable_bipot_current': mask.HasFlag(ExtraValueMask.BipotWE),
        'record_auxiliary_input': mask.HasFlag(ExtraValueMask.AuxInput),
        'record_cell_potential': mask.HasFlag(ExtraValueMask.CEPotential),
        'record_we_potential': mask.HasFlag(ExtraValueMask.PotentialExtraRE),
        'record_forward_and_reverse_currents': mask.HasFlag(ExtraValueMask.IForwardReverse),
        'record_we_current': mask.HasFlag(ExtraValueMask.CurrentExtraWE),
    }

    return ret


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


@dataclass
class ELevel:
    """Create a multi-step amperometry level method object.

    Attributes
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

    level: float = 0.0
    duration: float = 1.0
    record: bool = True
    use_limit_current_max: bool = False
    limit_current_max: float = 0.0
    use_limit_current_min: bool = False
    limit_current_min: float = 0.0
    trigger_at_level: bool = False
    trigger_at_level_lines: tuple[bool, bool, bool, bool] = (False, False, False, False)

    def to_psobj(self):
        obj = Techniques.ELevel()

        obj.Level = self.level
        obj.Duration = self.duration
        obj.Record = self.record

        obj.UseMaxLimit = self.use_limit_current_max
        obj.MaxLimit = self.limit_current_max
        obj.UseMinLimit = self.use_limit_current_min
        obj.MinLimit = self.limit_current_min

        obj.UseTriggerOnStart = self.trigger_at_level
        obj.TriggerValueOnStart = convert_bools_to_int(self.trigger_at_level_lines)

        return obj

    @classmethod
    def from_psobj(cls, psobj: Techniques.ELevel):
        """Construct ELevel dataclass from PalmSens.Techniques.ELevel object."""
        return cls(
            level=single_to_double(psobj.Level),
            duration=single_to_double(psobj.Duration),
            record=psobj.Record,
            use_limit_current_max=psobj.UseMaxLimit,
            limit_current_max=single_to_double(psobj.MaxLimit),
            use_limit_current_min=psobj.UseMinLimit,
            limit_current_min=single_to_double(psobj.MinLimit),
            trigger_at_level=psobj.UseTriggerOnStart,
            trigger_at_level_lines=convert_int_to_bools(psobj.TriggerValueOnStart),
        )
