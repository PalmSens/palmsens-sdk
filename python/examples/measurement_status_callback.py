import asyncio

import pypalmsens as ps
from pypalmsens.data import Status

pretreatment_data = []


def idle_status_callback(point: Status):
    if point.device_state == 'Pretreatment':
        pretreatment_data.append(
            {
                'phase': point.pretreatment_phase,
                'current': point.current,
                'potential': point.potential,
            }
        )

    print(f'{point.device_state}: {point}')


def new_data_callback(data):
    print(data.last_datapoint())


async def main():
    instruments = await ps.discover_async()
    print(instruments)

    async with await ps.connect_async(instruments[0]) as manager:
        manager.register_status_callback(idle_status_callback)

        # While sleeping, the callback reports the
        # idle current/potential every second
        await asyncio.sleep(5)

        # The status callback repurts the
        # current/potential during pretreatment phases
        method = ps.ChronoAmperometry(
            pretreatment=ps.settings.Pretreatment(
                conditioning_time=2,
                deposition_time=2,
            ),
            interval_time=0.02,
            potential=1.0,
            run_time=2.0,
        )

        measurement = await manager.measure(method, callback=new_data_callback)

        await asyncio.sleep(5)

        manager.unregister_status_callback()

    print(measurement)


asyncio.run(main())

print(pretreatment_data)
