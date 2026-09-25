from __future__ import annotations

import os
import platform
from importlib.resources import files
from pathlib import Path

import pythonnet

# On Linux (mono), the difference is in the version of the SerialPort library
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
    ('Windows', 'AMD64'): 'win',
}

PLATFORM = PLATFORMS[
    platform.system(),  # Windows, Linux, Darwin
    platform.machine(),  # AMD64, x86_64, arm64
]

PSSDK_DIR = files(f'pypalmsens._libpalmsens.{PLATFORM}')
LABLINK_DIR = os.getenv('LABLINK_SDK')


def unblock(path: Path):
    """Unblock DLL: https://stackoverflow.com/q/20886450

    Windows only."""
    zone_id = path.with_name(path.name + ':Zone.Identifier')
    zone_id.unlink(missing_ok=True)


def load_lablink(dll_path: Path, *, clr):
    assert PLATFORM == 'win'
    assert dll_path.exists()

    sdk_data = dll_path / 'PalmSens.Sdk.Data.dll'
    sdk_lablink = dll_path / 'PalmSens.Sdk.Lablink.Example.dll'

    assert isinstance(sdk_data, Path)
    assert isinstance(sdk_lablink, Path)

    assert sdk_data.exists()
    assert sdk_lablink.exists()

    unblock(sdk_data)
    unblock(sdk_lablink)

    clr.AddReference(str(sdk_data.with_suffix('')))
    clr.AddReference(str(sdk_lablink.with_suffix('')))


def load() -> str:
    """Load .NET platform dependencies and init SDK.

    Returns
    -------
    str
        Version of the PalmSens .NET SDK.
    """

    try:
        # runtime must be loaded before `clr` is imported
        pythonnet.load('coreclr', runtime_config=str(PSSDK_DIR / 'runtimeconfig.json'))
    except RuntimeError as e:
        e.add_note(
            '\nThis error usually means the .NET runtime could not be found. '
            '\nPyPalmSens requires .NET 10 or newer. '
            '\n\nLearn more: https://dev.palmsens.com/python/latest/_attachments/installation/'
        )
        raise

    import clr

    tag = 'Windows' if PLATFORM == 'win' else 'Linux'

    core_dll = PSSDK_DIR / 'PalmSens.Core.dll'
    core_platform_dll = PSSDK_DIR / f'PalmSens.Core.{tag}.dll'

    assert isinstance(core_dll, Path)
    assert isinstance(core_platform_dll, Path)

    assert core_dll.exists()
    assert core_platform_dll.exists()

    if PLATFORM == 'win':
        unblock(core_dll)
        unblock(core_platform_dll)

    clr.AddReference(str(core_dll.with_suffix('')))
    clr.AddReference(str(core_platform_dll.with_suffix('')))

    clr.AddReference('System')

    if LABLINK_DIR:
        load_lablink(Path(LABLINK_DIR), clr=clr)

    if PLATFORM == 'win':
        from PalmSens.Windows import CoreDependencies
    else:
        from PalmSens.Core.Linux import CoreDependencies

    CoreDependencies.Init()

    from System import Diagnostics

    return Diagnostics.FileVersionInfo.GetVersionInfo(str(core_dll)).ProductVersion
