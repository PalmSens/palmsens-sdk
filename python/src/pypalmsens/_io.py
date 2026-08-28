from __future__ import annotations

from collections.abc import Generator, Sequence
from contextlib import contextmanager
from pathlib import Path

import PalmSens
import System
from System.IO import MemoryStream, StreamReader, StreamWriter
from System.Text import Encoding

from ._data import Method
from ._data.measurement import Measurement
from ._types import MethodType


@contextmanager
def memory_reader(*args, **kwargs) -> Generator[MemoryStream]:
    mr = MemoryStream(*args, **kwargs)
    try:
        yield mr
    finally:
        mr.Close()


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
    """Load a session file (`.pssession`).

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

    try:
        with stream_reader(str(path), encoding=Encoding.Unicode) as stream:
            session.Load(stream.BaseStream, str(path))
    except System.IO.FileNotFoundException as exc:
        raise FileNotFoundError(exc.Message) from exc

    session.MethodForEditor.MethodFilename = str(path.absolute())

    for psmeasurement in session:
        psmeasurement.Method.MethodFilename = str(path.absolute())

    return [Measurement(psmeasurement=m) for m in session]


def save_session_file(path: str | Path, measurements: Sequence[Measurement]):
    """Save multiple measurements a session file (`.pssession`).

    Parameters
    ----------
    path : Path | str
        Path to save the session file
    measurements : Sequence[Measurement]
        List of measurements to save
    """
    path = Path(path)

    if not measurements or any((measurement is None) for measurement in measurements):
        raise ValueError('`measurements` must be a non-empty sequence of Measurement objects')

    session = PalmSens.Data.SessionManager()
    session.MethodForEditor = measurements[0]._psmeasurement.Method
    session.MethodForEditor.MethodFilename = str(path.absolute())

    for measurement in measurements:
        session.AddMeasurement(measurement._psmeasurement)

    with stream_writer(str(path), append=False, encoding=Encoding.Unicode) as stream:
        session.Save(stream.BaseStream, str(path))


def load_measurement(
    path: str | Path,
) -> Measurement:
    """Load a measurement from a session file (`.pssession`).

    To load multiple measurements, use [pypalmsens.load_session_file][].

    Parameters
    ----------
    path : Path | str
        Path to session file

    Returns
    -------
    measurement : Measurement
        Return measurement
    """
    measurements = load_session_file(path)

    n = len(measurements)
    if n > 1:
        raise ValueError(
            f'File contains {n} measurements. Use `load_session_file()` to access all of them.'
        )

    return measurements[0]


def save_measurement(path: str | Path, measurement: Measurement):
    """Save measurement a session file (`.pssession`).

    To save multiple measurements, use [pypalmsens.save_session_file][].

    Parameters
    ----------
    path : Path | str
        Path to save the session file
    measurement : Measurement
        Measurements to save
    """
    if isinstance(measurement, Sequence):
        raise TypeError('To save multiple measurements, use pypalmsens.save_session_file().')

    save_session_file(path, [measurement])


def _load_method_file(path: str | Path) -> Method:
    path = Path(path)

    try:
        with stream_reader(str(path), encoding=Encoding.UTF8) as stream:
            if path.suffix == PalmSens.DataFiles.MethodFile2.FileExtension:
                psmethod = PalmSens.DataFiles.MethodFile2.FromStream(stream)
            else:
                psmethod = PalmSens.DataFiles.MethodFile.FromStream(stream, str(path))
    except System.IO.FileNotFoundException as exc:
        raise FileNotFoundError(exc.Message) from exc

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
    """Save a method file (.psmethod).

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
