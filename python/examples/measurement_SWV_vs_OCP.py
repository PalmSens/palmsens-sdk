from pspython import pspyinstruments
from pspython.methods import SquareWaveParameters


def new_data_callback(new_data):
    for point in new_data:
        for type, value in point.items():
            print(f'{type} = {value}')


available_instruments = pspyinstruments.discover_instruments()

manager = pspyinstruments.InstrumentManager(new_data_callback=new_data_callback)
connected = manager.connect(available_instruments[0])

if connected != 1:
    print('connection failed')
    exit()

print('connection established')

method = SquareWaveParameters(
    conditioning_potential=2.0,  # V
    conditioning_time=2,  # seconds
    versus_ocp_mode=3,  # versus begin and end potential
    versus_ocp_max_ocp_time=1,  # seconds
    begin_potential=-0.5,  # V
    end_potential=0.5,  # V
    step_potential=0.01,  # V
    amplitude=0.08,  # V
    frequency=10,  # Hz
)

method.frequency = 50

measurement = manager.measure(method)

print(f'ocp: {measurement.curves[0].dotnet_curve.OCPValue}')

success = manager.disconnect()
if success:
    print('disconnected')
else:
    print('error while disconnecting')
