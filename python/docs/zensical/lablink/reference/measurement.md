# Measurement

A [Measurement][pypalmsens.lablink.Measurement] is a reference to a stored measurement on the server — its GUID plus a link back to the session it came from. A reference carries no data: fetch the payload with `get_data()`, which returns an [xarray.Dataset][] (single run) or [xarray.DataTree][] (stacked runs).

A [MeasurementJob][pypalmsens.lablink.MeasurementJob] is a handle to a measurement in progress. Starting a measurement returns a job immediately — it does not wait for the measurement to finish. Await the job to block until it finishes and receive a [Measurement][pypalmsens.lablink.Measurement]. The job carries the measurement's GUID, which is durable: store it and you can find the measurement again later via `session.get_measurement(guid)`.

```python
job = await claim.start_measurement(method=method)  # returns immediately
measurement = await job                             # blocks until it finishes
data = await measurement.get_data()                # xr.Dataset / DataTree
```

The job can also be inspected (`is_finished`), and interrupted with `abort()`, `pause()`, and `resume()`. A reference is only valid while its session lives — if you need to detach it, reattach with `session.get_measurement(ref)` before calling `get_data()`.

The measurement data API is still work in progress.

::: pypalmsens.lablink.Measurement
::: pypalmsens.lablink.MeasurementJob
