"""This module contains the public api for circuit fitting."""

from __future__ import annotations

from ._fitting import (
    CircuitModel,
    FitResult,
    Parameter,
    Parameters,
)

__all__ = [
    'CircuitModel',
    'FitResult',
    'Parameter',
    'Parameters',
]
