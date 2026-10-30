# Lablink

Use this module to connect to your lablink server, manage instruments, start experiments, and retrieve data.

Basic usage:


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


::: pypalmsens.lablink