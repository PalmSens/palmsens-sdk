from __future__ import annotations

from typing import Literal

from PalmSens.Data import DataArrayType

AllowedArrayTypes = Literal[
    'None',
    'Time',
    'Potential',
    'Current',
    'Charge',
    'ExtraValue',
    'Frequency',
    'Phase',
    'ZRe',
    'ZIm',
    'Iac',
    'Z',
    'Y',
    'YRe',
    'YIm',
    'Cs',
    'CsRe',
    'CsIm',
    'Index',
    'Admittance',
    'Concentration',
    'Signal',
    'Func',
    'Integral',
    'AuxInput',
    'BipotCurrent',
    'BipotPotential',
    'ReverseCurrent',
    'CEPotential',
    'DCCurrent',
    'ForwardCurrent',
    'PotentialExtraRE',
    'CurrentExtraWE',
    'InverseDerative_dtdE',
    'mEdc',
    'Eac',
    'MeasuredStepStartIndex',
    'miDC',
    'SE2vsXPotential',
    # debug arrays
    'nPointsAC',
    'realtintac',
    'ymean',
    'debugtext',
    'Generic',
]


def array_enum_to_str(enum: DataArrayType | int) -> AllowedArrayTypes:
    """Convert DataArrayType to literal string."""
    if isinstance(enum, int):
        enum = DataArrayType(enum)

    return str(enum)  # type: ignore


def array_str_to_enum(s: AllowedArrayTypes) -> DataArrayType:
    """Convert literal string to DataArrayType."""
    return getattr(DataArrayType, s)  # type: ignore
