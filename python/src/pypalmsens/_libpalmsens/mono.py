from __future__ import annotations

import atexit
import platform
from importlib.resources import files
from pathlib import Path

import pythonnet

# Select the correct version of the SerialPort library
# To use serial devices the correct version of the libSystem.IO.Ports.Native.so
# library must be loaded to into pythonnet.
PLATFORMS = {
    ('Linux', 'x86_64'): 'linux-x64',
    # ('Linux', 'arm'): 'linux-arm',
    # ('Linux', 'aarch'): 'linux-arm',
    ('Linux', 'arm64'): 'linux-arm64',
    ('Linux', 'aarch64'): 'linux-arm64',  # raspberrypi / raspbian
    ('Darwin', 'arm64'): 'osx-arm64',
    ('Darwin', 'x86_64'): 'osx-x64',
}

PLATFORM = PLATFORMS[
    platform.system(),  # Windows, Linux, Darwin
    platform.machine(),  # AMD64, x86_64, arm64
]

PSSDK_DIR = files(f'pypalmsens._libpalmsens.{PLATFORM}')


def load() -> str:
    """Load .NET platform dependencies and init SDK.

    Returns
    -------
    str
        Version of the PalmSens .NET SDK."""

    # runtime must be imported before clr is loaded
    pythonnet.load('coreclr', runtime_config=str(PSSDK_DIR / 'runtimeconfig.json'))

    import clr  # noqa: E402

    core_dll = PSSDK_DIR / 'PalmSens.Core.dll'
    core_linux_dll = PSSDK_DIR / 'PalmSens.Core.Linux.dll'

    assert isinstance(core_dll, Path)
    assert isinstance(core_linux_dll, Path)

    assert core_dll.exists()
    assert core_linux_dll.exists()

    # This dll contains the classes in which the data is stored
    clr.AddReference(str(core_dll.with_suffix('')))

    # This dll is used to load your session file
    clr.AddReference(str(core_linux_dll.with_suffix('')))

    clr.AddReference('System')

    from PalmSens.Core.Linux import CoreDependencies  # noqa: E402

    CoreDependencies.Init()

    from System import Diagnostics  # noqa: E402

    return Diagnostics.FileVersionInfo.GetVersionInfo(str(core_dll)).ProductVersion


unload = pythonnet.unload

atexit.register(pythonnet.unload)

__all__ = ['load', 'unload']
