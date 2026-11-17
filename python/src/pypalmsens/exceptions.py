"""This module contains the set of PyPalmSenss' exceptions."""

from __future__ import annotations

from ._instruments import CommProtocolError, FileSystemException
from ._instruments.shared import MethodIncompatibleError

__all__ = [
    'CommProtocolError',
    'FileSystemException',
    'MethodIncompatibleError',
]
