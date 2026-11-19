"""Single source of truth for technique parameter sets used across test suites.

Each entry maps a unique variant name to ``(technique id, model kwargs)``. The offline
suite round-trips every variant through save/load; the instrument and lablink suites
build parameters from the same table and attach their own measurement validation.
"""

from __future__ import annotations

from typing import Any, NamedTuple


class TechniqueSpec(NamedTuple):
    id: str
    kwargs: dict[str, Any]


TECHNIQUE_SPECS: dict[str, TechniqueSpec] = {
    'cv': TechniqueSpec(
        'cv',
        {
            'begin_potential': 0.25,
            'vertex1_potential': 0.6,
            'vertex2_potential': -0.6,
            'step_potential': 0.25,
            'scanrate': 5,
            'n_scans': 2,
            'current_range': {'max': '1mA', 'min': '100nA', 'start': '100uA'},
        },
    ),
    'fcv': TechniqueSpec(
        'fcv',
        {
            'begin_potential': -1,
            'vertex1_potential': -1,
            'vertex2_potential': 1,
            'step_potential': 0.25,
            'scanrate': 500,
            'n_scans': 3,
            'n_avg_scans': 2,
            'n_equil_scans': 2,
            'current_range': '10uA',
        },
    ),
    'lsv': TechniqueSpec(
        'lsv',
        {
            'begin_potential': -1.0,
            'end_potential': 1.0,
            'step_potential': 0.1,
            'scanrate': 2.0,
            'current_range': {'max': '1mA', 'min': '100nA', 'start': '100uA'},
        },
    ),
    'lsv_aux': TechniqueSpec(
        'lsv',
        {
            'begin_potential': 0.0,
            'end_potential': 1.0,
            'step_potential': 0.2,
            'scanrate': 8.0,
            'record_auxiliary_input': True,
        },
    ),
    'acv': TechniqueSpec(
        'acv',
        {
            'begin_potential': -0.15,
            'end_potential': 0.15,
            'step_potential': 0.15,
            'ac_potential': 0.25,
            'frequency': 200.0,
            'scanrate': 0.2,
            'current_range': {'max': '1mA', 'min': '100nA', 'start': '100uA'},
        },
    ),
    'swv': TechniqueSpec(
        'swv',
        {
            'equilibration_time': 0.0,
            'begin_potential': -0.5,
            'end_potential': 0.5,
            'step_potential': 0.1,
            'frequency': 10.0,
            'amplitude': 0.05,
            'record_forward_and_reverse_currents': True,
            'current_range': {'max': '1mA', 'min': '100nA', 'start': '100uA'},
        },
    ),
    'cp': TechniqueSpec(
        'pot',
        {
            'current': 0.0,
            'applied_current_range': '100uA',
            'interval_time': 0.1,
            'run_time': 1.0,
            'potential_range': {'max': '1V', 'min': '100mV', 'start': '1V'},
        },
    ),
    'scp': TechniqueSpec(
        'scp',
        {
            'current': 0.1,
            'applied_current_range': '100uA',
            'measurement_time': 1.0,
            'potential_range': '100mV',
            'pretreatment': {'deposition_time': 1, 'deposition_potential': 0.1},
        },
    ),
    'lsp': TechniqueSpec(
        'lsp',
        {
            'applied_current_range': '100uA',
            'current_step': 0.1,
            'scan_rate': 8.0,
            'potential_range': {'max': '1V', 'min': '100mV', 'start': '1V'},
        },
    ),
    'ocp': TechniqueSpec(
        'ocp',
        {
            'interval_time': 0.1,
            'run_time': 1.0,
            'potential_range': {'max': '1V', 'min': '100mV', 'start': '1V'},
        },
    ),
    'ca': TechniqueSpec(
        'ad',
        {
            'interval_time': 0.1,
            'run_time': 1.0,
        },
    ),
    'fam': TechniqueSpec(
        'fam',
        {
            'interval_time': 0.1,
            'run_time': 1.0,
        },
    ),
    'dpv': TechniqueSpec(
        'dpv',
        {
            'begin_potential': -0.25,
            'end_potential': 0.25,
            'step_potential': 0.25,
            'pulse_potential': 0.10,
            'pulse_time': 0.1,
            'scan_rate': 0.5,
        },
    ),
    'pad': TechniqueSpec(
        'pad',
        {
            'potential': 0.5,
            'pulse_potential': 1.0,
            'pulse_time': 0.1,
            'mode': 'pulse',
            'run_time': 1.0,
            'interval_time': 0.2,
        },
    ),
    'mpad': TechniqueSpec(
        'mpad',
        {
            'run_time': 2.5,
            'potential_1': 0.1,
            'potential_2': 0.1,
            'potential_3': 0.1,
            'duration_1': 0.15,
            'duration_2': 0.15,
            'duration_3': 0.15,
        },
    ),
    'npv': TechniqueSpec(
        'npv',
        {
            'begin_potential': -0.25,
            'end_potential': 0.25,
            'step_potential': 0.25,
            'pulse_time': 0.1,
            'scan_rate': 0.5,
        },
    ),
    'ma': TechniqueSpec(
        'ma',
        {
            'equilibration_time': 0.0,
            'interval_time': 0.01,
            'n_cycles': 2,
            'levels': [
                {'level': 0.5, 'duration': 0.1},
                {'level': 0.3, 'duration': 0.2},
            ],
        },
    ),
    'mp': TechniqueSpec(
        'mp',
        {
            'interval_time': 0.01,
            'potential_range': {'min': '100mV', 'max': '1V', 'start': '1V'},
            'n_cycles': 2,
            'levels': [
                {'level': 0.5, 'duration': 0.1},
                {'level': 0.3, 'duration': 0.2},
            ],
        },
    ),
    'cc': TechniqueSpec(
        'cc',
        {
            'equilibration_time': 0.0,
            'interval_time': 0.01,
            'step1_run_time': 0.1,
            'step2_run_time': 0.2,
        },
    ),
    'eis': TechniqueSpec(
        'eis',
        {
            'n_frequencies': 5,
            'max_frequency': 1e5,
            'min_frequency': 1e3,
            'scan_type': 'fixed',
            'frequency_type': 'scan',
            'min_sampling_time': 0.01,
            'max_equilibration_time': 0.01,
            'potential_range': {'min': '100mV', 'max': '1V', 'start': '1V'},
        },
    ),
    'eis_pot_fixed': TechniqueSpec(
        'eis',
        {
            'n_frequencies': 5,
            'max_frequency': 1e5,
            'min_frequency': 1e3,
            'scan_type': 'potential',
            'frequency_type': 'fixed',
            'begin_potential': 0.0,
            'end_potential': -0.1,
            'step_potential': 0.1,
            'potential_range': {'min': '100mV', 'max': '1V', 'start': '1V'},
        },
    ),
    'eis_pot_scan': TechniqueSpec(
        'eis',
        {
            'n_frequencies': 5,
            'max_frequency': 1e5,
            'min_frequency': 1e3,
            'scan_type': 'potential',
            'frequency_type': 'scan',
            'begin_potential': 0.0,
            'end_potential': -0.1,
            'step_potential': 0.1,
            'potential_range': {'min': '100mV', 'max': '1V', 'start': '1V'},
        },
    ),
    'eis_time_fixed': TechniqueSpec(
        'eis',
        {
            'n_frequencies': 5,
            'max_frequency': 1e5,
            'min_frequency': 1e3,
            'scan_type': 'time',
            'frequency_type': 'fixed',
            'run_time': 1.3,
            'potential_range': {'min': '100mV', 'max': '1V', 'start': '1V'},
        },
    ),
    'eis_time_scan': TechniqueSpec(
        'eis',
        {
            'n_frequencies': 5,
            'max_frequency': 1e5,
            'min_frequency': 1e3,
            'scan_type': 'time',
            'frequency_type': 'scan',
            'run_time': 0.4,
            'potential_range': {'min': '100mV', 'max': '1V', 'start': '1V'},
        },
    ),
    'eis_single_point': TechniqueSpec(
        'eis',
        {
            'n_frequencies': 5,
            'max_frequency': 1e5,
            'min_frequency': 1e3,
            'scan_type': 'fixed',
            'frequency_type': 'fixed',
            'potential_range': {'min': '100mV', 'max': '1V', 'start': '1V'},
        },
    ),
    'fis': TechniqueSpec(
        'fis',
        {
            'frequency': 40000,
            'run_time': 0.1,
            'interval_time': 0.9,
            'potential_range': {'min': '100mV', 'max': '1V', 'start': '1V'},
        },
    ),
    'gis': TechniqueSpec(
        'gis',
        {
            'applied_current_range': '1uA',
            'equilibration_time': 0.0,
            'n_frequencies': 5,
            'max_frequency': 1e5,
            'min_frequency': 1e3,
            'min_sampling_time': 0.01,
            'max_equilibration_time': 0.01,
            'potential_range': {'min': '100mV', 'max': '1V', 'start': '1V'},
        },
    ),
    'gis_cur_fixed': TechniqueSpec(
        'gis',
        {
            'n_frequencies': 3,
            'max_frequency': 1e5,
            'min_frequency': 1e3,
            'scan_type': 'current',
            'frequency_type': 'fixed',
            'begin_current': 0.0,
            'end_current': -0.1,
            'step_current': 0.1,
            'potential_range': {'min': '100mV', 'max': '1V', 'start': '1V'},
        },
    ),
    'gis_cur_scan': TechniqueSpec(
        'gis',
        {
            'n_frequencies': 3,
            'max_frequency': 1e5,
            'min_frequency': 1e3,
            'scan_type': 'current',
            'frequency_type': 'scan',
            'begin_current': 0.0,
            'end_current': -0.1,
            'step_current': 0.1,
            'potential_range': {'min': '100mV', 'max': '1V', 'start': '1V'},
        },
    ),
    'gis_time_fixed': TechniqueSpec(
        'gis',
        {
            'n_frequencies': 3,
            'max_frequency': 1e5,
            'min_frequency': 1e3,
            'scan_type': 'time',
            'frequency_type': 'fixed',
            'run_time': 0.5,
            'potential_range': {'min': '100mV', 'max': '1V', 'start': '1V'},
        },
    ),
    'gis_time_scan': TechniqueSpec(
        'gis',
        {
            'n_frequencies': 3,
            'max_frequency': 1e5,
            'min_frequency': 1e3,
            'scan_type': 'time',
            'frequency_type': 'scan',
            'run_time': 0.3,
            'potential_range': {'min': '100mV', 'max': '1V', 'start': '1V'},
        },
    ),
    'gis_single_point': TechniqueSpec(
        'gis',
        {
            'n_frequencies': 5,
            'max_frequency': 1e5,
            'min_frequency': 1e3,
            'scan_type': 'fixed',
            'frequency_type': 'fixed',
            'potential_range': {'min': '100mV', 'max': '1V', 'start': '1V'},
        },
    ),
    'fgis': TechniqueSpec(
        'fgis',
        {
            'applied_current_range': '1uA',
            'run_time': 0.3,
            'interval_time': 0.9,
            'potential_range': {'min': '100mV', 'max': '1V', 'start': '1V'},
        },
    ),
    'ms': TechniqueSpec(
        'ms',
        {
            'script': (
                'var p\n'
                'var c\n'
                'set_pgstat_chan 0\n'
                'set_pgstat_mode 2\n'
                'cell_on\n'
                'meas_loop_ca p c 100m 200m 1000m\n'
                '    pck_start\n'
                '    pck_add p\n'
                '    pck_add c\n'
                '    pck_end\n'
                'endloop\n'
            )
        },
    ),
    'mm': TechniqueSpec(
        'mm',
        {
            'cycles': 3,
            'interval_time': 0.02,
            'stages': [
                {
                    'stage_type': 'ConstantE',
                    'current_limits': {'max': 10.0, 'min': 1},
                    'potential': 0.5,
                    'run_time': 0.1,
                    'measurement_triggers': {'d0': True, 'd2': True},
                },
                {
                    'stage_type': 'ConstantI',
                    'potential_limits': {'max': 1, 'min': -1},
                    'current': 1.0,
                    'applied_current_range': '100nA',
                    'run_time': 0.1,
                },
                {
                    'stage_type': 'SweepE',
                    'begin_potential': -0.5,
                    'end_potential': 0.5,
                    'step_potential': 0.25,
                    'scanrate': 20.0,
                    'measurement_triggers': {'d1': True},
                },
                {'stage_type': 'OpenCircuit', 'run_time': 0.1},
                {
                    'stage_type': 'Impedance',
                    'run_time': 0.2,
                    'dc_potential': 0.0,
                    'ac_potential': 0.01,
                    'min_sampling_time': 0.01,
                    'max_equilibration_time': 5.0,
                },
            ],
        },
    ),
}
