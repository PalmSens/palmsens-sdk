# Event System

PyPalmSens provides an event-driven interface for reacting to instrument activity during measurements. Events are exposed as methods on [pypalmsens.InstrumentManager][] and allow you to subscribe callbacks that trigger at specific moments in the measurement lifecycle, receive real-time data updates, or track communication messages from the device.

## Event Handles

Every event subscription returns an [EventHandle][] object that can be used to cancel the callback:

```python
import pypalmsens as ps

with ps.connect() as manager:
    handle = ps.on_curve_new_data(print)
    manager.measure(ps.CyclicVoltammetry())
    handle.cancel()
```

Calling [EventHandle.cancel][] removes the callback from the emitter's listeners. This is useful when you want temporary subscriptions that don't persist for the lifetime of the connection.

## Measurement Lifecycle Events

These events track the progression of a measurement from setup to completion:

### Setup and Teardown

[InstrumentManager.on_measurement_setup][] fires before the measurement begins, making it ideal for initializing resources like file handles or database connections:

```python
import pypalmsens as ps

def setup():
    print("Opening output file...")

with ps.connect() as manager:
    handle = manager.on_measurement_setup(setup)
    result = manager.measure(ps.LinearSweepVoltammetry())
    handle.cancel()
```

[InstrumentManager.on_measurement_teardown][] fires after the measurement ends, whether it completed successfully or encountered an error. Use this for cleanup:

```python
import pypalmsens as ps

def cleanup():
    print("Closing output file...")

with ps.connect() as manager:
    handle = manager.on_measurement_teardown(cleanup)
    result = manager.measure(ps.CyclicVoltammetry())
    handle.cancel()
```

### Measurement Boundaries

[InstrumentManager.on_measurement_begin][] fires when a measurement starts, and [InstrumentManager.on_measurement_end][] fires when it finishes. These provide clear boundaries for tracking overall measurement progress:

```python
import pypalmsens as ps

def on_start(measurement):
    print(f"Starting {measurement.method_name()}")

def on_finish():
    print("Measurement complete")

with ps.connect() as manager:
    handle1 = manager.on_measurement_begin(on_start)
    handle2 = manager.on_measurement_end(on_finish)
    result = manager.measure(ps.CyclicVoltammetry())
    handle1.cancel()
    handle2.cancel()
```

## Curve Events (Amperometric Methods)

For techniques like LinearSweepVoltammetry, CyclicVoltammetry, and similar methods that produce curves:

[InstrumentManager.on_curve_begin][] fires when a new curve starts. [InstrumentManager.on_curve_new_data][] fires repeatedly as new data points arrive during the curve — note that data are batched depending on available resources. [InstrumentManager.on_curve_end][] fires when the curve finishes.

```python
import pypalmsens as ps

def on_new_data(data):
    # data is a CallbackData instance with voltage and current values
    print(f"Received {len(data.voltage)} points")

with ps.connect() as manager:
    handle = manager.on_curve_new_data(on_new_data)
    result = manager.measure(ps.LinearSweepVoltammetry())
    handle.cancel()
```

For multi-curve measurements (e.g., multiple cycles in CyclicVoltammetry), each curve triggers its own sequence of `curve_begin`, `curve_new_data`, and `curve_end` events.

## EIS Events (Electrochemical Impedance Spectroscopy)

EIS measurements use a separate set of events to track impedance data collection:

[InstrumentManager.on_eis_data_begin][] fires when a new EIS dataset starts. [InstrumentManager.on_eis_new_data][] fires as new frequency points are received — these are also batched depending on available resources. [InstrumentManager.on_eis_data_end][] fires when the EIS measurement completes.

```python
import pypalmsens as ps

def on_eis_points(data):
    # data is a CallbackDataEIS instance with impedance values
    print(f"Received {len(data.frequencies)} frequency points")

with ps.connect() as manager:
    handle = manager.on_eis_new_data(on_eis_points)
    result = manager.measure(ps.EIS())
    handle.cancel()
```

## Communication Events

These events track communication between the instrument and your code:

### Receive Messages

[InstrumentManager.on_receive_message][] fires when a message string is received from the device. This includes notifications when methods start, or custom messages sent via MethodSCRIPT's `send_string`:

```python
import pypalmsens as ps

def on_message(msg):
    print(f"Message: {msg}")

with ps.connect() as manager:
    handle = manager.on_receive_message(on_message)
    result = manager.measure(ps.CyclicVoltammetry())
    handle.cancel()
```

### Receive Status

[InstrumentManager.on_receive_status][] fires for idle status update events during idle state or pretreatment phases. The callback receives a [Status][] object containing current/potential values reported by the instrument. **This event requires an active event loop (async only).**

```python
import asyncio
import pypalmsens as ps

async def main():
    async with ps.connect_async() as manager:
        handle = await manager.on_receive_status(lambda status: print(status))
        # ... use during measurements

asyncio.run(main())
```

## Error Handling

[InstrumentManager.on_error][] fires when an error occurs during a measurement, such as connection failures or communication errors. This provides a way to react to unexpected issues rather than relying solely on exceptions:

```python
import pypalmsens as ps

def on_error(error):
    print(f"Error occurred: {error}")

with ps.connect() as manager:
    handle = manager.on_error(on_error)
    result = manager.measure(ps.CyclicVoltammetry())
    handle.cancel()
```

## Event Flow Summary

Here's a typical event sequence for a Cyclic Voltammetry measurement with 3 cycles:

1. `measurement_setup` — Prepare resources
2. `measurement_begin` — CV starts
3. For each cycle:
   - `curve_begin` — Cycle N begins
   - `curve_new_data` — Repeated as data arrives (batched)
   - `curve_end` — Cycle N finishes
4. `measurement_end` — All cycles complete

For EIS measurements:

1. `measurement_setup` — Prepare resources
2. `eis_data_begin` — EIS measurement starts
3. `eis_new_data` — Repeated as frequency points arrive (batched)
4. `measurement_end` — Measurement finishes

## Error Handling

Events do not propagate exceptions from callbacks to other listeners or the measurement flow. If a callback raises an error, it is logged but does not cancel the measurement. This ensures that event subscriptions remain independent and failures in one callback don't affect others.
