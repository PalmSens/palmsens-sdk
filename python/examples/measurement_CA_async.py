import asyncio

from pspython import pspyinstruments
from pspython.methods import ChronoAmperometryParameters


def new_data_callback(new_data):
    for point in new_data:
        for type, value in point.items():
            print(f'{type} = {value}')


async def main():
    manager = pspyinstruments.InstrumentManagerAsync(new_data_callback=new_data_callback)
    available_instruments = await pspyinstruments.discover_instruments_async()
    print('connecting to ' + available_instruments[0].name)
    success = await manager.connect(available_instruments[0])

    if success != 1:
        print('connection failed')
        exit()

    print('connection established')

    serial = await manager.get_instrument_serial()
    print(serial)

    # Chronoamperometry measurement using helper class
    method = ChronoAmperometryParameters(
        interval_time=0.02,
        potential=1.0,
        run_time=2.0,
    )

    measurement = await manager.measure(method)

    if measurement is not None:
        print('measurement finished')
    else:
        print('failed to start measurement')

    success = await manager.disconnect()

    if success == 1:
        print('disconnected')
    else:
        print('error while disconnecting')


asyncio.run(main())
