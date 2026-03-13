import asyncio
import functools

import pypalmsens as ps
from pypalmsens.data import CallbackData

method = ps.ChronoAmperometry(run_time=10, record_we_potential=True)


def abort_measurement(data: CallbackData, mgr: ps.InstrumentManagerAsync):
    print(data)

    # y corresponds to the current for CA
    if data.last_y >= 0.2:
        print('current reached, aborting...')
        _ = asyncio.create_task(mgr.abort())
        print('aborted!')


async def main():
    mgr = await ps.connect_async()

    callback = functools.partial(abort_measurement, mgr=mgr)

    task_a = asyncio.create_task(mgr.measure(method, callback=callback))

    measurement = await task_a

    return measurement


asyncio.run(main())
