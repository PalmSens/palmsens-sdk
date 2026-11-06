# Exceptions

All errors raised by the lablink module derive from `LablinkApiError`, which carries the server's `status_code` and `resource_key` for programmatic handling. Catch the base class to handle anything, or a specific subclass to be precise:

| Exception | Meaning |
|---|---|
| `LablinkApiError` | Base class; also covers errors without a status code (e.g. a malformed response) |
| `LablinkClientError` | 4xx — the request is invalid (bad credentials, unknown instrument, ...) |
| `LablinkServerError` | 5xx — the server failed to process the request |
| `NoActiveMeasurementError` | Conflict: the instrument has no active measurement (e.g. pausing, resuming, or aborting one that never started) |

```python
from pypalmsens.lablink import LablinkClientError, NoActiveMeasurementError

try:
    session = await local.login(name, password)
except LablinkClientError as e:
    print(f'rejected: {e}')
```

::: pypalmsens.lablink.LablinkApiError
::: pypalmsens.lablink.NoActiveMeasurementError
::: pypalmsens.lablink.LablinkClientError
::: pypalmsens.lablink.LablinkServerError
