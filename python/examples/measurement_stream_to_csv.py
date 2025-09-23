import csv

import pypalmsens as ps


def stream_to_csv_callback(new_data):
    for point in new_data:
        csv_writer.writerow([point['index'], point['x'], point['y']])
        # csv_writer.writerow([point['frequency'], point['zre'], point['zim']]) #for EIS


csv_file = open('test.csv', 'w', newline='')
csv_writer = csv.writer(csv_file, delimiter=' ')

instruments = ps.discover()
print(instruments)

with ps.connect(instruments[0]) as manager:
    manager.callback = stream_to_csv_callback

    serial = manager.get_instrument_serial()
    print(serial)

    # Chronoamperometry measurement using helper class
    method = ps.ChronoAmperometry(
        interval_time=0.0004,
        potential=1.0,
        run_time=10.0,
    )

    measurement = manager.measure(method)

print(measurement)

csv_file.close()
