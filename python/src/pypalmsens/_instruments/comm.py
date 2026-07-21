from __future__ import annotations

import re
import time
from collections import deque

import PalmSens
from typing_extensions import override

from .capabilities_listing import (
    COMMUNICATION_CAPABILITIES,
    METHODSCRIPT_CAPABILITIES,
    METHODSCRIPT_ERRORS,
)
from .instrument import Instrument

ERROR_PATTERN = re.compile(r'.*!([0-9A-Fa-f]{4})(:.*|\n)')


class MethodScriptRuntimeError(ConnectionError):
    def __init__(self, *args, error_code: str, **kwargs):
        super().__init__()
        self.error_code: str = error_code


def parse_capabilities(data: str, mapping: dict[int, str]) -> set[str]:
    try:
        bitmask = bin(int(data[1:-1], 16))
    except ValueError:
        raise ValueError(f'Invalid input: {data}')

    features = set()

    for i, n in enumerate(bitmask[2:]):
        if not int(n):
            continue

        if feature := mapping.get(i):
            features.add(feature)

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

        self.device: PalmSens.Devices.Device = self.instrument.device
        """Low-level device implementing low-level communication primitives."""

        self.timeout: float = 1.0  # s
        """Read timeout."""

        self.delay: float = 0.1  # s
        """Delay between write and read for query commands."""

        self.history: deque[str] = deque(maxlen=100)
        """Response history."""

    @override
    def __repr__(self) -> str:
        return f"{type(self).__name__}('{self.instrument.id}', connected={self.device.IsOpen})"

    def __enter__(self) -> CommunicationInterface:
        self.open()
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def __iter__(self):
        while True:
            response = self.read()

            if response:
                yield response

            time.sleep(self.delay)

    def open(self) -> None:
        """Open device connection."""
        self.device.Open()

    def close(self) -> None:
        """Close device connection."""
        self.device.Close()

    def write(self, data: str):
        """Write to device.

        Parameters
        ----------
        data : str
            Data to write to device. To commit a command,
            the data string should end with newline '\n'.
        """
        self.device.Write(data)

    def read(self) -> str:
        """Read response line from device.

        Returns
        ----------
        response : str
            Read next packet from device buffer.
            Returns empty string ('') if buffer is empty.
        """
        response = self.device.Read()

        if response:
            self.history.append(response)

        return response

    def wait_until(self, start: str) -> str:
        """Wait for until packet that starts with `start` is received.

        Parameters
        ----------
        start : str
            Package initiation character that marks the start of a response.
            This corresponds to the first character of a command.

        Returns
        -------
        response : str
            Response including termination character.

        """
        deadline = time.monotonic() + self.timeout

        for response in self:
            if response.startswith(start):
                return response

            if time.monotonic() > deadline:
                break

        raise TimeoutError

    def read_until(
        self,
        end: str = '\n',
        delay: float | None = None,
    ):
        """Receive all lines until `end` is reached.

        Parameters
        ----------
        end : str
            Termination character that marks the end of a response.
            This is different for each command, scripts and other commands
            with variable length responses use '\n\n', others use '\n' (default).
        delay : float, optional
            Optional delay between read calls. Defaults
            to self.delay.

        Returns
        -------
        response : str
            Response including termination character.
        """
        buffer: list[str] = []

        if delay is None:
            delay = self.delay

        for line in self:
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

    def query(self, command: str, end: str = '\n', delay: float | None = None) -> str:
        """Send a command and return the response in a single call.

        This is the primary method for request/response in interactive
        environments. It writes a command to the device, waits until the command
        completes (termination character `end` is reached), and returns the
        response.

        Parameters
        ---------
        command : str
            Command to run
        end : str
            Termination character that marks the end of a response.
            This is different for each command, scripts and other commands
            with variable length responses use '\n\n', others use '\n' (default).
        delay : float, optional
            Optional delay between read calls. Defaults
            to self.delay.

        Returns
        -------
        response : str
            Response for command
        """
        if delay is None:
            delay = self.delay

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
        script = script.rstrip()

        return self.query(f'e\n{script}\n\n', end='\n\n')

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
        return self.query('fs_dir', end='\n\n')

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

    def abort(self):
        """Abort a possibly running script and wait for it to finish.

        This method aborts any running script. If a script was still running, it
        will wait for it to complete. Note that this could take a while, depending
        on the measurement that was running.
        """
        response = self.query('')

        try:
            response = self.query('Z')
        except MethodScriptRuntimeError as exc:
            if not exc.error_code == '0006':
                raise

            time.sleep(0.1)

        if response == 'Z\n':
            _ = self.read_until('\n\n')
