# Session

An authenticated connection to a Lablink instance, obtained from `Instance.login()`. The session is the root object: listing instruments, claiming them, starting measurements, and looking up stored measurements all hang off it.

Two things to keep in mind:

- `instruments` and `instrument_info` are **caches**, not live queries. They hold the result of the most recent `list_instruments()` / `get_instrument_info()` call, so they may be stale or empty. Call those methods to refresh.
- Claims are held until released. Prefer `async with` so the claim is released even if the block raises:

```python
instruments = await session.list_instruments()
instrument, *_ = instruments

async with await instrument.claim() as claim:
    job = await claim.start_measurement(method=method)
    measurement = await job   # claim released here

data = await measurement.get_data()
```

To work with several instruments at once, use the batch methods on the session: `session.claim(instruments)` returns an [InstrumentClaimBatch][pypalmsens.lablink.InstrumentClaimBatch] and `session.start_measurement(claims, method=...)` one [MeasurementJob][pypalmsens.lablink.MeasurementJob] per instrument.

::: pypalmsens.lablink.Session
