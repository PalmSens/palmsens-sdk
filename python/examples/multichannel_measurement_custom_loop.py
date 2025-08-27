import asyncio
from attrs import evolve
import pypalmsens


def new_data_callback(channel):
    def print_results(new_data):
        for point in new_data:
            print(f'channel {channel + 1}: {point}')

    return lambda x: print_results(x)


async def run_steps(manager, channel, steps):
    # Create a new method, a separate method is required for each channel
    method = pypalmsens.ChronoPotentiometry(
        potential_range=pypalmsens.settings.PotentialRange(
            max=pypalmsens.settings.POTENTIAL_RANGE.pr_1_V,  # 1V range
            min=pypalmsens.settings.POTENTIAL_RANGE.pr_10_mV,  # 10mV range
            start=pypalmsens.settings.POTENTIAL_RANGE.pr_1_V,  # 1V range
        ),
        applied_current_range=pypalmsens.settings.CURRENT_RANGE.cr_10_uA,  # 10µA range
        current=0.5,  # applied current in range, i.e. 5µA when the 10µA range is set as the applied range
        interval_time=0.05,  # seconds
        run_time=5,  # seconds
    )
    measurements = []

    for step in steps:
        method = evolve(method, **step)
        measurements.append(await manager.measure(method))

    return measurements


async def main():
    # Create a list of of parameters you want to change
    steps = [
        {
            'current': 0.1,
            'potential_limits': pypalmsens.settings.PotentialLimits(
                limit_max=2, use_limit_min=False
            ),
        },
        {
            'current': -0.2,
            'potential_limits': pypalmsens.settings.PotentialLimits(
                limit_max=-0.5, use_limit_max=False
            ),
        },
        {
            'current': 2,
            'potential_limits': pypalmsens.settings.PotentialLimits(limit_min=2, limit_max=2),
        },
    ]

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

    if all(connected):
        # start measurements asynchronously
        tasks = [run_steps(manager, channel, steps) for (channel, manager) in managers.items()]
        channels = await asyncio.gather(*tasks)  # use gather to await results

        for measurements in channels:
            pypalmsens.save_session_file('example.pssession', measurements)

        for channel, manager in managers.items():
            success = manager.disconnect()
            if success:
                print(f'channel {channel + 1}: disconnected')
            else:
                print(f'channel {channel + 1}: error while disconnecting')


asyncio.run(main())
