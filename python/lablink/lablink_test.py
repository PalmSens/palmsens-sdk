from __future__ import annotations

import asyncio

import nest_asyncio

import pypalmsens as ps
from pypalmsens._instruments.shared import create_future

nest_asyncio.apply()

from lablink import LablinkInfo


def a(f):
    return asyncio.run(create_future(f))


def r(f):
    return asyncio.run(f)


async def main():
    method = ps.ChronoAmperometry(run_time=1)

    # handles = await discover()

    # for handle in handles:
    #     print(handle)

    local_handle = await LablinkInfo.from_uri('https://127.0.0.1/')

    lablink = await local_handle.login('test', 'test')

    instruments = lablink.instruments

    for instrument in instruments:
        print(instrument)

    measurements = await lablink.measurements()

    for measurement in measurements[0:5]:
        print(measurement)

    instrument_handles = await lablink.claim(instruments)

    m, *_ = await lablink.start_measurements(instrument_handles, method)

    while not m.is_finished:
        await asyncio.sleep(1)
        print('waiting...')

    assert m.is_finished

    ds = m.datasets[0]

    t = ds[0]

    breakpoint()  # noqa


if __name__ == '__main__':
    asyncio.run(main())
