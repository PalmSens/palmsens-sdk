from __future__ import annotations

import logging
import re
import time

import PalmSens

logger = logging.getLogger(__name__)

ERROR_PATTERN = re.compile(r'.*!([0-9A-Fa-f]{4})(:.*|\n)')


class CommunicationInterface:
    """Communication interface for MethodSCRIPT instruments.

    This class contains high-level communication methods that are independent
    of the physical interface (e.g.: serial port, USB, Bluetooth, ...). The
    low-level communication should be provided by a communication object that
    is passed to the initializer.
    """

    def __init__(self, device: PalmSens.Devices.Device):
        """Initialize the object.

        `comm` must be a communication object as described in the
        documentation of this class.
        """
        self.device = device

    def write(self, text: str):
        """Write to device."""
        logger.debug('TX: %r', text)
        self.device.Write(text)

    def read(self) -> str:
        """Read response line from device."""
        text = self.device.Read()

        if text:
            logger.debug('RX: %r', text)

        return text

    def get_methodscript_version(self, delay: float = 0.02) -> str:
        self.write('v\n')
        response = self.read_until_end(delay=delay)
        return response

    def get_firmware_version(self, delay: float = 0.02) -> str:
        self.write('t\n')
        response = self.read_until_end(delay=delay)
        return response

    def get_serial_number(self, delay: float = 0.02) -> str:
        self.write('i\n')
        response = self.read_until_end(delay=delay)
        return response

    def get_fs_info(self, delay: float = 0.02) -> str:
        self.write('fs_info\n')
        response = self.read_until_end(delay=delay)
        return response

    def get_fs_dir(self, delay: float = 0.02) -> str:
        self.write('fs_dir\n')
        response = self.read_until_end(delay=delay, end='\n\n')
        return response

    def read_until_end(self, delay: float = 0.01, end: str = '\n'):
        """Receive all lines until end is reached."""
        lines: list[str] = []

        while True:
            line = self.read()

            match = ERROR_PATTERN.match(line)

            if match:
                error_code = match.group(1) + match.group(2).strip()
                raise ConnectionError(f'MethodSCRIPT error: {error_code}')

            lines.append(line)

            if line.endswith(end):
                break

            time.sleep(delay)

        return ''.join(lines)
