# Lablink

!!! warning "Work in progress"

    Lablink support is currently being developed. More details coming soon!

!!! note "Lablink API not final"

    Although the examples here should mostly hold up, method names and signatures may change in future versions. Keep an eye on the [changelog](../releases).

The [pypalmsens.lablink][] module lets you connect to a Lablink server and control the instruments attached to it.
You can use it to list instruments, claim them, start measurements, and retrieve previously recorded data.

Everything in this module is async, so its calls are awaited.

## Connecting to an instance

A Lablink [instance] is a server, identified by an address, that manages one or more instruments.

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

A newly created instance only knows its address. Call [get_info][pypalmsens.lablink.Instance.get_info] to fill in the name, version, and serial number:

```python
await local.get_info()
# LablinkInfo(name='My Lablink', version='2.1.0', special_version='Standard', os_version='Fedora Linux 43 (WSL)', model='WSL', serial_number='SERIAL_NUMBER', is_measuring=False)
```
print(local.name, local.version, local.serial_number)
```

## Logging in

Log in with a username and password to get a [Session][pypalmsens.lablink.Session]:

```python
session = await local.login('Alice', 'hunter2')
```

The session is your entry point for everything that follows: listing instruments, claiming them, starting measurements, and retrieving data.

## Registering a new user

If this is enabled on the server, you can register as a new user via the API:

```python
await local.register_new_user('Bob', 'badpassword')
```

## Instruments

A session keeps track of the instruments attached to its Lablink instance. The [Session.instruments][pypalmsens.lablink.Session.instruments] property holds the result of the most recent [list_instruments][pypalmsens.lablink.Session.list_instruments] call, and may be stale or empty.

```python
instruments = await session.list_instruments()
instrument, *_ = instruments
```

An [Instrument][pypalmsens.lablink.Instrument] references an instrument by its serial number. You can query the information you need to identify it:

```python
print(instrument.serial_number)
```

### Claiming instruments

Before an instrument can be used for a measurement, you must claim it. Claiming locks the instrument to the session: while a claim is held, no one else can use it.

Use [Instrument.claim][pypalmsens.lablink.Instrument.claim] and the returned [InstrumentClaim][pypalmsens.lablink.InstrumentClaim] as an async context manager. The claim is released when the `async with` block exits:

```python
async with await instrument.claim() as claim:
    # only this session can use the instrument here
    ...
```

To claim several instruments at once, use [claim][pypalmsens.lablink.Session.claim]:

```python
async with await session.claim(instruments) as claims:
    ...
```

The returned [InstrumentClaimBatch][pypalmsens.lablink.InstrumentClaimBatch] releases every claim when the block exits.

## Starting a measurement

Start a measurement on a claimed instrument with [Session.start_measurement][pypalmsens.lablink.Session.start_measurement]. The measurement method is passed as a keyword argument:

```python
method = ps.CyclicVoltammetry()
job = await session.start_measurement(claim, method=method)
```

The call returns a [MeasurementJob][pypalmsens.lablink.MeasurementJob] for the ongoing measurement. Await the job to wait for it to finish and receive the data:

```python
measurement = await job
```

You can [pause][pypalmsens.lablink.MeasurementJob.pause], [resume][pypalmsens.lablink.MeasurementJob.resume], and stop the measurement early with [abort][pypalmsens.lablink.MeasurementJob.abort]

```python
await job.pause()
await job.resume()
await job.abort()
```

To measure on several instruments at once, use [start_measurement][pypalmsens.lablink.Session.start_measurement] with multiple claims. It returns one [MeasurementJob][pypalmsens.lablink.MeasurementJob] per instrument.

## Previous measurements

A session can also look up measurements that were recorded before. Use [list_measurements][pypalmsens.lablink.Session.list_measurements] to get a list of [Measurement][pypalmsens.lablink.Measurement] objects:

```python
measurements = await session.list_measurements()
measurement, *_ = measurements
```

## Measurement data

A reference only carries the measurement's metadata: name, timestamp, method ID, and number of points. Fetch the full data with [get_data][pypalmsens.lablink.Measurement.get_data]:

```python
data = await ref.get_data()
```

The data are returned as an [xarray.Dataset][]. or [xarray.DataTree][].

The measurement data API is still work in progress.

## Complete example

```python
import asyncio

import pypalmsens as ps
from pypalmsens import lablink

async def main():
    method = ps.CyclicVoltammetry()

    local = lablink.Instance('https://127.0.0.1/')
    await local.get_info()
    session = await local.login('test', 'test')

    instrument, _* = session.instruments

    async with await instrument.claim() as claim:
        job = await claim.start_measurement(method=method)
        measurement = await job

    print(measurement)

    data = measurement.get_data()
    print(data)

if __name__ == '__main__':
    asyncio.run(main())
```
