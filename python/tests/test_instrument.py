from __future__ import annotations

import warnings
from dataclasses import dataclass

import pytest
from PalmSens.Comm import enumDeviceType

import pypalmsens as ps
from pypalmsens._instruments._common import firmware_warning
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
