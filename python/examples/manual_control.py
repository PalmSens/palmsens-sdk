from pspython import pspyinstruments, pspymethods

manager = pspyinstruments.InstrumentManager()

available_instruments = pspyinstruments.discover_instruments()
print('connecting to ' + available_instruments[0].name)
success = manager.connect(available_instruments[0])

if success != 1:
    print('connection failed')
    exit()

print('connection established')

manager.set_cell(True)
print('cell enabled')

manager.set_potential(1)
print('set potential to 1V')

manager.set_current_range(pspymethods.get_current_range(7))
print('set cell to to 1mA currrent range')

current = manager.read_current()
print('current = ' + str(current) + ' µA')

manager.set_cell(False)
print('cell disabled')

success = manager.disconnect()

if success == 1:
    print('disconnected')
else:
    print('error while disconnecting')
