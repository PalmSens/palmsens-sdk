# Lablink

The [pypalmsens.lablink][] module lets you connect to a Lablink server and control the instruments attached to it. You can use it to list instruments, claim them, start measurements, and retrieve previously recorded data.

Everything in this module is async, so its calls are awaited.

## Connecting to an instance

A Lablink instance is a server, identified by an address, that manages one or more instruments.

### Discovering instances

[pypalmsens.lablink.discover][] returns every Lablink instance reachable on the network:

```python
instances = await lablink.discover()

for instance in instances:
    print(instance.address, instance.name)
```

### Connecting to a known instance

If you already know the address of the server, create an [Instance][pypalmsens.lablink.Instance] directly. The default address points to the local server:

```python
local = lablink.Instance('https://127.0.0.1/')
```

A newly created instance only knows its address. Call [fetch_metadata][pypalmsens.lablink.Instance.fetch_metadata] to fill in the name, version, and serial number:

```python
await local.fetch_metadata()
print(local.name, local.version, local.serial_number)
```

## Logging in

Log in with a username and password to get a [Session][pypalmsens.lablink.Session]:

```python
session = await local.login('test', 'test')
```

The session is your entry point for everything that follows: listing instruments, claiming them, starting measurements, and retrieving data.

## Instruments

A session keeps track of the instruments attached to its Lablink instance. The [Session.instruments][pypalmsens.lablink.Session.instruments] property holds the result of the most recent [list_instruments][pypalmsens.lablink.Session.list_instruments] call, and may be stale or empty.

```python
instruments = await session.list_instruments()
instrument, *_ = instruments
```

An [InstrumentRef][pypalmsens.lablink.InstrumentRef] is a lightweight snapshot of an instrument, with the information you need to identify it:

```python
print(instrument.name, instrument.serial_number)
print(instrument.model, instrument.status)
```

The [status][pypalmsens.lablink.InstrumentRef.status] is `Idle`, `Measuring`, or `Error`.

### Claiming instruments

Before an instrument can be used for a measurement, you must claim it. Claiming locks the instrument: while a claim is held, no one else can use it.

Use [Session.claim][pypalmsens.lablink.Session.claim] and the returned [InstrumentClaim][pypalmsens.lablink.InstrumentClaim] as an async context manager. The claim is released when the `async with` block exits:

```python
async with await session.claim(instrument) as claim:
    # only this session can use the instrument here
    ...
```

To claim several instruments at once, use [claim_many][pypalmsens.lablink.Session.claim_many]:

```python
async with await session.claim_many(instruments) as claims:
    ...
```

The returned [ClaimBatch][pypalmsens.lablink.ClaimBatch] releases every claim when the block exits.

## Starting a measurement

Start a measurement on a claimed instrument with [Session.start][pypalmsens.lablink.Session.start]. The measurement method is passed as a keyword argument:

```python
method = ps.CyclicVoltammetry()
job = await session.start(claim, method=method)
```

The call returns a [MeasurementJob][pypalmsens.lablink.MeasurementJob] for the ongoing measurement. Await the job to wait for it to finish and receive the data:

```python
measurement = await job
```

You can also check progress with [is_finished][pypalmsens.lablink.MeasurementJob.is_finished] or stop the measurement early with [cancel][pypalmsens.lablink.MeasurementJob.cancel]:

```python
if job.is_finished:
    print('done')
else:
    job.cancel()
```

To measure on several instruments at once, use [start_many][pypalmsens.lablink.Session.start_many] with multiple claims. It returns one [MeasurementJob][pypalmsens.lablink.MeasurementJob] per instrument.

## Previous measurements

A session can also look up measurements that were recorded before. Use [list_measurements][pypalmsens.lablink.Session.list_measurements] to get a list of [MeasurementRef][pypalmsens.lablink.MeasurementRef] objects:

```python
refs = await session.list_measurements()
ref, *_ = refs
```

A reference only carries the measurement's metadata: name, timestamp, method ID, and number of points. Fetch the full data with [fetch][pypalmsens.lablink.MeasurementRef.fetch]:

```python
measurement = await ref.fetch()
```

## Measurement data

A [Measurement][pypalmsens.lablink.Measurement] is a sequence of datasets. Each dataset can be converted to an xarray [`xr.Dataset`][] with [xarray][pypalmsens.lablink.Dataset.xarray]:

```python
data = measurement[0].xarray()
```

The measurement data API is still work in progress.

## Complete example

```python
import asyncio

import pypalmsens as ps
from pypalmsens import lablink

async def main():
    method = ps.CyclicVoltammetry()

    local = lablink.Instance('https://127.0.0.1/')
    await local.fetch_metadata()
    session = await local.login('test', 'test')

    # Grab first instrument
    instrument, _* = session.instruments

    async with await session.claim(instrument) as claim:
        job = await session.start(claim, method=method)
        measurement = await job

    print(measurement)

    data = measurement[0].xarray()

if __name__ == '__main__':
    asyncio.run(main())
```
