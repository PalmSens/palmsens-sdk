from __future__ import annotations

import sys

if sys.platform == 'win32':
    from ._lib.windows import version
else:
    from ._lib.mono import version


__version__ = '0.0.1'
__sdk_version__ = version
