import csv

from pspython import pspyinstruments
from pspython.methods import ChronoAmperometryParameters


def stream_to_csv_callback(new_data):
    for point in new_data:
        csv_writer.writerow([point['index'], point['x'], point['y']])
        # csv_writer.writerow([point['frequency'], point['zre'], point['zim']]) #for EIS


csv_file = open('test.csv', 'w', newline='')
csv_writer = csv.writer(csv_file, delimiter=' ')

manager = pspyinstruments.InstrumentManager(new_data_callback=stream_to_csv_callback)

available_instruments = pspyinstruments.discover_instruments()
print('connecting to ' + available_instruments[0].name)
success = manager.connect(available_instruments[0])

if success != 1:
    print('connection failed')
    exit()

print('connection established')

serial = manager.get_instrument_serial()
print(serial)

# #Chronoamperometry measurement using helper class
method = ChronoAmperometryParameters(
    interval_time=0.0004,
    potential=1.0,
    run_time=10.0,
)

measurement = manager.measure(method)
if measurement is not None:
    print('measurement finished')
else:
    print('failed to start measurement')

csv_file.close()

success = manager.disconnect()

if success == 1:
    print('disconnected')
else:
    print('error while disconnecting')
