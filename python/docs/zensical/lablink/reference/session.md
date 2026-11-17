# Session

A [Session][pypalmsens.lablink.Session] is an authenticated connection to a Lablink instance, obtained from [Instance.login][pypalmsens.lablink.Instance.login]. The session is the main object for interacting with the Lablink: listing and claiming instruments, starting measurements, retrieving stored measurements, etc.

Some calls are cached. For example, [Session.instruments][pypalmsens.lablink.Session.instruments] holds the result of the most recent [Session.list_instruments][pypalmsens.lablink.Session.list_instruments] call. They may be stale or empty. Call those methods to refresh.

| Attribute | Updated by |
| :--- | :--- |
| [Session.info][pypalmsens.lablink.Session.info] | [Session.get_info][pypalmsens.lablink.Session.get_info] |
| [Session.instrument_info][pypalmsens.lablink.Session.instrument_info] | [Session.list_instruments][pypalmsens.lablink.Session.list_instruments], [Session.get_instrument_info][pypalmsens.lablink.Session.get_instrument_info] |
| [Session.instruments][pypalmsens.lablink.Session.instruments] | [Session.list_instruments][pypalmsens.lablink.Session.list_instruments], [Session.get_instrument_info][pypalmsens.lablink.Session.get_instrument_info] |

Claims are held until released. Use `async with` so the claim is released even if the measurement raises an exception:

```python
instruments = await session.list_instruments()
instrument, *_ = instruments

async with await instrument.claim() as claim:
    job = await claim.start_measurement(method=method)
    measurement = await job   # claim released here

data = await measurement.get_data()
```

To work with several instruments at once, use the batch methods on the session.
`session.claim(instruments)` returns an [InstrumentClaimBatch][pypalmsens.lablink.InstrumentClaimBatch] and `session.start_measurement(claims, method=...)` one [MeasurementJob][pypalmsens.lablink.MeasurementJob] per instrument:

```python
instruments = await session.list_instruments()

async with await session.claim(instruments) as claims:
    jobs = await session.start_measurement(claims, method=method)
    refs = await asyncio.gather(*jobs)   # claims released here

data = [await ref.get_data() for ref in refs]
```

!!! TIP

    Similarly named methods exist on both [Session][pypalmsens.lablink.Session] and [Instrument][pypalmsens.lablink.Instrument]. As a guideline, use [Session][pypalmsens.lablink.Session] for batch (multi-instrument) operations, use [Instrument][pypalmsens.lablink.Instrument] for single-instrument operations.

::: pypalmsens.lablink.Session
