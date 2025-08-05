from __future__ import annotations

import numpy as np


def single_to_double(val: float) -> float:
    """Cast single precision to double precision.

    Pythonnet returns System.Single, whereas python defaults to double precision.
    This leads to incorrect rounding, which makes comparing values difficult.

    By going through np.float32/str we can correctly round back to python float
    (which is double precision)."""
    return float(str(np.float32(val)))
