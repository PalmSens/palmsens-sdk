from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Literal, final

import PalmSens

if TYPE_CHECKING:
    from .instrument_manager import InstrumentManager


class GPIOError(ValueError): ...


class PinNotSupportedError(GPIOError): ...


def pins_to_bitmask(pins: Sequence[int]) -> int:
    """Convert a list of pin indices into a bitmask (integer)."""
    mask = 0
    for pin in pins:
        mask |= 1 << pin

    return mask


def bitmask_to_pins(mask: int) -> list[int]:
    """Convert a bitmask (integer) into a list pin indices."""
    return [i for i in range(8) if (mask & (1 << i))]


def is_methodscript(client_connection: PalmSens.Comm.ClientConnection) -> bool:
    return isinstance(client_connection, PalmSens.Comm.ClientConnectionMS)


def writable_pins(client_connection: PalmSens.Comm.ClientConnection) -> list[int]:
    """Return the pin numbers that support digital output.

    Returns
    -------
    list[int]
        Sorted list of pin numbers that can be used with
        `write`, `write_many`, `toggle`,
        and `toggle_many`.
    """
    if not is_methodscript(client_connection):
        raise GPIOError('Only supported on MethodSCRIPT devices.')
    mask = client_connection.Capabilities.SupportedDigitalOutputLineMask
    return bitmask_to_pins(mask)


def readable_pins(client_connection: PalmSens.Comm.ClientConnection) -> list[int]:
    """Return the pin numbers that support digital input.

    Returns
    -------
    list[int]
        Sorted list of pin numbers that can be used with
        `read` and `read_many`.
    """
    if not is_methodscript(client_connection):
        raise GPIOError('Only supported on MethodSCRIPT devices.')
    mask = client_connection.Capabilities.SupportedDigitalInputLineMask
    return bitmask_to_pins(mask)


def raise_if_pins_not_supported(
    client_connection: PalmSens.Comm.ClientConnection,
    pins: Sequence[int],
    mode: Literal['read', 'write'],
):
    if min(pins) < 0:
        raise PinNotSupportedError('Pin cannot be negative.')

    if is_methodscript(client_connection):
        pin_mask = pins_to_bitmask(pins)
        supported_mask = {
            'write': client_connection.Capabilities.SupportedDigitalOutputLineMask,
            'read': client_connection.Capabilities.SupportedDigitalInputLineMask,
        }[mode]

        if pin_mask & supported_mask:
            return
    else:
        if max(pins) < 4:
            return

    raise PinNotSupportedError(f'Requested {mode} pin is not supported by device.')


@final
class GPIO:
    """Digital general-purpose input/output (GPIO) interface.

    This class provides high-level access to the instrument's digital
    pins. Pin numbering is hardware-specific. Consult the instrument
    manual for the physical mapping.

    Note that the pins are typically referred to as `d0` or `d3`.
    These correspond to pins 0 and 3 in this interface, respectively.

    For MethodSCRIPT devices, the underlying libraries auto-configures
    read/write direction on read/write instructions.

    For explicit control, use the low-level MethodSCRIPT primitives directly:

        - [pypalmsens.CommProtocol][]
        - [MethodSCRIPT manual](https://dev.palmsens.com/methodscript/latest/methodscript/methodscript_main.html)
    """

    def __init__(self, manager: InstrumentManager):
        self._manager = manager

    def read(self, pin: int) -> Literal['low', 'high']:
        """Read the logic level of a single digital input pin.

        The pin configuration is automatically switched to input if needed.

        Check your device documentation for the available input pins.

        Parameters
        ----------
        pin: integer
            Pin number to read.

        Returns
        -------
        level : {'low', 'high'}
            Current logic level of the requested pin.

        Raises
        ------
        PinNotSupportedError:
            If ``pin`` is not a supported input pin.
        """
        [level] = self.read_many([pin])
        return level

    def read_many(self, pins: Sequence[int]) -> list[Literal['low', 'high']]:
        """Read the logic levels of multiple digital input pins.

        Parameters
        ----------
        pins : Sequence[int]
            Pin numbers to read. The order is preserved in the
            returned values.

        Returns
        -------
        levels : list of {'low', 'high'}
            Logic levels corresponding to the requested ``pins``,
            in the same order.

        Raises
        ------
        PinNotSupportedError
            If any pin in ``pins`` is not a supported input pin.
        """
        raise_if_pins_not_supported(
            self._manager._comm.ClientConnection, pins=pins, mode='read'
        )

        mask = pins_to_bitmask(pins)

        with self._manager._lock():
            level_mask = self._manager._comm.ClientConnection.ReadDigitalLine(mask)

        levels = []
        for pin in pins:
            pin_mask = 1 << pin
            levels.append(pin_mask & level_mask == pin_mask)

        return [('low', 'high')[level] for level in levels]

    def _write_many(self, pins: Sequence[int], func: Callable[[int, int], int]):
        raise_if_pins_not_supported(
            self._manager._comm.ClientConnection, pins=pins, mode='write'
        )

        mask = pins_to_bitmask(pins)

        current = self._manager._comm.DigitalOutput

        level_mask = func(current, mask)

        with self._manager._lock():
            self._manager._comm.ClientConnection.SetDigitalOutput(level_mask)

    def write_many(self, pins: Sequence[int], level: Literal['low', 'high'] = 'high'):
        """Set the logic level of multiple digital output pins.

        Parameters
        ----------
        pins : Sequence[int]
            Pin numbers to write.
        level : {'low', 'high'}, optional
            Logic level to set on all specified pins.  Default is
            ``'high'``.

        Raises
        ------
        PinNotSupportedError
            If any pin in ``pins`` is not a supported output pin.
        """
        if level == 'high':

            def func(current: int, mask: int) -> int:
                return current | mask  # high

        elif level == 'low':

            def func(current: int, mask: int) -> int:
                return current & ~mask  # low

        else:
            raise ValueError("`level` must be one of 'low' or 'high'")

        return self._write_many(pins, func)

    def write(self, pin: int, level: Literal['low', 'high'] = 'high'):
        """Set the logic level of a single digital output pin.

        Parameters
        ----------
        pin : int
            Pin number to write.
        level : {'low', 'high'}, optional
            Logic level to set.  Default is ``'high'``.

        Raises
        ------
        PinNotSupportedError:
            If ``pin`` is not a supported input pin.
        """
        self.write_many([pin], level=level)

    def toggle(self, pin: int):
        """Invert the logic level of a single digital output pin.

        A ``high`` state becomes ``low`` and vice-versa.

        Parameters
        ----------
        pin : int
            Pin number to toggle.

        Returns
        -------
        None

        Raises
        ------
        PinNotSupportedError
            If ``pin`` is not a supported output pin.
        """
        return self.toggle_many([pin])

    def toggle_many(self, pins: Sequence[int]):
        """Invert the logic level of multiple digital output pins.

        Each pin is toggled independently: ``high`` becomes ``low``
        and ``low`` becomes ``high``.

        Parameters
        ----------
        pins : Sequence[int]
            Pin numbers to toggle.

        Raises
        ------
        PinNotSupportedError
            If any pin in ``pins`` is not a supported output pin.
        """

        def func(current: int, mask: int) -> int:
            return current ^ mask  # toggle

        return self._write_many(pins, func)

    @property
    def writable_pins(self) -> list[int]:
        """Return the pin numbers that support digital output.

        Returns
        -------
        list[int]
            Sorted list of pin numbers that can be used with
            `write`, `write_many`, `toggle`,
            and `toggle_many`.
        """
        return writable_pins(self._manager._comm.ClientConnection)

    @property
    def readable_pins(self) -> list[int]:
        """Return the pin numbers that support digital input.

        Returns
        -------
        list[int]
            Sorted list of pin numbers that can be used with
            `read` and `read_many`.
        """
        return readable_pins(self._manager._comm.ClientConnection)
