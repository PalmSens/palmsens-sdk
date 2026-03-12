from __future__ import annotations

from pydantic import TypeAdapter

from . import types

technique_adapter = TypeAdapter(types.TechniqueType)
