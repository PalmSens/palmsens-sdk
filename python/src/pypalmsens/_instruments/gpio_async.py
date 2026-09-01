from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Literal, final

from .gpio import pins_to_bitmask, raise_if_pins_not_supported, readable_pins, writable_pins
from .shared import create_future

if TYPE_CHECKING:
    from .instrument_manager_async import InstrumentManagerAsync


@final
class GPIOAsync:
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

    def __init__(self, manager: InstrumentManagerAsync):
        self._manager = manager

    async def read(self, pin: int) -> Literal['low', 'high']:
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
        [level] = await self.read_many([pin])
        return level

    async def read_many(self, pins: Sequence[int]) -> list[Literal['low', 'high']]:
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

        async with self._manager._lock():
            level_mask: int = await create_future(
                self._manager._comm.ClientConnection.ReadDigitalLineAsync(mask)
            )

        levels = []
        for pin in pins:
            pin_mask = 1 << pin
            levels.append(pin_mask & level_mask == pin_mask)

        return [('low', 'high')[level] for level in levels]

    async def _write_many(self, pins: Sequence[int], func: Callable[[int, int], int]):
        raise_if_pins_not_supported(
            self._manager._comm.ClientConnection, pins=pins, mode='write'
        )

        mask = pins_to_bitmask(pins)

        current = self._manager._comm.DigitalOutput

        mask = func(mask, current)

        async with self._manager._lock():
            await create_future(
                self._manager._comm.ClientConnection.SetDigitalOutputAsync(mask)
            )

    async def write_many(self, pins: Sequence[int], level: Literal['low', 'high'] = 'high'):
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

        return await self._write_many(pins, func)

    async def write(self, pin: int, level: Literal['low', 'high'] = 'high'):
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
        _ = await self.write_many([pin], level=level)

    async def toggle(self, pin: int):
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
        return await self.toggle_many([pin])

    async def toggle_many(self, pins: Sequence[int]):
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

        return await self._write_many(pins, func)

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
