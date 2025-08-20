from __future__ import annotations

from attrs import asdict
from pytest import approx

from pypalmsens import (
    load_method_file,
    load_session_file,
    save_method_file,
    save_session_file,
)
from pypalmsens.methods import techniques


def test_save_load_session(tmpdir, data_dpv):
    path = tmpdir / 'test.pssession'

    save_session_file(path=path, measurements=data_dpv)

    data_dpv2 = load_session_file(path=path)

    assert len(data_dpv2) == len(data_dpv)

    meas = data_dpv[0]
    meas2 = data_dpv2[0]

    assert meas2.method.filename == path
    assert meas2.method.filename.is_absolute()

    assert meas == meas2
    assert meas.timestamp == meas2.timestamp
    assert meas.title == meas2.title
    assert meas.device == meas2.device


def test_save_load_method(tmpdir):
    path = tmpdir / 'test.psmethod'
    cv = techniques.CyclicVoltammetry()
    save_method_file(path=path, method=cv)

    method_cv2 = load_method_file(path=path, as_method=True)

    assert method_cv2.filename == path

    cv2 = method_cv2.to_parameters()

    cv_dict = asdict(cv)
    cv2_dict = asdict(cv2)

    for k, v in cv_dict.items():
        assert k in cv2_dict
        v2 = cv2_dict[k]
        if isinstance(v, float):
            # work around for floating point rounding error on round-trip
            assert v2 == approx(v)
        else:
            assert v == v2
