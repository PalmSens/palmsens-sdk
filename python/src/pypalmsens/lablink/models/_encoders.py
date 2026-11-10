import json
import math
from collections.abc import Iterator
from decimal import Decimal
from typing import Any, override


class PlainFloatEncoder(json.JSONEncoder):
    """Write floats in plain decimal notation (0.000001 instead of 1e-06).

    This encoder overrides json's private float handler.
    Unfortunately there is no clean, supported way to achieve this:
    https://stackoverflow.com/q/17503981
    """

    @override
    def iterencode(self, o: Any, _one_shot: bool = False) -> Iterator[str]:
        markers = {} if self.check_circular else None  # type: ignore
        _encoder = (
            json.encoder.encode_basestring_ascii
            if self.ensure_ascii
            else json.encoder.encode_basestring
        )  # type: ignore

        def floatstr(x, allow_nan: bool = self.allow_nan):
            if math.isnan(x):
                if not allow_nan:
                    raise ValueError('Out of range float values are not JSON compliant: nan')
                return 'NaN'
            if math.isinf(x):
                if not allow_nan:
                    raise ValueError(f'Out of range float values are not JSON compliant: {x!r}')
                return 'Infinity' if x > 0 else '-Infinity'
            return format(Decimal(repr(x)), 'f')

        _iterencode = json.encoder._make_iterencode(  # type: ignore
            markers,
            self.default,
            _encoder,
            self.indent,
            floatstr,
            self.key_separator,
            self.item_separator,
            self.sort_keys,
            self.skipkeys,
            _one_shot,
        )
        return _iterencode(o, 0)
