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

    # local = lablink.Instance('http://127.0.0.1/')
    local = lablink.Instance('http://192.168.178.79:5000')
    info = await local.fetch_metadata()
    print(info)
    session = await local.login('test', 'test')
    print(session)

    instruments = await session.list_instruments()
    print(instruments)

    [instrument] = session.instruments

    ret = r(session.list_measurements())
    data = r(ret[0].fetch())

    async with await session.claim(instrument) as claim:
        job = await session.start(claim, method=method)

        print(job)

        measurement = await job

    breakpoint()
    return

    print(job)
    print(measurement)

    arr = measurement[0].xarray()
    print(arr)

    # breakpoint()


if __name__ == '__main__':
    asyncio.run(main())
