import csv

import pypalmsens as ps


def stream_to_csv_callback(data):
    for point in data.new_datapoints():
        csv_writer.writerow([point['index'], point['x'], point['y']])

        ## for EIS
        # csv_writer.writerow([point['Frequency'], point['ZRe'], point['ZIm']])


csv_file = open('test.csv', 'w', newline='')
csv_writer = csv.writer(csv_file)

instruments = ps.discover()
print(instruments)

with ps.connect(instruments[0]) as manager:
    serial = manager.get_instrument_serial()
    print(serial)

    # Chronoamperometry measurement using helper class
    method = ps.ChronoAmperometry(
        interval_time=0.004,
        potential=1.0,
        run_time=10.0,
    )

    measurement = manager.measure(method, callback=stream_to_csv_callback)

print(measurement)

csv_file.close()
