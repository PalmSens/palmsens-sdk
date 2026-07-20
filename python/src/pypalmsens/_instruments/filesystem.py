from __future__ import annotations

import sys

import PalmSens
import System
from PalmSens.Data import DeviceFile
from typing_extensions import Iterator

from ..data import Measurement
from .instrument import Instrument
from .instrument_manager import InstrumentManager


class FileSystemException(OSError):
    """Raised when a filesystem operation fails."""

    pass


if sys.version_info < (3, 12):
    # In 3.10 and 3.11, PurePath does not support subclassing
    # See: https://docs.python.org/3.12/whatsnew/3.12.html#pathlib

    from pathlib import PurePosixPath

    class DevicePath(PurePosixPath):
        """A path object representing a file or directory on the device.

        Subclasses [pathlib.PurePath][] to provide POSIX-style path semantics
        for PalmSens device filesystem paths.
        """

        def __str__(self):
            try:
                return self._str
            except AttributeError:
                self._str = self._format_parsed_parts(self._drv, self._root, self._parts) or ''
                return self._str

else:
    import posixpath
    from pathlib import PurePath

    class DevicePath(PurePath):
        """A path object representing a file or directory on the device.

        Subclasses [pathlib.PurePath][] to provide POSIX-style path semantics
        for PalmSens device filesystem paths.
        """

        parser = posixpath  # type:ignore

        def __str__(self):
            try:
                return self._str
            except AttributeError:
                self._str: str = (
                    self._format_parsed_parts(self.drive, self.root, self._tail) or ''
                )
                return self._str

        def _from_parsed_string(self, path_str):
            path = self.with_segments(path_str)
            path._str = path_str or ''
            return path


class DeviceFileSystem:
    """Provide a file-system-like interface to a PalmSens device.

    Allows browsing, reading, writing, and deleting files on the connected
    instrument as if they were entries in a local directory tree.
    """

    def __init__(self, instrument_or_manager: Instrument | InstrumentManager):
        """Initialize the filesystem.

        Note that if not used as a context manager,
        the manager must have an active connection with the device.

        Parameters
        ----------
        instrument_or_manager : Instrument | InstrumentManager
            An instrument instance or an existing `InstrumentManager`.
            If an instrument is passed, a new manager will be created.
        """
        self.manager: InstrumentManager

        if isinstance(instrument_or_manager, Instrument):
            self.manager = InstrumentManager(instrument_or_manager)
        else:
            self.manager = instrument_or_manager

        if not self.manager.capabilities.supports_storage:
            raise ValueError(
                f'{self.manager.instrument.name!r} does not have or support internal storage.'
            )

    @property
    def _client_connection(self) -> PalmSens.Comm.ClientConnection:
        """The active client connection used for device communication."""
        return self.manager._comm.ClientConnection

    def __repr__(self) -> str:
        return f"{type(self).__name__}('{self.manager.instrument.id}')"

    def __enter__(self):
        self.manager.connect()
        return self

    def __exit__(self, *_) -> None:
        self.manager.disconnect()

    def __truediv__(self, path_str: str) -> DevicePath:
        """Join a path component to the root directory."""
        return self.root / path_str

    def _get_device_file(self, path: str | DevicePath) -> PalmSens.Data.DeviceFile:
        """Retrieve the DeviceFile` for the given path."""
        if not isinstance(path, DevicePath):
            path = DevicePath(path)

        if hasattr(path, '_cached_device_file'):
            return path._cached_device_file

        with self.manager._lock():
            try:
                ret = self._client_connection.GetDeviceFile(f'/{path}')
            except System.Exception as exc:
                # Error codes:
                # https://dev.palmsens.com/methodscript/latest/methodscript/methodscript_main.html#app_err_error_codes
                raise FileSystemException(exc.Message) from exc

        path._cached_device_file = ret  # type: ignore
        return ret

    def _get_device_files(self, directory: DevicePath | str | None = None) -> list[DeviceFile]:
        if not directory:
            directory = self.root

        if isinstance(directory, str):
            directory = DevicePath(directory)

        with self.manager._lock():
            ret = self._client_connection.GetDeviceFiles(str(directory))

        return ret

    @property
    def root(self) -> DevicePath:
        """Return path of root directory.

        Returns
        -------
        DevicePath
            Path of root directory.
        """
        return DevicePath('')

    def exists(self, path: str | DevicePath) -> bool:
        """Check whether a path exists on the device.

        Parameters
        ----------
        path : str | DevicePath
            The file or directory path to check.

        Returns
        -------
        bool
            True if the path exists, False otherwise.
        """
        if not isinstance(path, DevicePath):
            path = DevicePath(path)

        if str(path) == '':  # root always exists
            return True

        for entry in self.iterdir(path.parent):
            if entry == path:  # check if direct match
                return True

            if entry.is_relative_to(path):  # check for subdirectory match
                return True

        return False

    def load_measurement(self, path: str | DevicePath) -> Measurement:
        """Load measurement from path on device.

        Parameters
        ----------
        path : str | DevicePath
            The file path to load.

        Returns
        -------
        Measurement
            Measurement data.
        """
        f = self._get_device_file(path)

        psmeasurement = self._client_connection.LoadDeviceFile(f)

        return Measurement(psmeasurement=psmeasurement)

    def remove(self, path: str | DevicePath) -> None:
        """Remove a file from the device.

        Parameters
        ----------
        path : str | DevicePath
            The file path to remove.
        """
        if isinstance(path, str):
            path = DevicePath(path)

        with self.manager._lock():
            self._client_connection.DeleteDeviceFile(path.__fspath__())

    def delete_all_files(self, confirm: bool = False) -> None:
        """Delete all files on the device.

        Parameters
        ----------
        confirm : bool, optional
            If True, clear all files on the device. Default is False.
            This acts as a sentinel to avoid accidental deletes in
            interactive REPL or Jupyter environments.
        """
        if confirm:
            with self.manager._lock():
                self._client_connection.ClearDeviceFiles()

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
        """Get the modification timestamp of a file.

        Parameters
        ----------
        path : str | DevicePath
            The file path.

        Returns
        -------
        str
            Timestamp in ISO format.
        """
        f = self._get_device_file(path)

        return f.Timestamp.ToString('s', System.Globalization.CultureInfo.InvariantCulture)

    def size_of(self, path: str | DevicePath) -> int:
        """Get the size of a file.

        Parameters
        ----------
        path : str | DevicePath
            The file path.

        Returns
        -------
        int
            File size in bytes.
        """
        f = self._get_device_file(path)

        return f.Size

    def read_text(self, path: DevicePath) -> str:
        """Read the content of a file as text.

        Parameters
        ----------
        path : DevicePath
            The file path.

        Returns
        -------
        str
            File contents as a string.
        """
        f = self._get_device_file(path)

        return f.Content

    def listdir(self, directory: DevicePath | str | None = None) -> list[DevicePath]:
        """List all entries in a device directory.

        Note that some devices like EmStat4 return all subdirectories and files
        at once.

        Parameters
        ----------
        directory : DevicePath | str | None, optional
            The directory to iterate. Defaults to the root directory.

        Yields
        ------
        paths: Iterator[DevicePath]
            Path objects for each entry in the directory.
        """
        return list(self.iterdir(directory=directory))

    def iterdir(self, directory: DevicePath | str | None = None) -> Iterator[DevicePath]:
        """Iterate over entries in a device directory.

        Note that some devices like EmStat4 return all subdirectories and files
        at once.

        Parameters
        ----------
        directory : DevicePath | str | None, optional
            The directory to iterate. Defaults to the root directory.

        Yields
        ------
        paths: Iterator[DevicePath]
            Path objects for each entry in the directory.
        """
        paths = self._get_device_files(directory=directory)

        for path in paths:
            yield DevicePath(path.Dir, path.Name)

    def walk(self, directory: DevicePath | str | None = None) -> Iterator[DevicePath]:
        """Generate file names by walking the directory tree starting from a device directory.

        Parameters
        ----------
        directory : DevicePath | str | None, optional
            The directory to walk through. Defaults to the root directory.

        Yields
        ------
        paths: Iterator[DevicePath]
            Path objects for each entry in the directory.
        """
        paths = self._get_device_files(directory=directory)

        for path in paths:
            df = DevicePath(path.Dir, path.Name)

            if str(path.Type) == 'Folder':
                yield from self.walk(str(df))
            else:
                yield df
