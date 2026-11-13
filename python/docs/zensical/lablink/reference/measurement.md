# Measurement

A [Measurement][pypalmsens.lablink.Measurement] is a reference to a measurement stored on the server.
A reference is a GUID without any additional data. Get the data with [Measurement.get_data][pypalmsens.lablink.Measurement.get_data]. This returns an [xarray.Dataset][] (single run) or [xarray.DataTree][] (stacked runs). The getters only work while the measurement reference is attached to a live session. You can re-attach with `session.get_measurement(ref)` before calling [Measurement.get_data][pypalmsens.lablink.Measurement.get_data].

A [MeasurementJob][pypalmsens.lablink.MeasurementJob] is a handle to a measurement in progress. It consists of a reference (GUID) and is attached to a [Session][pypalmsens.lablink.Session]. Starting a measurement returns the job immediately. You can await the job to block until it finishes and receive a [Measurement][pypalmsens.lablink.Measurement].

```python
job = await claim.start_measurement(method=method)  #(1)!
measurement = await job  #(2)!
data = await measurement.get_data()
```

1. returns immediately
2. blocks until it finishes

The current job status is reported via [is_finished][pypalmsens.lablink.MeasurementJob.is_finished]. Jobs can be interrupted with [abort][pypalmsens.lablink.MeasurementJob.abort], [pause][pypalmsens.lablink.MeasurementJob.pause], and [resume][pypalmsens.lablink.MeasurementJob.resume].

The measurement data API is still work in progress.

**Classes:**

- [`Measurement`][pypalmsens.lablink.Measurement]
- [`MeasurementJob`][pypalmsens.lablink.MeasurementJob]

::: pypalmsens.lablink.Measurement
::: pypalmsens.lablink.MeasurementJob
