from __future__ import annotations

import logging
import tempfile
from pathlib import Path

import pytest
from pydantic import ValidationError

import pypalmsens as ps
from pypalmsens._methods import BaseTechnique

logger = logging.getLogger(__name__)


def test_forbid_extra_keys():
    with pytest.raises(ValidationError):
        _ = ps.CyclicVoltammetry(foo=123, bar=678)


class CV:
    id = 'cv'
    kwargs = {
        'begin_potential': 0.25,
        'vertex1_potential': 0.6,
        'vertex2_potential': -0.6,
        'step_potential': 0.25,
        'scanrate': 5,
        'n_scans': 2,
        'current_range': {'max': '1mA', 'min': '100nA', 'start': '100uA'},
    }


class FCV:
    id = 'fcv'
    kwargs = {
        'begin_potential': -1,
        'vertex1_potential': -1,
        'vertex2_potential': 1,
        'step_potential': 0.25,
        'scanrate': 500,
        'n_scans': 3,
        'n_avg_scans': 2,
        'n_equil_scans': 2,
        'current_range': '10uA',
    }


class LSV:
    id = 'lsv'
    kwargs = {
        'begin_potential': -1.0,
        'end_potential': 1.0,
        'step_potential': 0.1,
        'scanrate': 2.0,
        'current_range': {'max': '1mA', 'min': '100nA', 'start': '100uA'},
    }


class LSV_aux:
    id = 'lsv'
    kwargs = {
        'begin_potential': 0.0,
        'end_potential': 1.0,
        'step_potential': 0.2,
        'scanrate': 8.0,
        'record_auxiliary_input': True,
    }


class ACV:
    id = 'acv'
    kwargs = {
        'begin_potential': -0.15,
        'end_potential': 0.15,
        'step_potential': 0.15,
        'ac_potential': 0.25,
        'frequency': 200.0,
        'scanrate': 0.2,
        'current_range': {'max': '1mA', 'min': '100nA', 'start': '100uA'},
    }


class SWV:
    id = 'swv'
    kwargs = {
        'equilibration_time': 0.0,
        'begin_potential': -0.5,
        'end_potential': 0.5,
        'step_potential': 0.1,
        'frequency': 10.0,
        'amplitude': 0.05,
        'record_forward_and_reverse_currents': True,
        'current_range': {'max': '1mA', 'min': '100nA', 'start': '100uA'},
    }


class CP:
    id = 'pot'
    kwargs = {
        'current': 0.0,
        'applied_current_range': '100uA',
        'interval_time': 0.1,
        'run_time': 1.0,
        'potential_range': {'max': '1V', 'min': '100mV', 'start': '1V'},
    }


class SCP:
    id = 'scp'
    kwargs = {
        'current': 0.1,
        'applied_current_range': '100uA',
        'measurement_time': 1.0,
        'potential_range': '100mV',
        'pretreatment': {'deposition_time': 1, 'deposition_potential': 0.1},
    }


class LSP:
    id = 'lsp'
    kwargs = {
        'applied_current_range': '100uA',
        'current_step': 0.1,
        'scan_rate': 8.0,
        'potential_range': {'max': '1V', 'min': '100mV', 'start': '1V'},
    }


class OCP:
    id = 'ocp'
    kwargs = {
        'interval_time': 0.1,
        'run_time': 1.0,
        'potential_range': {'max': '1V', 'min': '100mV', 'start': '1V'},
    }


class CA:
    id = 'ad'
    kwargs = {
        'interval_time': 0.1,
        'run_time': 1.0,
    }


class FAM:
    id = 'fam'
    kwargs = {
        'interval_time': 0.1,
        'run_time': 1.0,
    }


class DPV:
    id = 'dpv'
    kwargs = {
        'begin_potential': -0.25,
        'end_potential': 0.25,
        'step_potential': 0.25,
        'pulse_potential': 0.10,
        'pulse_time': 0.1,
        'scan_rate': 0.5,
    }


class PAD:
    id = 'pad'
    kwargs = {
        'potential': 0.5,
        'pulse_potential': 1.0,
        'pulse_time': 0.1,
        'mode': 'pulse',
        'run_time': 1.0,
        'interval_time': 0.2,
    }


class MPAD:
    id = 'mpad'
    kwargs = {
        'run_time': 2.5,
        'potential_1': 0.1,
        'potential_2': 0.1,
        'potential_3': 0.1,
        'duration_1': 0.15,
        'duration_2': 0.15,
        'duration_3': 0.15,
    }


class NPV:
    id = 'npv'
    kwargs = {
        'begin_potential': -0.25,
        'end_potential': 0.25,
        'step_potential': 0.25,
        'pulse_time': 0.1,
        'scan_rate': 0.5,
    }


class MA:
    id = 'ma'
    kwargs = {
        'equilibration_time': 0.0,
        'interval_time': 0.01,
        'n_cycles': 2,
        'levels': [
            {'level': 0.5, 'duration': 0.1},
            {'level': 0.3, 'duration': 0.2},
        ],
    }


class MP:
    id = 'mp'
    kwargs = {
        'interval_time': 0.01,
        'potential_range': {'min': '100mV', 'max': '1V', 'start': '1V'},
        'n_cycles': 2,
        'levels': [
            {'level': 0.5, 'duration': 0.1},
            {'level': 0.3, 'duration': 0.2},
        ],
    }


class CC:
    id = 'cc'
    kwargs = {
        'equilibration_time': 0.0,
        'interval_time': 0.01,
        'step1_run_time': 0.1,
        'step2_run_time': 0.2,
    }


class EIS:
    id = 'eis'
    kwargs = {
        'n_frequencies': 5,
        'max_frequency': 1e5,
        'min_frequency': 1e3,
        'scan_type': 'fixed',
        'frequency_type': 'scan',
        'min_sampling_time': 0.01,
        'max_equilibration_time': 0.01,
        'potential_range': {'min': '100mV', 'max': '1V', 'start': '1V'},
    }


class EIS_pot_fixed:
    id = 'eis'
    kwargs = {
        'n_frequencies': 5,
        'max_frequency': 1e5,
        'min_frequency': 1e3,
        'scan_type': 'potential',
        'frequency_type': 'fixed',
        'begin_potential': 0.0,
        'end_potential': -0.1,
        'step_potential': 0.1,
        'potential_range': {'min': '100mV', 'max': '1V', 'start': '1V'},
    }


class EIS_pot_scan:
    id = 'eis'
    kwargs = {
        'n_frequencies': 5,
        'max_frequency': 1e5,
        'min_frequency': 1e3,
        'scan_type': 'potential',
        'frequency_type': 'scan',
        'begin_potential': 0.0,
        'end_potential': -0.1,
        'step_potential': 0.1,
        'potential_range': {'min': '100mV', 'max': '1V', 'start': '1V'},
    }


class EIS_time_fixed:
    id = 'eis'
    kwargs = {
        'n_frequencies': 5,
        'max_frequency': 1e5,
        'min_frequency': 1e3,
        'scan_type': 'time',
        'frequency_type': 'fixed',
        'run_time': 1.3,
        'potential_range': {'min': '100mV', 'max': '1V', 'start': '1V'},
    }


class EIS_time_scan:
    id = 'eis'
    kwargs = {
        'n_frequencies': 5,
        'max_frequency': 1e5,
        'min_frequency': 1e3,
        'scan_type': 'time',
        'frequency_type': 'scan',
        'run_time': 0.4,
        'potential_range': {'min': '100mV', 'max': '1V', 'start': '1V'},
    }


class EIS_single_point:
    id = 'eis'
    kwargs = {
        'n_frequencies': 5,
        'max_frequency': 1e5,
        'min_frequency': 1e3,
        'scan_type': 'fixed',
        'frequency_type': 'fixed',
        'potential_range': {'min': '100mV', 'max': '1V', 'start': '1V'},
    }


class FIS:
    id = 'fis'
    kwargs = {
        'frequency': 40000,
        'run_time': 0.1,
        'interval_time': 0.9,
        'potential_range': {'min': '100mV', 'max': '1V', 'start': '1V'},
    }


class GIS:
    id = 'gis'
    kwargs = {
        'applied_current_range': '1uA',
        'equilibration_time': 0.0,
        'n_frequencies': 5,
        'max_frequency': 1e5,
        'min_frequency': 1e3,
        'min_sampling_time': 0.01,
        'max_equilibration_time': 0.01,
        'potential_range': {'min': '100mV', 'max': '1V', 'start': '1V'},
    }


class GIS_cur_fixed:
    id = 'gis'
    kwargs = {
        'n_frequencies': 3,
        'max_frequency': 1e5,
        'min_frequency': 1e3,
        'scan_type': 'current',
        'frequency_type': 'fixed',
        'begin_current': 0.0,
        'end_current': -0.1,
        'step_current': 0.1,
        'potential_range': {'min': '100mV', 'max': '1V', 'start': '1V'},
    }


class GIS_cur_scan:
    id = 'gis'
    kwargs = {
        'n_frequencies': 3,
        'max_frequency': 1e5,
        'min_frequency': 1e3,
        'scan_type': 'current',
        'frequency_type': 'scan',
        'begin_current': 0.0,
        'end_current': -0.1,
        'step_current': 0.1,
        'potential_range': {'min': '100mV', 'max': '1V', 'start': '1V'},
    }


class GIS_time_fixed:
    id = 'gis'
    kwargs = {
        'n_frequencies': 3,
        'max_frequency': 1e5,
        'min_frequency': 1e3,
        'scan_type': 'time',
        'frequency_type': 'fixed',
        'run_time': 0.5,
        'potential_range': {'min': '100mV', 'max': '1V', 'start': '1V'},
    }


class GIS_time_scan:
    id = 'gis'
    kwargs = {
        'n_frequencies': 3,
        'max_frequency': 1e5,
        'min_frequency': 1e3,
        'scan_type': 'time',
        'frequency_type': 'scan',
        'run_time': 0.3,
        'potential_range': {'min': '100mV', 'max': '1V', 'start': '1V'},
    }


class GIS_single_point:
    id = 'gis'
    kwargs = {
        'n_frequencies': 5,
        'max_frequency': 1e5,
        'min_frequency': 1e3,
        'scan_type': 'fixed',
        'frequency_type': 'fixed',
        'potential_range': {'min': '100mV', 'max': '1V', 'start': '1V'},
    }


class FGIS:
    id = 'fgis'
    kwargs = {
        'applied_current_range': '1uA',
        'run_time': 0.3,
        'interval_time': 0.9,
        'potential_range': {'min': '100mV', 'max': '1V', 'start': '1V'},
    }


class MS:
    id = 'ms'
    kwargs = {
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
    }


class MM:
    id = 'mm'
    kwargs = {
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
    }


@pytest.mark.parametrize(
    'method',
    (
        CV,
        FCV,
        LSV,
        LSV_aux,
        ACV,
        SWV,
        CP,
        SCP,
        LSP,
        OCP,
        CA,
        FAM,
        DPV,
        PAD,
        MPAD,
        NPV,
        MA,
        MP,
        CC,
        EIS,
        EIS_pot_fixed,
        EIS_pot_scan,
        EIS_time_scan,
        EIS_time_fixed,
        EIS_single_point,
        FIS,
        GIS,
        GIS_cur_fixed,
        GIS_cur_scan,
        GIS_time_scan,
        GIS_time_fixed,
        GIS_single_point,
        FGIS,
        MS,
        MM,
    ),
)
def test_params_round_trip(method):
    params = BaseTechnique._registry[method.id].from_dict(method.kwargs)

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp, f'{method.id}.psmethod')
        ps.save_method_file(path, params)
        new_params = ps.load_method_file(path)

    assert new_params == params
