from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime

import pytest

import pypalmsens as ps
from pypalmsens.data import Curve, DataArray, DataSet, Measurement


@pytest.fixture
def measurement(measurement_dpv):
    return measurement_dpv


def test_measurement_constructor():
    empty = Measurement()
    with pytest.raises(AttributeError):
        _ = empty.method
    assert not empty.dataset

    time = DataArray([1, 2, 3], array_type='Time')
    current = DataArray([10.1, 10.2, 10.3], array_type='Current')
    potential = DataArray([0.2, 0.3, 0.3], array_type='Potential')

    dataset = DataSet([time, current, potential])
    method = ps.CyclicVoltammetry()

    measurement = Measurement(dataset=dataset, method=method)

    assert measurement.title == 'Cyclic Voltammetry'
    assert measurement.method.id == 'cv'
    assert set(measurement.dataset) == {'Current', 'Potential', 'Time'}
    assert measurement.curves == []
    assert measurement.timestamp


def test_measurement_properties(measurement):
    assert measurement.title == 'Square Wave Voltammetry'
    assert isinstance(measurement.timestamp, datetime)
    assert measurement.metadata().timestamp == measurement.timestamp

    peaks = measurement.peaks
    assert len(peaks) == 0

    assert len(measurement.eis_fit) == 0

    curves = measurement.curves
    assert len(curves) == 1
    assert isinstance(curves[0], Curve)

    device = measurement.device
    with pytest.raises(FrozenInstanceError):
        device.type = 'foo'
