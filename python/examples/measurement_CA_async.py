import asyncio

import pypalmsens as ps


def new_data_callback(data):
    print(data.last_datapoint())


async def main():
    instrument, *_ = await ps.discover_async()
    print(instrument)

    async with await ps.connect_async(instrument) as manager:
        serial = await manager.get_instrument_serial()
        print(serial)

        method = ps.ChronoAmperometry(
            interval_time=0.02,
            potential=1.0,
            run_time=2.0,
        )

        measurement = await manager.measure(method, callback=new_data_callback)

    print(measurement)


asyncio.run(main())
