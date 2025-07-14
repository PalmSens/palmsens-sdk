import asyncio
import os

from pspython import pspyfiles, pspyinstruments, pspymethods


def new_data_callback(channel):
    def print_results(new_data):
        for point in new_data:
            for type, value in point.items():
                print(f'channel {channel + 1}: {type} = {value}')

    return lambda x: print_results(x)


def update_method(method, **kwargs):
    i_applied = kwargs.get('i_applied', None)
    upper_e_limit = kwargs.get('upper_e_limit', None)
    lower_e_limit = kwargs.get('lower_e_limit', None)

    if i_applied is not None:
        method.Current = i_applied

    if upper_e_limit is not None:
        method.UseLimitMaxValue = True
        method.LimitMaxValue = upper_e_limit
    else:
        method.UseLimitMaxValue = False

    if lower_e_limit is not None:
        method.UseLimitMinValue = True
        method.LimitMinValue = lower_e_limit
    else:
        method.UseLimitMinValue = False

    return method


async def run_steps(manager, channel, steps):
    # Create a new method, a separate method is required for each channel
    method = pspymethods.chronopotentiometry(
        potential_range_max=pspymethods.get_potential_range(7),  # 1V range
        potential_range_min=pspymethods.get_potential_range(1),  # 10mV range
        potential_range_start=pspymethods.get_potential_range(7),  # 1V range
        applied_current_range=pspymethods.get_current_range(5),  # 10µA range
        current=0.5,  # applied current in range, i.e. 5µA when the 10µA range is set as the applied range
        interval_time=0.05,  # seconds
        run_time=5,  # seconds
    )
    measurements = []

    for step in steps:
        method = update_method(method, **step)
        measurements.append(await manager.measure(method))

    return measurements


async def main():
    # Create a list of of parameters you want to change
    steps = [
        {'i_applied': 0.1, 'upper_e_limit': 2},
        {'i_applied': -0.2, 'lower_e_limit': -0.5},
        {'i_applied': 2, 'lower_e_limit': -2, 'upper_e_limit': 2},
    ]

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

    if all(connected):
        # start measurements asynchronously
        tasks = [run_steps(manager, channel, steps) for (channel, manager) in managers.items()]
        channels = await asyncio.gather(*tasks)  # use gather to await results

        for measurements in channels:
            pspyfiles.save_session_file(os.getcwd() + '\\example.pssession', measurements)

        for channel, manager in managers.items():
            success = manager.disconnect()
            if success:
                print(f'channel {channel + 1}: disconnected')
            else:
                print(f'channel {channel + 1}: error while disconnecting')


asyncio.run(main())
