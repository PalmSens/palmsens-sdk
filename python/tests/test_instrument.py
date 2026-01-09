from __future__ import annotations

import asyncio
import warnings
from dataclasses import dataclass
from itertools import groupby

import pytest
from PalmSens.Comm import enumDeviceType

import pypalmsens as ps
from pypalmsens._instruments.shared import firmware_warning
from pypalmsens.data import Measurement


@dataclass
class MockCapabilities:
    DeviceType: str
    FirmwareVersion: float
    MinFirmwareVersionRequired: float


@pytest.mark.parametrize(
    'cap',
    (
        MockCapabilities(
            DeviceType=enumDeviceType.Unknown,
            FirmwareVersion=0.0,
            MinFirmwareVersionRequired=1.2,
        ),
        MockCapabilities(
            DeviceType=enumDeviceType.PalmSens4,
            FirmwareVersion=1.9,
            MinFirmwareVersionRequired=1.9,
        ),
        MockCapabilities(
            DeviceType=enumDeviceType.PalmSens4,
            FirmwareVersion=2.8,
            MinFirmwareVersionRequired=1.9,
        ),
        MockCapabilities(
            DeviceType=enumDeviceType.EmStat4HR,
            FirmwareVersion=1.307,
            MinFirmwareVersionRequired=1.301,
        ),
        MockCapabilities(
            DeviceType=enumDeviceType.EmStat4HR,
            FirmwareVersion=1.401,
            MinFirmwareVersionRequired=1.307,
        ),
    ),
)
def test_firmware_warning_ok(cap):
    with warnings.catch_warnings():
        warnings.simplefilter('error')
        firmware_warning(cap)


@pytest.mark.parametrize(
    'cap',
    (
        MockCapabilities(
            DeviceType=enumDeviceType.PalmSens4,
            FirmwareVersion=1.2,
            MinFirmwareVersionRequired=1.9,
        ),
        MockCapabilities(
            DeviceType=enumDeviceType.PalmSens4,
            FirmwareVersion=2.8,
            MinFirmwareVersionRequired=3.1,
        ),
        MockCapabilities(
            DeviceType=enumDeviceType.EmStat4HR,
            FirmwareVersion=1.207,
            MinFirmwareVersionRequired=1.307,
        ),
        MockCapabilities(
            DeviceType=enumDeviceType.EmStat4HR,
            FirmwareVersion=1.307,
            MinFirmwareVersionRequired=1.401,
        ),
    ),
)
def test_firmware_warning_fail(cap):
    with pytest.warns(UserWarning):
        firmware_warning(cap)


@pytest.mark.instrument
def test_connect():
    with ps.connect() as manager:
        assert isinstance(manager, ps.InstrumentManager)


@pytest.mark.instrument
@pytest.mark.asyncio
async def test_connect_async():
    async with await ps.connect_async() as manager:
        assert isinstance(manager, ps.InstrumentManagerAsync)


@pytest.mark.instrument
def test_measure():
    method = ps.LinearSweepVoltammetry(
        begin_potential=0.0,
        end_potential=0.5,
        step_potential=0.1,
        scanrate=10.0,
    )
    measurement = ps.measure(method)
    assert isinstance(measurement, Measurement)


@pytest.mark.instrument
@pytest.mark.asyncio
async def test_measure_async():
    method = ps.LinearSweepVoltammetry(
        begin_potential=0.0,
        end_potential=0.5,
        step_potential=0.1,
        scanrate=10.0,
    )
    measurement = await ps.measure_async(method)
    assert isinstance(measurement, Measurement)


@pytest.mark.instrument
def test_discover():
    instruments = ps.discover()
    assert len(instruments) >= 0


@pytest.mark.instrument
@pytest.mark.asyncio
async def test_discover_async():
    instruments = await ps.discover_async()
    assert len(instruments) >= 0


@pytest.mark.instrument
@pytest.mark.asyncio
async def test_idle_status_callback_async():
    points = []

    def callback(status):
        points.append(status)

    async with await ps.connect_async() as manager:
        manager.register_status_callback(callback)

        await asyncio.sleep(1)

        method = ps.ChronoAmperometry(
            pretreatment=ps.settings.Pretreatment(
                conditioning_time=0.3,
                deposition_time=0.3,
            ),
            interval_time=0.02,
            potential=1.0,
            run_time=0.1,
        )
        _ = await manager.measure(method)
        await asyncio.sleep(1)

        manager.unregister_status_callback()

    assert len(points) == 6

    assert [_[0] for _ in groupby(points, key=lambda _: _.device_state)] == [
        'Idle',
        'Pretreatment',
        'Idle',
    ]
    assert [_[0] for _ in groupby(points, key=lambda _: _.pretreatment_phase)] == [
        'None',
        'Conditioning',
        'Depositing',
        'None',
    ]

    for point in points:
        assert isinstance(point.current, float)
        assert isinstance(point.potential, float)
        assert isinstance(point.current_we2, float)
