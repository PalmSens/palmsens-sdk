import asyncio

import pypalmsens as ps


def new_data_callback(new_data):
    for point in new_data:
        print(point)


async def main():
    instruments = await ps.discover_async()
    print(instruments)

    async with await ps.connect_async(instruments[0]) as manager:
        serial = await manager.get_instrument_serial()
        print(serial)

        # Chronoamperometry measurement using helper class
        method = ps.ChronoAmperometry(
            interval_time=0.02,
            potential=1.0,
            run_time=2.0,
        )

        measurement = await manager.measure(method, callback=new_data_callback)

    print(measurement)


asyncio.run(main())
