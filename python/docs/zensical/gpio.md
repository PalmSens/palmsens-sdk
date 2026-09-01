# Digital I/O (GPIO)

The [pypalmsens.GPIO][] and [pypalmsens.GPIOAsync][] classes provide access to the instrument’s digital input and output pins. Use it to read logic levels, drive outputs, or toggle control lines. The gpio api is exposed via the [InstrumentManager.gpio][pypalmsens.InstrumentManager.gpio] and [InstrumentManagerAsync.gpio][pypalmsens.InstrumentManagerAsync.gpio] attributes.

- **Direction auto-configuration:** For MethodSCRIPT devices, the library automatically configures pin direction when you call [read][pypalmsens.GPIO.read] (input) or [write][pypalmsens.GPIO.write] / [toggle][pypalmsens.GPIO.toggle] (output) operations. If you need explicit low-level control, use [MethodSCRIPT](https://dev.palmsens.com/methodscript/latest/methodscript/methodscript_main.html), either directly or via [pypalmsens.CommProtocol][].

- **Atomicity:** [write_many][pypalmsens.GPIO.write_many] and [toggle_many][pypalmsens.GPIO.toggle_many] are sent as a single instruction. How the chip process the instruction may differ from device to device. If your use case requires strict timing (e.g., simultaneous pin changes), prefer the batch methods over multiple single-pin calls.

## Pin numbering

The integers you pass to read / write are the internal pin numbers exposed by the firmware API, not necessarily the labels on the hardware (e.g., d0, d3). The mapping is consistent for a given instrument model, so code that works on one unit will work on an identical unit. Consult the instrument manual for the physical mapping.

Pin numbers and the mix of readable vs. writable pins depend on the specific instrument model. Consult [writable_pins][pypalmsens.GPIO.writable_pins] and [readable_pins][pypalmsens.GPIO.readable_pins] at runtime if you work with multiple device types.

## Available pins

Before reading or writing, check which pins are configured for input and output on the connected instrument, for example a PalmSens 4:

```pycon
>>> import pypalmsens as ps

>>> with ps.connect() as manager:
...     print("Outputs:", manager.gpio.writable_pins)
...     print("Inputs :", manager.gpio.readable_pins)
Outputs: [0, 1, 2, 3]
Inputs : [0]

```

## Writing digital outputs

Set a single pin high or low:

```pycon
>>> with ps.connect() as manager:
...     manager.gpio.write(1, level='high')
...     manager.gpio.write(2, level='low')

```

Set multiple pins at once:

```pycon
>>> with ps.connect() as manager:
...    # Set pins 1, 2 and 3 high in one call
...    manager.gpio.write_many([1, 2, 3], level='high')

```

## Reading digital inputs

Read the current level of a single pin or several pins:

```pycon
>>> with ps.connect() as manager:
...    level = manager.gpio.read(0)
...    print(f"Pin 0 is {level!r}")
...
...    levels = manager.gpio.read_many([0, 1])
...    print(levels)
Pin 0 is 'low'
['low', 'high']
```

## Toggling outputs

Invert the current state of an output pin without knowing its present level:

```pycon
>>> with ps.connect() as manager:
...     manager.gpio.toggle(1)               # single pin
...     manager.gpio.toggle_many([1, 2, 3])  # multiple pins

```

## Complete example

```python
import pypalmsens as ps

instrument, *_ = ps.discover()

with ps.InstrumentManager(instrument) as manager:
    # Initialise control pins
    manager.gpio.write_many([1, 2], level='low')

    # Enable external circuitry on pin 1
    manager.gpio.write(1, level='high')

    # Check status on pin 0
    if manager.gpio.read(0) == 'high':
        manager.gpio.toggle(2)

    # Bulk reset all pins
    output_pins = manager.gpio.writable_pins
    manager.gpio.write_many(output_pins, level='low')

```


## Async usage

For async workflows, use `AsyncInstrumentManager.gpio`. All these methods are `await`-able and behave identically to their synchronous counterparts.

```python
import asyncio
import pypalmsens as ps

async def main():
    instrument, *_ = await ps.discover_async()

    async with ps.InstrumentManagerAsync(instrument) as manager:
        await manager.gpio.write_async(1, level='high')
        state = await manager.gpio.read_async(0)
        print(f"Pin 0 is {state}")

asyncio.run(main())
```
