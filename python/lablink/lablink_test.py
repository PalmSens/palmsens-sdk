from __future__ import annotations

import asyncio

import nest_asyncio

import pypalmsens as ps
from pypalmsens._instruments.shared import create_future

nest_asyncio.apply()

from instance import Instance, discover


def a(f):
    return asyncio.run(create_future(f))


def r(f):
    return asyncio.run(f)


async def main():
    method = ps.CyclicVoltammetry(n_scans=3)
    method = ps.ChronoAmperometry(run_time=3)

    instances = await discover()
    print('\n# Lablink instances')
    for instance in instances:
        print(instance)

    print('---')

    local = Instance('https://127.0.0.1/')
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

    ds = measurement.datasets[0]

    for array in ds:
        print(list(array))

    t = ds[0]

    breakpoint()  # noqa


if __name__ == '__main__':
    asyncio.run(main())
