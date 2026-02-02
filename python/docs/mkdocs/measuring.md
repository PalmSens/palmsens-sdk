# Connecting and Measuring

The following chapter details how to connect to a device, read data from the device, manually controlling the potential, run measurements on the device and finally how to properly close a connection to a device.

The [pypalmsens](reference/index.md) top-level module contains all the relevant functions and classes for discovering and controlling instruments.
The [pypalmsens.InstrumentManager][] and [pypalmsens.InstrumentManagerAsync][]) class are wrappers around the PalmSens .NET libraries to connect to and control your instrument from Python.

!!! CAUTION "Mains Frequency"

    To eliminate noise induced by other electrical appliances it is highly recommended to set your regional mains frequency (50/60 Hz) in the general settings when performing a measurement `ps.settings.General.power_frequency`.

## Getting started

The simplest way to run an expirement is to use [pypalmsens.measure][].
This function connects to any plugged-in USB device it can find and starts the given measurement.

```python
>>> import pypalmsens as ps

>>> method = ps.ChronoAmperometry(
...     interval_time=0.01,
...     potential=1.0,
...     run_time=10.0,
... )

>>> ps.measure(method) # (1)!
Measurement(title=Chronoamperometry, timestamp=17-Nov-25 13:42:16, device=EmStat4HR)
```

1. `measure` discovers any plugged-in device to start the measurement. An error is raised when more than 1 instruments are connected.

You can optionally pass the instrument to measure on if you have multiple connected.

```python
>>> instruments = ps.discover()
>>> first_instrument = instruments[0]

>>> ps.measure(method, instrument=first_instrument)
Measurement(title=Chronoamperometry, timestamp=17-Nov-25 14:12:02, device=EmStat4HR)
```

## Connecting to a device

The recommended way to connect to a device for most workflows is to use the `ps.connect()` [context manager](https://docs.python.org/3/library/stdtypes.html#typecontextmanager).
The contextmanager manages the connection, and closes the connection to the device if it is no longer needed.
[pypalmsens.connect][] returns an instance of [pypalmsens.InstrumentManager][], which can be used to control the instrument and start a measurement:

```python
>>> import pypalmsens as ps

>>> with ps.connect() as manager:
...     measurement = manager.measure(method)
```

By default, [pypalmsens.connect][] connects to any plugged-in USB instrument it discovers.
It gives an error when multiple instruments are discovered.
With more instruments connected, you can use [pypalmsens.discover][] to find all devices and manage them yourself.
For example, this is how to get a list of all available devices, and how to connect to the first one.

```python
>>> available_instruments = ps.discover()
>>> available_instruments
[Instrument(name='EmStat4 HR [1]', interface='usbcdc')]

>>> first_instrument = available_instruments[0]

>>> with ps.connect(first_instrument) as manager:
...    measurement = manager.measure(method)
```

Finally, you can set up the [pypalmsens.InstrumentManager][] yourself.

```python
>>> available_instruments = ps.discover()
>>> manager = ps.InstrumentManager()
>>> manager.connect(available_instruments[0])
```

 [pypalmsens.InstrumentManager.disconnect][] disconnects from the device freeing it up for other things to connect to it.

```python
>>> manager.disconnect()
```

Currently PyPalmSens supports discovering instruments connected via FTDI, serial (usbcdc/com), and Bluetooth (classic/low energy). By default scanning with Bluetooth is disabled.

You can enable scanning with Bluetooth by setting:

```python
>>> ps.discover(bluetooth=True)
```

## Manually controlling the device

Depending on your device’s capabilities it can be used to set a potential/current and to switch current ranges.
The potential can be set manually in potentiostatic mode and the current can be set in galvanostatic mode.
The following example show how to manually set a potential, for more examples refer to the [`ManualControlExample`](examples.md#manual-control) and [`ManualControlExampleAsync`](examples.md#manual-control-async)
scripts included with the SDK.

```python
>>> manager.set_potential(1)
```

## Idle status updates

When idle or during pretreatment, the instrument measures and publishes the current, voltage, device state, etc when a datapoint is measured.
You can register a callback to subscribe to these events.
The event is fired every second and every 0.25 seconds during pretreatment.

[NOTE]
.Async
====
The callback requires an active event loop and therefore only works in Async mode.
====

For example, using print as the callback prints the status to the terminal:

```python
>>> manager.register_status_callback(print)
>>> await asyncio.sleep(3)  &lt;1>
Idle: {'current': '0.000 * 1uA', 'potential': '0.527 V'}
Idle: {'current': '0.000 * 1uA', 'potential': '0.526 V'}
Idle: {'current': '0.000 * 1uA', 'potential': '0.526 V'}
>>> manager.unregister_status_callback()
```

(1): Sleep is used here to simulate another task

The callback returns a [pypalmsens.data.Status][] object, which can be used to customize the behaviour.

For example, to print data during the pretreatment phases:

```python
>>> def callback(status):
...     if status.device_state == 'Pretreatment':
...         print(f'{status.pretreatment_phase}: potential={status.potential:.3f} V, current={status.current:.3f} μA')

>>> manager.register_status_callback(callback)
>>> await manager.measure(ps.ChronoAmperometry(
...     pretreatment={'conditioning_time':2, 'conditioning_potential': 0.5},
... ))
Conditioning: potential=0.500 V, current=0.100 μA
Conditioning: potential=0.500 V, current=0.101 μA
...
Conditioning: potential=0.500 V, current=0.098 μA
>>> manager.unregister_status_callback()
```

See [pypalmsens.data.Status][] or the provided [Status callback](examples.md#status-callback) example for more information.

## Measuring

Starting a measurement is done by sending method parameters to a PalmSens/Nexus/EmStat/Sensit device.
The [pypalmsens.InstrumentManager.measure][] method returns a `Measurement` object and also supports keeping a reference to the underlying .NET object.
For more information please refer to [PalmSens.Net.Core](https://sdk.palmsens.com/start/core.html).

The following example runs a chronoamperometry measurement on an instrument.

```python
>>> method = ps.ChronoAmperometry(
...     interval_time=0.01,
...     e=1.0,
...     run_time=10.0
... )
>>> measurement = manager.measure(method)
```

### Callback

You process measurement results in real-time by specifying a callback function as argument.
In the example below we use `print` to simply log the data to the console:

```python
>>> manager.measure(method, callback=print)
{'index': 0, 'x': 0.0,  'y': -305.055}
{'index': 1, 'x': 0.01, 'y': -731.741}
{'index': 2, 'x': 0.02, 'y': -751.552}
...
```

The callback is passed a collection of points that have been added since the last time it was called.
Thus, `new_data` below is a batched list of points, so we can expand the `print` example to print each point on a new line:

```python
>>> def callback(data):
...    print({'start': data.start, 'x': data.x[data.start:], 'y': data.y[data.start:]})
...
>>> manager.measure(method, callback=callback)
{'start': 0, 'x': [0.00, 0.01, 0.02], 'y': [-305.055, -740.935, -750.604]}
```

Alternatively, you can use `data.last_datapoint()` or `data.new_datapoints()` to get a dictionary with new data since the last callback.

Since `data.x` and `data.y` are of the [pypalmsens.data.DataArray] type, you can access these directly for your own code.
`data.start` is an index pointing at the first at the first element of the array, and `data.index` at the last.
The data arrays contain the complete data for the measurement. See [pypalmsens.data.CallbackData][] for more information.

The type of data returned depends on the measurement.
For non-impedemetric technique, this will be time (s), potential (V), or current (μA) for x, and current (μA) or potential (V) for y.
Query the data array directly (`DataArray.unit`, `DataArray.quantity`) for these data.

For impedemetric techniques, the callback returns the EIS [Dataset](data.md#dataset). See [pypalmsens.data.CallbackDataEIS][] for more information.

```python
>>> def callback(data):
...    print(data.last_datapoint())

>>> eismethod = ps.ElectrochemicalImpedanceSpectroscopy()
>>> manager.measure(method, callback=callback)
{'index': 0, 'Idc': -5.683012, 'potential': 0.0, 'time': 0.0024332, 'Frequency': 10000.0, 'ZRe': 4846.639, 'ZIm': -31990.538, 'Z': 32355.593, 'Phase': -81.385, 'Iac': 0.015, 'miDC': -5.683, 'mEdc': 0.598, 'Eac': 0.000, 'Y': 3.090e-05, 'YRe': 4.629e-06, 'YIm': -3.055e-05, 'Capacitance': -4.975e-10, "Capacitance'": -4.863e-10, "Capacitance''": 7.368e-11}
```

## MethodSCRIPT™

The MethodSCRIPT™ scripting language is designed to integrate PalmSens OEM potentiostat (modules) effortlessly in your hardware setup or product.

MethodSCRIPT™ allows you to program a human-readable script directly into the potentiostat module by means of a serial (TTL) connection.
The simple script language allows for running all supported electrochemical techniques and makes it easy to combine different measurements and other tasks.

More script features include:

* Use of variables
* (Nested) loops
* Logging results to an SD card
* Digital I/O for example for waiting for an external trigger
* Reading auxiliary values like pH or temperature
* Going to sleep or hibernate mode

See the [MethodSCRIPT™ documentation](https://www.palmsens.com/methodscript) for more information.

### Sandbox Measurements

PSTrace includes an option to make use MethodSCRIPT™ Sandbox to write and run scripts.
This is a great place to test MethodSCRIPT™ measurements to see what the result would be.
That script can then be used in the MethodScriptSandbox technique in the SDK as demonstrated below.

![Graphical editor for MethodSCRIPT™](assets/method_script_editor.png){ width="80%" }

## Multichannel measurements

PyPalmSens supports multichannel experiments via [pypalmsens.InstrumentPool][] and [pypalmsens.InstrumentPoolAsync][].

This class manages a pool of instruments ([pypalmsens.InstrumentManagerAsync][]), so that one method can be executed on all instruments at the same time.

A basic multichannel measurement can be set up by passing a list of instruments, either from a multichannel device, or otherwise connected:

```python
>>> instruments = ps.discover()
>>> instruments
[Instrument(name='EmStat4 HR [1]', interface='usbcdc'), Instrument(name='EmStat4 HR [1]', interface='usbcdc')]

>>> method = ps.CyclicVoltammetry()

>>> with ps.InstrumentPool(instruments) as pool: # (1)!
...    measurements = pool.measure(method)

>>> measurements
[Measurment(...), Measurement(...)]
```

1. `InstrumentPool` is a context manager, so all instruments are disconnected after use.

The above example uses blocking calls for the instrument pool.
While this works well for many straightforward use-cases, the backend for multichannel measurements is asynchronous by necessity.
The rest of the documentation here focuses on the async version of the instrument pool, [pypalmsens.InstrumentPool][].
This is more powerful and more flexible for more demanding use cases.
Note that most of the functionality and method names are shared between [pypalmsens.InstrumentPool][] and [pypalmsens.InstrumentPoolAsync][].

```python
>>> instruments = await ps.discover_async()

>>> method = ps.CyclicVoltammetry()

>>> async with ps.InstrumentPoolAsync(instruments) as pool:
...    results = await pool.measure(method)

>>> measurements
[Measurment(...), Measurement(...)]
```

The pool takes a [Callback](#callback) in its `measure()` method, just like a regular [pypalmsens.InstrumentManager][].

```python
>>> async with ps.InstrumentPoolAsync(instruments) as pool:
...    results = await pool.measure(method, callback=callback)
```

You can add ([pypalmsens.InstrumentPool.add][]) and remove ([pypalmsens.InstrumentPool.remove][]) managers from the pool:

```python
>>> serial_numbers = ['ES4HR20B0008', ...]

>>> async with ps.InstrumentPoolAsync(instruments) as pool:
...     for manager in pool:
...        if await manager.get_instrument_serial() not in [serial_numbers]:
...             await pool.remove(manager)
```

You can also manage the pool yourself by passing the _instrument managers_ directly:

```python
>>> instruments = await ps.discover_async()

>>> managers = [
...     ps.InstrumentManagerAsync(instrument) for instrument in instruments
... ]

>>> async with ps.InstrumentPoolAsync(managers) as pool:
...     pass  # pool operations
```

To define your own measurement functions, you can use the [pypalmsens.InstrumentPoolAsync][] method.
Pass a function that must take [instrument/index.html#pypalmsens.InstrumentManagerAsync) as the first argument.
Any other keyword arguments will be passed on.

For example to run two methods in sequence:

```python
>>> async def my_custom_function(manager, *, method1, method2):
...     measurement1 = await manager.measure(method1)
...     measurement2 = await manager.measure(method2)
...     return measurement1, measurement2

>>> async with ps.InstrumentPoolAsync(instruments) as pool:
...     results = await pool.submit(my_task, method=method)
```

See [CSV writer](examples.md#multichannel_csv_writer) and [Custom loop](examples.md#multichannel_custom_loop) examples for a practical example of setting a custom function.

To use hardware synchronization, use the same `measure` method. See also the [Hardware sync](examples.md#multichannel_hw_sync) example.
Make sure the method has the `general.use_hardware_sync` flag set.

In addition, the pool must contain:
- channels from a single multi-channel instrument only
- the first channel of the multi-channel instrument
- at least two channels

All instruments are prepared and put in a waiting state.
The measurements are started via a hardware sync trigger on channel 1.

```python
>>> method.general.use_hardware_sync = True

>>> async with ps.InstrumentPoolAsync(instruments) as pool:
...      results = await pool.measure_hw_sync(method)
```
