import pypalmsens as ps


def new_data_callback(new_data):
    for point in new_data:
        print(point)


instruments = ps.discover()
print(instruments)

with ps.connect(instruments[0]) as manager:
    manager.callback = new_data_callback

    serial = manager.get_instrument_serial()
    print(serial)

    method = ps.CyclicVoltammetry(
        current_range=ps.settings.CurrentRange(
            max=ps.settings.CURRENT_RANGE.cr_1_A,  # 1 A range
            min=ps.settings.CURRENT_RANGE.cr_1_uA,  # 1 µA range
            start=ps.settings.CURRENT_RANGE.cr_1_mA,  # 1 mA range
        ),
        equilibration_time=2,  # seconds
        begin_potential=-2,  # V
        vertex1_potential=-2,  # V
        vertex2_potential=3,  # V
        step_potential=0.05,  # V
        scanrate=5,  # V/s
        n_scans=3,  # number of scans
    )

    measurement = manager.measure(method)

print(measurement)
