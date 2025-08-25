import asyncio

import pypalmsens


async def main():
    available_instruments = await pypalmsens.discover_async()
    print(f'connecting to {available_instruments[0].name}')

    async with await pypalmsens.connect_async(available_instruments[0]) as manager:
        print('connection established')

        await manager.set_cell(True)
        print('cell enabled')

        await manager.set_potential(1)
        print('set potential to 1V')

        await manager.set_current_range(pypalmsens.settings.CURRENT_RANGE.cr_1_mA)
        print('set cell to to 1mA currrent range')

        current = await manager.read_current()
        print(f'current = {current} µA')

        await manager.set_cell(False)
        print('cell disabled')


asyncio.run(main())
