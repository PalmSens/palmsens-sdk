from __future__ import annotations

import logging

import pytest
from PalmSens import Techniques
from pytest import approx

import pypalmsens
from pypalmsens.data import Measurement
from pypalmsens.settings import (
    CURRENT_RANGE,
    POTENTIAL_RANGE,
    ELevel,
)

logger = logging.getLogger(__name__)


def assert_params_match_kwargs(params, *, kwargs):
    for key, exp in kwargs.items():
        ret = getattr(params, key)
        if isinstance(exp, float):
            assert ret == approx(exp), f'{key}: expected {exp}, got {ret}'
        else:
            assert ret == exp, f'{key}: expected {exp}, got {ret}'


def assert_params_round_trip_equal(*, pscls, pycls, kwargs):
    obj = pscls()

    params = pycls(**kwargs)
    params._update_psmethod(obj=obj)

    new_params = pycls()
    new_params._update_params(obj=obj)

    assert_params_match_kwargs(new_params, kwargs=kwargs)


@pytest.fixture(scope='module')
def manager():
    with pypalmsens.connect() as mgr:
        logger.warning('Connected to %s' % mgr.instrument.name)
        yield mgr


@pytest.mark.instrument
def test_get_instrument_serial(manager):
    val = manager.get_instrument_serial()
    assert val
    assert isinstance(val, str)


@pytest.mark.instrument
def test_read_current(manager):
    val = manager.read_current()
    assert val
    assert isinstance(val, float)


@pytest.mark.instrument
def test_read_potential(manager):
    val = manager.read_current()
    assert val
    assert isinstance(val, float)


class TestCV:
    kwargs = {
        'begin_potential': -1,
        'vertex1_potential': -1,
        'vertex2_potential': 1,
        'step_potential': 0.25,
        'scanrate': 5,
        'n_scans': 2,
    }
    pycls = pypalmsens.CyclicVoltammetry
    pscls = Techniques.CyclicVoltammetry

    def test_params_round_trip(self):
        assert_params_round_trip_equal(
            pscls=self.pscls,
            pycls=self.pycls,
            kwargs=self.kwargs,
        )

    @pytest.mark.instrument
    def test_measurement(self, manager):
        method = self.pycls(
            current_range=pypalmsens.settings.CurrentRange(
                max=CURRENT_RANGE.cr_1_mA,
                min=CURRENT_RANGE.cr_100_nA,
                start=CURRENT_RANGE.cr_100_uA,
            ),
            **self.kwargs,
        )
        measurement = manager.measure(method)

        assert measurement
        assert isinstance(measurement, Measurement)
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


class TestLSV:
    kwargs = {
        'begin_potential': -1.0,
        'end_potential': 1.0,
        'step_potential': 0.1,
        'scanrate': 2.0,
    }
    pycls = pypalmsens.LinearSweepVoltammetry
    pscls = Techniques.LinearSweep

    def test_params_round_trip(self):
        assert_params_round_trip_equal(
            pscls=self.pscls,
            pycls=self.pycls,
            kwargs=self.kwargs,
        )

    @pytest.mark.instrument
    def test_measurement(self, manager):
        method = self.pycls(
            current_range=pypalmsens.settings.CurrentRange(
                max=CURRENT_RANGE.cr_1_mA,
                min=CURRENT_RANGE.cr_100_nA,
                start=CURRENT_RANGE.cr_100_uA,
            ),
            **self.kwargs,
        )
        measurement = manager.measure(method)

        assert measurement
        assert isinstance(measurement, Measurement)
        assert measurement.method.psmethod.nScans == 1

        dataset = measurement.dataset
        assert len(dataset) == 4

        assert dataset.array_names == {'charge', 'potential', 'current', 'time'}
        assert dataset.array_quantities == {'Charge', 'Current', 'Potential', 'Time'}


class TestSWV:
    kwargs = {
        'equilibration_time': 0.0,
        'begin_potential': -0.5,
        'end_potential': 0.5,
        'step_potential': 0.1,
        'frequency': 10.0,
        'amplitude': 0.05,
        'record_forward_and_reverse_currents': True,
    }
    pycls = pypalmsens.SquareWaveVoltammetry
    pscls = Techniques.SquareWave

    def test_params_round_trip(self):
        assert_params_round_trip_equal(
            pscls=self.pscls,
            pycls=self.pycls,
            kwargs=self.kwargs,
        )

    @pytest.mark.instrument
    def test_measurement(self, manager):
        method = self.pycls(
            current_range=pypalmsens.settings.CurrentRange(
                max=CURRENT_RANGE.cr_1_mA,
                min=CURRENT_RANGE.cr_100_nA,
                start=CURRENT_RANGE.cr_100_uA,
            ),
            **self.kwargs,
        )
        measurement = manager.measure(method)

        assert measurement
        assert isinstance(measurement, Measurement)
        assert measurement.method.psmethod.nScans == 1

        dataset = measurement.dataset
        assert len(dataset) == 5

        assert dataset.array_names == {'potential', 'current', 'time', 'reverse', 'forward'}
        assert dataset.array_quantities == {'Current', 'Potential', 'Time'}


class TestCP:
    kwargs = {
        'current': 0.0,
        'applied_current_range': CURRENT_RANGE.cr_100_uA,
        'interval_time': 0.1,
        'run_time': 1.0,
    }
    pycls = pypalmsens.ChronoPotentiometry
    pscls = Techniques.Potentiometry

    def test_params_round_trip(self):
        assert_params_round_trip_equal(
            pscls=self.pscls,
            pycls=self.pycls,
            kwargs=self.kwargs,
        )

    @pytest.mark.instrument
    def test_measurement(self, manager):
        method = self.pycls(
            potential_range=pypalmsens.settings.PotentialRange(
                max=POTENTIAL_RANGE.pr_1_V,
                min=POTENTIAL_RANGE.pr_10_mV,
                start=POTENTIAL_RANGE.pr_1_V,
            ),
            **self.kwargs,
        )
        measurement = manager.measure(method)

        assert measurement
        assert isinstance(measurement, Measurement)

        dataset = measurement.dataset
        assert len(dataset) == 4

        assert dataset.array_names == {'potential', 'current', 'time', 'charge'}
        assert dataset.array_quantities == {'Current', 'Potential', 'Time', 'Charge'}


class TestOCP:
    kwargs = {
        'interval_time': 0.1,
        'run_time': 1.0,
    }
    pycls = pypalmsens.OpenCircuitPotentiometry
    pscls = Techniques.OpenCircuitPotentiometry

    def test_params_round_trip(self):
        assert_params_round_trip_equal(
            pscls=self.pscls,
            pycls=self.pycls,
            kwargs=self.kwargs,
        )

    @pytest.mark.instrument
    def test_measurement(self, manager):
        method = self.pycls(
            potential_range=pypalmsens.settings.PotentialRange(
                max=POTENTIAL_RANGE.pr_1_V,
                min=POTENTIAL_RANGE.pr_10_mV,
                start=POTENTIAL_RANGE.pr_1_V,
            ),
            **self.kwargs,
        )
        measurement = manager.measure(method)

        assert measurement
        assert isinstance(measurement, Measurement)

        dataset = measurement.dataset
        assert len(dataset) == 2

        assert dataset.array_names == {'potential', 'time'}
        assert dataset.array_quantities == {'Potential', 'Time'}


class TestCA:
    kwargs = {
        'interval_time': 0.1,
        'run_time': 1.0,
    }
    pycls = pypalmsens.ChronoAmperometry
    pscls = Techniques.AmperometricDetection

    def test_params_round_trip(self):
        assert_params_round_trip_equal(
            pscls=self.pscls,
            pycls=self.pycls,
            kwargs=self.kwargs,
        )

    @pytest.mark.instrument
    def test_measurement(self, manager):
        method = self.pycls(**self.kwargs)
        measurement = manager.measure(method)

        assert measurement
        assert isinstance(measurement, Measurement)

        dataset = measurement.dataset
        assert len(dataset) == 4

        assert dataset.array_names == {'potential', 'time', 'charge', 'current'}
        assert dataset.array_quantities == {'Potential', 'Time', 'Charge', 'Current'}


class TestDP:
    kwargs = {
        'begin_potential': -0.4,
        'end_potential': 0.4,
        'step_potential': 0.15,
        'pulse_potential': 0.10,
        'pulse_time': 0.1,
        'scan_rate': 0.5,
    }
    pycls = pypalmsens.DifferentialPulseVoltammetry
    pscls = Techniques.DifferentialPulse

    def test_params_round_trip(self):
        assert_params_round_trip_equal(
            pscls=self.pscls,
            pycls=self.pycls,
            kwargs=self.kwargs,
        )

    @pytest.mark.instrument
    def test_measurement(self, manager):
        method = self.pycls(**self.kwargs)
        measurement = manager.measure(method)

        assert measurement
        assert isinstance(measurement, Measurement)

        dataset = measurement.dataset
        assert len(dataset) == 3

        assert dataset.array_names == {'potential', 'time', 'current'}
        assert dataset.array_quantities == {'Potential', 'Time', 'Current'}


class TestMA:
    kwargs = {
        'equilibration_time': 0.0,
        'interval_time': 0.01,
        'n_cycles': 2,
        'levels': [
            ELevel(level=0.5, duration=0.1),
            ELevel(level=0.3, duration=0.2),
        ],
    }
    pycls = pypalmsens.MultiStepAmperometry
    pscls = Techniques.MultistepAmperometry

    def test_params_round_trip(self):
        assert_params_round_trip_equal(
            pscls=self.pscls,
            pycls=self.pycls,
            kwargs=self.kwargs,
        )

    @pytest.mark.instrument
    def test_measurement(self, manager):
        method = self.pycls(**self.kwargs)
        measurement = manager.measure(method)

        assert measurement
        assert isinstance(measurement, Measurement)

        dataset = measurement.dataset
        assert len(dataset) == 4

        assert dataset.array_names == {
            'potential',
            'time',
            'current',
            'charge',
        }
        assert dataset.array_quantities == {'Charge', 'Potential', 'Time', 'Current'}


class TestEIS:
    kwargs = {
        'n_frequencies': 7,
        'max_frequency': 1e5,
        'min_frequency': 1e3,
    }
    pycls = pypalmsens.ElectrochemicalImpedanceSpectroscopy
    pscls = Techniques.ImpedimetricMethod

    def test_params_round_trip(self):
        assert_params_round_trip_equal(
            pscls=self.pscls,
            pycls=self.pycls,
            kwargs=self.kwargs,
        )

    @pytest.mark.instrument
    def test_measurement(self, manager):
        method = self.pycls(**self.kwargs)
        measurement = manager.measure(method)

        assert measurement
        assert isinstance(measurement, Measurement)

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


class TestGIS:
    kwargs = {
        'applied_current_range': CURRENT_RANGE.cr_10_uA,
        'equilibration_time': 0.0,
        'n_frequencies': 7,
        'max_frequency': 1e5,
        'min_frequency': 1e3,
    }
    pycls = pypalmsens.GalvanostaticImpedanceSpectroscopy
    pscls = Techniques.ImpedimetricGstatMethod

    def test_params_round_trip(self):
        assert_params_round_trip_equal(
            pscls=self.pscls,
            pycls=self.pycls,
            kwargs=self.kwargs,
        )

    @pytest.mark.instrument
    def test_measurement(self, manager):
        method = self.pycls(**self.kwargs)
        measurement = manager.measure(method)

        assert measurement
        assert isinstance(measurement, Measurement)

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


class TestMS:
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
    pycls = pypalmsens.MethodScript
    pscls = Techniques.MethodScriptSandbox

    def test_params_round_trip(self):
        assert_params_round_trip_equal(
            pscls=self.pscls,
            pycls=self.pycls,
            kwargs=self.kwargs,
        )

    @pytest.mark.instrument
    def test_measurement(self, manager):
        method = self.pycls(**self.kwargs)
        measurement = manager.measure(method)

        assert measurement
        assert isinstance(measurement, Measurement)

        dataset = measurement.dataset
        assert len(dataset) == 2

        assert dataset.array_names == {'AppliedPotential1_1', 'Current1_1'}
        assert dataset.array_quantities == {'Current', 'Potential'}
