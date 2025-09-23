import asyncio
import pypalmsens as ps


async def main():
    method = ps.ChronoAmperometry(
        interval_time=0.004,
        potential=1.0,
        run_time=5.0,
    )
    method.general.use_hardware_sync = True

    instruments = await ps.discover_async(ftdi=True)

    print(instruments)

    async with ps.InstrumentPoolAsync(instruments) as pool:
        results = await pool.measure(method)

    print(results)


asyncio.run(main())
