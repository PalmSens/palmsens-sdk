import pypalmsens as ps


def new_data_callback(new_data):
    for point in new_data:
        print(point)


instruments = ps.discover()
print(instruments)

with ps.connect(instruments[0]) as manager:
    serial = manager.get_instrument_serial()
    print(serial)

    method = ps.ElectrochemicalImpedanceSpectroscopy()

    measurement = manager.measure(method, callback=new_data_callback)

print(measurement)
