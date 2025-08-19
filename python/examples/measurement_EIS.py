import pypalmsens
from pypalmsens.methods import ElectrochemicalImpedanceSpectroscopyParameters


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

    # EIS measurement using helper class
    method = ElectrochemicalImpedanceSpectroscopyParameters()

    measurement = manager.measure(method)

    if measurement is not None:
        print('measurement finished')
    else:
        print('failed to start measurement')
