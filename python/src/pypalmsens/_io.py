from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Union

from PalmSens.Data import SessionManager
from PalmSens.DataFiles import MethodFile, MethodFile2
from System.IO import StreamReader, StreamWriter
from System.Text import Encoding

from ._data.measurement import Measurement
from ._methods import Method, MethodSettings

if TYPE_CHECKING:
    from ._methods.method import Method


@contextmanager
def stream_reader(*args, **kwargs):
    sr = StreamReader(*args, **kwargs)
    try:
        yield sr
    finally:
        sr.Close()


@contextmanager
def stream_writer(*args, **kwargs):
    sw = StreamWriter(*args, **kwargs)
    try:
        yield sw
    finally:
        sw.Close()


def load_session_file(
    path: Union[str, Path],
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

    session = SessionManager()

    with stream_reader(str(path)) as stream:
        session.Load(stream.BaseStream, str(path))

    session.MethodForEditor.MethodFilename = str(path.absolute())

    for psmeasurement in session:
        psmeasurement.Method.MethodFilename = str(path.absolute())

    return [Measurement(psmeasurement=m) for m in session]


def save_session_file(path: Union[str, Path], measurements: list[Measurement]):
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

    session = SessionManager()
    session.MethodForEditor = measurements[0]._psmeasurement.Method
    session.MethodForEditor.MethodFilename = str(path.absolute())

    for measurement in measurements:
        session.AddMeasurement(measurement._psmeasurement)

    with stream_writer(str(path), False, Encoding.Unicode) as stream:
        session.Save(stream.BaseStream, str(path))


def load_method_file(
    path: Union[str, Path], as_method: bool = False
) -> MethodSettings | Method:
    """Load a method file (.psmethod).

    Parameters
    ----------
    path : Path | str
        Path to method file
    as_method : bool
        If True, load as method wrapper object

    Returns
    -------
    method : Parameters
        Return method parameters
    """
    path = Path(path)

    with stream_reader(str(path)) as stream:
        if path.suffix == MethodFile2.FileExtension:
            psmethod = MethodFile2.FromStream(stream)
        else:
            psmethod = MethodFile.FromStream(stream, str(path))

    psmethod.MethodFilename = str(path.absolute())

    method = Method(psmethod=psmethod)

    if as_method:
        return method
    else:
        return method.to_settings()


def save_method_file(path: Union[str, Path], method: Union[Method, MethodSettings]):
    """Load a method file (.psmethod).

    Parameters
    ----------
    path : Path | str
        Path to save the method file
    method : Method
        Method to save
    """
    from pypalmsens import __sdk_version__

    if isinstance(method, MethodSettings):
        psmethod = method._to_psmethod()
    elif isinstance(method, Method):
        psmethod = method.psmethod
    else:
        raise ValueError(f'Unknown data type: {type(method)}')

    path = Path(path)

    with stream_writer(str(path), False, Encoding.Unicode) as stream:
        MethodFile2.Save(psmethod, stream.BaseStream, str(path), True, __sdk_version__)


def read_notes(path: Union[str, Path], n_chars: int = 3000):
    with open(path, encoding='utf16') as myfile:
        contents = myfile.read()
    raw_txt = contents[1:n_chars].split('\\r\\n')
    notes_list = [x for x in raw_txt if 'NOTES=' in x]
    notes_txt = (
        notes_list[0].replace('%20', ' ').replace('NOTES=', '').replace('%crlf', os.linesep)
    )
    return notes_txt
