from pypalmsens.methods import ChronoAmperometryParameters
import pypalmsens


def new_data_callback(new_data):
    for point in new_data:
        print(point)


available_instruments = pypalmsens.discover()
print('connecting to ' + available_instruments[0].name)

with pypalmsens.connect(available_instruments[0]) as manager:
    print('connection established')

    manager.callback = new_data_callback

    serial = manager.get_instrument_serial()
    print(serial)

    # Chronoamperometry measurement using helper class
    method = ChronoAmperometryParameters(
        interval_time=0.01,
        potential=1.0,
        run_time=10.0,
    )

    measurement = manager.measure(method)

    if measurement is not None:
        print('measurement finished')
    else:
        print('failed to start measurement')
