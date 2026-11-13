# Exceptions

All errors raised by the lablink API derive from `LablinkApiError`. The error carries the server's `status_code` and `response` for programmatic handling.

For example:

```python
from pypalmsens.lablink import LablinkApiError

try:
    session = r(local.login('bob', 'wrongpassword'))
except LablinkApiError as e:
    print(f'rejected: {e}')
```

**Classes:**

| Exception | Meaning |
|---|---|
| [`LablinkApiError`][pypalmsens.lablink.LablinkApiError] | Base class, also covers errors without a status code (e.g. a malformed response) |
| [`LablinkClientError`][pypalmsens.lablink.LablinkClientError] | Client errors (4xx): the request is invalid (bad credentials, unknown instrument, ...) |
| [`LablinkServerError`][pypalmsens.lablink.LablinkServerError] | Server error (5xx): the server failed to process the request |
| [`NoActiveMeasurementError`][pypalmsens.lablink.NoActiveMeasurementError] | The instrument has no active measurement (e.g. pausing, resuming, or aborting one that never started) |

::: pypalmsens.lablink.LablinkApiError
::: pypalmsens.lablink.NoActiveMeasurementError
::: pypalmsens.lablink.LablinkClientError
::: pypalmsens.lablink.LablinkServerError
