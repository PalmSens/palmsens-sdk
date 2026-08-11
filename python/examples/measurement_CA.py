import pypalmsens as ps


def new_data_callback(data):
    print(data.last_datapoint())


instrument, *_ = ps.discover()
print(instrument)

with ps.connect(instrument) as manager:
    serial = manager.get_instrument_serial()
    print(serial)

    # Chronoamperometry measurement using helper class
    method = ps.ChronoAmperometry(
        interval_time=0.01,
        potential=1.0,
        run_time=10.0,
    )

    measurement = manager.measure(method, callback=new_data_callback)

print(measurement)
