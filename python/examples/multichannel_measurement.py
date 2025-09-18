import pypalmsens


def new_data_callback(new_data):
    for point in new_data:
        print(point)


method = pypalmsens.ChronoAmperometry(
    interval_time=0.004,
    potential=1.0,
    run_time=5.0,
)

instruments = pypalmsens.discover()

print(instruments)

# run multichannel experiment with callback
with pypalmsens.InstrumentPool(instruments, callback=new_data_callback) as pool:
    results = pool.measure(method=method)

print(results)
