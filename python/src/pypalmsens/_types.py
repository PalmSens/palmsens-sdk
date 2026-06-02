from __future__ import annotations

from typing import Any, Literal, Protocol

import PalmSens

AllowedTimingStatus = Literal['Unknown', 'OK', 'OverStep']
"""Possible values for measurement timing status."""

AllowedReadingStatus = Literal['OK', 'Overload', 'Underload', 'OverloadWarning']
"""Possible values for current or potential readings."""

AllowedDeviceState = Literal[
    'Unknown', 'Idle', 'Measurement', 'Download', 'Pretreatment', 'Error', 'MeasOCP'
]
"""Possible values for the device state."""

AllowedCurrentRanges = Literal[
    '100pA',
    '1nA',
    '10nA',
    '100nA',
    '1uA',
    '10uA',
    '100uA',
    '1mA',
    '10mA',
    '100mA',
    '2uA',
    '4uA',
    '8uA',
    '16uA',
    '32uA',
    '63uA',
    '125uA',
    '250uA',
    '500uA',
    '5mA',
    '6uA',
    '13uA',
    '25uA',
    '50uA',
    '200uA',
    '1A',
]
"""Possible current ranges.

See the device documentation or query the instrument manager
for supported current ranges."""


AllowedMethods = Literal[
    'acv',
    'ad',
    'cp',
    'cpot',
    'cv',
    'dpv',
    'eis',
    'eis_it',
    'fam',
    'fcv',
    'fgis',
    'fis',
    'geis_it',
    'gis',
    'gs',
    'lp',
    'lsp',
    'lsv',
    'ma',
    'mm',
    'mp',
    'mpad',
    'ms',
    'npv',
    'pad',
    'pot',
    'ps',
    'scp',
    'swv',
]
"""All available method IDs.

See the device documentation or query the instrument manager
for supported methods."""


AllowedPotentialRanges = Literal[
    '1mV',
    '10mV',
    '20mV',
    '50mV',
    '100mV',
    '200mV',
    '500mV',
    '1V',
]
"""Possible potential ranges.

See the device documentation or query the instrument manager
for supported potential ranges."""


AllowedScanTypes = Literal['potential', 'time', 'fixed']
"""Possible scan types."""

AllowedFrequencyTypes = Literal['fixed', 'scan']
"""Possible frequency types."""


class MethodTypeCompatible(Protocol):
    """All methods, including MethodType and those that generate compatible MethodSCRIPT."""

    @property
    def id(self) -> AllowedMethods: ...

    def _to_psmethod(self) -> PalmSens.Method: ...


class MethodType(MethodTypeCompatible, Protocol):
    """Methods with complete implementation in .NET."""

    @property
    def _use_hardware_sync(self) -> bool: ...

    def to_dict(self) -> dict[str, Any]: ...
    def _serialize(self) -> str: ...
    def _update_params(self, psmethod: PalmSens.Method, /) -> None: ...
    def _update_params_nested(self, psmethod: PalmSens.Method, /) -> None: ...
    def _update_psmethod(self, psmethod: PalmSens.Method, /) -> None: ...
    def _update_psmethod_nested(self, psmethod: PalmSens.Method, /) -> None: ...
