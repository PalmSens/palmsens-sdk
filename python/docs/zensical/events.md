# Events API

This section documents the event system exposed by :class:`pypalmsens.InstrumentManager` and its mixin.  The events mirror the asynchronous callbacks that PalmSens instruments emit during a measurement. They are grouped into categories:
- **Measurement lifecycle** – ``measurement_setup`` / ``measurement_begin`` / ``measurement_end`` / ``measurement_teardown``
- **Curve & EIS data** – ``curve_*`` and ``eis_*`` events
- **Generic events** – ``error``
- **Communication events** – ``receive_message`` / ``receive_status``

All methods return a :class:`EventHandle` which can be used to cancel the subscription.  The API is intentionally very close to the underlying communication layer, but keeps the public interface simple for users.

---
## Measurement lifecycle

```python
import pypalmsens as ps

with ps.connect() as manager:
    # Setup resources before any measurement starts
    handle_setup = manager.on_measurement_setup(lambda: print("Setup resources"))

    # The first point of the measurement is reported when this event fires
    handle_begin = manager.on_measurement_begin(lambda meas: print(f"Started {meas.method}"))

    # Measurement finishes – either success or error
    handle_end = manager.on_measurement_end(lambda: print("Measurement finished"))

    # Final cleanup after measurement ends
    handle_teardown = manager.on_measurement_teardown(lambda: print("Cleanup resources"))

    manager.measure(ps.CyclicVoltammetry())

    # cancel if needed
    handle_setup.cancel()
```

### Event signatures
| Event | Callback signature |
|-------|--------------------|
| ``measurement_setup`` | :func:`Callable[[], None]` |
| ``measurement_begin`` | :func:`Callable[[Measurement], None]` |
| ``measurement_end`` | :func:`Callable[[], None]` |
| ``measurement_teardown`` | :func:`Callable[[], None]` |

---
## Curve & EIS data events

These events fire while a measurement is actively sending data.  For most users you will subscribe to:
- ``curve_begin`` – notified when the first point of a curve arrives.
- ``curve_new_data`` – called repeatedly with :class:`CallbackData` containing batched points.
- ``curve_end`` – fired once all points for that curve are received.

EIS data follows a similar pattern but uses :class:`EISData` and :class:`CallbackDataEIS` objects:

```python
with ps.connect() as manager:
    handle_curve = manager.on_curve_new_data(lambda data: print(f"{len(data.x)} points received"))
    handle_eis = manager.on_eis_new_data(lambda d: print("EIS point", d.frequency, d.impedance))
```

### Event signatures
| Event | Callback signature |
|-------|--------------------|
| ``curve_begin`` | :func:`Callable[[Curve], None]` |
| ``curve_new_data`` | :func:`Callable[[CallbackData], None]` |
| ``curve_end`` | :func:`Callable[[Curve], None]` |
| ``eis_data_begin`` | :func:`Callable[[EISData], None]` |
| ``eis_new_data`` | :func:`Callable[[CallbackDataEIS], None]` |
| ``eis_data_end`` | :func:`Callable[[], None]` |

---
## Generic events

The library also provides a simple error channel:

```python
handle_err = manager.on_error(lambda e: print("Error occurred", e))
```

### Event signatures
| Event | Callback signature |
|-------|--------------------|
| ``error`` | :func:`Callable[[], None]` |

---
## Communication events

PalmSens instruments can emit arbitrary text messages or status updates while idle.  These are exposed as:
- ``receive_message`` – receives a string message.
- ``receive_status`` – receives a :class:`Status` object representing the current voltage/current.

```python
handle_msg = manager.on_receive_message(lambda msg: print("MSG:", msg))
handle_stat = manager.on_receive_status(lambda st: print(st.potential, st.current))
```

**Note:** ``receive_status`` requires an active :class:`asyncio.AbstractEventLoop`.  If you call it from synchronous code it will raise a :class:`RuntimeError`.

---
## Getting the event handle

All ``on_*`` methods return an :class:`EventHandle`.  The returned object implements:
- :func:`cancel() <pypalmsens._instruments.events_mixin.EventHandle.cancel>` – removes the callback so it no longer fires.

---
## Summary table

| Category | Events |
|----------|--------|
| Measurement | ``measurement_setup``, ``measurement_begin``, ``measurement_end``, ``measurement_teardown`` |
| Curve | ``curve_begin``, ``curve_new_data``, ``curve_end`` |
| EIS | ``eis_data_begin``, ``eis_new_data``, ``eis_data_end`` |
| Error | ``error`` |
| Communication | ``receive_message``, ``receive_status`` |
|
---
## Reference
- :class:`pypalmsens._instruments.events_mixin.EventsMixin`
- :class:`pypalmsens._instruments.callback.Status`
- :class:`pypalmsens._instruments.callback.CallbackData`
- :class:`pypalmsens._instruments.callback.CallbackDataEIS`
