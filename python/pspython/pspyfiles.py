from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Union

from PalmSens.Data import SessionManager
from PalmSens.DataFiles import MethodFile, MethodFile2
from System.IO import StreamReader, StreamWriter
from System.Text import Encoding

from pspython.methods.method import Method
from pspython.methods.techniques import ParameterType

from .data.measurement import Measurement

if TYPE_CHECKING:
    from .methods.method import Method


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
    session.MethodForEditor = measurements[0].psmeasurement.Method
    session.MethodForEditor.MethodFilename = str(path.absolute())

    for measurement in measurements:
        session.AddMeasurement(measurement.psmeasurement)

    with stream_writer(str(path), False, Encoding.Unicode) as stream:
        session.Save(stream.BaseStream, str(path))


def load_method_file(path: Union[str, Path]) -> Method:
    """Load a method file (.psmethod).

    Parameters
    ----------
    path : Path | str
        Path to method file

    Returns
    -------
    method : Method
        Return method instance
    """
    path = Path(path)

    with stream_reader(str(path)) as stream:
        if path.suffix == MethodFile2.FileExtension:
            method = MethodFile2.FromStream(stream)
        else:
            method = MethodFile.FromStream(stream, str(path))

    method.MethodFilename = str(path.absolute())

    return Method(psmethod=method)


def save_method_file(path: Union[str, Path], method: Union[Method, ParameterType]):
    """Load a method file (.psmethod).

    Parameters
    ----------
    path : Path | str
        Path to save the method file
    method : Method
        Method to save
    """
    from pspython import __sdk_version__

    if isinstance(method, ParameterType):
        psmethod = method.to_psmethod()
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
