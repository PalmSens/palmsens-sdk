from __future__ import annotations

import asyncio
import warnings
from math import floor
from typing import TYPE_CHECKING, TypeVar

import System
from PalmSens.Comm import enumDeviceType

from .. import __sdk_version__

if TYPE_CHECKING:
    from PalmSens.Devices import DeviceCapabilities


T = TypeVar('T')


class MethodIncompatibleError(ValueError): ...


def wrap_task(clr_task: System.Task[T]) -> asyncio.Future[T]:
    """Wrap a C# Task in an awaitable asyncio.Future."""
    loop = asyncio.get_running_loop()
    future = loop.create_future()

    def _clr_completed():
        if future.done():
            return
        if clr_task.IsFaulted:
            future.set_exception(clr_task.Exception.GetBaseException())
            return
        if clr_task.IsCanceled:
            _ = future.cancel()
            return
        try:
            result = clr_task.GetAwaiter().GetResult()
        except System.OperationCanceledException:
            _ = future.cancel()
        except System.Exception as e:
            future.set_exception(e)
        else:
            future.set_result(result)

    clr_task.GetAwaiter().OnCompleted(
        System.Action(lambda: loop.call_soon_threadsafe(_clr_completed))
    )

    def _py_cancelled(future: asyncio.Future[T]):
        if not future.cancelled() or clr_task.IsCompleted:
            return
        try:
            clr_task.Cancel()
        except System.InvalidOperationException:
            pass
        except Exception as e:  # noqa
            print('Could not cancel CLR task: %r', e)

    future.add_done_callback(_py_cancelled)
    return future


def firmware_warning(capabilities: DeviceCapabilities, /) -> None:
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
        not_supported = floor(firmware_version * 10) < floor(min_version * 10)
    else:
        return

    if not_supported:
        warnings.warn(
            (
                f'Device firmware: {firmware_version} on {device_type} '
                f'is not supported by SDK ({__sdk_version__}), '
                f'minimum required firmware version: {min_version}.\n\n'
                'Update the firmware using a recent version of PSTrace. '
                'See chapter "Updating firmware" in the user manual: '
                'https://www.palmsens.com/knowledgebase-article/pstrace-user-manual/'
            ),
            UserWarning,
            stacklevel=2,
        )
