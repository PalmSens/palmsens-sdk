import pypalmsens as ps


def new_data_callback(data):
    print(data.last_datapoint())


instrument, *_ = ps.discover()
print(instrument)

with ps.connect(instrument) as manager:
    serial = manager.get_instrument_serial()
    print(serial)

    method = ps.CyclicVoltammetry(
        current_range={
            'max': '1A',  # 1 A range
            'min': '1uA',  # 1 µA range
            'start': '1mA',  # 1 mA range
        },
        equilibration_time=2,  # seconds
        begin_potential=-2,  # V
        vertex1_potential=-2,  # V
        vertex2_potential=3,  # V
        step_potential=0.05,  # V
        scanrate=5,  # V/s
        n_scans=3,  # number of scans
    )

    measurement = manager.measure(method, callback=new_data_callback)

print(measurement)
