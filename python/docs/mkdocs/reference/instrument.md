# Instrument management

Use the `InstrumentManager()` to start experiments and control your PalmSens instrument.

The most high-level way to start a measurement is to use the `measure()` function:

```python
>>> import pypalmsens as ps

>>> method = ps.CyclicVoltammetry()
>>> ps.measure(method)
```

You can also manage the connection yourself, using `connect()`, for example:

```python
>>> with ps.connect() as manager:
...    method = ps.ChronoAmperometry()
...    measurement = manager.measure(method)
```

Or using `InstrumentManager()` directly as a context manager:

```python
>>> instruments = discover()

>>> with ps.InstrumentManager(instruments[0]) as manager:
...    measurement = manager.measure(method)
```

Or managing the instrument connection yourself:

```python
>>> instruments = discover()

>>> manager = ps.InstrumentManager(instruments[0])
>>> manager.connect()
>>> # ...
>>> manager.disconnect()
```

For more information, see the [measurement documentation](https://dev.palmsens.com/python/latest/_attachments/measuring/).

::: pypalmsens.connect
::: pypalmsens.discover
::: pypalmsens.measure
::: pypalmsens.InstrumentManager
::: pypalmsens.InstrumentPool
