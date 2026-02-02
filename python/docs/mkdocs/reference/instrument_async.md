# Instrument management (async)

The `InstrumentManagerAsync()` class and supporting functions use [asyncio](https://docs.python.org/3/library/asyncio.html) to provide a high-performance concurrent interface for instrument control.

These api for these functions and classes remain largely the same as the [sequential (non-async) version](./instrument.md).

The main difference is that these are async enabled.
This means you have to use the await/async expressions to manage the event loop.

For example, to start a measurement:

```python
>>> import pypalmsens as ps

>>> method = ps.CyclicVoltammetry()
>>> await ps.measure(method)
```

Or to manage the connection yourself:

```python
>>> async with await ps.connect_async() as manager:
...     method = ps.ChronoAmperometry()
...     measurement = await manager.measure(method)
```

Or using `InstrumentManagerAsync()` directly as a context manager:

```python
>>> instruments = await discover_async()

>>> async with ps.InstrumentManagerAsync(instruments[0]) as manager:
...     measurement = await manager.measure(method)
```

Or managing the instrument connection yourself:

```python
>>> instruments = await discover_async()

>>> manager = ps.InstrumentManagerAsync(instruments[0])
>>> await manager.connect()
... # ...
>>> await manager.disconnect()
```

For more information, see the [measurement documentation](https://sdk.palmsens.com/python/latest/measuring.html).

::: pypalmsens.connect_async
::: pypalmsens.discover_async
::: pypalmsens.measure_async
::: pypalmsens.InstrumentManagerAsync
::: pypalmsens.InstrumentPoolAsync
