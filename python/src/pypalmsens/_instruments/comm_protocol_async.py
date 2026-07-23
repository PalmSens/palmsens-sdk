from __future__ import annotations

import asyncio
import time
from collections import deque

import PalmSens
from typing_extensions import override

from .capabilities_listing import (
    COMMUNICATION_CAPABILITIES,
    METHODSCRIPT_CAPABILITIES,
    NEWLINE_TERMINATORS,
)
from .comm_protocol import ERROR_PATTERN, MethodScriptRuntimeError, parse_capabilities
from .instrument import Instrument


class CommProtocolAsync:
    """Communication interface for MethodSCRIPT instruments.

    This class provides high-level communication methods that are independent
    of the physical connection type (e.g., serial port, USB, Bluetooth).
    The low-level communication primitives are provided by an instrument object.
    """

    def __init__(self, instrument: Instrument):
        self.instrument: Instrument = instrument
        """Instrument handle."""

        self._device: PalmSens.Devices.Device = self.instrument.device
        """Low-level device implementing low-level communication primitives."""

        self.timeout: float = 10.0  # s
        """Maximum time (in seconds) to wait for a response before timing out."""

        self.delay: float = 0.1  # s
        """Pause (in seconds) between writing a command and reading its response.
        This delay is necessary to ensure the device has processed the command.
        Adjust based on your specific hardware and connection type."""

        self.history: deque[str] = deque(maxlen=100)
        """Response history (defaults to last 100 responses)."""

    @override
    def __repr__(self) -> str:
        return f"{type(self).__name__}('{self.instrument.id}', connected={self._device.IsOpen})"

    async def __aenter__(self) -> CommProtocolAsync:
        await self.open()
        return self

    async def __aexit__(self, *exc) -> None:
        await self.close()

    async def open(self) -> None:
        """Open device connection."""
        await self._device.OpenAsync()

    async def close(self) -> None:
        """Close device connection."""
        await self._device.CloseAsync()

    async def write(self, data: str):
        """Write a command or data to the instrument.

        Parameters
        ----------
        data : str
            Command or data to send. To submit a command for execution,
            append a newline character ('\n') to the end of the string.
        """
        await self._device.WriteAsync(data)

    async def read(self) -> str:
        """Read the next available chunk from the instrument's input buffer.

        This method does not block. It returns immediately with whatever
        data is currently available in the buffer.

        Returns
        -------
        response : str
            The next response chunk, or an empty string ('') if the buffer
            contains no data. Each read is recorded in `self.history` for
            debugging and inspection.
        """
        response = await self._device.ReadAsync()

        if response:
            self.history.append(response)

        return response

    async def lines(
        self,
        timeout: float | None = None,
        delay: float | None = None,
    ):
        """Yield response chunks until a timeout occurs or no more data arrives.

        This is an async generator that continuously reads from the device buffer,
        yielding chunks as they arrive.
        It stops when the elapsed time between responses exceeds `timeout`.

        Parameters
        ----------
        timeout : float, optional
            Maximum total time (in seconds) between responses.
            Defaults to `self.timeout`.
        delay : float, optional
            Pause (in seconds) between read attempts when no data is available.
            Defaults to `self.delay`.

        Yields
        ------
        response : str
            Response chunks as they arrive from the device.
        """
        delay = delay or self.delay
        timeout = timeout or self.timeout

        deadline = time.monotonic() + timeout

        while True:
            response = await self.read()

            if response:
                yield response
                deadline = time.monotonic() + timeout

            if time.monotonic() > deadline:
                raise TimeoutError('Timed out waiting for response')

            if not response:
                await asyncio.sleep(delay)

    async def wait_until(self, prefix: str, timeout: float | None = None) -> str:
        """Wait until a response line starting with `prefix` arrives.

        When you send a command, the device echoes back its first character
        before returning the actual result. Use this method to wait for
        that echo.

        Parameters
        ----------
        prefix : str
            The first character of an expected response line. This usually
            matches the command abbreviation (e.g., 'E' for a measurement start).
        timeout : float, optional
            Maximum time (in seconds) to wait before raising `TimeoutError`.
            Defaults to `self.timeout`.

        Returns
        -------
        response : str
            The response chunk that starts with `prefix`, including
            its termination character.

        Raises
        ------
        TimeoutError
            If no matching line arrives within the timeout period.
        """
        timeout = timeout or self.timeout

        deadline = time.monotonic() + timeout

        async for response in self.lines():
            if response.startswith(prefix):
                return response

            if time.monotonic() > deadline:
                break

        raise TimeoutError(f'Timed out waiting for response starting with {prefix!r}')

    async def read_until(
        self,
        end: str = '\n',
        delay: float | None = None,
    ) -> str:
        """Read lines from the device until a termination sequence is found.

        Continuously reads responses and concatenates them until
        `end` appears.

        Parameters
        ----------
        end : str
            The termination sequence that marks the end of the response.
            Most commands use '\n'. Scripts and variable-length responses
            typically use '\n\n'.
        delay : float, optional
            Pause (in seconds) between read attempts. Defaults to `self.delay`.

        Returns
        -------
        response : str
            Accumulated response up to and including the termination sequence.

        Raises
        ------
        MethodScriptRuntimeError
            If the device returns an error response during reading.
        """
        buffer: list[str] = []

        async for line in self.lines(delay=delay):
            match = ERROR_PATTERN.match(line)

            if match:
                error_code = match.group(1) + match.group(2).strip()
                raise MethodScriptRuntimeError(error_code=error_code)

            if line:
                buffer.append(line)

            if line.endswith(end):
                break

        response = ''.join(buffer)

        return response

    async def query(
        self, command: str, end: str | None = None, delay: float | None = None
    ) -> str:
        """Send a command and return its response in a single call.

        This is the primary method for interactive communication with the
        instrument. It writes the command to the device, waits for completion,
        reads the full response, and returns it as a string.

        For commands that run for a long time (e.g. scripts), this
        method will block until the script completes or times out.

        Parameters
        ----------
        command : str
            The command to send (e.g., 'i' to get the serial number).
            If `command` does not end with `'\\n'`, one is automatically added.
        end : str, optional
            The termination character(s) that mark the end of the response.

            If `None`, a lookup table determines the appropriate terminator
            based on the command. Most commands use `'\\n'`. Commands with
            variable-length responses (e.g. scripts) use `'\\n\\n'`.
        delay : float, optional
            Pause (in seconds) between read attempts. Defaults to `self.delay`.

        Returns
        -------
        response : str
            The complete response from the device, including termination characters.
        """
        delay = delay or self.delay

        if not end:
            func = command.split(' ', maxsplit=1)[0]
            end = NEWLINE_TERMINATORS.get(func, '\n')

        if not command.endswith('\n'):
            command = f'{command}\n'

        await self.write(command)

        prefix = command[0]

        response = await self.wait_until(prefix)
        if not response.endswith(end):
            response += await self.read_until(end=end, delay=delay)

        return response.removeprefix(prefix).removeprefix('\n').removesuffix('\n')

    async def run_methodscript(self, script: str) -> str:
        """Load and execute a MethodSCRIPT on the instrument.

        MethodSCRIPTs are scripts that run directly on the PalmSens device,
        This method uploads the script, runs it to completion,
        and returns any output produced by the script.

        See the MethodSCRIPT documentation for more information.

        Parameters
        ----------
        script : str
            The MethodSCRIPT to run. The entire script must end
            with exactly one newline ('\n').

        Returns
        -------
        str
            Output produced by the running script, if any.
        """
        script = script.rstrip('\n')

        return await self.query(f'e\n{script}\n\n')

    async def get_methodscript_capabilities(self) -> set[str]:
        """Retrieve which MethodSCRIPT features are available on this instrument.

        Returns a set of command names that are licensed
        and supported by the connected instrument's hardware and firmware.

        Returns
        -------
        set[str]
            Set of available MethodSCRIPT command names.
        """

        response = await self.query('CM')
        return parse_capabilities(response, mapping=METHODSCRIPT_CAPABILITIES)

    async def get_communication_capabilities(self) -> set[str]:
        """Retrieve which communication commands are available on this instrument.

        Returns a set of commands part of the communication protocol that
        are supported by the device's firmware.

        Returns
        -------
        set[str]
            Set of supported commands for the instrument.
        """
        response = await self.query('CC')
        return parse_capabilities(response, mapping=COMMUNICATION_CAPABILITIES)

    async def flush(self):
        """Send a blank line to the device and read its response.

        This does not modify the write buffer. It sends
        an empty command and reads whatever response follows.

        Returns
        -------
        str
            The response from the device after sending `'\\n'`.
        """
        return await self.query('\n')

    async def abort(self):
        """Abort any currently running script or measurement and wait for completion.

        This method sends the abort signal to the instrument. If a script was
        still running, it will wait for it to complete.
        Note that this could take a while, depending on the measurement that
        was running.
        """
        _ = await self.flush()

        try:
            response = await self.query('Z')
        except MethodScriptRuntimeError as exc:
            if exc.error_code != '0006':
                raise

            await asyncio.sleep(0.1)

        if response == 'Z\n':  # type: ignore
            _ = await self.read_until('\n\n')
