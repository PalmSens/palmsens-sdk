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
    # Claim one instrument, start a measurement
    async with await session.claim(instruments[0]) as claim:
        job = await session.start(claim, method=method)
        print(job)
        measurement = await job

    print(measurement)

    return

    # Start same method on many instruments
    claims = await session.claim_many(instruments)
    try:
        batch = await session.start_many(claims, method)
        assert not batch.is_finished
        for job in batch.jobs:
            print(job.status, job.ref)
        data = await batch.jobs[0]
        for ref, error in batch.failures:
            print(f'{ref} failed: {error}')
    finally:
        for claim in claims:
            await claim.release()

    assert batch.is_finished

    while not job.is_finished:
        await asyncio.sleep(1)
        print('waiting...')

    assert job.is_finished

    ds = job.datasets[0]

    for array in ds:
        print(list(array))

    t = ds[0]

    breakpoint()  # noqa


if __name__ == '__main__':
    asyncio.run(main())
