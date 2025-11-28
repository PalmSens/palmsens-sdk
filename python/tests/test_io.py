from __future__ import annotations

from pytest import approx

import pypalmsens as ps


def test_save_load_session(tmpdir, data_dpv):
    path = tmpdir / 'test.pssession'

    ps.save_session_file(path=path, measurements=data_dpv)

    data_dpv2 = ps.load_session_file(path=path)

    assert len(data_dpv2) == len(data_dpv)

    meas = data_dpv[0]
    meas2 = data_dpv2[0]

    assert meas2.method.filename == path
    assert meas2.method.filename.is_absolute()

    assert len(meas.dataset) == len(meas2.dataset) == 0
    assert meas.n_curves == meas2.n_curves == 1
    assert meas.curves[0].n_points == meas2.curves[0].n_points
    assert meas.timestamp == meas2.timestamp
    assert meas.title == meas2.title
    assert meas.device == meas2.device


def test_save_load_method(tmpdir):
    path = tmpdir / 'test.psmethod'
    cv = ps.CyclicVoltammetry()
    ps.save_method_file(path=path, method=cv)

    method_cv2 = ps.load_method_file(path=path, as_method=True)

    assert method_cv2.filename == path

    cv2 = method_cv2.to_settings()

    cv_dict = cv.to_dict()
    cv2_dict = cv2.to_dict()

    for k, v in cv_dict.items():
        assert k in cv2_dict
        v2 = cv2_dict[k]
        if isinstance(v, float):
            # work around for floating point rounding error on round-trip
            assert v2 == approx(v)
        else:
            assert v == v2
