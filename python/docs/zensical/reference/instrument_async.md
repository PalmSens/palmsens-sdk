# Instrument management (async)

The `InstrumentManagerAsync()` class and supporting functions use [asyncio](https://docs.python.org/3/library/asyncio.html) to provide a high-performance concurrent interface for instrument control.

These api for these functions and classes remain largely the same as the [sequential (non-async) version](./instrument.md).

The main difference is that these are async enabled.
This means you have to use the await/async expressions to manage the event loop.

For example, to start a measurement:

```pycon
>>> import pypalmsens as ps
>>> import asyncio

>>> method = ps.CyclicVoltammetry()

>>> async def main():
...     await ps.measure_async(method)

>>> asyncio.run(main())

```

Or to manage the connection yourself:

```pycon
>>> async def main():
...     async with await ps.connect_async() as manager:
...         method = ps.ChronoAmperometry()
...         measurement = await manager.measure(method)

>>> asyncio.run(main())

```

Or using `InstrumentManagerAsync()` directly as a context manager:

```pycon
>>> async def main():
...     instruments = await ps.discover_async()
...     async with ps.InstrumentManagerAsync(instruments[0]) as manager:
...         measurement = await manager.measure(method)

>>> asyncio.run(main())

```

Or managing the instrument connection yourself:

```pycon
>>> async def main():
...     instruments = await ps.discover_async()
...     manager = ps.InstrumentManagerAsync(instruments[0])
...     await manager.connect()
...     # ...
...     await manager.disconnect()

>>> asyncio.run(main())

```

For more information, see the [measurement documentation](https://dev.palmsens.com/python/latest/_attachments/measuring/).

- [`pypalmsens.connect_async`][pypalmsens.connect_async]
- [`pypalmsens.discover_async`][pypalmsens.discover_async]
- [`pypalmsens.measure_async`][pypalmsens.measure_async]

**Classes:**

- [`pypalmsens.InstrumentManagerAsync`][pypalmsens.InstrumentManagerAsync]
- [`pypalmsens.InstrumentPoolAsync`][pypalmsens.InstrumentPoolAsync]

::: pypalmsens.connect_async
::: pypalmsens.discover_async
::: pypalmsens.measure_async
::: pypalmsens.InstrumentManagerAsync
::: pypalmsens.InstrumentPoolAsync
