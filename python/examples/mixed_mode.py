import pypalmsens as ps


def new_data_callback(new_data):
    for point in new_data:
        print(point)


instruments = ps.discover()
print(instruments)

method = ps.mixed_mode.MixedMode(
    current_range=ps.settings.CurrentRange(
        max=ps.settings.CURRENT_RANGE.cr_1_A,  # 1 A range
        min=ps.settings.CURRENT_RANGE.cr_1_uA,  # 1 µA range
        start=ps.settings.CURRENT_RANGE.cr_1_mA,  # 1 mA range
    ),
    cycles=2,
    stages=[
        ps.mixed_mode.ConstantE(
            run_time=1.0,
            potential=0.5,
        ),
        ps.mixed_mode.ConstantI(
            run_time=1.0,
            current=1.0,
            applied_current_range=ps.settings.CURRENT_RANGE.cr_100_nA,
        ),
        ps.mixed_mode.SweepE(
            begin_potential=-0.5,
            end_potential=0.5,
            step_potential=0.1,
            scanrate=2.0,
        ),
        ps.mixed_mode.OpenCircuit(
            run_time=5.0,
        ),
        ps.mixed_mode.Impedance(
            frequency=50000,
            ac_potential=0.01,
            dc_potential=0.0,
            run_time=1.0,
        ),
    ],
)


with ps.connect(instruments[0]) as manager:
    manager.callback = new_data_callback

    serial = manager.get_instrument_serial()
    print(serial)

    measurement = manager.measure(method)

print(measurement)
