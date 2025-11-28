import pypalmsens as ps


def new_data_callback(new_data):
    for point in new_data:
        print(point)


instruments = ps.discover()
print(instruments)

with ps.connect(instruments[0]) as manager:
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
