import pytest
from PalmSens.Techniques import CyclicVoltammetry, Potentiometry

from pspython.methods import settings
from pspython.methods._shared import get_current_range, get_mux8r2_settings, get_potential_range


def test_AutorangingCurrentSettings():
    obj = CyclicVoltammetry()
    params = settings.AutorangingCurrentSettings(
        current_range_max=get_current_range(6),
        current_range_min=get_current_range(3),
        current_range_start=get_current_range(5),
    )
    params.add_to_object(obj=obj)

    assert obj.Ranging.MaximumCurrentRange.Description == '100 uA'
    assert obj.Ranging.MinimumCurrentRange.Description == '100 nA'
    assert obj.Ranging.StartCurrentRange.Description == '10 uA'


def test_AutorangingPotentialSettings():
    obj = Potentiometry()
    params = settings.AutorangingPotentialSettings(
        potential_range_max=get_potential_range(4),
        potential_range_min=get_potential_range(0),
        potential_range_start=get_potential_range(1),
    )
    params.add_to_object(obj=obj)
    assert obj.RangingPotential.MaximumPotentialRange.Description == '100 mV'
    assert obj.RangingPotential.MinimumPotentialRange.Description == '1 mV'
    assert obj.RangingPotential.StartPotentialRange.Description == '10 mV'


def test_PretreatmentSettings():
    obj = CyclicVoltammetry()

    params = settings.PretreatmentSettings(
        deposition_potential=12,
        deposition_time=34,
        conditioning_potential=56,
        conditioning_time=78,
    )
    params.add_to_object(obj=obj)

    assert obj.DepositionPotential == 12
    assert obj.DepositionTime == 34
    assert obj.ConditioningPotential == 56
    assert obj.ConditioningTime == 78


def test_VersusOcpSettings():
    obj = CyclicVoltammetry()

    params = settings.VersusOcpSettings(
        versus_ocp_mode=7,
        versus_ocp_max_ocp_time=200.0,
        versus_ocp_stability_criterion=123,
    )
    params.add_to_object(obj=obj)

    assert obj.OCPmode == 7
    assert obj.OCPMaxOCPTime == 200
    assert obj.OCPStabilityCriterion == 123


def test_BipotSettings():
    obj = CyclicVoltammetry()

    params = settings.BipotSettings(
        enable_bipot_current=True,
        bipot_mode=1,
        bipot_potential=10.0,
        bipot_current_range_max=get_current_range(6),
        bipot_current_range_min=get_current_range(2),
        bipot_current_range_start=get_current_range(5),
    )
    params.add_to_object(obj=obj)

    assert obj.BiPotModePS == CyclicVoltammetry.EnumPalmSensBipotMode(1)
    assert obj.BiPotPotential == 10.0
    assert obj.BipotRanging.MaximumCurrentRange.Description == '100 uA'
    assert obj.BipotRanging.MinimumCurrentRange.Description == '10 nA'
    assert obj.BipotRanging.StartCurrentRange.Description == '10 uA'


@pytest.mark.xfail(reason='https://github.com/PalmSens/PalmSens_SDK/issues/37')
def test_ExtraValueMask():
    assert False


def test_PostMeasurementSettings():
    obj = CyclicVoltammetry()

    params = settings.PostMeasurementSettings(
        cell_on_after_measurement=True,
        cell_on_after_measurement_potential=123,
    )

    params.add_to_object(obj=obj)

    assert obj.CellOnAfterMeasurement is True
    assert obj.StandbyPotential == 123


def test_CurrentLimitSettings():
    obj = CyclicVoltammetry()

    params = settings.CurrentLimitSettings(
        use_limit_current_max=True,
        limit_current_max=123.0,
        use_limit_current_min=True,
        limit_current_min=678.0,
    )

    params.add_to_object(obj=obj)

    assert obj.UseLimitMaxValue is True
    assert obj.LimitMaxValue == 123.0
    assert obj.UseLimitMinValue is True
    assert obj.LimitMinValue == 678.0


def test_PotentialLimitSettings():
    obj = CyclicVoltammetry()

    params = settings.PotentialLimitSettings(
        use_limit_potential_max=True,
        limit_potential_max=123.0,
        use_limit_potential_min=True,
        limit_potential_min=678.0,
    )
    params.add_to_object(obj=obj)
    assert obj.UseLimitMaxValue is True
    assert obj.LimitMaxValue == 123.0
    assert obj.UseLimitMinValue is True
    assert obj.LimitMinValue == 678.0


def test_ChargeLimitSettings():
    obj = CyclicVoltammetry()

    params = settings.ChargeLimitSettings(
        use_limit_charge_max=True,
        limit_charge_max=123.0,
        use_limit_charge_min=True,
        limit_charge_min=678.0,
    )
    params.add_to_object(obj=obj)

    assert obj.UseChargeLimitMax is True
    assert obj.ChargeLimitMax == 123.0
    assert obj.UseChargeLimitMin is True
    assert obj.ChargeLimitMin == 678.0


def test_IrDropCompensationSettings():
    obj = CyclicVoltammetry()

    params = settings.IrDropCompensationSettings(
        use_ir_compensation=True,
        ir_compensation=123.0,
    )
    params.add_to_object(obj=obj)

    assert obj.UseIRDropComp is True
    assert obj.IRDropCompRes == 123


def test_TriggerAtEquilibrationSettings():
    obj = CyclicVoltammetry()

    params = settings.TriggerAtEquilibrationSettings(
        trigger_at_equilibration=True,
        trigger_at_equilibration_lines=(True, False, True, True),
    )
    params.add_to_object(obj=obj)

    assert obj.UseTriggerOnEquil is True
    assert obj.TriggerValueOnEquil == 13


def test_TriggerAtMeasurementSettings():
    obj = CyclicVoltammetry()

    params = settings.TriggerAtMeasurementSettings(
        trigger_at_measurement=True,
        trigger_at_measurement_lines=(True, True, False, True),
    )
    params.add_to_object(obj=obj)

    assert obj.UseTriggerOnStart is True
    assert obj.TriggerValueOnStart == 11


def test_MultiplexerSettings():
    obj = CyclicVoltammetry()

    params = settings.MultiplexerSettings(
        set_mux_mode=0,
        set_mux_channels=[True, False, True, False, True],
        set_mux8r2_settings=get_mux8r2_settings(
            connect_sense_to_working_electrode=True,
            combine_reference_and_counter_electrodes=True,
            use_channel_1_reference_and_counter_electrodes=True,
            set_unselected_channel_working_electrode=1,
        ),
    )
    params.add_to_object(obj=obj)
    assert int(obj.MuxMethod) == 0
    for i, v in enumerate([True, False, True, False, True]):
        assert obj.UseMuxChannel[i] is v

    assert obj.MuxSett.ConnSEWE is True
    assert obj.MuxSett.ConnectCERE is True
    assert obj.MuxSett.CommonCERE is True
    assert int(obj.MuxSett.UnselWE) == 1


def test_FilterSettings():
    obj = CyclicVoltammetry()

    params = settings.FilterSettings(
        dc_mains_filter=60,
        default_curve_post_processing_filter=1,
    )
    params.add_to_object(obj=obj)

    assert obj.DCMainsFilter == 60
    assert obj.DefaultCurvePostProcessingFilter == 1


def test_OtherSettings():
    obj = CyclicVoltammetry()

    params = settings.OtherSettings(
        save_on_internal_storage=True,
        use_hardware_sync=True,
    )
    params.add_to_object(obj=obj)

    obj.SaveOnDevice = True
    obj.UseHWSync = True
