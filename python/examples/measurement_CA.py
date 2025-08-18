from pypalmsens import instruments
from pypalmsens.methods import ChronoAmperometryParameters


def new_data_callback(new_data):
    for point in new_data:
        print(point)


manager = instruments.InstrumentManager(callback=new_data_callback)

available_instruments = instruments.discover()
print('connecting to ' + available_instruments[0].name)
success = manager.connect(available_instruments[0])

if success != 1:
    print('connection failed')
    exit()

print('connection established')

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

success = manager.disconnect()

if success == 1:
    print('disconnected')
else:
    print('error while disconnecting')
