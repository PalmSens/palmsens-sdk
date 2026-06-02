from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import pytest
from pydantic import TypeAdapter

import pypalmsens as ps
from pypalmsens._data.curve import CurveMetadata
from pypalmsens._data.eisdata import EISDataMetadata
from pypalmsens._data.measurement import MeasurementMetadata
from pypalmsens._instruments.callback import DataRow
from pypalmsens.types import MethodTypeCompatible


def _test_stream(path: Path, method: MethodTypeCompatible):
    with ps.connect() as manager:
        measurement = manager.measure(
            method,
            stream=Path(path),
        )

    assert measurement

    assert path.exists()
    lines = path.read_text(encoding='utf-8').splitlines()

    assert lines

    curves = defaultdict(list)
    curves_metadata = {}
    measurement_metadata = None

    for i, line in enumerate(lines):
        parsed: Any = TypeAdapter(MeasurementMetadata | CurveMetadata | DataRow).validate_json(
            line
        )

        if isinstance(parsed, DataRow):
            curves[parsed.id].append(parsed)
        elif isinstance(parsed, CurveMetadata):
            curves_metadata[parsed.id] = parsed
        elif isinstance(parsed, MeasurementMetadata):
            measurement_metadata = parsed
            assert i == 0
        else:
            raise ValueError(f'This should not happen: {parsed}')

    assert measurement_metadata

    assert len(curves) == len(curves_metadata) == len(measurement.curves)
    assert set(curves) == set(curves_metadata)

    for curve in measurement.curves:
        hash = curve._pscurve.GetHashCode()

        metadata = curves_metadata[hash]
        assert metadata.title == curve.title
        assert metadata.units[0] == curve.x_unit
        assert metadata.units[1] == curve.y_unit

        data = np.array([point.data for point in curves[hash]])

        np.testing.assert_allclose(data[:, 0], curve.x_array)
        np.testing.assert_allclose(data[:, 1], curve.y_array)

    return measurement


@pytest.mark.instrument
def test_measure_stream_cv_multiple_scans(tmpdir):
    path = Path('cv.jsonl')

    method = ps.CyclicVoltammetry(
        n_scans=3,
        step_potential=0.15,
        scanrate=5,
        # use a fixed current range
        # because Measurement seems to do a post-processing step in a different CR ?
        current_range='1uA',
    )

    _ = _test_stream(method=method, path=path)


@pytest.mark.instrument
def test_measure_stream_cp_with_aux(tmpdir):
    path = tmpdir / 'cp.jsonl'

    method = ps.ChronoPotentiometry(
        run_time=3,
        record_auxiliary_input=True,
        record_we_current=True,
    )

    _ = _test_stream(method=method, path=path)


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

    with ps.connect() as manager:
        measurement = manager.measure(
            method,
            stream=Path(path),
        )

    assert measurement

    assert path.exists()
    lines = path.read_text(encoding='utf-8').splitlines()

    assert lines

    eis_data_points = defaultdict(list)
    eis_data = {}
    measurement_metadata = None

    for i, line in enumerate(lines):
        parsed = TypeAdapter(MeasurementMetadata | EISDataMetadata | DataRow).validate_json(
            line
        )

        if isinstance(parsed, DataRow):
            eis_data_points[parsed.id].append(parsed)
        elif isinstance(parsed, EISDataMetadata):
            eis_data[parsed.id] = parsed
        elif isinstance(parsed, MeasurementMetadata):
            measurement_metadata = parsed
            # This is a quirk of EIS measurements
            # EISDataEvent is always after the first EISData.NewDataEvent
            assert i == 1
        else:
            raise ValueError(f'This should not happen: {parsed}')

    assert measurement_metadata

    assert len(eis_data_points) == len(eis_data) == len(measurement.eis_data)
    assert set(eis_data_points) == set(eis_data)

    for eis in measurement.eis_data:
        hash = eis._pseis.GetHashCode()

        metadata = eis_data[hash]
        assert metadata.title == eis.title
        assert metadata.n_frequencies == eis.n_frequencies
        assert metadata.frequency_type == eis.frequency_type
        assert metadata.scan_type == eis.scan_type

        points = eis_data_points[hash]

        assert len(points) == eis.n_points

        columns = list(metadata.columns)

        arrays = {array.name: array for array in eis.arrays()}

        data = np.array([point.data for point in points])

        for i, col in enumerate(columns):
            ref_array = arrays[col]

            assert ref_array.name == metadata.columns[i]
            assert ref_array.unit == metadata.units[i]
            assert ref_array.quantity == metadata.quantities[i]

            np.testing.assert_allclose(data[:, i], ref_array)
