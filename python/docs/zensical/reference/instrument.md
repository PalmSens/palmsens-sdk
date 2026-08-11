# Instrument management

Use the `InstrumentManager()` to start experiments and control your PalmSens instrument.

The most high-level way to start a measurement is to use the `measure()` function:

```pycon
>>> import pypalmsens as ps

>>> method = ps.CyclicVoltammetry()
>>> ps.measure(method)
Measurement(title=Cyclic Voltammetry, timestamp=..., device=EmStat4LR)

```

You can also manage the connection yourself, using `connect()`, for example:

```pycon
>>> with ps.connect() as manager:
...    method = ps.ChronoAmperometry()
...    measurement = manager.measure(method)

```

Or using `InstrumentManager()` directly as a context manager:

```pycon
>>> instrument, *_ = ps.discover()
>>> instrument
Instrument(name='EmStat4 LR [1]', interface='usbcdc')

>>> with ps.InstrumentManager(instrument) as manager:
...    measurement = manager.measure(method)

```

Or managing the instrument connection yourself:

```pycon
>>> manager = ps.InstrumentManager(instrument)
>>> manager.connect()
>>> # ...
>>> manager.disconnect()

```

For more information, see the [measurement documentation](https://dev.palmsens.com/python/latest/_attachments/measuring/).

**Functions:**

- [`pypalmsens.connect`][pypalmsens.connect]
- [`pypalmsens.discover`][pypalmsens.discover]
- [`pypalmsens.measure`][pypalmsens.measure]

**Classes:**

- [`pypalmsens.Instrument`][pypalmsens.Instrument]
- [`pypalmsens.InstrumentManager`][pypalmsens.InstrumentManager]
- [`pypalmsens.InstrumentPool`][pypalmsens.InstrumentPool]

::: pypalmsens.connect
::: pypalmsens.discover
::: pypalmsens.measure
::: pypalmsens.Instrument
::: pypalmsens.InstrumentManager
::: pypalmsens.InstrumentPool
