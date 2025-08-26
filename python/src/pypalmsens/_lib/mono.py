from __future__ import annotations

import atexit
import platform
from importlib.resources import files
from pathlib import Path

from pythonnet import load, unload

PSSDK_DIR = files('pypalmsens._pssdk.mono')

# runtime must be imported before clr is loaded
load('coreclr', runtime_config=str(PSSDK_DIR / 'runtimeconfig.json'))

import clr  # noqa: E402

core_dll = PSSDK_DIR / 'PalmSens.Core.dll'
core_linux_dll = PSSDK_DIR / 'PalmSens.Core.Linux.dll'

RUNTIME_DIR = files('pypalmsens._runtimes')

system = platform.system()  # Windows, Linux, Darwin
machine = platform.machine()  # AMD64, x86_64, arm64

# Select the correct version of the SerialPort library
# To use serial devices the correct version of the libSystem.IO.Ports.Native.so
# library must be loaded to into pythonnet.
PLATFORMS = {
    ('Linux', 'x86_64'): 'linux-x64',
    ('Linux', 'arm'): 'linux-arm',
    ('Linux', 'aarch'): 'linux-arm',
    ('Linux', 'arm64'): 'linux-arm64',
    ('Linux', 'aarch64'): 'linux-arm64',
    ('Darwin', 'arm64'): 'osx-arm64',
    ('Darwin', 'x86_64'): 'osx-x64',
}

plat = PLATFORMS[system, machine]

ioports_dll = RUNTIME_DIR / plat / 'native' / 'System.IO.Ports.dll'

assert isinstance(core_dll, Path)
assert isinstance(core_linux_dll, Path)
assert isinstance(ioports_dll, Path)

# This dll contains the classes in which the data is stored
clr.AddReference(str(core_dll.with_suffix('')))

# This dll is used to load your session file
clr.AddReference(str(core_linux_dll.with_suffix('')))

clr.AddReference(str(ioports_dll.with_suffix('')))

clr.AddReference('System')

from PalmSens.Core.Linux import CoreDependencies  # noqa: E402
from System import Diagnostics  # noqa: E402

CoreDependencies.Init()

sdk_version = Diagnostics.FileVersionInfo.GetVersionInfo(str(core_dll)).ProductVersion

atexit.register(unload)
