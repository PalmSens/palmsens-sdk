from __future__ import annotations

import asyncio

import nest_asyncio

import pypalmsens as ps
from pypalmsens._instruments.shared import create_future

nest_asyncio.apply()

from lablink import LablinkInfo, discover


def a(f):
    return asyncio.run(create_future(f))


def r(f):
    return asyncio.run(f)


async def main():
    method = ps.CyclicVoltammetry()

    handles = await discover()

    for handle in handles:
        print(handle)

    local_handle = await LablinkInfo.from_uri('https://127.0.0.1/')

    lablink = await local_handle.login('test', 'test')

    instrument_handles = lablink.instruments

    for instrument_handle in instrument_handles:
        print(instrument_handle)

    measurements = await lablink.measurements()

    for measurement in measurements[0:5]:
        print(measurement)

    instruments = await lablink.claim(instrument_handles)


if __name__ == '__main__':
    asyncio.run(main())
