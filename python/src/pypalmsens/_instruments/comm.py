from __future__ import annotations

import logging
import re
import time
from collections import deque

import PalmSens
from typing_extensions import override

from .capabilities_listing import (
    COMMUNICATION_CAPABILITIES,
    METHODSCRIPT_CAPABILITIES,
)
from .instrument import Instrument

logger = logging.getLogger(__name__)

ERROR_PATTERN = re.compile(r'.*!([0-9A-Fa-f]{4})(:.*|\n)')


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
        """Instrument handle"""

        self.device: PalmSens.Devices.Device = self.instrument.device
        """Low-level device implementing low-level communication primitives"""

        self.timeout: float = 1.0  # s
        """Read timeout."""

        self.delay: float = 0.1  # s
        """Delay between write and read for query commands."""

        self.history: deque[str] = deque(maxlen=100)
        """Response history."""

    def __iter__(self):
        while True:
            yield self.read()

            time.sleep(self.delay)

    @override
    def __repr__(self) -> str:
        return f"{type(self).__name__}('{self.instrument.id}', connected={self.device.IsOpen})"

    def open(self) -> None:
        self.device.Open()

    def close(self) -> None:
        self.device.Close()

    def __enter__(self) -> CommunicationInterface:
        self.open()
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def write(self, text: str):
        """Write to device."""
        self.device.Write(text)

    def read(self) -> str:
        """Read response line from device."""
        text = self.device.Read()

        if text:
            self.history.append(text)

        return text

    def wait_for_packet(self, start: str) -> str:
        t0 = time.monotonic()

        for line in self:
            if line.startswith(start):
                return line

            if time.monotonic() - t0 > self.timeout:
                break

        raise TimeoutError

    def read_until(self, start: str = '', end: str = '\n', delay: float | None = None):
        """Receive all lines until end is reached."""
        lines: list[str] = []

        if delay is None:
            delay = self.delay

        if start:
            line = self.wait_for_packet(start)
            if line.endswith(end):
                return line

            lines.append(line)

        for line in self:
            match = ERROR_PATTERN.match(line)

            if match:
                error_code = match.group(1) + match.group(2).strip()
                raise ConnectionError(f'MethodSCRIPT error: {error_code}')

            if line:
                lines.append(line)

            if line.endswith(end):
                break

        response = ''.join(lines)

        return response

    def query(self, command: str, delay: float | None = None, end: str = '\n') -> str:
        if delay is None:
            delay = self.delay

        if not command.endswith('\n'):
            command = f'{command}\n'

        self.write(command)
        return self.read_until(start=command[0], end=end, delay=delay)

    def get_methodscript_version(self) -> str:
        return self.query('v')

    def get_firmware_version(self) -> str:
        return self.query('t')

    def get_serial_number(self) -> str:
        return self.query('i')

    def get_fs_info(self) -> str:
        return self.query('fs_info')

    def get_fs_dir(self) -> str:
        return self.query('fs_dir', end='\n\n')

    def methodscript_capabilities(self) -> set[str]:
        response = self.query('CM')
        return parse_capabilities(response, mapping=METHODSCRIPT_CAPABILITIES)

    def communication_capabilities(self) -> set[str]:
        response = self.query('CC')
        return parse_capabilities(response, mapping=COMMUNICATION_CAPABILITIES)
