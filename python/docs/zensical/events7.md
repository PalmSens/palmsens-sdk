# Events

PyPalmSens exposes a callback-based event system that lets you react to measurement progress, incoming data, and device status updates. All events are registered through methods on [pypalmsens.InstrumentManager][] (or its async counterpart). Each registration returns an [EventHandle][], which can be used to cancel the subscription at any time.

## Registering callbacks

Use the `on()` method to subscribe to a named event:

```python
import pypalmsens as ps

def my_callback(data):
    print(f"Got data: {data}")

with ps.connect() as manager:
    handle = manager.on('curve_new_data', my_callback)
    # ... run measurements ...
    handle.cancel()  # unsubscribe
```

For convenience, each event also has a dedicated method (e.g. `on_curve_new_data()`). These are described in detail below.

## Measurement lifecycle events

These events fire at key points during the measurement pipeline:

### Before the measurement starts

[pypalmsens.InstrumentManager.on_measurement_setup][] fires before the instrument begins executing a method. Use this to prepare resources such as file handles or database connections:

```python
import pypalmsens as ps

def on_setup(measurement):
    print(f"Preparing for {measurement.metadata.title}")

with ps.connect() as manager:
    manager.on_measurement_setup(on_setup)
    manager.measure(ps.CyclicVoltammetry())
```

### After the measurement ends

[pypalmsens.InstrumentManager.on_measurement_teardown][] fires after a measurement finishes, whether successfully or due to an error. Use this for cleanup:

```python
def on_teardown(measurement):
    print("Cleaning up resources")

with ps.connect() as manager:
    manager.on_measurement_teardown(on_teardown)
    manager.measure(ps.LinearSweepVoltammetry())
```

### Measurement begin and end

[pypalmsens.InstrumentManager.on_measurement_begin][] fires when the measurement starts executing on the device, and [pypalmsens.InstrumentManager.on_measurement_end][] fires when it completes. These are useful for tracking overall progress:

```python
def on_begin(m):
    print(f"Measurement started: {m.metadata.title}")

def on_end(m):
    print(f"Measurement finished: {m.metadata.title}")

with ps.connect() as manager:
    manager.on_measurement_begin(on_begin)
    manager.on_measurement_end(on_end)
    manager.measure(ps.CyclicVoltammetry())
```

## Curve data events

For standard voltammetric and potentiostatic/galvanostatic methods, use these events to receive curve metadata and streaming data:

### Curve lifecycle

- [pypalmsens.InstrumentManager.on_curve_begin][] — fires when a new curve starts being recorded. Receives a [pypalmsans.data.Curve][] object with the curve's metadata.
- [pypalmsens.InstrumentManager.on_curve_end][] — fires when a curve is complete. Also receives the finished [pypalmsans.data.Curve][].

### Streaming data

[pypalmsens.InstrumentManager.on_curve_new_data][] fires periodically as new data points arrive during a measurement. The callback receives a [pypalmsens._instruments.callback.CallbackData][] object:

```python
import pypalmsens as ps

def on_new_data(data):
    print(f"New point: x={data.last_x}, y={data.last_y}")

with ps.connect() as manager:
    handle = ps.on_curve_new_data(on_new_data)
    manager.measure(ps.CyclicVoltammetry())
    handle.cancel()
```

The [pypalmsens._instruments.callback.CallbackData][] object provides several helpers for working with the data:

- `last_x`, `last_y` — last measured x and y values
- `last_datapoint()` — dict with `'index'`, `'x'`, and `'y'` keys
- `new_datapoints()` — generator yielding dicts for each new point since the last callback

Data is batched depending on available resources, so multiple points may arrive in a single callback invocation.

## EIS data events

For electrochemical impedance spectroscopy (EIS) methods, use the dedicated EIS event handlers:

- [pypalmsens.InstrumentManager.on_eis_data_begin][] — fires when a new EIS dataset starts. Receives a [pypalmsans.data.EISData][] object with metadata.
- [pypalmsens.InstrumentManager.on_eis_new_data][] — fires periodically as new frequency points are measured. Receives a [pypalmsens._instruments.callback.CallbackDataEIS][] object.
- [pypalmsens.InstrumentManager.on_eis_data_end][] — fires when an EIS dataset is complete.

The [pypalmsens._instruments.callback.CallbackDataEIS][] object provides:

- `last_datapoint()` — dict mapping array names to values for the last frequency point
- `new_datapoints()` — generator yielding dicts for each new frequency point since the last callback
- `data` — the underlying [pypalmsens.data.DataSet][] containing all arrays

```python
import pypalmsens as ps

def on_eis_data(data):
    print(f"Frequency: {data.last_datapoint()['frequency']} Hz")

with ps.connect() as manager:
    handle = ps.on_eis_new_data(on_eis_data)
    manager.measure(ps.EIS())
    handle.cancel()
```

## Error events

[pypalmsens.InstrumentManager.on_error][] fires when a connection or communication error occurs during a measurement. This is useful for handling failures gracefully:

```python
def on_error():
    print("An error occurred during measurement")

with ps.connect() as manager:
    manager.on_error(on_error)
    try:
        manager.measure(ps.CyclicVoltammetry())
    except Exception:
        pass  # handled by the callback
```

## Low-level events

### Receiving messages

[pypalmsens.InstrumentManager.on_receive_message][] registers a callback for raw messages received from the instrument. This fires, for example, when a method starts or when `send_string` is called in MethodSCRIPT:

```python
def on_message(msg: str):
    print(f"Received: {msg}")

with ps.connect() as manager:
    handle = ps.on_receive_message(on_message)
    manager.measure(ps.CyclicVoltammetry())
    handle.cancel()
```

### Receiving status updates (async only)

[pypalmsens.InstrumentManager.on_receive_status][] registers a callback for idle status update events. The instrument sends updated current/potential values during idle state or pretreatment phases. This event **requires an active event loop** and is only available in async contexts:

```python
import asyncio
import pypalmsens as ps

async def main():
    instruments = await ps.discover_async()
    manager = ps.InstrumentManagerAsync(instruments[0])
    await manager.connect()

    def on_status(status):
        print(f"Current: {status.current:.6f} µA, Potential: {status.potential:.3f} V")

    handle = ps.on_receive_status(on_status)
    manager.measure(ps.CyclicVoltammetry())
    handle.cancel()

asyncio.run(main())
```

The [pypalmsens._instruments.callback.Status][] object provides access to:

- `device_state` — current device state (e.g. `'Idle'`, `'Running'`)
- `potential` — potential in V
- `current` — current in µA
- `pretreatment_phase` — pretreatment phase name
- `aux_input` — raw auxiliary input value
- `noise` — measured noise

## Cancelling subscriptions

Every event registration returns an [EventHandle][]. Call its `cancel()` method to unsubscribe:

```python
import pypalmsens as ps

with ps.connect() as manager:
    handle = ps.on_curve_new_data(print)
    manager.measure(ps.CyclicVoltammetry())
    handle.cancel()  # stop receiving data callbacks
```

Once cancelled, the callback will no longer be invoked for subsequent events. The event is not removed from the instrument — only your subscription is dropped.

## Async support

For async workflows, use [pypalmsens.InstrumentManagerAsync][] with the same event methods. Most events work identically in both sync and async contexts. The exception is `on_receive_status()`, which requires an active event loop:

```python
import asyncio
import pypalmsens as ps

async def main():
    instruments = await ps.discover_async()
    manager = ps.InstrumentManagerAsync(instruments[0])
    await manager.connect()

    handle = ps.on_curve_new_data(lambda data: print(data.last_datapoint()))
    await manager.measure(ps.CyclicVoltammetry())
    handle.cancel()

asyncio.run(main())
```
