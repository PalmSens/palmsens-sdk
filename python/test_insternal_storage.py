from __future__ import annotations

import posixpath
from contextlib import contextmanager
from pathlib import PurePath
from typing import Generator, Iterator, Self

from typing_extensions import override

import pypalmsens as ps
from pypalmsens.data import Measurement

if True:
    import PalmSens
    import System
    from System.IO import MemoryStream

manager = ps.connect()

storage = manager.internal_storage()


def internal_storage(manager: ps.InstrumentManager) -> DevicePath:
    return DevicePath('', manager=manager)


@contextmanager
def memory_reader(*args, **kwargs) -> Generator[MemoryStream]:
    mr = MemoryStream(*args, **kwargs)
    try:
        yield mr
    finally:
        mr.Close()


class DevicePath(PurePath):
    parser = posixpath

    def __init__(self, *pathsegments, manager: ps.InstrumentManager):
        super().__init__(*pathsegments)
        self.manager = manager

    def __repr__(self) -> str:
        return f"{type(self).__name__}('{self}', manager={self.manager.instrument.name})"

    def __str__(self):
        """Return the string representation of the path, suitable for
        passing to system calls."""
        try:
            return self._str
        except AttributeError:
            self._str = self._format_parsed_parts(self.drive, self.root, self._tail) or ''
            return self._str

    @property
    def _client_connection(self):
        return self.manager._comm.ClientConnection

    def _get_device_file(self) -> PalmSens.Data.DeviceFile:
        try:
            return self._f
        except AttributeError:
            with self.manager._lock():
                self._f = self._client_connection.GetDeviceFile(self.__fspath__())
            return self._f

    @override
    def with_segments(self, *pathsegments):
        return type(self)(*pathsegments, manager=self.manager)

    def exists(self): ...

    def glob(self): ...

    def is_dir(self) -> bool:
        f = self._get_device_file()
        return f.Type.value__ == 1

    def is_file(self) -> bool:
        f = self._get_device_file()
        return f.Type.value__ == 0

    def iterdir(self) -> Iterator[Self]:
        with manager._lock():
            ret = self._client_connection.GetDeviceFiles(self.__fspath__())

        for f in ret:
            new = self.with_segments(f.Dir, f.Name)
            yield new

    @property
    def timestamp(self) -> str:
        """Return timestamp in isoformat."""
        f = self._get_device_file()

        return f.Timestamp.ToString('s', System.Globalization.CultureInfo.InvariantCulture)

    @property
    def size(self) -> int:
        """Return file size in bytes."""
        f = self._get_device_file()

        return f.Size

    def load_measurement(self) -> Measurement:
        f = self._get_device_file()

        psmeasurement = self._client_connection.LoadDeviceFile(f)

        return Measurement(psmeasurement=psmeasurement)

    def read_bytes(self) -> bytes:
        f = self._get_device_file()

        return f.Content.encode()

    def read_text(self) -> str:
        f = self._get_device_file()

        return f.Content

    def remove(self):
        with self.manager._lock():
            self._client_connection.DeleteDeviceFile(self.__fspath__())


# 'unlink',
# 'absolute',
# 'chmod',
# 'copy_into',
# 'cwd',
# 'expanduser',
# 'from_uri',
# 'group',
# 'hardlink_to',
# 'is_block_device',
# 'is_char_device',
# 'is_fifo',
# 'is_junction',
# 'is_mount',
# 'is_socket',
# 'is_symlink',
# 'move_into',
# 'owner',
# 'resolve',
# 'rglob',
# 'samefile',
# 'symlink_to',
# 'touch',
# 'unlink',


root = DevicePath(manager=manager)

files = list(root.iterdir())

lsv = files[4]


breakpoint()
