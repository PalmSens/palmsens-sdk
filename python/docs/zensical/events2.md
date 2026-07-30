# Events

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
| `on_measurement_setup` | Before the measurement starts (useful for resource setup) | None |
| `on_measurement_begin` | At the start of a measurement | [Measurement][pypalmsens.data.Measurement] |
| `on_measurement_end` | After a measurement ends (successfully or due to error) | None |
| `on_measurement_teardown` | After the measurement ends (useful for cleanup) | None |

### Curve and EIS events

For measurements that produce multiple curves or data sets (like Cyclic Voltammetry or EIS), you can subscribe to events related to individual curves:

#### Standard Curves (e.g., CV, LSV)

| Method | Triggered when... | Callback argument |
| :--- | :--- | :--- |
| `on_curve_begin` | A new curve starts being recorded | [Curve][pypalmsens.data.Curve] |
| `on_curve_new_data` | New data points are received (batched) | [CallbackData][pypalmsens._instruments.callback.CallbackData] |
| `on_curve_end` | A curve has finished recording | [Curve][pypalmsens.data.Curve] |

#### EIS Data

Electrochemical Impedance Spectroscopy (EIS) uses a slightly different set of events:

| Method | Triggered when... | Callback argument |
| :--- | :--- | :--- |
| `on_eis_data_begin` | A new EIS data set starts being recorded | [EISData][pypalmsens.data.EISData] |
| `on_eis_new_data` | New EIS data points are received (batched) | [CallbackDataEIS][pypalmsens._instruments.callback.CallbackDataEIS] |
| `on_eis_data_end` | An EIS data set has finished recording | None |

### Communication and Status events

These events provide insight into the communication layer and instrument state:

| Method | Triggered when... | Callback argument | Notes |
| :--- | :--- | :--- | :--- |
| `on_receive_message` | A new message is received from the device | `str` | Useful for debugging MethodSCRIPT output. |
| `on_receive_status` | The instrument's idle status changes | [Status][pypalmsens._instruments.callback.Status] | **Requires an active event loop (async only).** |
| `on_error` | An error occurs during a measurement | None | Covers connection and communication errors. |

## Async events

For asynchronous workflows, use the corresponding async methods on [pypalmsens.InstrumentManagerAsync][]. The callback signatures remain the same, but you must ensure your callbacks are compatible with an async environment if you are using `asyncio`.

Note that `on_receive_status` specifically requires an active event loop to function correctly as it uses thread-safe scheduling to bridge the communication layer and your code.
