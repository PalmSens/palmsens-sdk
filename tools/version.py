# /// script
# dependencies = [
#   "pythonnet",
# ]
# ///

from __future__ import annotations

import json
import sys
from pathlib import Path
import platform

ROOT = Path(__file__).parents[1]

if platform.system() != "Windows":
    import pythonnet

    pythonnet.load("coreclr", runtime_config=str(ROOT / "tools" / "runtimeconfig.json"))

import clr  # noqa: E402

clr.AddReference("System")

from System import Diagnostics  # noqa: E402


def version(write_json=False):
    dirs = (
        ROOT / "python" / "src",
        ROOT / "matlab",
        ROOT / "labview",
        ROOT / "winforms",
    )

    directories = {}

    for drc in dirs:
        assert drc.exists()
        paths = drc.glob("**/PalmSens*.dll")

        for path in paths:
            version = Diagnostics.FileVersionInfo.GetVersionInfo(
                str(path)
            ).ProductVersion

            if path.parent not in directories:
                directories[path.parent] = {}

            directories[path.parent][path.name] = version

    for drc, data in directories.items():
        if write_json:
            with open(drc / "version.json", "w") as f:
                json.dump(data, f, indent=4)

        else:
            print(drc)
            for file, value in data.items():
                print(f"- {file}: {value}")
            print()


if __name__ == "__main__":
    write_json = "json" in sys.argv

    version(write_json=write_json)
