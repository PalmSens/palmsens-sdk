from __future__ import annotations

import logging
import tempfile
from pathlib import Path

import pytest
from pydantic import ValidationError

import pypalmsens as ps
from pypalmsens._methods import BaseTechnique

logger = logging.getLogger(__name__)


@pytest.fixture(scope='module')
def manager():
    instruments = ps.discover()
    with ps.connect(instruments[0]) as mgr:
        logger.warning('Connected to %s' % mgr.instrument.id)
        yield mgr


@pytest.mark.instrument
def test_get_instrument_serial(manager):
    val = manager.get_instrument_serial()
    assert val
    assert isinstance(val, str)


@pytest.mark.instrument
def test_read_current(manager):
    manager.set_cell(True)

    manager.set_current_range('1uA')
    val1 = manager.read_current()
    assert val1

    manager.set_current_range('10uA')
    val2 = manager.read_current()
    assert val2

    manager.set_cell(False)


@pytest.mark.instrument
def test_read_potential(manager):
    manager.set_cell(True)

    manager.set_potential(1)
    val1 = manager.read_potential()
    assert val1

    manager.set_potential(0)
    val2 = manager.read_potential()
    assert val2

    manager.set_cell(False)


def test_forbid_extra_keys():
    with pytest.raises(ValidationError):
        _ = ps.CyclicVoltammetry(foo=123, bar=678)


class CV:
    id = 'cv'
    kwargs = {
        'begin_potential': -1,
        'vertex1_potential': -1,
        'vertex2_potential': 1,
        'step_potential': 0.25,
        'scanrate': 5,
        'n_scans': 2,
        'current_range': {'max': '1mA', 'min': '100nA', 'start': '100uA'},
    }

    @staticmethod
    def validate(measurement):
        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

        for curve in measurement.curves:
            assert curve.n_points >= 5

        assert measurement.method.psmethod.nScans == 2

        dataset = measurement.dataset
        assert len(dataset) == 7
        assert list(dataset.keys()) == [
            'Time',
            'Potential_1',
            'Current_1',
            'Charge_1',
            'Potential_2',
            'Current_2',
            'Charge_2',
        ]
        assert dataset.array_names == {'scan1', 'scan2', 'time'}
        assert dataset.array_quantities == {'Charge', 'Current', 'Potential', 'Time'}


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

    @staticmethod
    def validate(measurement):
        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

        for curve in measurement.curves:
            assert curve.n_points >= 5

        assert measurement.method.psmethod.nScans == 3
        assert measurement.method.psmethod.nAvgScans == 2
        assert measurement.method.psmethod.nEqScans == 2

        dataset = measurement.dataset

        assert len(dataset) == 10
        assert list(dataset.keys()) == [
            'Time',
            'Potential_1',
            'Current_1',
            'Charge_1',
            'Potential_2',
            'Current_2',
            'Charge_2',
            'Potential_3',
            'Current_3',
            'Charge_3',
        ]
        assert dataset.array_names == {'scan1', 'scan2', 'scan3', 'time'}
        assert dataset.array_quantities == {'Charge', 'Current', 'Potential', 'Time'}


class LSV:
    id = 'lsv'
    kwargs = {
        'begin_potential': -1.0,
        'end_potential': 1.0,
        'step_potential': 0.1,
        'scanrate': 2.0,
        'current_range': {'max': '1mA', 'min': '100nA', 'start': '100uA'},
    }

    @staticmethod
    def validate(measurement):
        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

        for curve in measurement.curves:
            assert curve.n_points >= 5

        dataset = measurement.dataset
        assert len(dataset) == 4

        assert dataset.array_names == {'charge', 'potential', 'current', 'time'}
        assert dataset.array_quantities == {'Charge', 'Current', 'Potential', 'Time'}


class LSV_aux:
    id = 'lsv'
    kwargs = {
        'begin_potential': 0.0,
        'end_potential': 1.0,
        'step_potential': 0.2,
        'scanrate': 8.0,
        'record_auxiliary_input': True,
    }

    @staticmethod
    def validate(measurement):
        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

        assert len(measurement.curves) == 2

        for curve in measurement.curves:
            assert curve.n_points >= 5

        dataset = measurement.dataset
        assert len(dataset) == 5

        assert dataset.array_names == {
            'charge',
            'potential',
            'current',
            'time',
            'Auxiliary input',
        }
        assert dataset.array_quantities == {'Charge', 'Current', 'Potential', 'Time'}


class ACV:
    id = 'acv'
    kwargs = {
        'begin_potential': -0.15,
        'end_potential': 0.15,
        'step_potential': 0.05,
        'ac_potential': 0.25,
        'frequency': 200.0,
        'scanrate': 0.2,
        'current_range': {'max': '1mA', 'min': '100nA', 'start': '100uA'},
    }

    @staticmethod
    def validate(measurement):
        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

        for curve in measurement.curves:
            assert curve.n_points >= 5

        dataset = measurement.dataset
        assert len(dataset) == 8

        assert dataset.array_names == {
            'Applied E DC',
            'E AC RMS',
            'E DC',
            "Y'",
            "Y''",
            'i AC RMS',
            'i DC',
            'time',
        }
        assert dataset.array_quantities == {'Current', 'Potential', 'Time', "Y'", "Y''"}


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

    @staticmethod
    def validate(measurement):
        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

        for curve in measurement.curves:
            assert curve.n_points >= 5

        assert measurement.method.psmethod.nScans == 1

        dataset = measurement.dataset
        assert len(dataset) == 5

        assert dataset.array_names == {'potential', 'current', 'time', 'reverse', 'forward'}
        assert dataset.array_quantities == {'Current', 'Potential', 'Time'}


class CP:
    id = 'pot'
    kwargs = {
        'current': 0.0,
        'applied_current_range': '100uA',
        'interval_time': 0.1,
        'run_time': 1.0,
        'potential_range': {'max': '1V', 'min': '10mV', 'start': '1V'},
    }

    @staticmethod
    def validate(measurement):
        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

        for curve in measurement.curves:
            assert curve.n_points >= 5

        dataset = measurement.dataset
        assert len(dataset) == 4

        assert dataset.array_names == {'potential', 'current', 'time', 'charge'}
        assert dataset.array_quantities == {'Current', 'Potential', 'Time', 'Charge'}


class SCP:
    id = 'scp'
    kwargs = {
        'current': 0.1,
        'applied_current_range': '100uA',
        'measurement_time': 1.0,
        'potential_range': '100mV',
        'pretreatment': {'deposition_time': 1, 'deposition_potential': 0.1},
    }

    @staticmethod
    def validate(measurement):
        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

        for curve in measurement.curves:
            assert curve.n_points >= 5

        dataset = measurement.dataset
        assert len(dataset) == 4

        assert dataset.array_names == {'potential', 'current', 'time', 'charge'}
        assert dataset.array_quantities == {'Current', 'Potential', 'Time', 'Charge'}


class LSP:
    id = 'lsp'
    kwargs = {
        'applied_current_range': '100uA',
        'current_step': 0.1,
        'scan_rate': 8.0,
        'potential_range': {'max': '1V', 'min': '10mV', 'start': '1V'},
    }

    @staticmethod
    def validate(measurement):
        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

        for curve in measurement.curves:
            assert curve.n_points >= 5

        dataset = measurement.dataset
        assert len(dataset) == 4

        assert dataset.array_names == {'potential', 'current', 'time', 'charge'}
        assert dataset.array_quantities == {'Current', 'Potential', 'Time', 'Charge'}


class OCP:
    id = 'ocp'
    kwargs = {
        'interval_time': 0.1,
        'run_time': 1.0,
        'potential_range': {'max': '1V', 'min': '10mV', 'start': '1V'},
    }

    @staticmethod
    def validate(measurement):
        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

        for curve in measurement.curves:
            assert curve.n_points >= 5

        dataset = measurement.dataset
        assert len(dataset) == 2

        assert dataset.array_names == {'potential', 'time'}
        assert dataset.array_quantities == {'Potential', 'Time'}


class CA:
    id = 'ad'
    kwargs = {
        'interval_time': 0.1,
        'run_time': 1.0,
    }

    @staticmethod
    def validate(measurement):
        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

        for curve in measurement.curves:
            assert curve.n_points >= 5

        dataset = measurement.dataset
        assert len(dataset) == 4

        assert dataset.array_names == {'potential', 'time', 'charge', 'current'}
        assert dataset.array_quantities == {'Potential', 'Time', 'Charge', 'Current'}


class FAM:
    id = 'fam'
    kwargs = {
        'interval_time': 0.1,
        'run_time': 1.0,
    }

    @staticmethod
    def validate(measurement):
        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

        for curve in measurement.curves:
            assert curve.n_points >= 5

        dataset = measurement.dataset
        assert len(dataset) == 4

        assert dataset.array_names == {'potential', 'time', 'charge', 'current'}
        assert dataset.array_quantities == {'Potential', 'Time', 'Charge', 'Current'}


class DPV:
    id = 'dpv'
    kwargs = {
        'begin_potential': -0.4,
        'end_potential': 0.4,
        'step_potential': 0.15,
        'pulse_potential': 0.10,
        'pulse_time': 0.1,
        'scan_rate': 0.5,
    }

    @staticmethod
    def validate(measurement):
        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

        for curve in measurement.curves:
            assert curve.n_points >= 5

        dataset = measurement.dataset
        assert len(dataset) == 3

        assert dataset.array_names == {'potential', 'time', 'current'}
        assert dataset.array_quantities == {'Potential', 'Time', 'Current'}


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

    @staticmethod
    def validate(measurement):
        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

        for curve in measurement.curves:
            assert curve.n_points >= 5

        dataset = measurement.dataset
        assert len(dataset) == 3

        assert dataset.array_names == {'potential', 'time', 'current'}
        assert dataset.array_quantities == {'Potential', 'Time', 'Current'}


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

    @staticmethod
    def validate(measurement):
        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

        for curve in measurement.curves:
            assert curve.n_points >= 5

        dataset = measurement.dataset
        assert len(dataset) == 3

        assert dataset.array_names == {'potential', 'time', 'current'}
        assert dataset.array_quantities == {'Potential', 'Time', 'Current'}


class NPV:
    id = 'npv'
    kwargs = {
        'begin_potential': -0.4,
        'end_potential': 0.4,
        'step_potential': 0.15,
        'pulse_time': 0.1,
        'scan_rate': 0.5,
    }

    @staticmethod
    def validate(measurement):
        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

        for curve in measurement.curves:
            assert curve.n_points >= 5

        dataset = measurement.dataset
        assert len(dataset) == 3

        assert dataset.array_names == {'potential', 'time', 'current'}
        assert dataset.array_quantities == {'Potential', 'Time', 'Current'}


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

    @staticmethod
    def validate(measurement):
        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

        for curve in measurement.curves:
            assert curve.n_points >= 5

        dataset = measurement.dataset
        assert len(dataset) == 4

        assert dataset.array_names == {
            'potential',
            'time',
            'current',
            'charge',
        }
        assert dataset.array_quantities == {'Charge', 'Potential', 'Time', 'Current'}


class MP:
    id = 'mp'
    kwargs = {
        'interval_time': 0.01,
        'n_cycles': 2,
        'levels': [
            {'level': 0.5, 'duration': 0.1},
            {'level': 0.3, 'duration': 0.2},
        ],
    }

    @staticmethod
    def validate(measurement):
        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

        for curve in measurement.curves:
            assert curve.n_points >= 5

        dataset = measurement.dataset
        assert len(dataset) == 4

        assert dataset.array_names == {
            'potential',
            'time',
            'current',
            'charge',
        }
        assert dataset.array_quantities == {'Charge', 'Potential', 'Time', 'Current'}


class CC:
    id = 'cc'
    kwargs = {
        'equilibration_time': 0.0,
        'interval_time': 0.01,
        'step1_run_time': 0.1,
        'step2_run_time': 0.2,
    }

    @staticmethod
    def validate(measurement):
        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

        for curve in measurement.curves:
            assert curve.n_points >= 5

        dataset = measurement.dataset
        assert len(dataset) == 4

        assert dataset.array_names == {
            'potential',
            'time',
            'current',
            'charge',
        }
        assert dataset.array_quantities == {'Charge', 'Potential', 'Time', 'Current'}


def check_eis_measurement(measurement):
    assert measurement
    assert isinstance(measurement, ps.data.Measurement)

    for curve in measurement.curves:
        assert curve.n_points >= 5

    dataset = measurement.dataset
    assert len(dataset) == 18

    assert dataset.array_names == {
        "Capacitance'",
        "Capacitance''",
        'Capacitance',
        'Eac',
        'Frequency',
        'Iac',
        'Idc',
        'Phase',
        'Y',
        'YIm',
        'YRe',
        'Z',
        'ZIm',
        'ZRe',
        'mEdc',
        'miDC',
        'potential',
        'time',
    }
    assert dataset.array_quantities == {
        "-C''",
        '-Phase',
        "-Z''",
        'C',
        "C'",
        'Current',
        'Frequency',
        'Potential',
        'Time',
        'Y',
        "Y'",
        "Y''",
        'Z',
        "Z'",
    }

    eis_datas = measurement.eis_data
    for eis_data in eis_datas:
        assert list(eis_data.dataset) == [
            'Current',
            'Potential',
            'Time',
            'Frequency',
            'ZRe',
            'ZIm',
            'Z',
            'Phase',
            'Iac',
            'miDC',
            'mEdc',
            'Eac',
            'Y',
            'YRe',
            'YIm',
            'Cs',
            'CsRe',
            'CsIm',
        ]


class EIS:
    id = 'eis'
    kwargs = {
        'n_frequencies': 5,
        'max_frequency': 1e5,
        'min_frequency': 1e3,
        'scan_type': 'fixed',
        'frequency_type': 'scan',
    }

    @staticmethod
    def validate(measurement):
        check_eis_measurement(measurement)

        eis_datas = measurement.eis_data
        assert len(eis_datas) == 1
        for eis_data in eis_datas:
            assert eis_data.n_points == 5
            assert eis_data.n_subscans == 0
            assert eis_data.n_frequencies == 10


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
    }

    @staticmethod
    def validate(measurement):
        check_eis_measurement(measurement)

        eis_datas = measurement.eis_data
        assert len(eis_datas) == 1
        for eis_data in eis_datas:
            assert eis_data.n_points == 2
            assert eis_data.n_subscans == 0
            assert eis_data.n_frequencies == 1


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
    }

    @staticmethod
    def validate(measurement):
        check_eis_measurement(measurement)

        eis_datas = measurement.eis_data
        assert len(eis_datas) == 1
        for eis_data in eis_datas:
            assert eis_data.n_points == 10
            assert eis_data.n_subscans == 2
            assert eis_data.n_frequencies == 5


class EIS_time_fixed:
    id = 'eis'
    kwargs = {
        'n_frequencies': 5,
        'max_frequency': 1e5,
        'min_frequency': 1e3,
        'scan_type': 'time',
        'frequency_type': 'fixed',
        'run_time': 1.3,
    }

    @staticmethod
    def validate(measurement):
        check_eis_measurement(measurement)

        eis_datas = measurement.eis_data
        assert len(eis_datas) == 1
        for eis_data in eis_datas:
            # n_points is tricky to reproduce because of specific timings, target is 4
            assert eis_data.n_points in (3, 4, 5)
            assert eis_data.n_subscans == 0
            assert eis_data.n_frequencies == 1


class EIS_time_scan:
    id = 'eis'
    kwargs = {
        'n_frequencies': 5,
        'max_frequency': 1e5,
        'min_frequency': 1e3,
        'scan_type': 'time',
        'frequency_type': 'scan',
        'run_time': 0.4,
    }

    @staticmethod
    def validate(measurement):
        check_eis_measurement(measurement)

        eis_datas = measurement.eis_data
        assert len(eis_datas) == 1
        for eis_data in eis_datas:
            assert eis_data.n_points == 10
            assert eis_data.n_subscans == 2
            assert eis_data.n_frequencies == 5


class EIS_single_point:
    id = 'eis'
    kwargs = {
        'n_frequencies': 5,
        'max_frequency': 1e5,
        'min_frequency': 1e3,
        'scan_type': 'fixed',
        'frequency_type': 'fixed',
    }

    @staticmethod
    def validate(measurement):
        check_eis_measurement(measurement)

        eis_datas = measurement.eis_data
        assert len(eis_datas) == 1
        for eis_data in eis_datas:
            assert eis_data.n_points == 1
            assert eis_data.n_subscans == 0
            assert eis_data.n_frequencies == 1


class FIS:
    id = 'fis'
    kwargs = {
        'frequency': 40000,
        'run_time': 0.5,
    }

    @staticmethod
    def validate(measurement):
        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

        for curve in measurement.curves:
            assert curve.n_points >= 5

        dataset = measurement.dataset
        assert len(dataset) == 18

        assert dataset.array_names == {
            "Capacitance'",
            "Capacitance''",
            'Capacitance',
            'Eac',
            'Frequency',
            'Iac',
            'Idc',
            'Phase',
            'Y',
            'YIm',
            'YRe',
            'Z',
            'ZIm',
            'ZRe',
            'mEdc',
            'miDC',
            'potential',
            'time',
        }
        assert dataset.array_quantities == {
            "-C''",
            '-Phase',
            "-Z''",
            'C',
            "C'",
            'Current',
            'Frequency',
            'Potential',
            'Time',
            'Y',
            "Y'",
            "Y''",
            'Z',
            "Z'",
        }


class GIS:
    id = 'gis'
    kwargs = {
        'applied_current_range': '10uA',
        'equilibration_time': 0.0,
        'n_frequencies': 7,
        'max_frequency': 1e5,
        'min_frequency': 1e3,
    }

    @staticmethod
    def validate(measurement):
        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

        for curve in measurement.curves:
            assert curve.n_points >= 5

        dataset = measurement.dataset
        assert len(dataset) == 18

        assert dataset.array_names == {
            "Capacitance'",
            "Capacitance''",
            'Capacitance',
            'Eac',
            'Frequency',
            'Iac',
            'Idc',
            'Phase',
            'Y',
            'YIm',
            'YRe',
            'Z',
            'ZIm',
            'ZRe',
            'mEdc',
            'miDC',
            'potential',
            'time',
        }
        assert dataset.array_quantities == {
            "-C''",
            '-Phase',
            "-Z''",
            'C',
            "C'",
            'Current',
            'Frequency',
            'Potential',
            'Time',
            'Y',
            "Y'",
            "Y''",
            'Z',
            "Z'",
        }


class FGIS:
    id = 'fgis'
    kwargs = {
        'applied_current_range': '10uA',
        'run_time': 0.3,
    }

    @staticmethod
    def validate(measurement):
        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

        for curve in measurement.curves:
            assert curve.n_points >= 5

        dataset = measurement.dataset
        assert len(dataset) == 18

        assert dataset.array_names == {
            "Capacitance'",
            "Capacitance''",
            'Capacitance',
            'Eac',
            'Frequency',
            'Iac',
            'Idc',
            'Phase',
            'Y',
            'YIm',
            'YRe',
            'Z',
            'ZIm',
            'ZRe',
            'mEdc',
            'miDC',
            'potential',
            'time',
        }
        assert dataset.array_quantities == {
            "-C''",
            '-Phase',
            "-Z''",
            'C',
            "C'",
            'Current',
            'Frequency',
            'Potential',
            'Time',
            'Y',
            "Y'",
            "Y''",
            'Z',
            "Z'",
        }


class MS:
    id = 'ms'
    kwargs = {
        'script': (
            'e\n'  # must start with e
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
            '\n'  # must end with 2 newlines
        )
    }

    @staticmethod
    def validate(measurement):
        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

        for curve in measurement.curves:
            assert curve.n_points >= 5

        dataset = measurement.dataset
        assert len(dataset) == 2

        assert dataset.array_names == {'AppliedPotential1_1', 'Current1_1'}
        assert dataset.array_quantities == {'Current', 'Potential'}


class MM:
    id = 'mm'
    kwargs = {
        'cycles': 2,
        'interval_time': 0.02,
        'stages': [
            {
                'stage_type': 'ConstantE',
                'current_limits': {'max': 10.0, 'min': 1},
                'potential': 0.5,
                'run_time': 0.1,
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
            },
            {'stage_type': 'OpenCircuit', 'run_time': 0.1},
            {
                'stage_type': 'Impedance',
                'run_time': 0.1,
                'dc_potential': 0.0,
                'ac_potential': 0.01,
                'min_sampling_time': 0.0,
                'max_equilibration_time': 5.0,
            },
        ],
    }

    @staticmethod
    def validate(measurement):
        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

        params = measurement.method.to_settings()
        stages = [stage.stage_type for stage in params.stages]

        assert stages == ['ConstantE', 'ConstantI', 'SweepE', 'OpenCircuit', 'Impedance']

        for curve in measurement.curves:
            assert curve.n_points >= 5

        dataset = measurement.dataset

        assert len(dataset) == 4

        assert dataset.array_names == {'charge', 'current', 'potential', 'time'}
        assert dataset.array_quantities == {'Charge', 'Current', 'Potential', 'Time'}

        eis = measurement.eis_data
        assert len(eis) == 2

        eis_dataset = eis[0].dataset

        assert eis_dataset.array_names == {
            'Capacitance',
            "Capacitance'",
            "Capacitance''",
            'Eac',
            'Frequency',
            'Iac',
            'Idc',
            'Phase',
            'Y',
            'YIm',
            'YRe',
            'Z',
            'ZIm',
            'ZRe',
            'mEdc',
            'miDC',
            'potential',
            'time',
        }
        assert eis_dataset.array_quantities == {
            "-C''",
            '-Phase',
            "-Z''",
            'C',
            "C'",
            'Current',
            'Frequency',
            'Potential',
            'Time',
            'Y',
            "Y'",
            "Y''",
            'Z',
            "Z'",
        }


@pytest.mark.instrument
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
        pytest.param(
            SCP,
            marks=pytest.mark.xfail(
                raises=ValueError,
                reason='Not all devices support SCP.',
            ),
        ),
        LSP,
        OCP,
        CA,
        FAM,
        DPV,
        PAD,
        pytest.param(
            MPAD,
            marks=pytest.mark.xfail(
                raises=ValueError,
                reason='Not all devices support MPAD.',
            ),
        ),
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
        FGIS,
        MS,
        MM,
    ),
)
def test_measure(manager, method):
    params = BaseTechnique._registry[method.id].from_dict(method.kwargs)

    measurement = manager.measure(params)

    method.validate(measurement)


@pytest.mark.instrument
def test_callback(manager):
    points = []

    def callback(data):
        points.extend(data)

    params = ps.LinearSweepVoltammetry(scanrate=10)
    _ = manager.measure(params, callback=callback)

    assert len(points) == 11

    point = points[-1]
    assert isinstance(point, dict)
    assert point['index'] == 11
    assert isinstance(point['x'], float)
    assert point['x_unit'] == 'V'
    assert point['x_type'] == 'Potential'
    assert isinstance(point['y'], float)
    assert point['y_unit'] == 'µA'
    assert point['y_type'] == 'Current'


@pytest.mark.instrument
def test_callback_eis(manager):
    points = []

    def callback(data):
        points.extend(data)

    params = ps.ElectrochemicalImpedanceSpectroscopy(
        frequency_type='fixed',
        scan_type='fixed',
        # fixed_frequency=1000,
    )
    _ = manager.measure(params, callback=callback)

    assert len(points) == 1

    point = points[0]
    assert point['index'] == 1
    assert point['frequency'] == 1000.0
    assert isinstance(point['zre'], float)
    assert isinstance(point['zim'], float)


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
