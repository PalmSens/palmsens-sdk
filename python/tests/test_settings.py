from __future__ import annotations

from PalmSens import Techniques

import pypalmsens as ps
from pypalmsens._methods.shared import (
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
    obj = Techniques.CyclicVoltammetry()

    params = ps.settings.CurrentRange(max='100uA', min='100nA', start='10uA')
    params._update_psmethod(obj)

    assert obj.Ranging.MaximumCurrentRange.Description == '100 uA'
    assert obj.Ranging.MinimumCurrentRange.Description == '100 nA'
    assert obj.Ranging.StartCurrentRange.Description == '10 uA'

    new_params = ps.settings.CurrentRange()
    new_params._update_params(obj)

    assert new_params == params


def test_AutorangingPotentialSettings():
    obj = Techniques.Potentiometry()

    params = ps.settings.PotentialRange(
        max='100mV',
        min='1mV',
        start='10mV',
    )
    params._update_psmethod(obj)

    assert obj.RangingPotential.MaximumPotentialRange.Description == '100 mV'
    assert obj.RangingPotential.MinimumPotentialRange.Description == '1 mV'
    assert obj.RangingPotential.StartPotentialRange.Description == '10 mV'

    new_params = ps.settings.PotentialRange()
    new_params._update_params(obj)

    assert new_params == params


def test_PretreatmentSettings():
    obj = Techniques.CyclicVoltammetry()

    params = ps.settings.Pretreatment(
        deposition_potential=12,
        deposition_time=34,
        conditioning_potential=56,
        conditioning_time=78,
    )
    params._update_psmethod(obj)

    assert obj.DepositionPotential == 12
    assert obj.DepositionTime == 34
    assert obj.ConditioningPotential == 56
    assert obj.ConditioningTime == 78

    new_params = ps.settings.Pretreatment()
    new_params._update_params(obj)

    assert new_params == params


def test_VersusOcpSettings():
    obj = Techniques.CyclicVoltammetry()

    params = ps.settings.VersusOCP(
        mode=7,
        max_ocp_time=200.0,
        stability_criterion=123,
    )
    params._update_psmethod(obj)

    assert obj.OCPmode == 7
    assert obj.OCPMaxOCPTime == 200
    assert obj.OCPStabilityCriterion == 123

    new_params = ps.settings.VersusOCP()
    new_params._update_params(obj)

    assert new_params == params


def test_BipotSettings():
    obj = Techniques.CyclicVoltammetry()

    params = ps.settings.BiPot(
        mode='offset',
        potential=10.0,
        current_range={
            'max': '100uA',
            'min': '10nA',
            'start': '10uA',
        },
    )
    params._update_psmethod(obj)

    assert obj.BipotModePS == Techniques.CyclicVoltammetry.EnumPalmSensBipotMode(1)
    assert obj.BiPotPotential == 10.0
    assert obj.BipotRanging.MaximumCurrentRange.Description == '100 uA'
    assert obj.BipotRanging.MinimumCurrentRange.Description == '10 nA'
    assert obj.BipotRanging.StartCurrentRange.Description == '10 uA'

    new_params = ps.settings.BiPot()
    new_params._update_params(obj)

    assert new_params == params


def test_BipotSettings_fixed():
    obj = Techniques.CyclicVoltammetry()

    params = ps.settings.BiPot(mode='constant', current_range='10mA')
    params._update_psmethod(obj)

    assert obj.BipotModePS == Techniques.CyclicVoltammetry.EnumPalmSensBipotMode(0)
    assert obj.BipotRanging.MaximumCurrentRange.Description == '10 mA'
    assert obj.BipotRanging.MinimumCurrentRange.Description == '10 mA'
    assert obj.BipotRanging.StartCurrentRange.Description == '10 mA'

    new_params = ps.settings.BiPot()
    new_params._update_params(obj)

    assert new_params == params


def test_PostMeasurementSettings():
    obj = Techniques.CyclicVoltammetry()

    params = ps.settings.PostMeasurement(
        cell_on_after_measurement=True,
        standby_potential=123,
        standby_time=678,
    )
    params._update_psmethod(obj)

    assert obj.CellOnAfterMeasurement is True
    assert obj.StandbyPotential == 123
    assert obj.StandbyTime == 678

    new_params = ps.settings.PostMeasurement()
    new_params._update_params(obj)

    assert new_params == params


def test_CurrentLimitSettings():
    obj = Techniques.CyclicVoltammetry()

    params = ps.settings.CurrentLimits(
        min=123.0,
        max=678.0,
    )
    params._update_psmethod(obj)

    assert obj.UseLimitMinValue is True
    assert obj.LimitMinValue == 123.0
    assert obj.UseLimitMaxValue is True
    assert obj.LimitMaxValue == 678.0

    new_params = ps.settings.CurrentLimits()
    new_params._update_params(obj)

    assert new_params == params


def test_PotentialLimitSettings():
    obj = Techniques.CyclicVoltammetry()

    params = ps.settings.PotentialLimits(
        min=123.0,
        max=678.0,
    )
    params._update_psmethod(obj)

    assert obj.UseLimitMinValue is True
    assert obj.LimitMinValue == 123.0
    assert obj.UseLimitMaxValue is True
    assert obj.LimitMaxValue == 678.0

    new_params = ps.settings.PotentialLimits()
    new_params._update_params(obj)

    assert new_params == params


def test_ChargeLimitSettings():
    obj = Techniques.CyclicVoltammetry()

    params = ps.settings.ChargeLimits(
        min=123.0,
        max=678.0,
    )
    params._update_psmethod(obj)

    assert obj.UseChargeLimitMin is True
    assert obj.ChargeLimitMin == 123.0
    assert obj.UseChargeLimitMax is True
    assert obj.ChargeLimitMax == 678.0

    new_params = ps.settings.ChargeLimits()
    new_params._update_params(obj)

    assert new_params == params


def test_IrDropCompensationSettings():
    obj = Techniques.CyclicVoltammetry()

    params = ps.settings.IrDropCompensation(
        resistance=123.0,
    )
    params._update_psmethod(obj)

    assert obj.UseIRDropComp is True
    assert obj.IRDropCompRes == 123

    new_params = ps.settings.IrDropCompensation()
    new_params._update_params(obj)

    assert new_params == params


def test_TriggerAtEquilibrationSettings():
    obj = Techniques.CyclicVoltammetry()

    params = ps.settings.EquilibrationTriggers(
        d0=True,
        d1=False,
        d2=True,
        d3=True,
    )
    params._update_psmethod(obj)

    assert obj.UseTriggerOnEquil is True
    assert obj.TriggerValueOnEquil == 13

    new_params = ps.settings.EquilibrationTriggers()
    new_params._update_params(obj)

    assert new_params == params


def test_TriggerAtMeasurementSettings():
    obj = Techniques.CyclicVoltammetry()

    params = ps.settings.MeasurementTriggers(
        d0=True,
        d1=True,
        d2=False,
        d3=True,
    )
    params._update_psmethod(obj)

    assert obj.UseTriggerOnStart is True
    assert obj.TriggerValueOnStart == 11

    new_params = ps.settings.MeasurementTriggers()
    new_params._update_params(obj)

    assert new_params == params


def test_TriggerAtDelaySettings():
    obj = Techniques.PulsedAmpDetection()

    params = ps.settings.DelayTriggers(
        delay=1.0,
        d0=True,
        d1=True,
        d2=False,
        d3=True,
    )
    params._update_psmethod(obj)

    assert obj.UseTriggerOnDelay is True
    assert obj.TriggerValueOnDelay == 11
    assert obj.TriggerDelayPeriod == 1.0

    new_params = ps.settings.DelayTriggers()
    new_params._update_params(obj)

    assert new_params == params


def test_MultiplexerSettings():
    obj = Techniques.CyclicVoltammetry()

    params = ps.settings.Multiplexer(
        mode='consecutive',
        channels=[1, 3, 5],
        connect_sense_to_working_electrode=True,
        combine_reference_and_counter_electrodes=True,
        use_channel_1_reference_and_counter_electrodes=True,
        set_unselected_channel_working_electrode=1,
    )
    params._update_psmethod(obj)

    assert int(obj.MuxMethod) == 0
    for i, v in enumerate([True, False, True, False, True]):
        assert obj.UseMuxChannel[i] is v

    assert obj.MuxSett.ConnSEWE is True
    assert obj.MuxSett.ConnectCERE is True
    assert obj.MuxSett.CommonCERE is True
    assert int(obj.MuxSett.UnselWE) == 1

    new_params = ps.settings.Multiplexer()
    new_params._update_params(obj)

    assert new_params == params


def test_PeakSettings():
    obj = Techniques.CyclicVoltammetry()

    params = ps.settings.DataProcessing(
        smooth_level=1,
        min_width=13,
        min_height=37,
    )
    params._update_psmethod(obj)

    assert obj.SmoothLevel == 1
    assert obj.MinPeakWidth == 13
    assert obj.MinPeakHeight == 37

    new_params = ps.settings.DataProcessing()
    new_params._update_params(obj)

    assert new_params == params


def test_CommonSettings():
    obj = Techniques.CyclicVoltammetry()

    params = ps.settings.General(
        save_on_internal_storage=True,
        use_hardware_sync=True,
        notes='testtest',
        power_frequency=60,
    )
    params._update_psmethod(obj)

    assert obj.SaveOnDevice
    assert obj.UseHWSync
    assert obj.Notes == 'testtest'
    assert obj.PowerFreq == 60

    new_params = ps.settings.General()
    new_params._update_params(obj)

    assert new_params == params
