import pypalmsens as ps


def new_data_callback(data):
    print(data.last_datapoint())


instruments = ps.discover()
print(instruments)

with ps.connect(instruments[0]) as manager:
    n_multiplexer_channels = manager.initialize_multiplexer(2)
    manager.set_mux8r2_settings()

    for channel in range(n_multiplexer_channels):
        manager.set_multiplexer_channel(channel)

    # When measuring alternatingly the selection is restricted to the first n channels
    altnernating_multiplexer_method = ps.ChronoAmperometry(
        interval_time=0.5,  # seconds
        potential=1.0,  # volts
        run_time=5.0,  # seconds
        multiplexer={
            'mode': 'alternate',  # 'none', 'consecutive', 'alternate'
            'channels': [1, 2],  # 8 channels, 1 and 2 are enabled
            'connect_sense_to_working_electrode': False,
            'combine_reference_and_counter_electrodes': False,
            'use_channel_1_reference_and_counter_electrodes': False,
            'set_unselected_channel_working_electrode': 0,
        },
    )
    measurement = manager.measure(altnernating_multiplexer_method, callback=new_data_callback)
    print(measurement)

    consecutive_multiplexer_method = ps.SquareWaveVoltammetry(
        begin_potential=-0.5,  # volts
        end_potential=0.5,  # volts
        step_potential=0.01,  # volts
        amplitude=0.1,  # volts
        frequency=10,  # hertz
        multiplexer={
            'mode': 'consecutive',  # 'none', 'consecutive', 'alternate'
            'channels': [1, 2, 7, 8],  # channels 1, 2, 7 and 8 are enabled
            'connect_sense_to_working_electrode': False,
            'combine_reference_and_counter_electrodes': False,
            'use_channel_1_reference_and_counter_electrodes': False,
            'set_unselected_channel_working_electrode': 0,
        },
    )

    measurement = manager.measure(consecutive_multiplexer_method, callback=new_data_callback)
    print(measurement)
