from __future__ import annotations

from attrs import asdict
from PalmSens import Techniques

from pypalmsens.methods import settings
from pypalmsens.methods._shared import (
    CURRENT_RANGE,
    POTENTIAL_RANGE,
    get_extra_value_mask,
    set_extra_value_mask,
)


def test_set_extra_value_mask():
    obj = Techniques.CyclicVoltammetry()
    assert obj.ExtraValueMsk.value__ == 0

    set_extra_value_mask(
        obj=obj,
        record_auxiliary_input=True,
        record_cell_potential=True,
        record_we_potential=True,
    )
    assert obj.ExtraValueMsk.value__ == 274

    dct = get_extra_value_mask(obj)

    assert dct['record_auxiliary_input']
    assert dct['record_cell_potential']
    assert dct['record_we_potential']
    assert not dct['enable_bipot_current']
    assert not dct['record_forward_and_reverse_currents']
    assert not dct['record_we_current']

    set_extra_value_mask(
        obj=obj,
        enable_bipot_current=True,
        record_forward_and_reverse_currents=True,
        record_we_current=True,
    )
    assert obj.ExtraValueMsk.value__ == 101

    dct = get_extra_value_mask(obj)

    assert dct['enable_bipot_current']
    assert dct['record_forward_and_reverse_currents']
    assert dct['record_we_current']
    assert not dct['record_auxiliary_input']
    assert not dct['record_cell_potential']
    assert not dct['record_we_potential']


def test_AutorangingCurrentSettings():
    kwargs = {
        'max': CURRENT_RANGE.cr_100_uA,
        'min': CURRENT_RANGE.cr_100_nA,
        'start': CURRENT_RANGE.cr_10_uA,
    }

    obj = Techniques.CyclicVoltammetry()

    params = settings.CurrentRanges(**kwargs)
    params._update_psmethod(obj=obj)

    assert obj.Ranging.MaximumCurrentRange.Description == '100 uA'
    assert obj.Ranging.MinimumCurrentRange.Description == '100 nA'
    assert obj.Ranging.StartCurrentRange.Description == '10 uA'

    new_params = settings.CurrentRanges()
    new_params._update_params(obj=obj)

    assert asdict(new_params) == kwargs


def test_AutorangingPotentialSettings():
    kwargs = {
        'max': POTENTIAL_RANGE.pr_100_mV,
        'min': POTENTIAL_RANGE.pr_1_mV,
        'start': POTENTIAL_RANGE.pr_10_mV,
    }

    obj = Techniques.Potentiometry()

    params = settings.PotentialRanges(**kwargs)
    params._update_psmethod(obj=obj)

    assert obj.RangingPotential.MaximumPotentialRange.Description == '100 mV'
    assert obj.RangingPotential.MinimumPotentialRange.Description == '1 mV'
    assert obj.RangingPotential.StartPotentialRange.Description == '10 mV'

    new_params = settings.PotentialRanges()
    new_params._update_params(obj=obj)

    assert asdict(new_params) == kwargs


def test_PretreatmentSettings():
    obj = Techniques.CyclicVoltammetry()

    kwargs = {
        'deposition_potential': 12,
        'deposition_time': 34,
        'conditioning_potential': 56,
        'conditioning_time': 78,
    }

    params = settings.Pretreatment(**kwargs)
    params._update_psmethod(obj=obj)

    assert obj.DepositionPotential == 12
    assert obj.DepositionTime == 34
    assert obj.ConditioningPotential == 56
    assert obj.ConditioningTime == 78

    new_params = settings.Pretreatment()
    new_params._update_params(obj=obj)

    assert asdict(new_params) == kwargs


def test_VersusOcpSettings():
    obj = Techniques.CyclicVoltammetry()

    kwargs = {
        'mode': 7,
        'max_ocp_time': 200.0,
        'stability_criterion': 123,
    }

    params = settings.VersusOCP(**kwargs)
    params._update_psmethod(obj=obj)

    assert obj.OCPmode == 7
    assert obj.OCPMaxOCPTime == 200
    assert obj.OCPStabilityCriterion == 123

    new_params = settings.VersusOCP()
    new_params._update_params(obj=obj)

    assert asdict(new_params) == kwargs


def test_BipotSettings():
    obj = Techniques.CyclicVoltammetry()

    kwargs = {
        'mode': 'offset',
        'potential': 10.0,
        'current_range_max': CURRENT_RANGE.cr_100_uA,
        'current_range_min': CURRENT_RANGE.cr_10_nA,
        'current_range_start': CURRENT_RANGE.cr_10_uA,
    }

    params = settings.BiPot(**kwargs)
    params._update_psmethod(obj=obj)

    assert obj.BipotModePS == Techniques.CyclicVoltammetry.EnumPalmSensBipotMode(1)
    assert obj.BiPotPotential == 10.0
    assert obj.BipotRanging.MaximumCurrentRange.Description == '100 uA'
    assert obj.BipotRanging.MinimumCurrentRange.Description == '10 nA'
    assert obj.BipotRanging.StartCurrentRange.Description == '10 uA'

    new_params = settings.BiPot()
    new_params._update_params(obj=obj)

    assert asdict(new_params) == kwargs


def test_PostMeasurementSettings():
    obj = Techniques.CyclicVoltammetry()

    kwargs = {
        'cell_on_after_measurement': True,
        'standby_potential': 123,
        'standby_time': 678,
    }

    params = settings.PostMeasurement(**kwargs)
    params._update_psmethod(obj=obj)

    assert obj.CellOnAfterMeasurement is True
    assert obj.StandbyPotential == 123
    assert obj.StandbyTime == 678

    new_params = settings.PostMeasurement()
    new_params._update_params(obj=obj)

    assert asdict(new_params) == kwargs


def test_CurrentLimitSettings():
    obj = Techniques.CyclicVoltammetry()

    kwargs = {
        'use_limit_max': True,
        'limit_max': 123.0,
        'use_limit_min': True,
        'limit_min': 678.0,
    }

    params = settings.CurrentLimits(**kwargs)
    params._update_psmethod(obj=obj)

    assert obj.UseLimitMaxValue is True
    assert obj.LimitMaxValue == 123.0
    assert obj.UseLimitMinValue is True
    assert obj.LimitMinValue == 678.0

    new_params = settings.CurrentLimits()
    new_params._update_params(obj=obj)

    assert asdict(new_params) == kwargs


def test_PotentialLimitSettings():
    obj = Techniques.CyclicVoltammetry()

    kwargs = {
        'use_limit_max': True,
        'limit_max': 123.0,
        'use_limit_min': True,
        'limit_min': 678.0,
    }

    params = settings.PotentialLimits(**kwargs)
    params._update_psmethod(obj=obj)

    assert obj.UseLimitMaxValue is True
    assert obj.LimitMaxValue == 123.0
    assert obj.UseLimitMinValue is True
    assert obj.LimitMinValue == 678.0

    new_params = settings.PotentialLimits()
    new_params._update_params(obj=obj)

    assert asdict(new_params) == kwargs


def test_ChargeLimitSettings():
    obj = Techniques.CyclicVoltammetry()

    kwargs = {
        'use_limit_max': True,
        'limit_max': 123.0,
        'use_limit_min': True,
        'limit_min': 678.0,
    }

    params = settings.ChargeLimits(**kwargs)
    params._update_psmethod(obj=obj)

    assert obj.UseChargeLimitMax is True
    assert obj.ChargeLimitMax == 123.0
    assert obj.UseChargeLimitMin is True
    assert obj.ChargeLimitMin == 678.0

    new_params = settings.ChargeLimits()
    new_params._update_params(obj=obj)

    assert asdict(new_params) == kwargs


def test_IrDropCompensationSettings():
    obj = Techniques.CyclicVoltammetry()

    kwargs = {
        'enable': True,
        'ir_compensation': 123.0,
    }

    params = settings.IrDropCompensation(**kwargs)
    params._update_psmethod(obj=obj)

    assert obj.UseIRDropComp is True
    assert obj.IRDropCompRes == 123

    new_params = settings.IrDropCompensation()
    new_params._update_params(obj=obj)

    assert asdict(new_params) == kwargs


def test_TriggerAtEquilibrationSettings():
    obj = Techniques.CyclicVoltammetry()

    kwargs = {
        'enable': True,
        'd0': True,
        'd1': False,
        'd2': True,
        'd3': True,
    }

    params = settings.EquilibrationTriggers(**kwargs)
    params._update_psmethod(obj=obj)

    assert obj.UseTriggerOnEquil is True
    assert obj.TriggerValueOnEquil == 13

    new_params = settings.EquilibrationTriggers()
    new_params._update_params(obj=obj)

    assert asdict(new_params) == kwargs


def test_TriggerAtMeasurementSettings():
    obj = Techniques.CyclicVoltammetry()

    kwargs = {
        'enable': True,
        'd0': True,
        'd1': True,
        'd2': False,
        'd3': True,
    }

    params = settings.MeasurementTriggers(**kwargs)
    params._update_psmethod(obj=obj)

    assert obj.UseTriggerOnStart is True
    assert obj.TriggerValueOnStart == 11

    new_params = settings.MeasurementTriggers()
    new_params._update_params(obj=obj)

    assert asdict(new_params) == kwargs


def test_MultiplexerSettings():
    obj = Techniques.CyclicVoltammetry()

    kwargs = {
        'mode': 'consecutive',
        'channels': [1, 3, 5],
        'connect_sense_to_working_electrode': True,
        'combine_reference_and_counter_electrodes': True,
        'use_channel_1_reference_and_counter_electrodes': True,
        'set_unselected_channel_working_electrode': 1,
    }

    params = settings.Multiplexer(**kwargs)
    params._update_psmethod(obj=obj)

    assert int(obj.MuxMethod) == 0
    for i, v in enumerate([True, False, True, False, True]):
        assert obj.UseMuxChannel[i] is v

    assert obj.MuxSett.ConnSEWE is True
    assert obj.MuxSett.ConnectCERE is True
    assert obj.MuxSett.CommonCERE is True
    assert int(obj.MuxSett.UnselWE) == 1

    new_params = settings.Multiplexer()
    new_params._update_params(obj=obj)

    assert asdict(new_params) == kwargs


def test_PeakSettings():
    obj = Techniques.CyclicVoltammetry()

    kwargs = {
        'smooth_level': 1,
        'min_width': 13,
        'min_height': 37,
    }

    params = settings.DataProcessing(**kwargs)
    params._update_psmethod(obj=obj)

    assert obj.SmoothLevel == 1
    assert obj.MinPeakWidth == 13
    assert obj.MinPeakHeight == 37

    new_params = settings.DataProcessing()
    new_params._update_params(obj=obj)

    assert asdict(new_params) == kwargs


def test_CommonSettings():
    obj = Techniques.CyclicVoltammetry()

    kwargs = {
        'save_on_internal_storage': True,
        'use_hardware_sync': True,
        'notes': 'testtest',
        'power_frequency': 60,
    }

    params = settings.General(**kwargs)
    params._update_psmethod(obj=obj)

    assert obj.SaveOnDevice
    assert obj.UseHWSync
    assert obj.Notes == 'testtest'
    assert obj.PowerFreq == 60

    new_params = settings.General()
    new_params._update_params(obj=obj)

    assert asdict(new_params) == kwargs
