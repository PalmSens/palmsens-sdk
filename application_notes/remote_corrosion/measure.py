# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pypalmsens>=1.8",
#   "numpy",
# ]
# ///

from pathlib import Path

import numpy as np
import pypalmsens as ps

this_dir = Path(__file__).parent
data_dir = Path("/var/www/html/")

method = ps.LinearSweepVoltammetry(
    begin_potential=-0.1,
    end_potential=0.1,
    step_potential=0.005,
    scanrate=0.02,
    versus_ocp={
        "max_ocp_time": 5.0,
        "mode": 3,
    },
)

measurement = ps.measure(method)

current = measurement.dataset["Current"]
potential = measurement.dataset["Potential"]

p, (resid, *_) = np.polynomial.Polynomial.fit(current, potential, 1, full=True)
p = p.convert()

_, slope = p.coef
rp = float(slope)

timestamp = measurement.timestamp

dct = {
    "timestamp": measurement.timestamp,
    "rp": rp,
    "ocp": measurement.ocp_value,
    "residual": float(np.squeeze(resid)),
}

datafile = data_dir / "data.csv"

write_header = not datafile.exists()

with open(datafile, "a") as f:
    if write_header:
        f.write(",".join(dct.keys()))
        f.write("\n")

    f.write(",".join(str(item) for item in dct.values()))
    f.write("\n")

print(timestamp, "OK")
