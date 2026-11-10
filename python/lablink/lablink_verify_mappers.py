"""Usage:

LABLINK_SDK="C:\\Users\\stef\\code\\palmsenssdkdotnet\\PalmSens.Sdk.Lablink\\PalmSens.Sdk.Lablink\\bin\\Debug\\net10.0"
python lablink_verify_mappers.py

"""

from __future__ import annotations

import pypalmsens as ps
from pypalmsens.lablink.models._method_mapper import to_payload

method = ps.ChronoAmperometry()

from PalmSens.Sdk.Lablink.Example.Lablink.Mappers import MethodMappers

dto = MethodMappers.ToDto(method._to_psmethod())

payload = {
    'Technique': dto.Technique,
    'MethodParameters': dict(dto.Parameters),
}

payload2 = to_payload(method)
