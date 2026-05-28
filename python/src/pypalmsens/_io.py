from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

import PalmSens
from System.IO import StreamReader, StreamWriter
from System.Text import Encoding

from ._data import Method
from ._data.measurement import Measurement
from ._types import MethodType


@contextmanager
def stream_reader(*args, **kwargs) -> Generator[StreamReader]:
    sr = StreamReader(*args, **kwargs)
    try:
        yield sr
    finally:
        sr.Close()


@contextmanager
def stream_writer(*args, **kwargs) -> Generator[StreamWriter]:
    sw = StreamWriter(*args, **kwargs)
    try:
        yield sw
    finally:
        sw.Close()


def load_session_file(
    path: str | Path,
) -> list[Measurement]:
    """Load a session file (.pssession).

    Parameters
    ----------
    path : Path | str
        Path to session file

    Returns
    -------
    measurements : list[Measurement]
        Return list of measurements
    """
    path = Path(path)

    session = PalmSens.Data.SessionManager()

    with stream_reader(str(path)) as stream:
        session.Load(stream.BaseStream, str(path))

    session.MethodForEditor.MethodFilename = str(path.absolute())

    for psmeasurement in session:
        psmeasurement.Method.MethodFilename = str(path.absolute())

    return [Measurement(psmeasurement=m) for m in session]


def save_session_file(path: str | Path, measurements: list[Measurement]):
    """Load a session file (.pssession).

    Parameters
    ----------
    path : Path | str
        Path to save the session file
    measurements : list[Measurement]
        List of measurements to save
    """
    path = Path(path)

    if any((measurement is None) for measurement in measurements):
        raise ValueError('cannot save null measurement')

    session = PalmSens.Data.SessionManager()
    session.MethodForEditor = measurements[0]._psmeasurement.Method
    session.MethodForEditor.MethodFilename = str(path.absolute())

    for measurement in measurements:
        session.AddMeasurement(measurement._psmeasurement)

    with stream_writer(str(path), False, Encoding.Unicode) as stream:
        session.Save(stream.BaseStream, str(path))


def _load_method_file(path: str | Path) -> Method:
    path = Path(path)

    with stream_reader(str(path)) as stream:
        if path.suffix == PalmSens.DataFiles.MethodFile2.FileExtension:
            psmethod = PalmSens.DataFiles.MethodFile2.FromStream(stream)
        else:
            psmethod = PalmSens.DataFiles.MethodFile.FromStream(stream, str(path))

    psmethod.MethodFilename = str(path.absolute())

    return Method(psmethod=psmethod)


def load_method_file(path: str | Path) -> MethodType:
    """Load a method file (.psmethod).

    Parameters
    ----------
    path : Path | str
        Path to method file

    Returns
    -------
    method : MethodType
        Return method parameters
    """
    method = _load_method_file(path)
    return method.to_settings()


def save_method_file(path: str | Path, method: MethodType):
    """Load a method file (.psmethod).

    Parameters
    ----------
    path : Path | str
        Path to save the method file
    method : MethodType
        Method to save
    """
    data = method._serialize()

    with open(path, 'w') as f:
        _ = f.write(data)
