import pypalmsens as ps


def new_data_callback(data):
    print(data.last_datapoint())


instrument, *_ = ps.discover()
print(instrument)

with ps.connect(instrument) as manager:
    serial = manager.get_instrument_serial()
    print(serial)

    method = ps.ElectrochemicalImpedanceSpectroscopy()

    measurement = manager.measure(method, callback=new_data_callback)

print(measurement)
