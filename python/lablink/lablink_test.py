from __future__ import annotations

import asyncio

import nest_asyncio

import pypalmsens as ps
from pypalmsens import lablink

nest_asyncio.apply()


def a(f):
    return asyncio.run(ps._instruments.shared.wrap_task(f))


def r(f):
    return asyncio.run(f)


async def main():
    method = ps.CyclicVoltammetry()

    instances = await lablink.discover()
    print('\n# Lablink instances')
    for instance in instances:
        print(instance)

    print('---')

    local = lablink.Instance('https://127.0.0.1/')
    await local.fetch_metadata()
    print(local)
    session = await local.login('test', 'test')

    print('\n# Instruments')
    # instruments = await session.fetch_instruments()  # needs SDK update
    instruments = session.instruments
    for instrument in instruments:
        print(instrument)

    print('\n# Data')
    measurements = await session.list_measurements()
    for ref in measurements[0:5]:
        print(ref)

    old_data = await measurements[0].fetch()
    print(old_data)

    print('\n# Measurements')

    print('\n## Single')
    # Claim one instrument, start a measurement
    async with await session.claim(instruments[0]) as claim:
        job = await session.start(claim, method=method)
        measurement = await job

    print(job)
    print(measurement)

    print('\n## Batch')

    # Start same method on many instruments
    async with await session.claim_many(instruments) as claims:
        jobs = await session.start_many(claims, method=method)
        measurements = await asyncio.gather(*jobs)

    print(jobs)
    print(measurements)

    print('\n# Data')

    arr = measurement[0].xarray()
    print(arr)

    breakpoint()


if __name__ == '__main__':
    asyncio.run(main())
