from __future__ import annotations

import posixpath
from pathlib import PurePath
from typing import Any, Iterator

import PalmSens
import System

from pypalmsens._instruments.instrument_manager import InstrumentManager
from pypalmsens.data import Measurement


class FileSystemException(OSError): ...


class DevicePath(PurePath):
    parser = posixpath  # type:ignore

    def __str__(self):
        try:
            return self._str
        except AttributeError:
            self._str: str = self._format_parsed_parts(self.drive, self.root, self._tail) or ''
            return self._str


class DeviceFileSystem:
    def __init__(self, manager: InstrumentManager):
        self.manager = manager

    @property
    def _client_connection(self):
        return self.manager._comm.ClientConnection

    def __enter__(self):
        self.manager.connect()
        return self

    def __exit__(self, *_):
        self.manager.disconnect()

    def __truediv__(self, path_str: str):
        return self.root / path_str

    def _get_device_file(self, path: str | DevicePath) -> PalmSens.Data.DeviceFile:
        path = DevicePath(path)

        if hasattr(path, '_cached_device_file'):
            return path._cached_device_file

        with self.manager._lock():
            try:
                ret = self._client_connection.GetDeviceFile(path.__fspath__())
            except System.Exception as exc:
                # Error codes:
                # https://dev.palmsens.com/methodscript/latest/methodscript/methodscript_main.html#app_err_error_codes
                raise FileSystemException(exc.Message) from exc

        path._cached_device_file = ret  # type: ignore
        return ret

    @property
    def root(self) -> DevicePath:
        """Return path of root directory."""
        return DevicePath('')

    def exists(self, path: str | DevicePath):
        """Return True if path exists"""
        path = DevicePath(path)

        node = self.tree()

        *dirs, leaf = path.parts

        for drc in dirs:
            if drc not in node:
                return False

            node = node[drc]

        if ('_files' in node) and (leaf in node['_files']):
            return True

        return leaf in node

    def load_measurement(self, path: str | DevicePath) -> Measurement:
        """Load measurement."""
        f = self._get_device_file(path)

        psmeasurement = self._client_connection.LoadDeviceFile(f)

        return Measurement(psmeasurement=psmeasurement)

    def remove(self, path: str | DevicePath):
        """Remove file."""
        if isinstance(path, str):
            path = DevicePath(path)

        with self.manager._lock():
            self._client_connection.DeleteDeviceFile(path.__fspath__())

    def clear(self, confirm: bool = False):
        """Delete all files in filesystem."""
        if confirm:
            with self.manager._lock():
                self._client_connection.ClearDeviceFiles

    def free(self) -> int:
        """Return free space on filesystem.

        Returns
        -------
        int
            Free space in bytes.
        """
        with self.manager._lock():
            return self._client_connection.GetDeviceFree()

    def size(self) -> int:
        """Return total size of filesystem.

        Returns
        -------
        int
            Total size in bytes.
        """
        with self.manager._lock():
            return self._client_connection.GetDeviceSize()

    def timestamp_of(self, path: str | DevicePath) -> str:
        """Return timestamp of file in isoformat."""
        f = self._get_device_file(path)

        return f.Timestamp.ToString('s', System.Globalization.CultureInfo.InvariantCulture)

    def size_of(self, path: str | DevicePath) -> int:
        """Return file size in bytes."""
        f = self._get_device_file(path)

        return f.Size

    def read_text(self, path: DevicePath) -> str:
        """Read path as text."""
        f = self._get_device_file(path)

        return f.Content

    def tree(self, directory: DevicePath | str | None = None) -> dict[str, Any]:
        """Create directory tree from this directory.

        If None, default to root directory."""
        paths = self.iterdir(directory)

        root: dict[str, Any] = {}

        for path in paths:
            *parts, filename = path.parts

            node = root
            for part in parts:
                node = node.setdefault(part, {})

            node.setdefault('_files', [])
            node['_files'].append(filename)

        return root

    def iterdir(self, directory: DevicePath | str | None = None) -> Iterator[DevicePath]:
        """Yield path objects of the directory contents.

        If None, default to root directory.
        """
        if not directory:
            directory = self.root

        if isinstance(directory, str):
            directory = DevicePath(directory)

        with self.manager._lock():
            ret = self._client_connection.GetDeviceFiles(directory.__fspath__())

        for f in ret:
            yield DevicePath(f.Dir, f.Name)
