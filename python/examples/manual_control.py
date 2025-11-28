import pypalmsens as ps

instruments = ps.discover()
print(instruments)

with ps.connect(instruments[0]) as manager:
    manager.set_cell(True)
    print('cell enabled')

    manager.set_potential(1)
    print('set potential to 1V')

    manager.set_current_range(ps.settings.CURRENT_RANGE.cr_1_mA)
    print('set cell to to 1mA currrent range')

    current = manager.read_current()
    print(f'current = {current} µA')

    manager.set_cell(False)
    print('cell disabled')
