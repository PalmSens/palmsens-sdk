"""This module contains the public api for classes representing measurement data."""

from __future__ import annotations

from ._data.curve import Curve
from ._data.data_array import CurrentArray, DataArray, PotentialArray
from ._data.data_value import CurrentReading, PotentialReading
from ._data.dataset import DataSet
from ._data.eisdata import EISData
from ._data.measurement import DeviceInfo, Measurement
from ._data.peak import Peak
from ._data.shared import ArrayType
from ._instruments.callback import (
    CallbackData,
    CallbackDataEIS,
    Status,
)

__all__ = [
    'ArrayType',
    'CallbackData',
    'CallbackDataEIS',
    'CurrentArray',
    'CurrentReading',
    'Curve',
    'DataArray',
    'DataSet',
    'DeviceInfo',
    'EISData',
    'Measurement',
    'Peak',
    'PotentialArray',
    'PotentialReading',
    'Status',
]
