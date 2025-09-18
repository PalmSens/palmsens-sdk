import asyncio
import pypalmsens


async def main():
    method = pypalmsens.ChronoAmperometry(
        interval_time=0.004,
        potential=1.0,
        run_time=5.0,
    )

    instruments = await pypalmsens.discover_async(ftdi=True)

    print(instruments)

    async with pypalmsens.InstrumentPoolAsync(instruments) as pool:
        results = await pool.measure_hw_sync(method)

    print(results)


asyncio.run(main())
