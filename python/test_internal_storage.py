from __future__ import annotations

import pypalmsens as ps
from pypalmsens._instruments import DeviceFileSystem

if True:
    pass


if __name__ == '__main__':
    manager = ps.connect()

    fs = DeviceFileSystem(manager)

    files = list(fs.iterdir())

    path = files[0]

    measurement = fs.load_measurement(path)

    print(measurement.curves)
