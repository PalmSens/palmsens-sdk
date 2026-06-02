from __future__ import annotations

from abc import ABCMeta, abstractmethod
from contextlib import contextmanager
from typing import Any, ClassVar

import PalmSens
from System.IO import StringWriter

from .. import __version__
from .._types import MethodType
from .base_model import BaseModel


@contextmanager
def string_writer(*args, **kwargs):
    stream = StringWriter(*args, **kwargs)
    stream.NewLine = '\n'
    try:
        yield stream
    finally:
        stream.Close()


class BaseSettings(BaseModel, metaclass=ABCMeta):
    """Protocol to provide generic methods for parameters."""

    @abstractmethod
    def _update_psmethod(self, psmethod: PalmSens.Method, /): ...

    @abstractmethod
    def _update_params(self, psmethod: PalmSens.Method, /): ...


class BaseTechnique(BaseModel, metaclass=ABCMeta):
    """Protocol to provide base methods for method classes."""

    _registry: ClassVar[dict[str, type[MethodType]]] = {}

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if hasattr(cls, 'id'):
            cls._registry[cls.id] = cls  # type: ignore

    def to_dict(self) -> dict[str, Any]:
        """Return the technique instance as a new key/value dictionary mapping."""
        return self.model_dump()

    @classmethod
    def from_dict(cls, obj: dict[str, Any]) -> MethodType:
        """Structure technique instance from dict.

        Opposite of `.to_dict()`"""
        return cls.model_validate(obj)  # type:ignore

    @classmethod
    def from_method_id(cls, id: str) -> MethodType:
        """Create new instance of appropriate technique from method ID."""
        new = cls._registry[id]
        return new()

    def _serialize(self) -> str:
        """Serialize to string that can be written to pssession file."""
        psmethod = self._to_psmethod()
        with string_writer() as stream:
            PalmSens.DataFiles.MethodFile2.Serialize(
                psmethod, stream, 'PyPalmSens', __version__
            )
            return str(stream)

    @classmethod
    def _from_psmethod(cls, psmethod: PalmSens.Method, /) -> MethodType:
        """Generate parameters from dotnet method object."""
        new = cls.from_method_id(psmethod.MethodID)
        new._update_params(psmethod)
        new._update_params_nested(psmethod)
        return new

    @abstractmethod
    def _update_params(self, psmethod: PalmSens.Method, /) -> None: ...

    @property
    def _use_hardware_sync(self) -> bool:
        """Fallback method, implemented by derived classes or mixins"""
        return False

    def _update_params_nested(self, psmethod: PalmSens.Method, /) -> None:
        """Retrieve and convert dotnet method for nested field parameters."""
        for field in self.__class__.model_fields:
            attribute = getattr(self, field)
            try:
                # Update parameters if attribute has the `update_params` method
                attribute._update_params(psmethod)
            except AttributeError:
                pass

    def _to_psmethod(self) -> PalmSens.Method:
        """Convert parameters to dotnet method."""
        psmethod = PalmSens.Method.FromMethodID(self.id)  # type:ignore

        self._update_psmethod(psmethod)
        self._update_psmethod_nested(psmethod)
        return psmethod

    @abstractmethod
    def _update_psmethod(self, psmethod: PalmSens.Method, /) -> None: ...

    def _update_psmethod_nested(self, psmethod: PalmSens.Method, /) -> None:
        """Convert and set field parameters on dotnet method."""
        for field in self.__class__.model_fields:
            attribute = getattr(self, field)

            try:
                # Update parameters if attribute has the `update_params` method
                attribute._update_psmethod(psmethod)
            except AttributeError:
                pass
