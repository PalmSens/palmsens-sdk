import pypalmsens as ps

# example with a single cycle with reduced charge/discharge timeouts
N_CYCLES = 1
OCP_TIME = 5
TIMEOUT = 10

# # For a complete 1000-cycle run, you could use he following parameters
# # Note that this could take a while :-)
# N_CYCLES = 1000
# OCP_TIME = 300
# TIMEOUT = 10000


def new_data_callback(new_data):
    for point in new_data:
        print(point)


instruments = ps.discover()
print(instruments)

method = ps.mixed_mode.MixedMode(
    current_range={
        'min': '1mA',  # 1 mA range
        'max': '100mA',  # 100 mA range
        'start': '100mA',  # 100 mA range
    },
    interval_time=1.0,
    cycles=N_CYCLES,
    stages=[
        {
            'stage_type': 'OpenCircuit',
            'run_time': OCP_TIME,  # s
        },
        {
            'stage_type': 'ConstantI',
            'run_time': TIMEOUT,  # s
            'current': 3.0,
            'applied_current_range': '100mA',
            'potential_limits': {'max': 4.2},
        },
        {
            'stage_type': 'ConstantE',
            'run_time': TIMEOUT,  # s
            'potential': 4.2,
            'current_limits': {'min': 50000},  # mA
        },
        {
            'stage_type': 'OpenCircuit',
            'run_time': OCP_TIME,  # s
        },
        {
            'stage_type': 'ConstantI',
            'run_time': TIMEOUT,  # s
            'current': -3.0,
            'applied_current_range': '100mA',
            'potential_limits': {'min': 2.5},
        },
    ],
)


with ps.connect(instruments[0]) as manager:
    serial = manager.get_instrument_serial()
    print(serial)

    measurement = manager.measure(method, callback=new_data_callback)

print(measurement)
