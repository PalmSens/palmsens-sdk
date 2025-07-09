import asyncio

from pspython import pspyinstruments, pspymethods


def new_data_callback(channel):
    def print_results(new_data):
        for point in new_data:
            for type, value in point.items():
                print(f'channel {channel}: {type} = {value}')

    return lambda x: print_results(x)


async def main():
    available_instruments = await pspyinstruments.discover_instruments_async()
    managers = {}

    # create an instance of the instrumentmanager per channel
    async def connect(instrument, index):
        managers[index] = pspyinstruments.InstrumentManagerAsync(
            new_data_callback=new_data_callback(index)
        )
        success = await managers[index].connect(instrument)
        if success:
            print(f'{index + 1}: connected to {instrument.name}')
        else:
            print(f'{index + 1}: error while connecting to {instrument.name}')
        return success

    tasks = [connect(instrument, i) for (i, instrument) in enumerate(available_instruments)]
    connected = await asyncio.gather(*tasks)
    follower_channels = [manager for (channel, manager) in managers.items() if channel != 1]

    if all(connected) and 1 in managers:
        method = pspymethods.chronopotentiometry(
            potential_range_max=pspymethods.get_potential_range(7),  # 1V range
            potential_range_min=pspymethods.get_potential_range(1),  # 10mV range
            potential_range_start=pspymethods.get_potential_range(7),  # 1V range
            applied_current_range=pspymethods.get_current_range(5),  # 10µA range
            current=0.5,  # applied current in range, i.e. 5µA when the 10µA range is set as the applied range
            interval_time=0.05,  # seconds
            run_time=5,  # seconds
            use_hardware_sync=True,  # enable hw sync
        )

        # start measurements asynchronously on follower channels
        follower_channels_initiated = []
        follower_channels_measurement_results = []

        for manager in follower_channels:
            initiated, result = manager.initiate_hardware_sync_follower_channel(method)
            follower_channels_initiated.append(initiated)
            follower_channels_measurement_results.append(result)

        await asyncio.gather(*follower_channels_initiated)

        # start the measurement on primary channel
        follower_channels_measurement_results.append(managers[1].measure(method))
        # use gather to await results
        measurements = await asyncio.gather(*follower_channels_measurement_results)
        print(f'Collected {len(measurements)} measurements')

        for channel, manager in managers.items():
            success = await manager.disconnect()
            if success:
                print(f'channel {channel}: disconnected')
            else:
                print(f'channel {channel}: error while disconnecting')


asyncio.run(main())
