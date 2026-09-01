# GPIO

This class provides high-level access to the instrument's digital pins.
The API is defined in [pypalmsens.GPIO][], and [pypalmsens.GPIOAsync][] for asynchronous workflows.

The intended usage of these classes is via the [InstrumentManager.gpio][pypalmsens.InstrumentManager.gpio] and [InstrumentManager.gpio][pypalmsens.InstrumentManager.gpio] attributes.

Example:

```pycon
>>> import pypalmsens as ps

>>> with ps.connect() as manager:
...     print("Outputs:", manager.gpio.writable_pins)
...     print("Inputs :", manager.gpio.readable_pins)
...     manager.gpio.write_many([0,1,2], level='high')
Outputs: [0, 1, 2, 3]
Inputs : [0]

```

For more information how to use these classes, see [the documentation here](../gpio.md).

**Classes:**

- [`pypalmsens.GPIO`][pypalmsens.GPIO]
- [`pypalmsens.GPIOAsync`][pypalmsens.GPIOAsync]

::: pypalmsens.GPIO
::: pypalmsens.GPIOAsync
