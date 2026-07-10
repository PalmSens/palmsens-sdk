from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

import pypalmsens as ps
from pypalmsens.types import MethodTypeCompatible


def _test_stream(path: Path, method: MethodTypeCompatible):
    with ps.connect() as manager:
        measurement_ref = manager.measure(
            method,
            stream=Path(path),
        )

    assert path.exists()

    measurement = ps.load_stream_file(path)

    curves = measurement.curves

    assert len(curves) == len(measurement_ref.curves)

    for curve, reference_curve in zip(measurement.curves, measurement_ref.curves):
        assert curve.metadata.title == reference_curve.title
        assert curve.metadata.units[0] == reference_curve.x_unit
        assert curve.metadata.units[1] == reference_curve.y_unit

        x, y = zip(*curve.data)

        np.testing.assert_allclose(x, reference_curve.x_array)
        np.testing.assert_allclose(y, reference_curve.y_array)

    for eis, eis_ref in zip(measurement.eis_data, measurement_ref.eis_data):
        assert eis.metadata.title == eis_ref.title
        assert eis.metadata.n_frequencies == eis_ref.n_frequencies
        assert eis.metadata.frequency_type == eis_ref.frequency_type
        assert eis.metadata.scan_type == eis_ref.scan_type

        assert len(eis.data) == eis_ref.n_points

        columns = list(eis.metadata.columns)

        arrays_ref = {array.name: array for array in eis_ref.arrays()}

        data = np.array(eis.data)

        for i, col in enumerate(columns):
            array_ref = arrays_ref[col]

            assert array_ref.name == eis.metadata.columns[i]
            assert array_ref.unit == eis.metadata.units[i]
            assert array_ref.quantity == eis.metadata.quantities[i]

            np.testing.assert_allclose(data[:, i], array_ref)

    return measurement


@pytest.mark.instrument
def test_measure_stream_cv_multiple_scans(tmpdir):
    path = tmpdir / 'cv.jsonl'

    method = ps.CyclicVoltammetry(
        n_scans=3,
        step_potential=0.15,
        scanrate=5,
        # use a fixed current range
        # because Measurement seems to do a post-processing step in a different CR ?
        current_range='1mA',
    )

    measurement = _test_stream(method=method, path=path)

    assert len(measurement.curves) == method.n_scans
    assert not measurement.eis_data


@pytest.mark.instrument
def test_measure_stream_cp_with_aux(tmpdir):
    path = tmpdir / 'cp.jsonl'

    method = ps.ChronoPotentiometry(
        run_time=3,
        record_auxiliary_input=True,
        record_we_current=True,
    )

    measurement = _test_stream(method=method, path=path)

    assert len(measurement.curves) == 3  # V, aux, we
    assert not measurement.eis_data


@pytest.mark.instrument
def test_measure_stream_eis(tmpdir):
    path = tmpdir / 'eis.jsonl'

    method = ps.ElectrochemicalImpedanceSpectroscopy(
        n_frequencies=3,
        begin_potential=0.5,
        step_potential=0.1,
        end_potential=1.0,
        min_sampling_time=0.01,
        scan_type='potential',
    )

    measurement = _test_stream(method=method, path=path)

    assert not measurement.curves
    assert len(measurement.eis_data) == 1
