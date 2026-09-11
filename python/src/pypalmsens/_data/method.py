from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar, Self

import PalmSens

from pypalmsens.types import MethodType

from .._methods.techniques import BaseTechnique


class Method:
    """Wrapper for PalmSens.Method.

    Notes
    -----
    Obtain internal instances via `_wrap`.
    """

    __slots__: ClassVar[tuple[str, ...]] = ('_internal',)
    _internal: PalmSens.Method  # pyright: ignore[reportUninitializedInstanceVariable]

    def __init__(self):
        raise TypeError(
            'Method cannot be instantiated directly. '
            'Obtain instances through the Technique methods.'
        )

    @classmethod
    def _wrap(cls, psmethod: PalmSens.Method) -> Self:
        obj = cls.__new__(cls)
        obj._internal = psmethod
        return obj

    def __repr__(self) -> str:
        return f'{type(self).__name__}(name={self.name!r}, id={self.id!r})'

    @property
    def id(self) -> str:
        """Unique id for method."""
        return self._internal.MethodID

    @property
    def name(self) -> str:
        """Name for the technique."""
        return self._internal.Name

    @property
    def short_name(self) -> str:
        """Short name for the technique."""
        return self._internal.ShortName

    @property
    def filename(self) -> Path | None:
        """Filename for the method if applicable."""
        fn = self._internal.MethodFilename
        if fn:
            return Path(fn)
        return None

    @property
    def supports_corrosion(self) -> bool:
        """Return true if corrosion is supported."""
        return self._internal.SupportsCorrosion

    @property
    def technique_number(self) -> int:
        """The technique number used in the firmware."""
        return self._internal.Technique

    def to_settings(self) -> MethodType:
        """Extract techniques parameters as dataclass."""
        return BaseTechnique._from_psmethod(self._internal)

    def to_dict(self) -> dict[str, Any]:
        """Return dictionary with technique parameters."""
        return self.to_settings().to_dict()
