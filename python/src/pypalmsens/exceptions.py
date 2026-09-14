"""This module contains the set of PyPalmSenss' exceptions."""

from __future__ import annotations

from ._instruments import CommProtocolError, FileSystemException

__all__ = [
    'CommProtocolError',
    'FileSystemException',
]
