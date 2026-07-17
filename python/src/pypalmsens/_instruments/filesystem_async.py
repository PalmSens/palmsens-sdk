from __future__ import annotations

from typing import Any

import PalmSens
import System

from ..data import Measurement
from .filesystem import DevicePath, FileSystemException
from .instrument import Instrument
from .instrument_manager_async import InstrumentManagerAsync
from .shared import create_future


class DeviceFileSystemAsync:
    """Provide a file-system-like interface to a PalmSens device.

    Allows browsing, reading, writing, and deleting files on the connected
    instrument as if they were entries in a local directory tree.
    """

    def __init__(self, instrument_or_manager: Instrument | InstrumentManagerAsync):
        """Initialize the filesystem.

        Note that if not used as a context manager,
        the manager must have an active connection with the device.

        Parameters
        ----------
        instrument_or_manager : Instrument | InstrumentManagerAsync
            An instrument instance or an existing `InstrumentManagerAsync`.
            If an instrument is passed, a new manager will be created.
        """
        self.manager: InstrumentManagerAsync

        if isinstance(instrument_or_manager, Instrument):
            self.manager = InstrumentManagerAsync(instrument_or_manager)
        else:
            self.manager = instrument_or_manager

    @property
    def _client_connection(self) -> PalmSens.Comm.ClientConnection:
        """The active client connection used for device communication."""
        return self.manager._comm.ClientConnection

    def __repr__(self) -> str:
        return f"{type(self).__name__}('{self.manager.instrument.id}')"

    async def __aenter__(self):
        await self.manager.connect()
        return self

    async def __aexit__(self, *_) -> None:
        await self.manager.disconnect()

    def __truediv__(self, path_str: str) -> DevicePath:
        """Join a path component to the root directory."""
        return self.root / path_str

    async def _get_device_file(self, path: str | DevicePath) -> PalmSens.Data.DeviceFile:
        """Retrieve the DeviceFile` for the given path."""
        if not isinstance(path, DevicePath):
            path = DevicePath(path)

        if hasattr(path, '_cached_device_file'):
            return path._cached_device_file

        fspath = path.__fspath__()
        if not fspath.startswith('/'):
            fspath = f'{fspath}'

        async with self.manager._lock():
            try:
                ret: PalmSens.Data.DeviceFile = await create_future(
                    self._client_connection.GetDeviceFileAsync(fspath)
                )
            except System.Exception as exc:
                # Error codes:
                # https://dev.palmsens.com/methodscript/latest/methodscript/methodscript_main.html#app_err_error_codes
                raise FileSystemException(exc.Message) from exc

        path._cached_device_file = ret  # type: ignore
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

    async def exists(self, path: str | DevicePath) -> bool:
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
        path = DevicePath(path)

        node = await self.tree()

        *dirs, leaf = path.parts

        for drc in dirs:
            if drc not in node:
                return False

            node = node[drc]

        if ('_files' in node) and (leaf in node['_files']):
            return True

        return leaf in node

    async def load_measurement(self, path: str | DevicePath) -> Measurement:
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
        f = await self._get_device_file(path)

        async with self.manager._lock():
            psmeasurement: PalmSens.Measurement = await create_future(
                self._client_connection.LoadDeviceFileAsync(f)
            )

        return Measurement(psmeasurement=psmeasurement)

    async def remove(self, path: str | DevicePath) -> None:
        """Remove a file from the device.

        Parameters
        ----------
        path : str | DevicePath
            The file path to remove.
        """
        if isinstance(path, str):
            path = DevicePath(path)

        async with self.manager._lock():
            await create_future(
                self._client_connection.DeleteDeviceFileAsync(path.__fspath__())
            )

    async def delete_all_files(self, confirm: bool = False) -> None:
        """Delete all files on the device.

        Parameters
        ----------
        confirm : bool, optional
            If True, clear all files on the device. Default is False.
            This acts as a sentinel to avoid accidental deletes in
            interactive REPL or Jupyter environments.
        """
        if confirm:
            async with self.manager._lock():
                await create_future(self._client_connection.ClearDeviceFilesAsync())

    async def free(self) -> int:
        """Return free space on filesystem.

        Returns
        -------
        int
            Free space in kB (1 kB = 1024 bytes).
        """
        async with self.manager._lock():
            return await create_future(self._client_connection.GetDeviceFreeAsync())

    async def size(self) -> int:
        """Return total size of filesystem.

        Returns
        -------
        int
            Total size in kB (1 kB = 1024 bytes).
        """
        async with self.manager._lock():
            return await create_future(self._client_connection.GetDeviceSizeAsync())

    async def timestamp_of(self, path: str | DevicePath) -> str:
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
        f = await self._get_device_file(path)

        return f.Timestamp.ToString('s', System.Globalization.CultureInfo.InvariantCulture)

    async def size_of(self, path: str | DevicePath) -> int:
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
        f = await self._get_device_file(path)

        return f.Size

    async def read_text(self, path: DevicePath) -> str:
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
        f = await self._get_device_file(path)

        return f.Content

    async def tree(self, directory: DevicePath | str | None = None) -> dict[str, Any]:
        """Build a nested dictionary representing the device directory structure.

        Parameters
        ----------
        directory : DevicePath | str | None, optional
            The directory to inspect. Defaults to the root directory.

        Returns
        -------
        dict[str, Any]
            A nested dict where keys are directory names and ``'_files'``
            contains a list of filenames at each level.
        """
        paths = await self.listdir(directory)

        root: dict[str, Any] = {}

        for path in paths:
            *parts, filename = path.parts

            node = root
            for part in parts:
                node = node.setdefault(part, {})

            node.setdefault('_files', [])
            node['_files'].append(filename)

        return root

    async def listdir(self, directory: DevicePath | str | None = None) -> list[DevicePath]:
        """Iterate over entries in a device directory.

        Parameters
        ----------
        directory : DevicePath | str | None, optional
            The directory to iterate. Defaults to the root directory.

        Returns
        -------
        list[DevicePath]
            Path objects for each entry in the directory.
        """
        if not directory:
            directory = self.root

        if isinstance(directory, str):
            directory = DevicePath(directory)

        async with self.manager._lock():
            ret: list[PalmSens.Data.DeviceFile] = await create_future(
                self._client_connection.GetDeviceFilesAsync(directory.__fspath__())
            )

        paths = [DevicePath(f.Dir, f.Name) for f in ret]
        return paths
