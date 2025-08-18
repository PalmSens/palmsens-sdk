import asyncio

from pypalmsens import instruments
from pypalmsens.methods import CURRENT_RANGE


async def main():
    manager = instruments.InstrumentManagerAsync()

    available_instruments = await instruments.discover_async()
    print(f'connecting to {available_instruments[0].name}')
    success = await manager.connect(available_instruments[0])

    if success != 1:
        print('connection failed')
        exit()

    print('connection established')

    await manager.set_cell(True)
    print('cell enabled')

    await manager.set_potential(1)
    print('set potential to 1V')

    await manager.set_current_range(CURRENT_RANGE.cr_1_mA)
    print('set cell to to 1mA currrent range')

    current = await manager.read_current()
    print(f'current = {current} µA')

    await manager.set_cell(False)
    print('cell disabled')

    success = await manager.disconnect()

    if success == 1:
        print('disconnected')
    else:
        print('error while disconnecting')


asyncio.run(main())
