# Event handling

When performing measurements or interacting with an instrument, you may want to react to specific occurrences in real-time, such as when a new data point is received or when a measurement starts. PyPalmSens provides an event system via [pypalmsens.InstrumentManager][].

Events are registered using `on_<event_name>` methods on the manager (or its async counterpart) and return an [EventHandle][]. To stop listening to an event, call the `.cancel()` method on the returned handle.

## Using events

The most common use case is to react to data as it arrives during a measurement. This is particularly useful for real-time plotting or monitoring.

```python
import pypalmsens as ps

with ps.connect() as manager:
    # Register a callback for new data points
    handle = manager.on_curve_new_data(print)

    # Start a measurement
    manager.measure(ps.CyclicVoltammetry())

    # Stop listening to the event
    handle.cancel()
```

## Event types

### Measurement events

These events allow you to monitor the lifecycle of a measurement:

| Method | Triggered when... | Callback argument |
| :--- | :--- | :--- |
| [on_measurement_setup][pypalmsens.InstrumentManager.on_measurement_setup] | Before the measurement starts (useful for resource setup) | None |
| [on_measurement_begin][pypalmsens.InstrumentManager.on_measurement_begin] | At the start of a measurement | [Measurement][pypalmsens.data.Measurement] |
| [on_measurement_end][pypalmsens.InstrumentManager.on_measurement_end] | After a measurement ends (successfully or due to error) | [Measurement][pypalmsens.data.Measurement] |
| [on_measurement_teardown][pypalmsens.InstrumentManager.on_measurement_teardown] | After the measurement ends (useful for cleanup) | None |

For example:

```python
import pypalmsens as ps
import time

def begin_callback(measurement):
    print(f"{measurement.title} started @ {time.ctime()}")
    #> Chronopotentiometry started @ Tue Aug  4 16:44:44 2026

def end_callback(measurement):
    print(f"{measurement.title} ended @ {time.ctime()}")
    #> Chronopotentiometry ended @ Tue Aug  4 16:44:54 2026

with ps.connect() as manager:
    manager.on_measurement_begin(begin_callback)
    manager.on_measurement_end(end_callback)
    manager.measure(ps.ChronoPotentiometry(run_time=10))
```

### Standard measurements

For measurements that produce (multiple) curves like Cyclic Voltammetry or Chronopotentiometry, you can subscribe to events related to individual curves:

| Method | Triggered when... | Callback argument |
| :--- | :--- | :--- |
| [on_curve_begin][pypalmsens.InstrumentManager.on_curve_begin] | A new curve starts being recorded | [Curve][pypalmsens.data.Curve] |
| [on_curve_new_data][pypalmsens.InstrumentManager.on_curve_new_data] | New data points are received (batched) | [CallbackData][pypalmsens._instruments.callback.CallbackData] |
| [on_curve_end][pypalmsens.InstrumentManager.on_curve_end] | A curve has finished recording | [Curve][pypalmsens.data.Curve] |

```python
import pypalmsens as ps
import time

def begin_callback(curve):
    print(f"New curve: {curve.title}")
    #> New curve: CV i vs E Scan 1

def end_callback(curve):
    print(f"Measured {len(curve)} points")
    #> Measured 20 points

with ps.connect() as manager:
    manager.on_curve_begin(begin_callback)
    manager.on_curve_end(end_callback)
    manager.measure(ps.CyclicVoltammetry(n_scans=3))
```

### Impedimetric measurements

Impedance Spectroscopy measurements (EIS/GEIS) use a slightly different set of events:

| Method | Triggered when... | Callback argument |
| :--- | :--- | :--- |
| [on_eis_data_begin][pypalmsens.InstrumentManager.on_eis_data_begin] | A new EIS data set starts being recorded | [EISData][pypalmsens.data.EISData] |
| [on_eis_new_data][pypalmsens.InstrumentManager.on_eis_new_data] | New EIS data points are received (batched) | [CallbackDataEIS][pypalmsens._instruments.callback.CallbackDataEIS] |
| [on_eis_data_end][pypalmsens.InstrumentManager.on_eis_data_end] | An EIS data set has finished recording | None |

### Communication and Status events

These events provide insight into the communication layer and instrument state:

| Method | Triggered when... | Callback argument |
| :--- | :--- | :--- |
| [on_receive_message][pypalmsens.InstrumentManager.on_receive_message] | A new message is received from the device | `str` |
| [on_receive_status][pypalmsens.InstrumentManager.on_receive_status] | The instrument's idle status changes | [Status][pypalmsens._instruments.callback.Status] |
| [on_error][pypalmsens.InstrumentManager.on_error] | An error occurs during a measurement | None |

If you use MethodSCRIPT, you can use `on_receive_message` to listen for messages from [`send_string`](https://dev.palmsens.com/methodscript/latest/methodscript/methodscript_main.html#ch_cmd_send_string).

For example:

```python
import pypalmsens as ps

method = ps.MethodScript(script='send_string "hello world!"')

with ps.connect() as manager:
    manager.on_receive_message(print)
    manager.measure(method)
    #> Running: MethodSCRIPT Sandbox
    #> hello world!
```

## Async events

For asynchronous workflows, use the corresponding async methods on [pypalmsens.InstrumentManagerAsync][]. The callback signatures remain the same, but you must ensure your callbacks are compatible with an async environment if you are using `asyncio`.

Note that `on_receive_status` specifically requires an active event loop to function correctly as it uses thread-safe scheduling to bridge the communication layer and your code.
