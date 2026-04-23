from __future__ import annotations

import PalmSens


def set_extra_value_mask(
    obj: PalmSens.Method,
    *,
    enable_bipot_current: bool = False,
    record_auxiliary_input: bool = False,
    record_cell_potential: bool = False,
    record_dc_current: bool = False,
    record_we_potential: bool = False,
    record_forward_and_reverse_currents: bool = False,
    record_we_current: bool = False,
):
    """Set the extra value mask for a given method."""
    extra_values = 0

    for flag, enum in (
        (enable_bipot_current, PalmSens.ExtraValueMask.BipotWE),
        (record_auxiliary_input, PalmSens.ExtraValueMask.AuxInput),
        (record_cell_potential, PalmSens.ExtraValueMask.CEPotential),
        (record_dc_current, PalmSens.ExtraValueMask.DCcurrent),
        (record_we_potential, PalmSens.ExtraValueMask.PotentialExtraRE),
        (record_forward_and_reverse_currents, PalmSens.ExtraValueMask.IForwardReverse),
        (record_we_current, PalmSens.ExtraValueMask.CurrentExtraWE),
    ):
        if flag:
            extra_values = extra_values | int(enum)

    obj.ExtraValueMsk = PalmSens.ExtraValueMask(extra_values)


def get_extra_value_mask(obj: PalmSens.Method) -> dict[str, bool]:
    mask = obj.ExtraValueMsk

    ret = {
        'enable_bipot_current': mask.HasFlag(PalmSens.ExtraValueMask.BipotWE),
        'record_auxiliary_input': mask.HasFlag(PalmSens.ExtraValueMask.AuxInput),
        'record_cell_potential': mask.HasFlag(PalmSens.ExtraValueMask.CEPotential),
        'record_dc_current': mask.HasFlag(PalmSens.ExtraValueMask.DCcurrent),
        'record_we_potential': mask.HasFlag(PalmSens.ExtraValueMask.PotentialExtraRE),
        'record_forward_and_reverse_currents': mask.HasFlag(
            PalmSens.ExtraValueMask.IForwardReverse
        ),
        'record_we_current': mask.HasFlag(PalmSens.ExtraValueMask.CurrentExtraWE),
    }

    return ret
