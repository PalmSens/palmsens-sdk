import csv

import pypalmsens


def stream_to_csv_callback(new_data):
    for point in new_data:
        csv_writer.writerow([point['index'], point['x'], point['y']])
        # csv_writer.writerow([point['frequency'], point['zre'], point['zim']]) #for EIS


csv_file = open('test.csv', 'w', newline='')
csv_writer = csv.writer(csv_file, delimiter=' ')

available_instruments = pypalmsens.discover()
print('connecting to ' + available_instruments[0].name)

with pypalmsens.connect(available_instruments[0]) as manager:
    manager.callback = stream_to_csv_callback

    print('connection established')

    serial = manager.get_instrument_serial()
    print(serial)

    # #Chronoamperometry measurement using helper class
    method = pypalmsens.ChronoAmperometry(
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
