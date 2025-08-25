import asyncio

import pypalmsens


def new_data_callback(channel):
    def print_results(new_data):
        for point in new_data:
            print(f'channel {channel}: {point}')

    return lambda x: print_results(x)


async def main():
    available_instruments = await pypalmsens.discover_async()
    managers = {}

    # create an instance of the instrumentmanager per channel
    async def connect(instrument, index):
        managers[index] = pypalmsens.InstrumentManagerAsync(
            instrument, callback=new_data_callback(index)
        )
        success = await managers[index].connect()
        if success:
            print(f'{index + 1}: connected to {instrument.name}')
        else:
            print(f'{index + 1}: error while connecting to {instrument.name}')
        return success

    tasks = [connect(instrument, i) for (i, instrument) in enumerate(available_instruments)]
    connected = await asyncio.gather(*tasks)
    follower_channels = [manager for (channel, manager) in managers.items() if channel != 1]

    if all(connected) and 1 in managers:
        method = pypalmsens.ChronoPotentiometry(
            potential_ranges=pypalmsens.settings.PotentialRanges(
                max=pypalmsens.settings.POTENTIAL_RANGE.pr_1_V,  # 1V range
                min=pypalmsens.settings.POTENTIAL_RANGE.pr_10_mV,  # 10mV range
                start=pypalmsens.settings.POTENTIAL_RANGE.pr_1_V,  # 1V range
            ),
            applied_current_range=pypalmsens.settings.CURRENT_RANGE.cr_10_uA,  # 10µA range
            current=0.5,  # applied current in range, i.e. 5µA when the 10µA range is set as the applied range
            interval_time=0.05,  # seconds
            run_time=5,  # seconds
            general=pypalmsens.settings.General(
                use_hardware_sync=True,  # enable hw sync
            ),
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
