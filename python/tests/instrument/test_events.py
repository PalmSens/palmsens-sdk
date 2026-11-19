from __future__ import annotations

import logging

import pytest

import pypalmsens as ps
from pypalmsens.data import DataArray, DataSet

logger = logging.getLogger(__name__)


@pytest.fixture(scope='module')
def manager():
    instrument, *_ = ps.discover()
    with ps.connect(instrument) as mgr:
        logger.warning('Connected to %s', mgr.instrument.id)
        yield mgr


@pytest.mark.instrument
def test_callback(manager):
    points = []

    def callback(data):
        points.append(data)

    params = ps.LinearSweepVoltammetry(scanrate=1)
    _ = manager.measure(params, callback=callback)

    assert len(points) == 11

    point = points[-1]
    assert point.start == 10

    assert isinstance(point.x_array, DataArray)
    assert point.x_array.name == 'potential'
    assert len(point.x_array) == 11

    assert isinstance(point.y_array, DataArray)
    assert point.y_array.name == 'current'
    assert len(point.y_array) == 11

    assert len(list(points[0].new_datapoints())) == 11


@pytest.mark.instrument
def test_callback_eis(manager):
    points = []

    def callback(data):
        points.append(data)

    params = ps.ElectrochemicalImpedanceSpectroscopy(
        frequency_type='fixed',
        scan_type='fixed',
    )
    _ = manager.measure(params, callback=callback)

    assert len(points) == 1

    point = points[0]

    assert point.start == 0
    assert isinstance(point.data, DataSet)
    assert point.data.n_points == 1

    assert len(list(points[0].new_datapoints())) == 1


@pytest.mark.instrument
@pytest.mark.parametrize(
    'method,event_names',
    [
        (
            ps.ElectrochemicalImpedanceSpectroscopy(scan_type='fixed', frequency_type='fixed'),
            (
                'eis_data_begin',
                'eis_new_data',
                'eis_data_end',
            ),
        ),
        (
            ps.ChronoAmperometry(run_time=0.1, interval_time=0.01),
            (
                'measurement_begin',
                'measurement_end',
                'curve_begin',
                'curve_new_data',
                'curve_end',
                'measurement_setup',
                'measurement_teardown',
            ),
        ),
        (
            ps.ChronoAmperometry(run_time=0.1, interval_time=0.01),
            (
                'curve_begin',
                'curve_end',
            ),
        ),
        (
            ps.ElectrochemicalImpedanceSpectroscopy(scan_type='fixed', frequency_type='fixed'),
            (
                'eis_data_begin',
                'eis_data_end',
            ),
        ),
    ],
)
def test_on_event(manager, method, event_names):
    triggered = set()

    def make_callback(event_name: str):
        def _callback(*args):
            triggered.add(event_name)

        return _callback

    handles = []

    for event_name in event_names:
        on = getattr(manager, f'on_{event_name}')
        handle = on(make_callback(event_name))
        assert event_name in manager._listeners
        handles.append(handle)

    _ = manager.measure(method)

    for handle in handles:
        handle.cancel()

    assert set(event_names) == triggered
