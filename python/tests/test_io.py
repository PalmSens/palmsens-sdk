from __future__ import annotations

from pathlib import Path

import pytest
from pytest import approx

import pypalmsens as ps


def test_save_load_session(tmpdir, measurement_dpv):
    path = tmpdir / 'test.pssession'

    session = [measurement_dpv]

    ps.save_session_file(path=path, measurements=session)

    session2 = ps.load_session_file(path=path)

    assert len(session) == len(session2)

    measurement_dpv2 = session2[0]

    method_filename = Path(measurement_dpv2._psmeasurement.Method.MethodFilename)
    assert method_filename == path
    assert method_filename.is_absolute()

    assert len(measurement_dpv.dataset) == len(measurement_dpv2.dataset) == 0
    assert measurement_dpv.n_curves == measurement_dpv2.n_curves == 1
    assert measurement_dpv.curves[0].n_points == measurement_dpv2.curves[0].n_points
    assert measurement_dpv.timestamp == measurement_dpv2.timestamp
    assert measurement_dpv.title == measurement_dpv2.title
    assert measurement_dpv.device == measurement_dpv2.device


def test_load_session_file_not_found():
    with pytest.raises(FileNotFoundError):
        _ = ps.load_method_file('foo.bar')


def test_save_load_measurement(tmpdir, measurement_dpv):
    path = tmpdir / 'test.psmethod'

    ps.save_measurement(path, measurement_dpv)

    meas2 = ps.load_measurement(path)

    assert len(measurement_dpv.dataset) == len(meas2.dataset) == 0
    assert measurement_dpv.n_curves == meas2.n_curves == 1
    assert measurement_dpv.curves[0].n_points == meas2.curves[0].n_points
    assert measurement_dpv.timestamp == meas2.timestamp
    assert measurement_dpv.title == meas2.title
    assert measurement_dpv.device == meas2.device


def test_save_load_measurement_fail(tmpdir, measurement_dpv, measurement_cv):
    path = tmpdir / 'test_multiple.psmethod'

    ps.save_session_file(path, [measurement_dpv, measurement_cv])

    with pytest.raises(ValueError):
        _ = ps.load_measurement(path)

    with pytest.raises(TypeError):
        ps.save_measurement(path, [measurement_dpv, measurement_cv])


def test_save_session_file_empty():
    with pytest.raises(ValueError):
        ps.save_session_file('test.pssession', [])


def test_save_load_method(tmpdir):
    path = tmpdir / 'test.psmethod'
    cv = ps.CyclicVoltammetry()
    ps.save_method_file(path=path, method=cv)

    method_cv2 = ps._io._load_method_file(path=path)

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


def test_load_method_file_not_found():
    with pytest.raises(FileNotFoundError):
        _ = ps.load_method_file('foo.bar')


def test_serialize():
    cv = ps.CyclicVoltammetry()
    s = cv._serialize()

    assert s.startswith('#PyPalmSens,')
