from __future__ import annotations

import logging

import pytest
from helpers.technique_specs import TECHNIQUE_SPECS
from pydantic import ValidationError

import pypalmsens as ps
from pypalmsens._instruments.shared import MethodIncompatibleError

logger = logging.getLogger(__name__)


@pytest.fixture(scope='module')
def manager():
    instrument, *_ = ps.discover()
    with ps.connect(instrument) as mgr:
        logger.warning('Connected to %s', mgr.instrument.id)
        yield mgr


def test_get_instrument_serial(manager):
    val = manager.get_instrument_serial()
    assert val
    assert isinstance(val, str)


def test_status(manager):
    status = manager.status()
    assert status.device_state == 'Idle'


def test_cell_on(manager):
    assert not manager.is_cell_on()
    manager.set_cell(True)
    assert manager.is_cell_on()
    manager.set_cell(False)
    assert not manager.is_cell_on()


def test_read_current(manager):
    assert not manager.is_cell_on()
    manager.set_cell(True)
    assert manager.is_cell_on()

    manager.set_current_range('1uA')
    val1 = manager.read_current()
    manager.set_current(0.1)
    cr1 = manager.get_current_range()
    assert val1 is not None
    assert cr1 == '1uA'

    manager.set_current_range('10uA')
    val2 = manager.read_current()
    manager.set_current(0.1)
    cr2 = manager.get_current_range()
    assert val2 is not None
    assert cr2 == '10uA'

    assert manager.get_mode() == 'galvanostatic'
    manager.set_mode('potentiostatic')

    manager.set_cell(False)
    assert not manager.is_cell_on()


def test_read_potential(manager):
    manager.set_cell(True)

    manager.set_potential_range('100mV')
    manager.set_potential(1)
    val1 = manager.read_potential()
    pr1 = manager.get_potential_range()
    assert val1 is not None
    assert pr1 == '100mV'

    manager.set_potential_range('1V')
    manager.set_potential(0)
    val2 = manager.read_potential()
    pr2 = manager.get_potential_range()
    assert val2 is not None
    assert pr2 == '1V'

    assert manager.get_mode() == 'potentiostatic'

    manager.set_cell(False)


def test_set_mode(manager):
    manager.set_cell(True)
    for mode in ['galvanostatic', 'potentiostatic', 'galvanostatic']:
        manager.set_mode(mode)
        assert manager.get_mode() == mode

    manager.set_mode('potentiostatic')
    manager.set_cell(False)


def test_forbid_extra_keys():
    with pytest.raises(ValidationError):
        _ = ps.CyclicVoltammetry(foo=123, bar=678)


class CV:
    method = TECHNIQUE_SPECS['cv']

    @staticmethod
    def validate(measurement):
        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

        for curve in measurement.curves:
            assert curve.n_points >= 5

        assert measurement._inner.Method.nScans == 2

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
    method = TECHNIQUE_SPECS['fcv']

    @staticmethod
    def validate(measurement):
        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

        for curve in measurement.curves:
            assert curve.n_points >= 5

        assert measurement._inner.Method.nScans == 3
        assert measurement._inner.Method.nAvgScans == 2
        assert measurement._inner.Method.nEqScans == 2

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
    method = TECHNIQUE_SPECS['lsv']

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
    method = TECHNIQUE_SPECS['lsv_aux']

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
    method = TECHNIQUE_SPECS['acv']

    @staticmethod
    def validate(measurement):
        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

        for curve in measurement.curves:
            assert curve.n_points >= 3

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
    method = TECHNIQUE_SPECS['swv']

    @staticmethod
    def validate(measurement):
        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

        for curve in measurement.curves:
            assert curve.n_points >= 5

        assert measurement._inner.Method.nScans == 1

        dataset = measurement.dataset
        assert len(dataset) == 5

        assert dataset.array_names == {'potential', 'current', 'time', 'reverse', 'forward'}
        assert dataset.array_quantities == {'Current', 'Potential', 'Time'}


class CP:
    method = TECHNIQUE_SPECS['cp']

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
    method = TECHNIQUE_SPECS['scp']

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
    method = TECHNIQUE_SPECS['lsp']

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
    method = TECHNIQUE_SPECS['ocp']

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
    method = TECHNIQUE_SPECS['ca']

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
    method = TECHNIQUE_SPECS['fam']

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
    method = TECHNIQUE_SPECS['dpv']

    @staticmethod
    def validate(measurement):
        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

        for curve in measurement.curves:
            assert curve.n_points >= 3

        dataset = measurement.dataset
        assert len(dataset) == 3

        assert dataset.array_names == {'potential', 'time', 'current'}
        assert dataset.array_quantities == {'Potential', 'Time', 'Current'}


class PAD:
    method = TECHNIQUE_SPECS['pad']

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
    method = TECHNIQUE_SPECS['mpad']

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
    method = TECHNIQUE_SPECS['npv']

    @staticmethod
    def validate(measurement):
        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

        for curve in measurement.curves:
            assert curve.n_points >= 2

        dataset = measurement.dataset
        assert len(dataset) == 3

        assert dataset.array_names == {'potential', 'time', 'current'}
        assert dataset.array_quantities == {'Potential', 'Time', 'Current'}


class MA:
    method = TECHNIQUE_SPECS['ma']

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
    method = TECHNIQUE_SPECS['mp']

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
    method = TECHNIQUE_SPECS['cc']

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
    method = TECHNIQUE_SPECS['eis']

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
    method = TECHNIQUE_SPECS['eis_pot_fixed']

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
    method = TECHNIQUE_SPECS['eis_pot_scan']

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
    method = TECHNIQUE_SPECS['eis_time_fixed']

    @staticmethod
    def validate(measurement):
        check_eis_measurement(measurement)

        eis_datas = measurement.eis_data
        assert len(eis_datas) == 1
        for eis_data in eis_datas:
            # n_points is tricky to reproduce because of device specific timings?
            assert eis_data.n_points > 1
            assert eis_data.n_subscans == 0
            assert eis_data.n_frequencies == 1


class EIS_time_scan:
    method = TECHNIQUE_SPECS['eis_time_scan']

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
    method = TECHNIQUE_SPECS['eis_single_point']

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
    method = TECHNIQUE_SPECS['fis']

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
    method = TECHNIQUE_SPECS['gis']

    @staticmethod
    def validate(measurement):
        check_eis_measurement(measurement)

        eis_datas = measurement.eis_data
        assert len(eis_datas) == 1
        for eis_data in eis_datas:
            assert eis_data.n_points == 5
            assert eis_data.n_subscans == 0
            assert eis_data.n_frequencies == 10


class GIS_cur_fixed:
    method = TECHNIQUE_SPECS['gis_cur_fixed']

    @staticmethod
    def validate(measurement):
        check_eis_measurement(measurement)

        eis_datas = measurement.eis_data
        assert len(eis_datas) == 1
        for eis_data in eis_datas:
            assert eis_data.n_points == 2
            assert eis_data.n_subscans == 0
            assert eis_data.n_frequencies == 1


class GIS_cur_scan:
    method = TECHNIQUE_SPECS['gis_cur_scan']

    @staticmethod
    def validate(measurement):
        check_eis_measurement(measurement)

        eis_datas = measurement.eis_data
        assert len(eis_datas) == 1
        for eis_data in eis_datas:
            assert eis_data.n_points == 6
            assert eis_data.n_subscans == 2
            assert eis_data.n_frequencies == 3


class GIS_time_fixed:
    method = TECHNIQUE_SPECS['gis_time_fixed']

    @staticmethod
    def validate(measurement):
        check_eis_measurement(measurement)

        eis_datas = measurement.eis_data
        assert len(eis_datas) == 1
        for eis_data in eis_datas:
            # n_points is tricky to reproduce because of device specific timings?
            assert eis_data.n_points > 1
            assert eis_data.n_subscans == 0
            assert eis_data.n_frequencies == 1


class GIS_time_scan:
    method = TECHNIQUE_SPECS['gis_time_scan']

    @staticmethod
    def validate(measurement):
        check_eis_measurement(measurement)

        eis_datas = measurement.eis_data
        assert len(eis_datas) == 1
        for eis_data in eis_datas:
            assert eis_data.n_points == 6
            assert eis_data.n_subscans == 2
            assert eis_data.n_frequencies == 3


class GIS_single_point:
    method = TECHNIQUE_SPECS['gis_single_point']

    @staticmethod
    def validate(measurement):
        check_eis_measurement(measurement)

        eis_datas = measurement.eis_data
        assert len(eis_datas) == 1
        for eis_data in eis_datas:
            assert eis_data.n_points == 1
            assert eis_data.n_subscans == 0
            assert eis_data.n_frequencies == 1


class FGIS:
    method = TECHNIQUE_SPECS['fgis']

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
    method = TECHNIQUE_SPECS['ms']

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
    method = TECHNIQUE_SPECS['mm']

    @staticmethod
    def validate(measurement):
        assert measurement
        assert isinstance(measurement, ps.data.Measurement)

        method = measurement.method
        stages = [stage.stage_type for stage in method.stages]

        assert stages == ['ConstantE', 'ConstantI', 'SweepE', 'OpenCircuit', 'Impedance']

        for curve in measurement.curves:
            assert curve.n_points >= 5

        dataset = measurement.dataset

        assert len(dataset) == 4

        assert dataset.array_names == {'charge', 'current', 'potential', 'time'}
        assert dataset.array_quantities == {'Charge', 'Current', 'Potential', 'Time'}

        eis = measurement.eis_data
        assert len(eis) == 3

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


@pytest.mark.parametrize(
    'case',
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
def test_measure(manager, case):
    method = case.method

    try:
        measurement = manager.measure(method)
    except MethodIncompatibleError as exc:
        message = str(exc)
        if (
            ('is not supported by this device.' in message)
            or ('Fast Impedance techniques are only supported by' in message)
            or ('Fast Galvanostatic Impedance techniques are only supported by' in message)
        ):
            pytest.skip(f'{manager.instrument.name} does not support {method.id!r}')
        if 'Contact PalmSens BV or your local distributor to upgrade your license.' in message:
            pytest.skip(f'Unlicensed method: {method.id!r}')
        raise

    case.validate(measurement)
