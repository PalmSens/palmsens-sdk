from __future__ import annotations

import logging

import pytest
import System
from PalmSens import Method as PSMethod
from pytest import approx

import pypalmsens as ps

logger = logging.getLogger(__name__)


def assert_params_match_kwargs(params, *, kwargs):
    for key, exp in kwargs.items():
        ret = getattr(params, key)
        if isinstance(exp, float):
            assert ret == approx(exp), f'{key}: expected {exp}, got {ret}'
        else:
            assert ret == exp, f'{key}: expected {exp}, got {ret}'


def assert_params_round_trip_equal(*, pycls, kwargs):
    obj = PSMethod.FromMethodID(pycls._id)

    params = pycls(**kwargs)
    params._update_psmethod(obj=obj)

    new_params = pycls()
    new_params._update_params(obj=obj)

    assert_params_match_kwargs(new_params, kwargs=kwargs)


@pytest.fixture(scope='module')
def manager():
    with ps.connect() as mgr:
        logger.warning('Connected to %s' % mgr.instrument.id)
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
    pycls = ps.CyclicVoltammetry

    def test_params_round_trip(self):
        assert_params_round_trip_equal(
            pycls=self.pycls,
            kwargs=self.kwargs,
        )

    @pytest.mark.instrument
    def test_measurement(self, manager):
        method = self.pycls(
            current_range=ps.settings.CurrentRange(
                max=ps.settings.CURRENT_RANGE.cr_1_mA,
                min=ps.settings.CURRENT_RANGE.cr_100_nA,
                start=ps.settings.CURRENT_RANGE.cr_100_uA,
            ),
            **self.kwargs,
        )
        measurement = manager.measure(method)

        assert measurement
        assert isinstance(measurement, ps.data.Measurement)
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


class TestFCV:
    kwargs = {
        'begin_potential': -1,
        'vertex1_potential': -1,
        'vertex2_potential': 1,
        'step_potential': 0.25,
        'scanrate': 500,
        'n_scans': 3,
        'n_avg_scans': 2,
        'n_equil_scans': 2,
    }
    pycls = ps.FastCyclicVoltammetry

    def test_params_round_trip(self):
        assert_params_round_trip_equal(
            pycls=self.pycls,
            kwargs=self.kwargs,
        )

    @pytest.mark.xfail(raises=AssertionError, reason='FCV only returns 1 scan with nScans>1')
    @pytest.mark.instrument
    def test_measurement(self, manager):
        method = self.pycls(
            current_range=ps.settings.CURRENT_RANGE.cr_10_uA,
            **self.kwargs,
        )
        measurement = manager.measure(method)

        assert measurement
        assert isinstance(measurement, ps.data.Measurement)
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


class TestLSV:
    kwargs = {
        'begin_potential': -1.0,
        'end_potential': 1.0,
        'step_potential': 0.1,
        'scanrate': 2.0,
    }
    pycls = ps.LinearSweepVoltammetry

    def test_params_round_trip(self):
        assert_params_round_trip_equal(
            pycls=self.pycls,
            kwargs=self.kwargs,
        )

    @pytest.mark.instrument
    def test_measurement(self, manager):
        method = self.pycls(
            current_range=ps.settings.CurrentRange(
                max=ps.settings.CURRENT_RANGE.cr_1_mA,
                min=ps.settings.CURRENT_RANGE.cr_100_nA,
                start=ps.settings.CURRENT_RANGE.cr_100_uA,
            ),
            **self.kwargs,
        )
        measurement = manager.measure(method)

        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

        dataset = measurement.dataset
        assert len(dataset) == 4

        assert dataset.array_names == {'charge', 'potential', 'current', 'time'}
        assert dataset.array_quantities == {'Charge', 'Current', 'Potential', 'Time'}


class TestACV:
    kwargs = {
        'begin_potential': -0.15,
        'end_potential': 0.15,
        'step_potential': 0.05,
        'ac_potential': 0.25,
        'frequency': 200.0,
        'scanrate': 0.2,
    }
    pycls = ps.ACVoltammetry

    def test_params_round_trip(self):
        assert_params_round_trip_equal(
            pycls=self.pycls,
            kwargs=self.kwargs,
        )

    @pytest.mark.instrument
    def test_measurement(self, manager):
        method = self.pycls(
            current_range=ps.settings.CurrentRange(
                max=ps.settings.CURRENT_RANGE.cr_1_mA,
                min=ps.settings.CURRENT_RANGE.cr_100_nA,
                start=ps.settings.CURRENT_RANGE.cr_100_uA,
            ),
            **self.kwargs,
        )
        measurement = manager.measure(method)

        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

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
    pycls = ps.SquareWaveVoltammetry

    def test_params_round_trip(self):
        assert_params_round_trip_equal(
            pycls=self.pycls,
            kwargs=self.kwargs,
        )

    @pytest.mark.instrument
    def test_measurement(self, manager):
        method = self.pycls(
            current_range=ps.settings.CurrentRange(
                max=ps.settings.CURRENT_RANGE.cr_1_mA,
                min=ps.settings.CURRENT_RANGE.cr_100_nA,
                start=ps.settings.CURRENT_RANGE.cr_100_uA,
            ),
            **self.kwargs,
        )
        measurement = manager.measure(method)

        assert measurement
        assert isinstance(measurement, ps.data.Measurement)
        assert measurement.method.psmethod.nScans == 1

        dataset = measurement.dataset
        assert len(dataset) == 5

        assert dataset.array_names == {'potential', 'current', 'time', 'reverse', 'forward'}
        assert dataset.array_quantities == {'Current', 'Potential', 'Time'}


class TestCP:
    kwargs = {
        'current': 0.0,
        'applied_current_range': ps.settings.CURRENT_RANGE.cr_100_uA,
        'interval_time': 0.1,
        'run_time': 1.0,
    }
    pycls = ps.ChronoPotentiometry

    def test_params_round_trip(self):
        assert_params_round_trip_equal(
            pycls=self.pycls,
            kwargs=self.kwargs,
        )

    @pytest.mark.instrument
    def test_measurement(self, manager):
        method = self.pycls(
            potential_range=ps.settings.PotentialRange(
                max=ps.settings.POTENTIAL_RANGE.pr_1_V,
                min=ps.settings.POTENTIAL_RANGE.pr_10_mV,
                start=ps.settings.POTENTIAL_RANGE.pr_1_V,
            ),
            **self.kwargs,
        )
        measurement = manager.measure(method)

        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

        dataset = measurement.dataset
        assert len(dataset) == 4

        assert dataset.array_names == {'potential', 'current', 'time', 'charge'}
        assert dataset.array_quantities == {'Current', 'Potential', 'Time', 'Charge'}


class TestSCP:
    kwargs = {
        'current': 0.1,
        'applied_current_range': ps.settings.CURRENT_RANGE.cr_100_uA,
        'measurement_time': 0.2,
    }
    pycls = ps.StrippingChronoPotentiometry

    def test_params_round_trip(self):
        assert_params_round_trip_equal(
            pycls=self.pycls,
            kwargs=self.kwargs,
        )

    @pytest.mark.xfail(
        raises=System.NotImplementedException,
        reason='Not all devices support SCP.',
    )
    @pytest.mark.instrument
    def test_measurement(self, manager):
        method = self.pycls(
            potential_range=ps.settings.PotentialRange(
                max=ps.settings.POTENTIAL_RANGE.pr_1_V,
                min=ps.settings.POTENTIAL_RANGE.pr_10_mV,
                start=ps.settings.POTENTIAL_RANGE.pr_1_V,
            ),
            **self.kwargs,
        )
        measurement = manager.measure(method)

        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

        dataset = measurement.dataset
        assert len(dataset) == 4

        assert dataset.array_names == {'potential', 'current', 'time', 'charge'}
        assert dataset.array_quantities == {'Current', 'Potential', 'Time', 'Charge'}


class TestLSP:
    kwargs = {
        'applied_current_range': ps.settings.CURRENT_RANGE.cr_100_uA,
        'current_step': 0.1,
        'scan_rate': 8.0,
    }
    pycls = ps.LinearSweepPotentiometry

    def test_params_round_trip(self):
        assert_params_round_trip_equal(
            pycls=self.pycls,
            kwargs=self.kwargs,
        )

    @pytest.mark.instrument
    def test_measurement(self, manager):
        method = self.pycls(
            potential_range=ps.settings.PotentialRange(
                max=ps.settings.POTENTIAL_RANGE.pr_1_V,
                min=ps.settings.POTENTIAL_RANGE.pr_10_mV,
                start=ps.settings.POTENTIAL_RANGE.pr_1_V,
            ),
            **self.kwargs,
        )
        measurement = manager.measure(method)

        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

        dataset = measurement.dataset
        assert len(dataset) == 4

        assert dataset.array_names == {'potential', 'current', 'time', 'charge'}
        assert dataset.array_quantities == {'Current', 'Potential', 'Time', 'Charge'}


class TestOCP:
    kwargs = {
        'interval_time': 0.1,
        'run_time': 1.0,
    }
    pycls = ps.OpenCircuitPotentiometry

    def test_params_round_trip(self):
        assert_params_round_trip_equal(
            pycls=self.pycls,
            kwargs=self.kwargs,
        )

    @pytest.mark.instrument
    def test_measurement(self, manager):
        method = self.pycls(
            potential_range=ps.settings.PotentialRange(
                max=ps.settings.POTENTIAL_RANGE.pr_1_V,
                min=ps.settings.POTENTIAL_RANGE.pr_10_mV,
                start=ps.settings.POTENTIAL_RANGE.pr_1_V,
            ),
            **self.kwargs,
        )
        measurement = manager.measure(method)

        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

        dataset = measurement.dataset
        assert len(dataset) == 2

        assert dataset.array_names == {'potential', 'time'}
        assert dataset.array_quantities == {'Potential', 'Time'}


class TestCA:
    kwargs = {
        'interval_time': 0.1,
        'run_time': 1.0,
    }
    pycls = ps.ChronoAmperometry

    def test_params_round_trip(self):
        assert_params_round_trip_equal(
            pycls=self.pycls,
            kwargs=self.kwargs,
        )

    @pytest.mark.instrument
    def test_measurement(self, manager):
        method = self.pycls(**self.kwargs)
        measurement = manager.measure(method)

        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

        dataset = measurement.dataset
        assert len(dataset) == 4

        assert dataset.array_names == {'potential', 'time', 'charge', 'current'}
        assert dataset.array_quantities == {'Potential', 'Time', 'Charge', 'Current'}


class TestFA:
    kwargs = {
        'interval_time': 0.1,
        'run_time': 1.0,
    }
    pycls = ps.FastAmperometry

    def test_params_round_trip(self):
        assert_params_round_trip_equal(
            pycls=self.pycls,
            kwargs=self.kwargs,
        )

    @pytest.mark.instrument
    def test_measurement(self, manager):
        method = self.pycls(**self.kwargs)
        measurement = manager.measure(method)

        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

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
    pycls = ps.DifferentialPulseVoltammetry

    def test_params_round_trip(self):
        assert_params_round_trip_equal(
            pycls=self.pycls,
            kwargs=self.kwargs,
        )

    @pytest.mark.instrument
    def test_measurement(self, manager):
        method = self.pycls(**self.kwargs)
        measurement = manager.measure(method)

        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

        dataset = measurement.dataset
        assert len(dataset) == 3

        assert dataset.array_names == {'potential', 'time', 'current'}
        assert dataset.array_quantities == {'Potential', 'Time', 'Current'}


class TestPAD:
    kwargs = {
        'potential': 0.5,
        'pulse_potential': 1.0,
        'pulse_time': 0.1,
        'mode': 'pulse',
        'run_time': 1.0,
        'interval_time': 0.2,
    }
    pycls = ps.PulsedAmperometricDetection

    def test_params_round_trip(self):
        assert_params_round_trip_equal(
            pycls=self.pycls,
            kwargs=self.kwargs,
        )

    @pytest.mark.instrument
    def test_measurement(self, manager):
        method = self.pycls(**self.kwargs)
        measurement = manager.measure(method)

        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

        dataset = measurement.dataset
        assert len(dataset) == 3

        assert dataset.array_names == {'potential', 'time', 'current'}
        assert dataset.array_quantities == {'Potential', 'Time', 'Current'}


class TestNPV:
    kwargs = {
        'begin_potential': -0.4,
        'end_potential': 0.4,
        'step_potential': 0.15,
        'pulse_time': 0.1,
        'scan_rate': 0.5,
    }
    pycls = ps.NormalPulseVoltammetry

    def test_params_round_trip(self):
        assert_params_round_trip_equal(
            pycls=self.pycls,
            kwargs=self.kwargs,
        )

    @pytest.mark.instrument
    def test_measurement(self, manager):
        method = self.pycls(**self.kwargs)
        measurement = manager.measure(method)

        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

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
            ps.settings.ELevel(level=0.5, duration=0.1),
            ps.settings.ELevel(level=0.3, duration=0.2),
        ],
    }
    pycls = ps.MultiStepAmperometry

    def test_params_round_trip(self):
        assert_params_round_trip_equal(
            pycls=self.pycls,
            kwargs=self.kwargs,
        )

    @pytest.mark.instrument
    def test_measurement(self, manager):
        method = self.pycls(**self.kwargs)
        measurement = manager.measure(method)

        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

        dataset = measurement.dataset
        assert len(dataset) == 4

        assert dataset.array_names == {
            'potential',
            'time',
            'current',
            'charge',
        }
        assert dataset.array_quantities == {'Charge', 'Potential', 'Time', 'Current'}


class TestMP:
    kwargs = {
        'interval_time': 0.01,
        'n_cycles': 2,
        'levels': [
            ps.settings.ILevel(level=0.5, duration=0.1),
            ps.settings.ILevel(level=0.3, duration=0.2),
        ],
    }
    pycls = ps.MultiStepPotentiometry

    def test_params_round_trip(self):
        assert_params_round_trip_equal(
            pycls=self.pycls,
            kwargs=self.kwargs,
        )

    @pytest.mark.instrument
    def test_measurement(self, manager):
        method = self.pycls(**self.kwargs)
        measurement = manager.measure(method)

        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

        dataset = measurement.dataset
        assert len(dataset) == 4

        assert dataset.array_names == {
            'potential',
            'time',
            'current',
            'charge',
        }
        assert dataset.array_quantities == {'Charge', 'Potential', 'Time', 'Current'}


class TestCC:
    kwargs = {
        'equilibration_time': 0.0,
        'interval_time': 0.01,
        'step1_run_time': 0.1,
        'step2_run_time': 0.2,
    }
    pycls = ps.ChronoCoulometry

    def test_params_round_trip(self):
        assert_params_round_trip_equal(
            pycls=self.pycls,
            kwargs=self.kwargs,
        )

    @pytest.mark.instrument
    def test_measurement(self, manager):
        method = self.pycls(**self.kwargs)
        measurement = manager.measure(method)

        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

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
    pycls = ps.ElectrochemicalImpedanceSpectroscopy

    def test_params_round_trip(self):
        assert_params_round_trip_equal(
            pycls=self.pycls,
            kwargs=self.kwargs,
        )

    @pytest.mark.instrument
    def test_measurement(self, manager):
        method = self.pycls(**self.kwargs)
        measurement = manager.measure(method)

        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

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


class TestFIS:
    kwargs = {
        'frequency': 40000,
        'run_time': 0.5,
    }
    pycls = ps.FastImpedanceSpectroscopy

    def test_params_round_trip(self):
        assert_params_round_trip_equal(
            pycls=self.pycls,
            kwargs=self.kwargs,
        )

    @pytest.mark.instrument
    def test_measurement(self, manager):
        method = self.pycls(**self.kwargs)
        measurement = manager.measure(method)

        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

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
        'applied_current_range': ps.settings.CURRENT_RANGE.cr_10_uA,
        'equilibration_time': 0.0,
        'n_frequencies': 7,
        'max_frequency': 1e5,
        'min_frequency': 1e3,
    }
    pycls = ps.GalvanostaticImpedanceSpectroscopy

    def test_params_round_trip(self):
        assert_params_round_trip_equal(
            pycls=self.pycls,
            kwargs=self.kwargs,
        )

    @pytest.mark.instrument
    def test_measurement(self, manager):
        method = self.pycls(**self.kwargs)
        measurement = manager.measure(method)

        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

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


class TestFGIS:
    kwargs = {
        'applied_current_range': ps.settings.CURRENT_RANGE.cr_10_uA,
        'run_time': 0.3,
    }
    pycls = ps.FastGalvanostaticImpedanceSpectroscopy

    def test_params_round_trip(self):
        assert_params_round_trip_equal(
            pycls=self.pycls,
            kwargs=self.kwargs,
        )

    @pytest.mark.instrument
    def test_measurement(self, manager):
        method = self.pycls(**self.kwargs)
        measurement = manager.measure(method)

        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

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
    pycls = ps.MethodScript

    def test_params_round_trip(self):
        assert_params_round_trip_equal(
            pycls=self.pycls,
            kwargs=self.kwargs,
        )

    @pytest.mark.instrument
    def test_measurement(self, manager):
        method = self.pycls(**self.kwargs)
        measurement = manager.measure(method)

        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

        dataset = measurement.dataset
        assert len(dataset) == 2

        assert dataset.array_names == {'AppliedPotential1_1', 'Current1_1'}
        assert dataset.array_quantities == {'Current', 'Potential'}


class TestMM:
    kwargs = {
        'cycles': 2,
        'interval_time': 0.02,
        'stages': [
            ps.mixed_mode.ConstantE(
                run_time=0.1,
                potential=0.5,
            ),
            ps.mixed_mode.ConstantI(
                run_time=0.1,
                current=1.0,
                applied_current_range=ps.settings.CURRENT_RANGE.cr_100_nA,
            ),
            ps.mixed_mode.SweepE(
                begin_potential=-0.5,
                end_potential=0.5,
                step_potential=0.25,
                scanrate=20.0,
            ),
            ps.mixed_mode.OpenCircuit(
                run_time=0.1,
            ),
            ps.mixed_mode.Impedance(
                frequency=50000,
                ac_potential=0.01,
                dc_potential=0.0,
                run_time=0.1,
                min_sampling_time=0.0,
            ),
        ],
    }
    pycls = ps.mixed_mode.MixedMode

    def test_params_round_trip(self):
        assert_params_round_trip_equal(
            pycls=self.pycls,
            kwargs=self.kwargs,
        )

    @pytest.mark.instrument
    def test_measurement(self, manager):
        method = self.pycls(**self.kwargs)
        measurement = manager.measure(method)

        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

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
