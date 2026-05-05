from __future__ import annotations

import warnings
from typing import Any


def __getattr__(name: str) -> Any:
    if name in (
        'ConstantE',
        'ConstantI',
        'Impedance',
        'OpenCircuit',
        'SweepE',
    ):
        warnings.warn(
            f"{name!r} has moved, use 'pypalmsens.stages.{name}'",
            DeprecationWarning,
            stacklevel=2,
        )
        from . import stages

        return getattr(stages, name)

    if name == 'MixedMode':
        warnings.warn(
            f"{name!r} has moved, use 'pypalmsens.{name}'",
            DeprecationWarning,
            stacklevel=2,
        )
        from ._methods.mixed_mode import MixedMode

        return MixedMode

    raise AttributeError(f'module {__name__!r} has no attribute {name!r}')
