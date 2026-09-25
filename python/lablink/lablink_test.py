from __future__ import annotations

import asyncio

import nest_asyncio

import pypalmsens as ps
from pypalmsens import lablink

nest_asyncio.apply()

assert lablink.IS_SUPPORTED


def a(f):
    return asyncio.run(ps._instruments.shared.wrap_task(f))


def r(f):
    return asyncio.run(f)


async def main():
    method = ps.CyclicVoltammetry()

    local = lablink.Instance('https://127.0.0.1/')
    await local.fetch_metadata()
    print(local)
    session = await local.login('test', 'test')

    [instrument] = session.instruments

    async with await session.claim(instrument) as claim:
        job = await session.start(claim, method=method)
        measurement = await job

    print(job)
    print(measurement)

    arr = measurement[0].xarray()
    print(arr)

    # breakpoint()


if __name__ == '__main__':
    asyncio.run(main())
