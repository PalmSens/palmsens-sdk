from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import Any, ClassVar

from PalmSens import Method as PSMethod

from .base_model import BaseModel


class BaseSettings(BaseModel, metaclass=ABCMeta):
    """Protocol to provide generic methods for parameters."""

    @abstractmethod
    def _update_psmethod(self, psmethod: PSMethod, /): ...

    @abstractmethod
    def _update_params(self, psmethod: PSMethod, /): ...


class BaseTechnique(BaseModel, metaclass=ABCMeta):
    """Protocol to provide base methods for method classes."""

    id: ClassVar[str] = ''
    _registry: ClassVar[dict[str, type[BaseTechnique]]] = {}

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        cls._registry[cls.id] = cls

    def to_dict(self) -> dict[str, Any]:
        """Return the technique instance as a new key/value dictionary mapping."""
        return self.model_dump()

    @classmethod
    def from_dict(cls, obj: dict[str, Any]) -> BaseTechnique:
        """Structure technique instance from dict.

        Opposite of `.to_dict()`"""
        return cls.model_validate(obj)

    @classmethod
    def from_method_id(cls, id: str) -> BaseTechnique:
        """Create new instance of appropriate technique from method ID."""
        new = cls._registry[id]
        return new()

    @classmethod
    def _from_psmethod(cls, psmethod: PSMethod, /) -> BaseTechnique:
        """Generate parameters from dotnet method object."""
        new = cls.from_method_id(psmethod.MethodID)
        new._update_params(psmethod)
        new._update_params_nested(psmethod)
        return new

    @abstractmethod
    def _update_params(self, psmethod: PSMethod, /) -> None: ...

    def _update_params_nested(self, psmethod: PSMethod, /) -> None:
        """Retrieve and convert dotnet method for nested field parameters."""
        for field in self.__class__.model_fields:
            attribute = getattr(self, field)
            try:
                # Update parameters if attribute has the `update_params` method
                attribute._update_params(psmethod)
            except AttributeError:
                pass

    def _to_psmethod(self) -> PSMethod:
        """Convert parameters to dotnet method."""
        psmethod = PSMethod.FromMethodID(self.id)

        self._update_psmethod(psmethod)
        self._update_psmethod_nested(psmethod)
        return psmethod

    @abstractmethod
    def _update_psmethod(self, psmethod: PSMethod, /) -> None: ...

    def _update_psmethod_nested(self, psmethod: PSMethod, /) -> None:
        """Convert and set field parameters on dotnet method."""
        for field in self.__class__.model_fields:
            attribute = getattr(self, field)

            try:
                # Update parameters if attribute has the `update_params` method
                attribute._update_psmethod(psmethod)
            except AttributeError:
                pass
