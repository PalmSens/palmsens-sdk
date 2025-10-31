from __future__ import annotations

import atexit
from importlib.resources import files
from pathlib import Path

import clr
import pythonnet

PSSDK_DIR = files('pypalmsens._libpalmsens.win')

core_dll = PSSDK_DIR / 'PalmSens.Core.dll'
ble_dll = PSSDK_DIR / 'PalmSens.Core.Windows.BLE.dll'


def unblock(path: Path):
    """Unblock DLL: https://stackoverflow.com/q/20886450"""
    zone_id = path.with_name(path.name + ':Zone.Identifier')
    if zone_id.exists():
        zone_id.unlink()


def load() -> str:
    """Load .NET platform dependencies and init SDK.

    Returns
    -------
    str
        Version of the PalmSens .NET SDK."""
    for dll in (core_dll, ble_dll):
        assert isinstance(dll, Path)
        unblock(dll)

    # This dll contains the classes in which the data is stored
    clr.AddReference(str(core_dll))

    # This dll is used to load your session file
    clr.AddReference(str(ble_dll))

    clr.AddReference('System')

    from PalmSens.Windows import CoreDependencies  # noqa: E402

    CoreDependencies.Init()

    from System import Diagnostics  # noqa: E402

    return Diagnostics.FileVersionInfo.GetVersionInfo(str(core_dll)).ProductVersion


atexit.register(pythonnet.unload)

unload = pythonnet.unload

__all__ = ['load', 'unload']
