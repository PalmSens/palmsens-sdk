from __future__ import annotations

import warnings
from dataclasses import dataclass

import pytest
from PalmSens.Comm import enumDeviceType

from pypalmsens.instruments.common import firmware_warning


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
