from __future__ import annotations

import sys

if sys.platform == 'win32':
    from .windows import load, unload
else:
    from .mono import load, unload

__all__ = ['load', 'unload']
