import asyncio
import csv

from pspython import pspyinstruments, pspymethods


def stream_to_csv_callback(csv_writer):
    def stream_to_csv_callback_channel(new_data):
        for point in new_data:
            csv_writer.writerow([point['index'], point['x'], point['y']])

    return lambda data: stream_to_csv_callback_channel(data)


async def main():
    available_instruments = await pspyinstruments.discover_instruments_async()
    managers = {}

    # create an instance of the instrumentmanager per channel
    async def connect(instrument, index):
        managers[index] = (
            pspyinstruments.InstrumentManagerAsync()
        )  # new_data_callback=new_data_callback(index)))
        success = await managers[index].connect(instrument)
        if success:
            print(f'{index + 1}: connected to {instrument.name}')
        else:
            print(f'{index + 1}: error while connecting to {instrument.name}')
        return success

    tasks = [connect(instrument, i) for (i, instrument) in enumerate(available_instruments)]
    connected = await asyncio.gather(*tasks)

    method = pspymethods.chronoamperometry(interval_time=0.0004, potential=1.0, run_time=5.0)

    if all(connected):

        async def measure(manager, channel):
            csv_file = open(f'test{channel + 1}.csv', 'w', newline='')
            csv_writer = csv.writer(csv_file, delimiter=' ')
            manager.new_data_callback = stream_to_csv_callback(csv_writer)
            measurement = await manager.measure(method)
            csv_file.close()
            return measurement

        # start measurements asynchronously
        tasks = [measure(manager, channel) for (channel, manager) in managers.items()]
        _ = await asyncio.gather(*tasks)  # use gather to await results
        print('measurement(s) finished')

        async def disconnect(instrument_manager, channel):
            success = await instrument_manager.disconnect()
            if success:
                print('channel ' + str(channel + 1) + ': disconnected')
            else:
                print('channel ' + str(channel + 1) + ': error while disconnecting')
            return success

        tasks = [disconnect(manager, channel) for (channel, manager) in managers.items()]
        await asyncio.gather(*tasks)


asyncio.run(main())
