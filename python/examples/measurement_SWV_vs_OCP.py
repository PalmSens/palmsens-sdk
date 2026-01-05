import pypalmsens as ps


def new_data_callback(data):
    print(data.last_datapoint())


instruments = ps.discover()
print(instruments)

with ps.connect(instruments[0]) as manager:
    method = ps.SquareWaveVoltammetry(
        pretreatment={
            'conditioning_potential': 2.0,  # V
            'conditioning_time': 2,  # seconds
        },
        versus_ocp={
            'mode': 3,  # versus begin and end potential
            'max_ocp_time': 1,  # seconds
        },
        begin_potential=-0.5,  # V
        end_potential=0.5,  # V
        step_potential=0.01,  # V
        amplitude=0.08,  # V
        frequency=50,  # Hz
    )

    measurement = manager.measure(method, callback=new_data_callback)

print(measurement)
print(f'ocp: {measurement.ocp_value}')
