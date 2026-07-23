from __future__ import annotations

import re
import time
from collections import deque

import PalmSens
from typing_extensions import Generator, override

from .capabilities_listing import (
    COMMUNICATION_CAPABILITIES,
    METHODSCRIPT_CAPABILITIES,
    METHODSCRIPT_ERRORS,
    NEWLINE_TERMINATORS,
)
from .instrument import Instrument

ERROR_PATTERN = re.compile(r'.*!([0-9A-Fa-f]{4})(:.*|\n)')


class MethodScriptRuntimeError(ConnectionError):
    def __init__(self, *args, error_code: str, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_code: str = error_code


def parse_capabilities(data: str, mapping: dict[int, str]) -> set[str]:
    try:
        value = int(data[1:-1], 16)
    except ValueError:
        raise ValueError(f'Invalid input: {data}')

    features = set()

    features = {feature for i, feature in mapping.items() if (value >> i) & 1}

    return features


class CommunicationInterface:
    """Communication interface for MethodSCRIPT instruments.

    This class contains high-level communication methods that are independent
    of the physical interface (e.g.: serial port, USB, Bluetooth, ...). The
    low-level communication should be provided by an istrument object.
    """

    def __init__(self, instrument: Instrument):
        self.instrument: Instrument = instrument
        """Instrument handle."""

        self._device: PalmSens.Devices.Device = self.instrument.device
        """Low-level device implementing low-level communication primitives."""

        self.timeout: float = 1.0  # s
        """Read timeout."""

        self.delay: float = 0.1  # s
        """Delay between write and read for query commands.
        The delay is device and connection dependent."""

        self.history: deque[str] = deque(maxlen=100)
        """Response history (defaults to last 100 responses)."""

    @override
    def __repr__(self) -> str:
        return f"{type(self).__name__}('{self.instrument.id}', connected={self._device.IsOpen})"

    def __enter__(self) -> CommunicationInterface:
        self.open()
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def open(self) -> None:
        """Open device connection."""
        self._device.Open()

    def close(self) -> None:
        """Close device connection."""
        self._device.Close()

    def write(self, data: str):
        """Write to device.

        Parameters
        ----------
        data : str
            Data to write to device. To commit a command,
            the data string should end with newline '\n'.
        """
        self._device.Write(data)

    def read(self) -> str:
        """Read response line from device.

        Returns
        ----------
        response : str
            Read next packet from device buffer.
            Returns empty string ('') if buffer is empty.
        """
        response = self._device.Read()

        if response:
            self.history.append(response)

        return response

    def lines(
        self,
        timeout: float | None = None,
        delay: float | None = None,
    ) -> Generator[str, None, None]:
        """Yield response lines until timeout or EOF.

        Parameters
        ----------
        timeout : float, optional
            Maximum time to wait for each line (in seconds). Defaults to `self.timeout`.
        delay : float, optional
            Optional delay between read calls. Defaults
            to `self.delay`.

        Yields
        ------
        str
            Response lines as they arrive.
        """
        delay = delay or self.delay
        timeout = timeout or self.timeout

        deadline = time.monotonic() + timeout

        while True:
            response = self.read()

            if response:
                yield response

            if deadline and time.monotonic() > deadline:
                break

            if not response:
                time.sleep(self.delay)

    def wait_until(self, start: str, timeout: float | None = None) -> str:
        """Wait for until packet that starts with `start` is received.

        Parameters
        ----------
        start : str
            Package initiation character that marks the start of a response.
            This corresponds to the first character of a command.
        timeout : float, optional
            Raise TimeoutError if initiation character is not reached
            within timeout (in s). Defaults to `self.timeout`.

        Returns
        -------
        response : str
            Response including termination character.
        """
        timeout = timeout or self.timeout

        deadline = time.monotonic() + timeout

        for response in self.lines():
            if response.startswith(start):
                return response

            if time.monotonic() > deadline:
                break

        raise TimeoutError(f'Timed out waiting for response starting with {start!r}')

    def read_until(
        self,
        end: str = '\n',
        delay: float | None = None,
    ) -> str:
        """Receive all lines until `end` is reached.

        Parameters
        ----------
        end : str
            Termination character that marks the end of a response.
            This is different for each command, scripts and other commands
            with variable length responses use '\n\n', others use '\n' (default).
        delay : float, optional
            Optional delay between read calls. Defaults
            to `self.delay`.

        Returns
        -------
        response : str
            Response including termination character.
        """
        buffer: list[str] = []

        for line in self.lines(delay=delay):
            match = ERROR_PATTERN.match(line)

            if match:
                error_code = match.group(1) + match.group(2).strip()
                message = METHODSCRIPT_ERRORS[error_code]
                raise MethodScriptRuntimeError(
                    f'{message} (0x{error_code})', error_code=error_code
                )

            if line:
                buffer.append(line)

            if line.endswith(end):
                break

        response = ''.join(buffer)

        return response

    def query(self, command: str, end: str | None = None, delay: float | None = None) -> str:
        """Send a command and return the response in a single call.

        This is the primary method for request/response in interactive
        environments. It writes a command to the device, waits until the command
        completes (termination character `end` is reached), and returns the
        response.

        Parameters
        ---------
        command : str
            Command to run. If None, send empty command
        end : str, optional
            Termination character that marks the end of a response.

            If None, use a look-up table to get the documented response
            termination sequence.

            The termination sequence is different for each command.
            Most commands return on a single line and use '\n'.
            Other commands with variable length responses (e.g. scripts)
            use '\n\n' or '\1xC' for 'fs_get'.
        delay : float, optional
            Optional delay between read calls. Defaults
            to `self.delay`.

        Returns
        -------
        response : str
            Response for command
        """
        delay = delay or self.delay

        if not end:
            func = command.split(maxsplit=1)[0]
            end = NEWLINE_TERMINATORS.get(func, '\n')

        if not command.endswith('\n'):
            command = f'{command}\n'

        self.write(command)

        response = self.wait_until(command[0])
        if response.endswith(end):
            return response

        return response + self.read_until(end=end, delay=delay)

    def send_methodscript(self, script: str) -> str:
        """Load and run a MethodSCRIPT until completion.

        Parameters
        ----------
        script : str
            The MethodSCRIPT to load, terminated with _one_ empty line.
            See the MethodSCRIPT documentation for more information.

        Returns
        -------
        str
            Script output.
        """
        script = script.rstrip('\n')

        return self.query(f'e\n{script}\n\n')

    def get_methodscript_version(self) -> str:
        """Get MethodSCRIPT version."""
        return self.query('v')

    def get_firmware_version(self) -> str:
        """Get firmware version."""
        return self.query('t')

    def get_serial_number(self) -> str:
        """Get serial number."""
        return self.query('i')

    def get_fs_info(self) -> str:
        """Get filesystem information."""
        return self.query('fs_info')

    def get_fs_dir(self) -> str:
        """Get directory listing."""
        return self.query('fs_dir')

    def get_methodscript_capabilities(self) -> set[str]:
        """Get the MethodSCRIPT capabilities.

        Returns
        -------
        set[str]
            List of MethodSCRIPT commands that are licensed and supported by the instrument.
        """

        response = self.query('CM')
        return parse_capabilities(response, mapping=METHODSCRIPT_CAPABILITIES)

    def get_communication_capabilities(self) -> set[str]:
        """Get the runtime capabilities.

        Returns
        -------
        set[str]
            list of supported commands for the instrument
        """
        response = self.query('CC')
        return parse_capabilities(response, mapping=COMMUNICATION_CAPABILITIES)

    def flush(self):
        """Flush write buffer by sending '\n'."""
        _ = self.query('\n')

    def abort(self):
        """Abort a possibly running script and wait for it to finish.

        This method aborts any running script. If a script was still running, it
        will wait for it to complete. Note that this could take a while, depending
        on the measurement that was running.
        """
        self.flush()

        try:
            response = self.query('Z')
        except MethodScriptRuntimeError as exc:
            if exc.error_code != '0006':
                raise

            time.sleep(0.1)

        if response == 'Z\n':  # type: ignore
            _ = self.read_until('\n\n')
