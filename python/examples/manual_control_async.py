import asyncio

import pypalmsens as ps


async def main():
    instruments = await ps.discover_async()
    print(instruments)

    async with await ps.connect_async(instruments[0]) as manager:
        await manager.set_cell(True)
        print('cell enabled')

        await manager.set_potential(1)
        print('set potential to 1V')

        await manager.set_current_range(ps.settings.CURRENT_RANGE.cr_1_mA)
        print('set cell to to 1mA currrent range')

        current = await manager.read_current()
        print(f'current = {current} µA')

        await manager.set_cell(False)
        print('cell disabled')


asyncio.run(main())
