from __future__ import annotations

import atexit
from importlib.resources import files
from pathlib import Path

import pythonnet

PSSDK_DIR = files('pypalmsens._libpalmsens.win')


def unblock(path: Path):
    """Unblock DLL: https://stackoverflow.com/q/20886450"""
    zone_id = path.with_name(path.name + ':Zone.Identifier')
    zone_id.unlink(missing_ok=True)


def load() -> str:
    """Load .NET platform dependencies and init SDK.

    Returns
    -------
    str
        Version of the PalmSens .NET SDK."""

    # runtime must be imported before clr is loaded
    pythonnet.load('coreclr', runtime_config=str(PSSDK_DIR / 'runtimeconfig.json'))

    import clr

    core_dll = PSSDK_DIR / 'PalmSens.Core.dll'
    core_windows_dll = PSSDK_DIR / 'PalmSens.Core.Windows.dll'

    assert isinstance(core_dll, Path)
    assert isinstance(core_windows_dll, Path)

    assert core_dll.exists()
    assert core_windows_dll.exists()

    for dll in (core_dll, core_windows_dll):
        unblock(dll)

    # This dll contains the classes in which the data is stored
    clr.AddReference(str(core_dll.with_suffix('')))

    # This dll is used to load your session file
    clr.AddReference(str(core_windows_dll.with_suffix('')))

    clr.AddReference('System')

    from PalmSens.Core.Windows import CoreDependencies

    CoreDependencies.Init()

    from System import Diagnostics

    return Diagnostics.FileVersionInfo.GetVersionInfo(str(core_dll)).ProductVersion


unload = pythonnet.unload

atexit.register(pythonnet.unload)

__all__ = ['load', 'unload']
