from pspython import pspyinstruments
from pspython.methods import CyclicVoltammetryParameters, CURRENT_RANGE


def new_data_callback(new_data):
    for point in new_data:
        print(point)


manager = pspyinstruments.InstrumentManager(new_data_callback=new_data_callback)

available_instruments = pspyinstruments.discover_instruments()
print('connecting to ' + available_instruments[0].name)
success = manager.connect(available_instruments[0])

if success != 1:
    print('connection failed')
    exit()

print('connection established')

serial = manager.get_instrument_serial()
print(serial)

method = CyclicVoltammetryParameters(
    current_range_max=CURRENT_RANGE.cr_1_A,  # 1A range
    current_range_min=CURRENT_RANGE.cr_1_uA,  # 1µA range
    current_range_start=CURRENT_RANGE.cr_1_mA,  # 1mA range
    equilibration_time=2,  # seconds
    begin_potential=-2,  # V
    vertex1_potential=-2,  # V
    vertex2_potential=3,  # V
    step_potential=0.05,  # V
    scanrate=5,  # V/s
    n_scans=3,  # number of scans
)

measurement = manager.measure(method)

if measurement is not None:
    print('measurement finished')
else:
    print('failed to start measurement')

success = manager.disconnect()

if success == 1:
    print('disconnected')
else:
    print('error while disconnecting')
