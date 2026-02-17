import pypalmsens as ps
import functools


def new_data_callback(data, channel: int):
    print(f'Channel {channel}: {data.last_datapoint()}')


method = ps.ChronoAmperometry(
    interval_time=0.004,
    potential=1.0,
    run_time=5.0,
)

instruments = ps.discover()

for instrument in instruments:
    print(instrument)

with ps.InstrumentPool(instruments) as pool:
    callback_list = [
        functools.partial(new_data_callback, channel=manager.instrument.channel)
        for manager in pool.managers
    ]

    measurements = pool.measure(method=method, callback=callback_list)

for measurement in measurements:
    print(measurement)
