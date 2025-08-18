from __future__ import annotations

import sys

# Load dotnet platform dependencies and init SDK
if sys.platform == 'win32':
    from ._lib.windows import sdk_version
else:
    from ._lib.mono import sdk_version

__version__ = '0.0.1'
__sdk_version__ = sdk_version

from ._io import load_method_file, load_session_file, save_method_file, save_session_file
from .instruments._instrument_manager import discover
from .instruments._instrument_manager_async import discover_async

__all__ = [
    'load_session_file',
    'save_session_file',
    'load_method_file',
    'save_method_file',
    'discover',
    # 'connect',
    # 'measure',
    'discover_async',
    # 'connect_async',
    # 'measure_async',
]
