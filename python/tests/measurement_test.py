from pathlib import Path

import pytest

from pspython.pspyfiles import load_session_file

DATA_FILE = Path(__file__).parents[1] / 'Demo CV DPV EIS IS-C electrode.pssession'


@pytest.fixture
def measurements():
    return load_session_file(
        str(DATA_FILE),
    )


def test_measurement(measurements):
    m = measurements[0]

    assert m.title == 'Differential Pulse Voltammetry'
    assert isinstance(m.timestamp, str)
    assert len(m.current_arrays[0]) == 219
    assert len(m.potential_arrays[0]) == 219
    assert len(m.time_arrays[0]) == 219

    assert len(m.freq_arrays) == 0
    assert len(m.zre_arrays) == 0
    assert len(m.zim_arrays) == 0
    assert len(m.aux_input_arrays) == 0

    assert len(m.peaks) == 1
    assert len(m.eis_fit) == 0
    assert len(m.curves) == 1
