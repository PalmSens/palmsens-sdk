from __future__ import annotations

import asyncio

import nest_asyncio

import pypalmsens as ps
from pypalmsens._instruments.shared import create_future

nest_asyncio.apply()

from lablink import Instance, discover


def a(f):
    return asyncio.run(create_future(f))


def r(f):
    return asyncio.run(f)


async def main():
    method = ps.ChronoAmperometry(run_time=1)
    method = ps.CyclicVoltammetry(n_scans=3)

    instances = await discover()

    for instance in instances:
        print(instance)

    local = await Instance.from_uri('https://127.0.0.1/')
    session = await local.login('test', 'test')

    instruments = await session.list_instruments()
    for instrument in instruments:
        print(instrument)

    measurements = await session.list_measurements()
    for ref in measurements[0:5]:
        print(ref)

    old_data = await measurements[0].fetch()
    print(old_data)

    # Claim one instrument, start a measurement
    async with await session.claim(instruments[0]) as claim:
        job = await session.start(claim, method)
        assert not job.is_finished
        data = await job
        assert job.is_finished

    claims = await session.claim(instruments)

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
