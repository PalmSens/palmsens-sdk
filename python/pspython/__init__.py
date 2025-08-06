from __future__ import annotations

import sys

# Load dotnet platform dependencies and init SDK
if sys.platform == 'win32':
    from ._lib.windows import sdk_version
else:
    from ._lib.mono import sdk_version

__version__ = '0.0.1'
__sdk_version__ = sdk_version
