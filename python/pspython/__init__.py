import os

import clr

# Load DLLs
scriptDir = os.path.dirname(os.path.realpath(__file__))
# This dll contains the classes in which the data is stored
clr.AddReference(scriptDir + '/PalmSens.Core.dll')
# This dll is used to load your session file
clr.AddReference(scriptDir + '/PalmSens.Core.Windows.BLE.dll')
clr.AddReference('System')

from PalmSens.Windows import CoreDependencies  # type: ignore  # noqa: E402

CoreDependencies.Init()
