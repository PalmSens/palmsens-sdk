from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from pydantic import Field, TypeAdapter
from pydantic.dataclasses import dataclass
from typing_extensions import override

from pypalmsens._data.curve import CurveMetadata
from pypalmsens._data.eisdata import EISDataMetadata
from pypalmsens._data.measurement import MeasurementMetadata
from pypalmsens._instruments.callback import DataRow


@dataclass
class Curve:
    metadata: CurveMetadata
    data: list[list[float | int]] = Field(default_factory=list)

    @override
    def __repr__(self):
        return f'{type(self).__name__}({self.metadata.title}, n_points={len(self.data)})'


@dataclass
class EISData:
    metadata: EISDataMetadata
    data: list[list[float | int]] = Field(default_factory=list)

    @override
    def __repr__(self):
        return f'{type(self).__name__}({self.metadata.title}, n_points={len(self.data)})'


@dataclass
class Measurement:
    metadata: MeasurementMetadata
    curves: list[Curve] = Field(default_factory=list)
    eis_data: list[EISData] = Field(default_factory=list)

    @override
    def __repr__(self):
        return f'{type(self).__name__}({self.metadata.title}, timestamp={self.metadata.timestamp}, device={self.metadata.device.type})'


def load_stream_file(path: str | Path) -> Measurement:
    """Load JSON lines (filetype: jsonl) stream file.

    See also: https://jsonlines.org/

    Returns
    -------
    measurement : Measurement
        Dataclass containing data from jsonl file.
        The data structure mimicks `pypalmsens.data.measurement`.

    """
    measurement_metadata = None

    data_rows = defaultdict(list)
    curves_metadata = {}
    eisdatas_metadata = {}

    with open(path, encoding='utf-8') as lines:
        for i, line in enumerate(lines):
            parsed: Any = TypeAdapter(
                DataRow | CurveMetadata | EISDataMetadata | MeasurementMetadata
            ).validate_json(line)

            if isinstance(parsed, DataRow):
                data_rows[parsed.id].append(parsed.data)
            elif isinstance(parsed, CurveMetadata):
                curves_metadata[parsed.id] = parsed
            elif isinstance(parsed, MeasurementMetadata):
                measurement_metadata = parsed
            elif isinstance(parsed, EISDataMetadata):
                eisdatas_metadata[parsed.id] = parsed
            else:
                raise ValueError(f'Could not parse line {i}: {parsed}')

    assert measurement_metadata

    measurement = Measurement(metadata=measurement_metadata)

    for curve_id, curve_metadata in curves_metadata.items():
        data = [row for row in data_rows[curve_id]]
        curve = Curve(metadata=curve_metadata, data=data)
        measurement.curves.append(curve)

    for eisdata_id, eisdata_metadata in eisdatas_metadata.items():
        data = [row for row in data_rows[eisdata_id]]
        eis_data = EISData(metadata=eisdata_metadata, data=data)
        measurement.eis_data.append(eis_data)

    return measurement
