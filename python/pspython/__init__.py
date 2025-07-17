import atexit
from pathlib import Path

import clr
from pythonnet import unload

script_dir = Path(__file__).parent

# This dll contains the classes in which the data is stored
clr.AddReference(str(script_dir / 'PalmSens.Core.dll'))

# This dll is used to load your session file
clr.AddReference(str(script_dir / 'PalmSens.Core.Windows.BLE.dll'))

clr.AddReference('System')

from PalmSens.Windows import CoreDependencies  # type: ignore  # noqa: E402

CoreDependencies.Init()

atexit.register(unload)
