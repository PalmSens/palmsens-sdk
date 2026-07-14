from __future__ import annotations

import pypalmsens as ps

if __name__ == '__main__':
    manager = ps.connect()

    with ps.DeviceFileSystem(manager) as fs:
        files = list(fs.iterdir())
        path = files[0]
        measurement = fs.load_measurement(path)

    print(measurement.curves)

    instrument = ps.discover()[0]
