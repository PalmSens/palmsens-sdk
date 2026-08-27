import pypalmsens as ps


def new_data_callback(data):
    print(data.last_datapoint())


instrument, *_ = ps.discover()
print(instrument)

with ps.connect(instrument) as manager:
    n_multiplexer_channels = manager.initialize_multiplexer('mux8r2')
    manager.configure_mux8r2()

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
            'connect_se_we': False,
            'combine_re_ce': False,
            'common_re_ce': False,
            'unused_we': 'float',
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
            'connect_se_we': False,
            'combine_re_ce': False,
            'common_re_ce': False,
            'unused_we': 'float',
        },
    )

    measurement = manager.measure(consecutive_multiplexer_method, callback=new_data_callback)
    print(measurement)
