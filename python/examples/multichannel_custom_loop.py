import asyncio
from attrs import evolve
import pypalmsens


async def custom_loop(manager, *, method, steps):
    measurements = []

    for step in steps:
        method = evolve(method, **step)
        measurements.append(await manager.measure(method))

    return measurements


async def main():
    method = pypalmsens.ChronoAmperometry(
        interval_time=0.004,
        run_time=5.0,
    )

    steps = [
        {
            'potential': 0.4,
        },
        {
            'potential': 0.6,
        },
        {
            'potential': 1.0,
        },
    ]

    instruments = await pypalmsens.discover_async(ftdi=True)

    print(instruments)

    async with pypalmsens.InstrumentPoolAsync(instruments) as pool:
        results = await pool.submit(custom_loop, method=method, steps=steps)

    print(results)

    for i, measurements in enumerate(results):
        pypalmsens.save_session_file(f'example-{i}.pssession', measurements)


asyncio.run(main())
