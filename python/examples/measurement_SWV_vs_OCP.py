import pypalmsens as ps


def new_data_callback(new_data):
    for point in new_data:
        print(point)


instruments = ps.discover()
print(instruments)

with ps.connect(instruments[0]) as manager:
    manager.callback = new_data_callback

    method = ps.SquareWaveVoltammetry(
        pretreatment=ps.settings.Pretreatment(
            conditioning_potential=2.0,  # V
            conditioning_time=2,  # seconds
        ),
        versus_ocp=ps.settings.VersusOCP(
            mode=3,  # versus begin and end potential
            max_ocp_time=1,  # seconds
        ),
        begin_potential=-0.5,  # V
        end_potential=0.5,  # V
        step_potential=0.01,  # V
        amplitude=0.08,  # V
        frequency=50,  # Hz
    )

    measurement = manager.measure(method)

print(measurement)
print(f'ocp: {measurement.ocp_value}')
