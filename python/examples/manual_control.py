import pypalmsens
from pypalmsens.methods import CURRENT_RANGE

available_instruments = pypalmsens.discover()
print('connecting to ' + available_instruments[0].name)

with pypalmsens.connect(available_instruments[0]) as manager:
    print('connection established')

    manager.set_cell(True)
    print('cell enabled')

    manager.set_potential(1)
    print('set potential to 1V')

    manager.set_current_range(CURRENT_RANGE.cr_1_mA)
    print('set cell to to 1mA currrent range')

    current = manager.read_current()
    print('current = ' + str(current) + ' µA')

    manager.set_cell(False)
    print('cell disabled')
