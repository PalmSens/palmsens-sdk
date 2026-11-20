from __future__ import annotations

import json
from typing import TYPE_CHECKING, cast

import pytest
from helpers.technique_specs import TECHNIQUE_SPECS

import pypalmsens as ps
from pypalmsens.lablink.models._method_mapper import (
    _BUILDERS,
    ID_TO_TECHNIQUE,
    _to_parameters,
    to_payload,
)
from pypalmsens.settings import (
    CurrentLimits,
    CurrentRange,
    ELevel,
    ILevel,
    Material,
    PotentialLimits,
    PotentialRange,
    VersusOCP,
)

if TYPE_CHECKING:
    from pydantic import BaseModel

    from pypalmsens._types import MethodType

IMPLEMENTED = sorted(_BUILDERS)
_BY_ID: dict[str, MethodType] = {method.id: method for method in TECHNIQUE_SPECS.values()}


def has_field(method_id: str, field: str) -> bool:
    """Whether the technique model exposes a settings field at all."""
    cls = cast('type[BaseModel]', type(_BY_ID[method_id]))
    return field in cls.model_fields


WITH_GENERAL = [method_id for method_id in IMPLEMENTED if has_field(method_id, 'general')]
WITH_DATA_PROCESSING = [
    method_id for method_id in IMPLEMENTED if has_field(method_id, 'data_processing')
]

# the two impedance techniques, parametrized by class with short test ids
IMPEDANCE_TECHNIQUES = [
    pytest.param(ps.ElectrochemicalImpedanceSpectroscopy, id='eis'),
    pytest.param(ps.GalvanostaticImpedanceSpectroscopy, id='gis'),
]


@pytest.mark.parametrize('method_id', IMPLEMENTED)
def test_to_payload_shape(method_id: str) -> None:
    payload = to_payload(type(_BY_ID[method_id])())

    assert payload['Technique'] == ID_TO_TECHNIQUE[method_id].value
    params = cast('dict[str, str]', payload['MethodParameters'])
    assert all(isinstance(value, str) for value in params.values())
    assert all(
        isinstance(json.loads(value), int if key in {'Levels', 'Stages', 'Curves'} else list)
        for key, value in params.items()
    )

    assert json.loads(params['Name']) == [ID_TO_TECHNIQUE[method_id].value]


def test_current_range_conversion() -> None:
    params = _to_parameters(
        ps.ChronoAmperometry(
            current_range=CurrentRange(min='100uA', max='100uA', start='100uA')
        )
    )
    assert params['MinimumCurrentRange'] == '0.000100'
    assert params['MaximumCurrentRange'] == '0.000100'
    assert params['StartingCurrentRange'] == '0.000100'


def test_potential_range_conversion() -> None:
    params = _to_parameters(
        ps.ChronoPotentiometry(potential_range=PotentialRange(min='10mV', max='1V', start='1V'))
    )
    assert params['MinimumPotentialRange'] == '0.010'
    assert params['MaximumPotentialRange'] == '1'
    assert params['StartingPotentialRange'] == '1'


def test_fastamperometry_fixes_one_range() -> None:
    params = _to_parameters(ps.FastAmperometry(current_range='100nA'))
    assert params['MinimumCurrentRange'] == '0.000000100'
    assert params['MaximumCurrentRange'] == '0.000000100'
    assert params['StartingCurrentRange'] == '0.000000100'


def test_stripping_omits_hardware_sync() -> None:
    assert 'EnableHardwareSync' not in _to_parameters(ps.StrippingChronoPotentiometry())


@pytest.mark.parametrize('cls', IMPEDANCE_TECHNIQUES)
def test_impedance_omits_hardware_sync(cls: type) -> None:
    assert 'EnableHardwareSync' not in _to_parameters(cls())


@pytest.mark.parametrize('cls', IMPEDANCE_TECHNIQUES)
def test_impedance_emits_no_measure_or_scan_type_keys(cls: type) -> None:
    params = _to_parameters(cls())
    assert not [key for key in params if key.startswith('Measure')]
    assert 'UseIRCompensation' not in params
    assert 'EISScanType' not in params
    assert 'EISFrequencyType' not in params


def test_eis_frequencies_per_decade_is_recomputed() -> None:
    params = _to_parameters(
        ps.ElectrochemicalImpedanceSpectroscopy(
            n_frequencies=21, max_frequency=1e4, min_frequency=10.0
        )
    )
    assert params['NumberOfFrequencies'] == 21
    assert params['NumberOfFrequenciesPerDecade'] == 6.666667

    with pytest.raises(ValueError):
        _ = _to_parameters(
            ps.ElectrochemicalImpedanceSpectroscopy(max_frequency=1e3, min_frequency=1e3)
        )


def test_eis_dc_potential_versus_ocp() -> None:
    # A fixed scan type offers only the 'potential' OCP flag, i.e. OCPmode bit 0.
    params = _to_parameters(
        ps.ElectrochemicalImpedanceSpectroscopy(
            versus_ocp=VersusOCP(potentials=['potential'], timeout=15.0)
        )
    )
    assert params['PotentialDirectCurrentOCP'] is True
    assert params['EnableOcp'] is True
    assert params['MaximumOCPTime'] == 15.0
    assert params['OCPStabilityCriterion'] == 0.0


def test_gis_is_galvanostatic_only() -> None:
    params = _to_parameters(
        ps.GalvanostaticImpedanceSpectroscopy(
            applied_current_range='1mA', dc_current=0.2, ac_current=0.05
        )
    )
    assert params['AppliedCurrentRange'] == '0.001'
    assert params['DCCurrent'] == 0.2
    assert params['ACCurrent'] == 0.05
    # The GIS record implements neither `IVsOcpParameters` nor a potentiostatic dc level.
    assert 'EnableOcp' not in params
    assert 'PotentialDirectCurrent' not in params


@pytest.mark.parametrize(
    'cls,kinds,absent',
    [
        pytest.param(
            ps.ElectrochemicalImpedanceSpectroscopy,
            ('Current', 'Charge', 'Temperature'),
            'Potential',
            id='eis',
        ),
        pytest.param(
            ps.GalvanostaticImpedanceSpectroscopy,
            ('Potential', 'Charge', 'Temperature'),
            'Current',
            id='gis',
        ),
    ],
)
def test_impedance_limits_are_flags_only(
    cls: type, kinds: tuple[str, ...], absent: str
) -> None:
    params = _to_parameters(cls())
    for kind in kinds:
        assert params[f'UseMinimum{kind}Limit'] is False
        assert params[f'UseMaximum{kind}Limit'] is False
        assert f'Minimum{kind}Limit' not in params
        assert f'Maximum{kind}Limit' not in params
    assert f'UseMinimum{absent}Limit' not in params


@pytest.mark.parametrize('cls', IMPEDANCE_TECHNIQUES)
def test_guard_scan_and_frequency_type(cls: type) -> None:
    with pytest.raises(NotImplementedError):
        _ = _to_parameters(cls(scan_type='time', run_time=1.0))
    with pytest.raises(NotImplementedError):
        _ = _to_parameters(cls(frequency_type='fixed'))


@pytest.mark.parametrize('cls', IMPEDANCE_TECHNIQUES)
def test_guard_multiplexer(cls: type) -> None:
    with pytest.raises(NotImplementedError):
        _ = _to_parameters(cls(multiplexer={'mode': 'consecutive', 'channels': [1]}))


def test_guard_eis_material() -> None:
    # Material only feeds the corrosion-rate analysis, so it never reaches the wire.
    with pytest.raises(NotImplementedError):
        _ = _to_parameters(
            ps.ElectrochemicalImpedanceSpectroscopy(material=Material(surface_area=1.5))
        )


def test_level_count_is_written_bare() -> None:
    payload = to_payload(ps.MultiStepAmperometry(levels=[ELevel(level=0.5, duration=0.1)]))
    params = cast('dict[str, str]', payload['MethodParameters'])
    assert params['Levels'] == '1'
    assert params['Levels/0/Level/Potential'] == '[0.5]'


def test_multistep_potentiometry_levels_apply_current() -> None:
    params = _to_parameters(
        ps.MultiStepPotentiometry(
            levels=[ILevel(level=0.5, duration=0.1, limit_potential_max=1.0)],
            record_auxiliary_input=True,
            record_we_current=True,
        )
    )
    assert params['Levels/0/Level/AppliedCurrent'] == 0.5
    assert params['Levels/0/Level/UseMaximumPotentialLimit'] is True
    assert params['Levels/0/Level/MaximumPotentialLimit'] == 1.0
    assert 'Levels/0/Level/MinimumPotentialLimit' not in params
    assert params['SelectLimitPerLevel'] is True
    assert params['AppliedCurrentRange'] == '0.000001'
    assert params['MeasureAuxiliaryInput'] is True
    assert params['MeasureWECurrent'] is True
    assert 'UseIRCompensation' not in params
    assert 'Levels/0/Level/Potential' not in params


def test_stage_count_is_written_bare() -> None:
    payload = to_payload(
        ps.MixedMode(
            stages=[
                ps.stages.OpenCircuit(run_time=0.1),
                ps.stages.ConstantE(potential=0.5, run_time=0.1),
            ]
        )
    )
    params = cast('dict[str, str]', payload['MethodParameters'])
    assert params['Stages'] == '2'
    assert params['Stages/0/OpenCircuitStage/RunTime'] == '[0.1]'
    assert params['Stages/1/ConstantPotentialStage/Potential'] == '[0.5]'


def test_stage_keys_nest_under_the_group_name() -> None:
    params = _to_parameters(
        ps.MixedMode(
            stages=[
                ps.stages.ConstantE(),
                ps.stages.ConstantI(),
                ps.stages.SweepE(),
                ps.stages.OpenCircuit(),
            ]
        )
    )
    groups = {key.split('/')[2] for key in params if key.startswith('Stages/')}
    assert groups == {
        'ConstantPotentialStage',
        'ConstantCurrentStage',
        'SweepPotentialStage',
        'OpenCircuitStage',
    }
    assert 'Stages/0/ConstantPotentialStage/Potential' in params
    assert 'Stages/1/ConstantCurrentStage/AppliedCurrent' in params
    assert 'Stages/2/SweepPotentialStage/ScanRate' in params
    assert 'Stages/3/OpenCircuitStage/RunTime' in params


def test_stage_versus_previous_flags_are_always_false() -> None:
    params = _to_parameters(
        ps.MixedMode(
            stages=[
                ps.stages.ConstantE(),
                ps.stages.ConstantI(),
                ps.stages.SweepE(),
                ps.stages.OpenCircuit(),
            ]
        )
    )
    versus_previous = [key for key in params if key.endswith('VersusPrevious')]
    assert versus_previous == [
        'Stages/0/ConstantPotentialStage/PotentialVersusPrevious',
        'Stages/1/ConstantCurrentStage/AppliedCurrentVersusPrevious',
        'Stages/2/SweepPotentialStage/BeginPotentialVersusPrevious',
        'Stages/2/SweepPotentialStage/EndPotentialVersusPrevious',
    ]
    assert all(params[key] is False for key in versus_previous)


def test_stage_limits_nest_and_follow_the_stage_kind() -> None:
    params = _to_parameters(
        ps.MixedMode(
            stages=[
                ps.stages.ConstantE(current_limits=CurrentLimits(min=-2.5)),
                ps.stages.OpenCircuit(potential_limits=PotentialLimits(max=0.75)),
            ]
        )
    )
    assert params['Stages/0/ConstantPotentialStage/UseMinimumCurrentLimit'] is True
    assert params['Stages/0/ConstantPotentialStage/MinimumCurrentLimit'] == -2.5
    assert params['Stages/0/ConstantPotentialStage/UseMaximumCurrentLimit'] is False
    assert 'Stages/0/ConstantPotentialStage/MaximumCurrentLimit' not in params
    assert 'Stages/0/ConstantPotentialStage/UseMinimumPotentialLimit' not in params
    assert params['Stages/1/OpenCircuitStage/UseMaximumPotentialLimit'] is True
    assert params['Stages/1/OpenCircuitStage/MaximumPotentialLimit'] == 0.75
    assert 'Stages/1/OpenCircuitStage/UseMinimumCurrentLimit' not in params


def test_mixed_mode_potential_ranges_are_the_legacy_defaults() -> None:
    assert 'potential_range' not in ps.MixedMode.model_fields
    params = _to_parameters(ps.MixedMode())
    assert params['MinimumPotentialRange'] == '0.001'
    assert params['MaximumPotentialRange'] == '1'
    assert params['StartingPotentialRange'] == '1'


def test_guard_mixed_mode_impedance_stage() -> None:
    with pytest.raises(NotImplementedError):
        _ = _to_parameters(
            ps.MixedMode(
                stages=[
                    ps.stages.Impedance(
                        run_time=0.2,
                        dc_potential=0.0,
                        ac_potential=0.01,
                        min_sampling_time=0.01,
                    )
                ]
            )
        )


def test_methodscript_sends_the_legacy_script() -> None:
    payload = to_payload(ps.MethodScript(script='cell_on\n'))
    params = cast('dict[str, str]', payload['MethodParameters'])
    assert params['Script'] == '["cell_on\\n"]'
    assert params['Name'] == '["MethodScriptSandbox"]'
    assert set(params) == {'Name', 'Script'}


def test_wire_number_formatting() -> None:
    payload = to_payload(
        ps.ChronoAmperometry(run_time=1.0, interval_time=1e-5, potential=1.2345678)
    )
    params = cast('dict[str, str]', payload['MethodParameters'])
    assert params['RunTime'] == '[1]'
    assert params['IntervalTime'] == '[1E-05]'
    assert params['Potential'] == '[1.234568]'
    assert params['Name'] == '["Chronoamperometry"]'
    assert params['CellModeAfterMeasurement'] == '["CellModeAfterMeasurementOff"]'


@pytest.mark.parametrize(
    'cls',
    [
        ps.ChronoAmperometry,
        ps.CyclicVoltammetry,
        ps.LinearSweepVoltammetry,
        ps.SquareWaveVoltammetry,
        ps.DifferentialPulseVoltammetry,
        ps.NormalPulseVoltammetry,
    ],
)
def test_guard_enable_bipot_current(cls: type) -> None:
    with pytest.raises(NotImplementedError):
        _ = _to_parameters(cls(enable_bipot_current=True))


@pytest.mark.parametrize(
    'cls',
    [
        ps.SquareWaveVoltammetry,
        ps.DifferentialPulseVoltammetry,
        ps.NormalPulseVoltammetry,
    ],
)
def test_guard_record_auxiliary_input(cls: type) -> None:
    with pytest.raises(NotImplementedError):
        _ = _to_parameters(cls(record_auxiliary_input=True))


@pytest.mark.parametrize(
    'cls',
    [type(_BY_ID[method_id]) for method_id in WITH_GENERAL],
    ids=WITH_GENERAL,
)
def test_guard_general_notes(cls: type) -> None:
    with pytest.raises(NotImplementedError):
        _ = _to_parameters(cls(general={'notes': 'not supported yet'}))


@pytest.mark.parametrize(
    'cls',
    [type(_BY_ID[method_id]) for method_id in WITH_GENERAL],
    ids=WITH_GENERAL,
)
def test_guard_general_save_on_internal_storage(cls: type) -> None:
    with pytest.raises(NotImplementedError):
        _ = _to_parameters(cls(general={'save_on_internal_storage': True}))


@pytest.mark.parametrize(
    'cls',
    [type(_BY_ID[method_id]) for method_id in WITH_DATA_PROCESSING],
    ids=WITH_DATA_PROCESSING,
)
def test_guard_data_processing(cls: type) -> None:
    with pytest.raises(NotImplementedError):
        _ = _to_parameters(cls(data_processing={'smooth_level': 2}))
