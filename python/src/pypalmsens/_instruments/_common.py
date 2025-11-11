from __future__ import annotations

import asyncio
import warnings
from collections.abc import Sequence
from dataclasses import dataclass, field
from math import floor
from typing import TYPE_CHECKING, Any, Protocol

from PalmSens.Comm import enumDeviceType
from System import Action
from typing_extensions import override

from .. import __sdk_version__

if TYPE_CHECKING:
    from PalmSens.Devices import Device as PSDevice
    from PalmSens.Devices import PalmSensCapabilities


class Callback(Protocol):
    """Type signature for callback"""

    def __call__(self, new_data: Sequence[dict[str, Any]]): ...


def create_future(clr_task):
    loop = asyncio.get_running_loop()
    future = asyncio.Future()
    callback = Action(lambda: on_completion(future, loop, clr_task))

    clr_task.GetAwaiter().OnCompleted(callback)
    return future


def on_completion(future, loop, task):
    if task.IsFaulted:
        clr_error = task.Exception.GetBaseException()
        future.set_exception(clr_error)
    else:
        loop.call_soon_threadsafe(lambda: future.set_result(task.GetAwaiter().GetResult()))


def firmware_warning(capabilities: PalmSensCapabilities, /) -> None:
    """Raise warning if firmware is not supported."""

    device_type = capabilities.DeviceType
    firmware_version = capabilities.FirmwareVersion
    min_version = capabilities.MinFirmwareVersionRequired

    if not min_version:
        return

    if device_type in (
        enumDeviceType.PalmSens,
        enumDeviceType.EmStat1,
        enumDeviceType.EmStat2,
        enumDeviceType.PalmSens3,
        enumDeviceType.PalmSens4,
        enumDeviceType.EmStat2BP,
        enumDeviceType.EmStat3,
        enumDeviceType.EmStat3P,
        enumDeviceType.EmStat3BP,
    ):
        not_supported = firmware_version < (min_version - 0.01)
    elif device_type in (
        enumDeviceType.EmStatPico,
        enumDeviceType.EmStat4LR,
        enumDeviceType.EmStat4HR,
    ):
        not_supported = int(floor(firmware_version * 10)) < int(floor(min_version * 10))
    else:
        return

    if not_supported:
        warnings.warn(
            (
                f'Device firmware: {firmware_version} on {device_type} '
                f'is not supported by SDK ({__sdk_version__}), '
                f'minimum required firmware version: {min_version}'
            ),
            UserWarning,
            stacklevel=2,
        )


@dataclass
class Instrument:
    """Dataclass holding instrument info."""

    id: str = field(repr=False)
    """Device ID of the instrument."""
    name: str = field(init=False)
    """Name of the instrument."""
    channel: int = field(init=False, default=-1)
    """Channel index if part of a multichannel device.

    Returns -1 if instrument is not part of a multi-channel device."""
    interface: str
    """Type of the connection."""
    device: PSDevice = field(repr=False)
    """Device connection class."""

    def __post_init__(self):
        try:
            idx = self.id.index('CH')
        except ValueError:
            self.name = self.id
        else:
            ch_str = self.id[idx : idx + 5]
            self.channel = int(ch_str[2:])
            self.name = self.id[:idx]

    @override
    def __repr__(self):
        args = ''.join(
            (
                f'name={self.name!r}, ',
                f'channel={self.channel}, ' if self.channel > 0 else '',
                f'interface={self.interface!r}',
            )
        )

        return f'{self.__class__.__name__}({args})'
