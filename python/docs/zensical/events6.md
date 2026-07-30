# Events

PyPalmSens provides an event-driven interface for reacting to measurement events and instrument communication through [pypalmsens.InstrumentManager][] methods. Each method returns an `EventHandle` that can be used to cancel the subscription when no longer needed.

## Event lifecycle

Events are organized into three main categories:

1. **Measurement-level events**: Triggered at the start, during data reception, and end of a measurement
2. **Curve-level events**: Triggered for each individual curve within a multi-curve measurement (e.g., cyclic voltammetry)
3. **EIS-specific events**: Specialized events for Electrochemical Impedance Spectroscopy measurements

Additionally, there are special communication events (`receive_message` and `receive_status`) that provide low-level access to instrument messages and status updates.

## Basic usage

The simplest way to use events is with a callback function:

```python
import pypalmsens as ps

with ps.connect() as manager:
    # Register callbacks for different events
    handle = manager.on_curve_new_data(print)

    # Run a measurement
    manager.measure(ps.CyclicVoltammetry())

    # Clean up when done
    handle.cancel()
```

## Measurement-level events

### `on_measurement_setup`

Register a callback to invoke before the measurement starts. Use this to set up file resources, database connections, or any other preparation needed for the measurement:

```python
import pypalmsens as ps

with ps.connect() as manager:
    def setup():
        print("Setting up measurement...")
        # Open files, connect databases, etc.

    handle = manager.on_measurement_setup(setup)
    manager.measure(ps.LinearSweepVoltammetry())
    handle.cancel()
```

### `on_measurement_begin`

Register a callback to invoke at the start of a measurement:

```python
import pypalmsens as ps

with ps.connect() as manager:
    def on_start():
        print("Measurement has started")

    handle = manager.on_measurement_begin(on_start)
    manager.measure(ps.LinearSweepVoltammetry())
    handle.cancel()
```

### `on_curve_new_data`

Register a callback to invoke when new data are received. Note that the data are batched depending on available resources:

```python
import pypalmsens as ps

with ps.connect() as manager:
    def on_data(data):
        print(f"Received {len(data)} data points")

    handle = manager.on_curve_new_data(on_data)
    manager.measure(ps.CyclicVoltammetry())
    handle.cancel()
```

### `on_measurement_end`

Register a callback to invoke at the end of a measurement. The measurement ends when it finishes successfully or after an error occurs:

```python
import pypalmsens as ps

with ps.connect() as manager:
    def on_complete():
        print("Measurement completed")

    handle = manager.on_measurement_end(on_complete)
    manager.measure(ps.LinearSweepVoltammetry())
    handle.cancel()
```

### `on_measurement_teardown`

Register a callback to invoke after the measurement ends. Use this to close files or clean up resources:

```python
import pypalmsens as ps

with ps.connect() as manager:
    def cleanup():
        print("Cleaning up...")
        # Close files, release connections, etc.

    handle = manager.on_measurement_teardown(cleanup)
    manager.measure(ps.LinearSweepVoltammetry())
    handle.cancel()
```

## Curve-level events

### `on_curve_begin`

Register a callback to invoke at the start of a new curve. For EIS use `on_eis_data_start`:

```python
import pypalmsens as ps

with ps.connect() as manager:
    def on_curve_start(curve):
        print(f"Starting curve: {curve.title}")

    handle = manager.on_curve_begin(on_curve_start)
    manager.measure(ps.CyclicVoltammetry())
    handle.cancel()
```

### `on_curve_new_data`

Register a callback to invoke when new data are received for a curve. Note that the data are batched depending on available resources:

```python
import pypalmsens as ps

with ps.connect() as manager:
    def on_curve_data(data):
        print(f"Received {len(data)} points")

    handle = manager.on_curve_new_data(on_curve_data)
    manager.measure(ps.CyclicVoltammetry())
    handle.cancel()
```

### `on_curve_end`

Register a callback to invoke at the end of a curve. For EIS use `on_eis_data_end`:

```python
import pypalmsens as ps

with ps.connect() as manager:
    def on_curve_complete(curve):
        print(f"Curve complete: {curve.title}")

    handle = manager.on_curve_end(on_curve_complete)
    manager.measure(ps.CyclicVoltammetry())
    handle.cancel()
```

## EIS-specific events

For Electrochemical Impedance Spectroscopy measurements, use these specialized event handlers:

### `on_eis_data_begin`

Register a callback to invoke at the start of a new EIS data set:

```python
import pypalmsens as ps

with ps.connect() as manager:
    def on_eis_start(data):
        print(f"EIS measurement started with {data.frequency_range} Hz range")

    handle = manager.on_eis_data_begin(on_eis_start)
    manager.measure(ps.ElectrochemicalImpedanceSpectroscopy())
    handle.cancel()
```

### `on_eis_new_data`

Register a callback to invoke when new EIS data are received. Data points are batched depending on available resources:

```python
import pypalmsens as ps

with ps.connect() as manager:
    def on_eis_data(data):
        print(f"Received {len(data)} frequency points")

    handle = manager.on_eis_new_data(on_eis_data)
    manager.measure(ps.ElectrochemicalImpedanceSpectroscopy())
    handle.cancel()
```

### `on_eis_data_end`

Register a callback to invoke at the end of an EIS data set:

```python
import pypalmsens as ps

with ps.connect() as manager:
    def on_eis_complete():
        print("EIS measurement completed")

    handle = manager.on_eis_data_end(on_eis_complete)
    manager.measure(ps.ElectrochemicalImpedanceSpectroscopy())
    handle.cancel()
```

## Error handling

### `on_error`

Register a callback to invoke when an error occurs during a measurement. These errors can be connection or communication errors:

```python
import pypalmsens as ps

with ps.connect() as manager:
    def on_error(error):
        print(f"Error occurred: {error}")

    handle = manager.on_error(on_error)
    try:
        manager.measure(ps.LinearSweepVoltammetry())
    except Exception as e:
        print(f"Exception caught: {e}")
    finally:
        handle.cancel()
```

## Communication events

### `on_receive_message`

Register a callback for when a new message is received. The callback will be invoked, for example, when a method is started, or when `send_string` is called in MethodSCRIPT:

```python
import pypalmsens as ps

with ps.connect() as manager:
    def on_message(message):
        print(f"Received: {message}")

    handle = manager.on_receive_message(on_message)

    # Send a command and receive response
    manager.send_string("START")
    handle.cancel()
```

### `on_receive_status`

Register a callback for idle status update events. Requires active event loop (i.e. async only). The callback will be invoked whenever the instrument sends updated current/potential values during idle state or pretreatment phases. The update frequency varies per device:

```python
import asyncio
import pypalmsens as ps

async def main():
    with await ps.connect_async() as manager:
        async def on_status(status):
            print(f"Status: {status}")

        handle = manager.on_receive_status(on_status)

        # Status updates will be received during idle phases
        await asyncio.sleep(10)

        handle.cancel()

asyncio.run(main())
```

## EventHandle and cancellation

Each event registration returns an `EventHandle` object that can be used to cancel the subscription:

```python
import pypalmsens as ps

with ps.connect() as manager:
    def callback(data):
        print(f"Data received: {data}")

    handle = manager.on_curve_new_data(callback)

    # ... do some work ...

    # Cancel the subscription when no longer needed
    handle.cancel()
```

## Multiple callbacks

You can register multiple callbacks for the same event. All registered callbacks will be invoked in order:

```python
import pypalmsens as ps

with ps.connect() as manager:
    def first_callback(data):
        print("First callback:", data)

    def second_callback(data):
        print("Second callback:", data)

    handle1 = manager.on_curve_new_data(first_callback)
    handle2 = manager.on_curve_new_data(second_callback)

    # Both callbacks will be invoked for each new data event

    handle1.cancel()  # Remove only the first callback
```

## Notes on async events

The `on_receive_message` and `on_receive_status` events have special handling:

- **`receive_message`**: Works in both sync and async contexts. The callback is invoked directly or scheduled via `call_soon_threadsafe` if running in an async context.
- **`receive_status`**: Requires an active event loop (async only). This is because status updates come from the instrument's communication layer which runs on a separate thread.

When using these events, ensure you're either:
1. Running in an async context with `ps.connect_async()` and awaiting operations
2. Or running the sync version within a properly configured event loop

## Example: Complete workflow

Here's a complete example showing how to use multiple events together:

```python
import asyncio
import pypalmsens as ps

async def main():
    with await ps.connect_async() as manager:
        # Setup callback
        setup_handle = manager.on_measurement_setup(lambda: print("Setup"))

        # Begin callback
        begin_handle = manager.on_measurement_begin(lambda: print("Measurement started"))

        # Data callbacks
        data_handle = manager.on_curve_new_data(lambda d: print(f"Data: {len(d)} points"))

        # EIS-specific (if applicable)
        eis_handle = manager.on_eis_new_data(lambda d: print(f"EIS data: {len(d)} points"))

        # End callbacks
        end_handle = manager.on_measurement_end(lambda: print("Measurement ended"))

        # Error callback
        error_handle = manager.on_error(lambda e: print(f"Error: {e}"))

        try:
            await manager.measure(ps.CyclicVoltammetry())
        finally:
            # Clean up all handles
            setup_handle.cancel()
            begin_handle.cancel()
            data_handle.cancel()
            eis_handle.cancel()
            end_handle.cancel()
            error_handle.cancel()

asyncio.run(main())
```
