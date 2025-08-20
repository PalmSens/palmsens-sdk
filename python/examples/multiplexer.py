import pypalmsens


def new_data_callback(new_data):
    for point in new_data:
        print(point)


available_instruments = pypalmsens.discover()
print(f'connecting to {available_instruments[0].name}')

with pypalmsens.connect(available_instruments[0]) as manager:
    manager.callback = new_data_callback

    print('connection established')

    n_multiplexer_channels = manager.initialize_multiplexer(2)
    manager.set_mux8r2_settings()

    for channel in range(n_multiplexer_channels):
        manager.set_multiplexer_channel(channel)

    # When measuring alternatingly the selection is restricted to the first n channels
    altnernating_multiplexer_method = pypalmsens.ChronoAmperometry(
        interval_time=0.5,  # seconds
        potential=1.0,  # volts
        run_time=5.0,  # seconds
        multiplexer=pypalmsens.config.Multiplexer(
            mode='alternate',  # 'none', 'consecutive', 'alternate'
            # 8 channels, 1 and 2 are enabled
            channels=[1, 2, 8],
            connect_sense_to_working_electrode=False,
            combine_reference_and_counter_electrodes=False,
            # use the reference and counter electrodes of channel 1 for all channels
            use_channel_1_reference_and_counter_electrodes=False,
            # working electrode of the unselected channels are disconnected/floating
            set_unselected_channel_working_electrode=0,
        ),
    )
    measurement = manager.measure(altnernating_multiplexer_method)

    if measurement is not None:
        print('measurement finished')
    else:
        print('failed to start measurement')

    consecutive_multiplexer_method = pypalmsens.SquareWaveVoltammetry(
        begin_potential=-0.5,  # volts
        end_potential=0.5,  # volts
        step_potential=0.01,  # volts
        amplitude=0.1,  # volts
        frequency=10,  # hertz
        multiplexer=pypalmsens.config.Multiplexer(
            mode='consecutive',  # 'none', 'consecutive', 'alternate'
            # 8 channels, 1, 2, 7 and 8 are enabled
            channels=[1, 2, 7, 8],
            connect_sense_to_working_electrode=False,
            combine_reference_and_counter_electrodes=False,
            # use the reference and counter electrodes of channel 1 for all channels
            use_channel_1_reference_and_counter_electrodes=False,
            # working electrode of the unselected channels are disconnected/floating
            set_unselected_channel_working_electrode=0,
        ),
    )

    measurement = manager.measure(consecutive_multiplexer_method)

    if measurement is not None:
        print('measurement finished')
    else:
        print('failed to start measurement')
