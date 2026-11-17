import pypalmsens as ps
from pypalmsens._capabilities import *
from pypalmsens._converters import cr_string_to_enum

capabilities = get_capabilities('emstat4hr')

method = ps.ChronoAmperometry()

method.current_range.max = '125uA'
method.current_range.start = '63uA'
method.current_range.min = '4uA'

psmethod = method._to_psmethod()

print(psmethod.Ranging.MinimumCurrentRange)
print(psmethod.Ranging.MaximumCurrentRange)
print(psmethod.Ranging.StartCurrentRange)

errors = psmethod.Validate(capabilities.capabilities)

for error in errors:
    print(error)

for s in [
    '100pA',
    '1nA',
    '10nA',
    '100nA',
    '1uA',
    '10uA',
    '100uA',
    '1mA',
    '10mA',
    '100mA',
    '2uA',
    '4uA',
    '8uA',
    '16uA',
    '32uA',
    '63uA',
    '125uA',
    '250uA',
    '500uA',
    '5mA',
    '6uA',
    '13uA',
    '25uA',
    '50uA',
    '200uA',
    '1A',
]:
    cr = cr_string_to_enum(s)

    psmethod.Ranging.MinimumCurrentRange = cr
    psmethod.Ranging.MaximumCurrentRange = cr
    psmethod.Ranging.StartCurrentRange = cr

    a = str(psmethod.Ranging.MinimumCurrentRange)
    b = str(psmethod.Ranging.MaximumCurrentRange)
    c = str(psmethod.Ranging.StartCurrentRange)

    print(f'in: {s:10} -> {cr!s:6} min={a:6} max={b:6} start={c:6}')
