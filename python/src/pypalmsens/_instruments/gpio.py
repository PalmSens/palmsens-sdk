from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Literal, final

import PalmSens

if TYPE_CHECKING:
    from .instrument_manager import InstrumentManager


@final
class GPIO:
    """High level gpio interface.

    For more fine-grained control, use MethodSCRIPT (if your device supports it):

        - [pypalmsens.CommProtocol][]
        - [MethodSCRIPT manual](https://dev.palmsens.com/methodscript/latest/methodscript/methodscript_main.html)


    """

    def __init__(self, manager: InstrumentManager):
        self.manager = manager

    def read_pin(self, pin: int) -> Literal['low', 'high']:
        """Reads the state of a GPIO pin.

        The pin configuration is automatically switched to input if needed.

        Check your device documentation for the available input pins.

        Parameters
        ----------
        pin: integer
            The integer index of the GPIO pin to read.

        Raises
        ------
        ValueError:
            If the requested output pin is not supported by the device.
        """
        if pin < 0:
            raise ValueError('Pin cannot be negative.')

        mask = 1 << pin

        is_methodscript = isinstance(
            self.manager._comm.ClientConnection, PalmSens.Comm.ClientConnectionMS
        )

        if is_methodscript:
            supported_mask = (
                self.manager._comm.ClientConnection.Capabilities.SupportedDigitalInputLineMask
            )

            if not (mask & supported_mask):
                raise ValueError('Requested input pin is not supported by device.')
        else:
            if pin > 1:
                raise ValueError('Requested input pin is not supported by device.')

        with self.manager._lock():
            level = self.manager._comm.ClientConnection.ReadDigitalLine(mask)

        return ('low', 'high')[level]

    def read_pins(self, pins: Sequence[int]) -> list[Literal['low', 'high']]:
        """Read pins configured as input."""
        mask = self._pins_to_bitmask(pins)

        return []

    def _write_pins(self, pins: Sequence[int], func: Callable[[int, int], int]):
        if min(pins) < 0:
            raise ValueError('Pin cannot be negative.')

        mask = self._pins_to_bitmask(pins)

        is_methodscript = isinstance(
            self.manager._comm.ClientConnection, PalmSens.Comm.ClientConnectionMS
        )

        with self.manager._lock():
            if is_methodscript:
                supported_mask = self.manager._comm.ClientConnection.Capabilities.SupportedDigitalOutputLineMask

                if not (mask & supported_mask):
                    raise ValueError('Requested output pin is not supported by device.')

                current = self.manager._comm.ClientConnection.ReadDigitalLine(supported_mask)
            else:
                if max(pins) > 3:
                    raise ValueError('Requested output pin is not supported by device.')

                current = self.manager._comm.DigitalOutput

            mask = func(mask, current)

            self.manager._comm.ClientConnection.SetDigitalOutput(mask)

    def write_pins(self, pins: Sequence[int], level: Literal['low', 'high'] = 'high'):
        if level == 'high':
            func = lambda current, mask: current | mask  # high
        elif level == 'low':
            func = lambda current, mask: current & ~mask  # low
        else:
            raise ValueError("`level` must be one of 'low', 'high', 'toggle'")

        return self._write_pins(pins, func)

    def write_pin(self, pin: int, level: Literal['low', 'high'] = 'high'):
        """Writes a specified state to a GPIO pin.

        The pin configuration is automatically switched to output if needed.

        Check your device documentation for available output pins.

        Parameters
        ----------
        pin: integer
            The integer index of the GPIO pin to control.
        level: Literal['low', 'high', 'toggle']
            The desired output level. Must be one of 'low', 'high', or 'toggle'.
            Defaults to 'high'.

        Raises
        ------
        ValueError:
            If the requested output pin is not supported by the device,
            or if an invalid value is provided for `level`.
        """
        self.write_pins([pin], level=level)

    def toggle_pin(self, pin: int):
        return self.toggle_pins([pin])

    def toggle_pins(self, pins: Sequence[int]):
        func = lambda mask, current: current ^ mask  # toggle

        return self._write_pins(pins, func)

    @staticmethod
    def _pins_to_bitmask(pins: Sequence[int]) -> int:
        """Convert a list of pin indices into a bitmask (integer)."""
        mask = 0
        for pin in pins:
            mask |= 1 << pin

        return mask

    @staticmethod
    def _bitmask_to_pins(mask: int) -> list[int]:
        """Convert a bitmask (integer) into a list pin indices."""
        return [i for i in range(8) if (mask & (1 << i))]
