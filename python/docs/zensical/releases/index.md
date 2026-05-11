# Changelog

\\ Latest
## PyPalmSens 1.8.1

> :fontawesome-brands-github: <a href="https://github.com/PalmSens/PalmSens_SDK/releases/tag/python-1.8.1">python-1.8.1</a>
| :fontawesome-brands-python: <a href="https://pypi.org/project/pypalmsens/1.8.1">pypalmsens-1.8.1</a>
| :fontawesome-solid-calendar: 2026-10-04

This is a small bugfix release

### What's Changed

* Add retry function to `pool.connect()` by [@stefsmeets](https://github.com/stefsmeets) in [#334](https://github.com/PalmSens/PalmSens_SDK/pull/334)
* Fix `DataSet.to_dict()` crash for datasets with no current by [@stefsmeets](https://github.com/stefsmeets) in [#338](https://github.com/PalmSens/PalmSens_SDK/pull/338)

## PyPalmSens 1.8.0

> :fontawesome-brands-github: <a href="https://github.com/PalmSens/PalmSens_SDK/releases/tag/python-1.8.0">python-1.8.0</a>
| :fontawesome-brands-python: <a href="https://pypi.org/project/pypalmsens/1.8.0">pypalmsens-1.8.0</a>
| :fontawesome-solid-calendar: 2026-03-26

This is a relatively small release that adds support for the PalmSens Nexus on Windows. This release also updates the PalmSens dotnet libraries to 5.13.011, which brings a bunch of small fixes and improvements.

### Nexus support

If you are using a Nexus, you can now connect to it via TCP/IP:

```python
>>> import pypalmsens as ps

>>> instrument = ps.Instrument.from_ip('192.168.1.123')
>>> instrument
Instrument(name='192.168.1.123', interface='tcp')
>>> with ps.connect(instrument) as manager:
...     print(manager.get_instrument_serial())
NEXUS24C0029
```

For more information, see [the documentation](https://dev.palmsens.com/python/latest/_attachments/measuring/#connecting-via-ethernet).

### What's Changed

* Update PalmSens.Core libraries to 5.13.011 by [@stefsmeets](https://github.com/stefsmeets) in [#281](https://github.com/PalmSens/PalmSens_SDK/pull/281)
* Fix rare crash when deleting Zone.Identifier by [@stefsmeets](https://github.com/stefsmeets) in [#309](https://github.com/PalmSens/PalmSens_SDK/pull/309)
* Add generic structure/unstructure using type adapter by [@stefsmeets](https://github.com/stefsmeets) in [#303](https://github.com/PalmSens/PalmSens_SDK/pull/303)
* Add seperate dependencies for assemblies by [@stefsmeets](https://github.com/stefsmeets) in [#308](https://github.com/PalmSens/PalmSens_SDK/pull/308)
* Add Nexus support by [@stefsmeets](https://github.com/stefsmeets) in [#328](https://github.com/PalmSens/PalmSens_SDK/pull/328)


## PyPalmSens 1.7.1

> :fontawesome-brands-github: <a href="https://github.com/PalmSens/PalmSens_SDK/releases/tag/python-1.7.1">python-1.7.1</a>
| :fontawesome-brands-python: <a href="https://pypi.org/project/pypalmsens/1.7.1">pypalmsens-1.7.1</a>
| :fontawesome-solid-calendar: 2026-02-24

This is a small release that adds a way to connect to a serial port directly, see [the docs for more information](https://dev.palmsens.com/python/latest/_attachments/measuring/#connecting-to-a-serial-port).

```python
import pypalmsens as ps

instrument = ps.Instrument.from_port('COM4')
ps.measure(ps.CyclicVoltammetry(), instrument=instrument)
```

### What's Changed

* Add AllowedMethods literal string by [@stefsmeets](https://github.com/stefsmeets) in [#291](https://github.com/PalmSens/PalmSens_SDK/pull/291)
* Refactor and add method to connect to comport by [@stefsmeets](https://github.com/stefsmeets) in [#298](https://github.com/PalmSens/PalmSens_SDK/pull/298)

## PyPalmSens 1.7.0

> :fontawesome-brands-github: <a href="https://github.com/PalmSens/PalmSens_SDK/releases/tag/python-1.7.0">python-1.7.0</a>
| :fontawesome-brands-python: <a href="https://pypi.org/project/pypalmsens/1.7.0">pypalmsens-1.7.0</a>
| :fontawesome-solid-calendar: 2026-02-20

### Current and potential readings

This release revises how to access current reading and potential reading data (https://github.com/PalmSens/PalmSens_SDK/pull/279).

It exposes the data in the concrete values in the underlying DataArray by adding 2 new derived classes derived from `ps.data.DataArray`:
- [CurrentArray](https://dev.palmsens.com/python/latest/_attachments/reference/data/#pypalmsens.data.CurrentArray)
- [PotentialArray](https://dev.palmsens.com/python/latest/_attachments/reference/data/#pypalmsens.data.PotentialArray)

These arrays have methods to get the current / potential reading data directly, e.g. for current readings:

```python
current = measurement.dataset['Current']
current.current()
current.current_range()
current.current_in_range()
current.timing_status()
current.reading_status()
current.current_readings()
current.to_dict()
```

And for potential readings:

```python
potential = measurement.dataset['Potential']
potential.potential()
potential.potential_range()
potential.potential_in_range()
potential.timing_status()
potential.reading_status()
potential.potential_reading()
potential.to_dict()
```

See [the documentation](https://dev.palmsens.com/python/latest/_attachments/data/#currentarray) for more information.

### Supported methods and current ranges

New methods on `InstrumentManager(Async)` to get the supported methods and current ranges (https://github.com/PalmSens/PalmSens_SDK/pull/279). See [the docs](https://dev.palmsens.com/python/latest/_attachments/reference/instrument/#pypalmsens.InstrumentManager.supported_applied_current_ranges) for more information.

```python
>>> import pypalmsens as ps
>>> manager = ps.connect()
>>> manager.supported_methods()
['lsv', 'dpv', 'swv', ..., 'mm', 'ms', 'pot']

>>> manager.supported_current_ranges()
['100nA', '1uA', '10uA', '100uA', '1mA', '10mA', '100mA']

>>> manager.supported_potential_ranges()
['50mV', '100mV', '200mV', '500mV', '1V']

>>> manager.supported_applied_current_ranges()
['1uA', '100uA', '10mA', '100mA']

>>> manager.supported_bipot_ranges()
[]
```

### Multichannel improvements

If you have a multichannel instrument, this release has 2 important changes.

1. We added support for hardware sync with MethodScript (https://github.com/PalmSens/PalmSens_SDK/pull/283). PyPalmSens will now recognize if you have set `set_channel_sync 1` in your script, and set up the main/follower channels.
2. More callbacks! `InstrumentPool.measure()` / `InstrumentPoolAsync.measure()` now supports passing a list of callbacks, so you can call a different function for every channel (https://github.com/PalmSens/PalmSens_SDK/pull/271). See [this link](https://dev.palmsens.com/python/latest/_attachments/examples/#multichannel_basic) for an example.

### What's Changed

* Add supported methods/ranges to instrument manager by [@stefsmeets](https://github.com/stefsmeets) in [#265](https://github.com/PalmSens/PalmSens_SDK/pull/265)
* Add methods to read/write methodscript file by [@stefsmeets](https://github.com/stefsmeets) in [#266](https://github.com/PalmSens/PalmSens_SDK/pull/266)
* Fix mistake in circuit fitting docs by [@stefsmeets](https://github.com/stefsmeets) in [#275](https://github.com/PalmSens/PalmSens_SDK/pull/275)
* Fix lost datapoints in CalbackData.new_datapoints()` by [@stefsmeets](https://github.com/stefsmeets) in [#278](https://github.com/PalmSens/PalmSens_SDK/pull/278)
* Revise access to CurrentReading/PotentialReading data by [@stefsmeets](https://github.com/stefsmeets) in [#279](https://github.com/PalmSens/PalmSens_SDK/pull/279)
* Refactor ArrayType -> Literal and remove accessors from Dataset by [@stefsmeets](https://github.com/stefsmeets) in [#280](https://github.com/PalmSens/PalmSens_SDK/pull/280)
* Add support for hardware sync with MethodScript by [@stefsmeets](https://github.com/stefsmeets) in [#283](https://github.com/PalmSens/PalmSens_SDK/pull/283)
* Specify callback per channel in instrument pool by [@stefsmeets](https://github.com/stefsmeets) in [#271](https://github.com/PalmSens/PalmSens_SDK/pull/271)


## PyPalmSens 1.6.1

> :fontawesome-brands-github: <a href="https://github.com/PalmSens/PalmSens_SDK/releases/tag/python-1.6.1">python-1.6.1</a>
| :fontawesome-brands-python: <a href="https://pypi.org/project/pypalmsens/1.6.1">pypalmsens-1.6.1</a>
| :fontawesome-solid-calendar: 2026-01-23

This is a patch release that adds support for setting measurement triggers for Mixed Mode measurements.

The API for setting measurement triggers for stages is the same as for methods:

```python
import pypalmsens as ps

method = ps.mixed_mode.MixedMode(
    stages = [{
         'stage_type': 'ConstantE',
         'measurement_triggers': {'d0': True, 'd1': True}
     }]
)
```

### What's Changed

* Support digital triggers in MixedMode by [@stefsmeets](https://github.com/stefsmeets) in [#259](https://github.com/PalmSens/PalmSens_SDK/pull/259)


## PyPalmSens 1.6.0

> :fontawesome-brands-github: <a href="https://github.com/PalmSens/PalmSens_SDK/releases/tag/python-1.6.0">python-1.6.0</a>
| :fontawesome-brands-python: <a href="https://pypi.org/project/pypalmsens/1.6.0">pypalmsens-1.6.0</a>
| :fontawesome-solid-calendar: 2026-01-09

### Measurement callbacks

This release changes how callbacks work. The callback now receives a dataclass, making it easier to integrate into your workflows. If you use callbacks, this may require small changes to your code. See [the documentation](https://dev.palmsens.com/python/latest/_attachments/measuring/#callback), [the API reference](https://dev.palmsens.com/python/latest/_attachments/reference/data/#pypalmsens.data.CallbackData) or one of [the examples](https://dev.palmsens.com/python/latest/_attachments/examples/) for more information.

```python
>>> def callback(data):
...    print({'start': data.start, 'x': data.x[data.start:], 'y': data.y[data.start:]})

>>> manager.measure(method, callback=callback)
{'start': 0, 'x': [0.00, 0.01, 0.02], 'y': [-305.055, -740.935, -750.604]}
```

### Reading idle status

You can pass register a callback to the instrument manager to get updates from the idle status/current/bipot/aux updates. These are also passed as data classes. You can also use the callback to retrieve data during the pretreatment (conditioning and depositing) phases. See [this example](https://dev.palmsens.com/python/latest/_attachments/examples/#status_callback) or checkout the [documentation](https://dev.palmsens.com/python/latest/_attachments/measuring/#idle_status_updates).

```python
>>> import pypalmsens as ps
>>> import asyncio

>>> async def main():
...     async with await ps.connect_async() as manager:
...         manager.register_status_callback(print)
...         await asyncio.sleep(5)
...         manager.unregister_status_callback()

>>> asyncio.run(main())
Idle: {'current': '0.000 * 1uA', 'potential': '0.527 V'}
Idle: {'current': '0.000 * 1uA', 'potential': '0.526 V'}
Idle: {'current': '0.000 * 1uA', 'potential': '0.526 V'}
```

### Fixing Bipot settings

Finally, this release fixes a bug when setting the BiPot, causing the setting not to register. This has been rectified. See [the documentation](https://dev.palmsens.com/python/latest/_attachments/reference/methods/settings/#pypalmsens.settings.BiPot) or #222 for more information.

Note that the syntax for setting the bipot current range has changed, more in line with the rest of the code. Bipot now expects a fixed current range by default, which is the expected setting for almost all devices:

```python
bipot = ps.settings.BiPot(current_range = '1uA')
```

For autoranging bipot (only available on the Nexus), you can use:

```python
bipot = ps.settings.BiPot(
    current_range = {'min': '1uA', 'max': '10mA', 'start': '1mA'},
)
```

### What's Changed

* Return data arrays for callbacks by [@stefsmeets](https://github.com/stefsmeets) in [#219](https://github.com/PalmSens/PalmSens_SDK/pull/219)
* Implement callback for Idle Status events by [@stefsmeets](https://github.com/stefsmeets) in [#223](https://github.com/PalmSens/PalmSens_SDK/pull/223)
* Add timing/reading status and current ranges to DataArray by [@stefsmeets](https://github.com/stefsmeets) in [#226](https://github.com/PalmSens/PalmSens_SDK/pull/226)
* Make bipot configurable for CV and set default to fixed CR by [@stefsmeets](https://github.com/stefsmeets) in [#222](https://github.com/PalmSens/PalmSens_SDK/pull/222)


## PyPalmSens 1.5.0

> :fontawesome-brands-github: <a href="https://github.com/PalmSens/PalmSens_SDK/releases/tag/python-1.5.0">python-1.5.0</a>
| :fontawesome-brands-python: <a href="https://pypi.org/project/pypalmsens/1.5.0">pypalmsens-1.5.0</a>
| :fontawesome-solid-calendar: 2025-12-19

### Validation

This release brings improvements to how the methods are defined. We migrated to [Pydantic](https://docs.pydantic.dev/latest/) to define methods. Pydantic offers automatic runtime validations against the type specification. This makes it more robust for user facing configs.

All values set on the methods are automatically validated, and converted to the correct type where possible. This protects against mistakes and typos.

For example:

```python
>>> cv = ps.CyclicVoltammetry(scanraet=2.0)
scanraet
  Extra inputs are not permitted [type=extra_forbidden, input_value=1.0, input_type=float]
    For further information visit https://errors.pydantic.dev/2.12/v/extra_forbidden
```

For more examples, see [the documentation](https://dev.palmsens.com/python/latest/_attachments/methods/#validation).

### Specifying current / potential ranges

We also changed how current and potential ranges are defined. From this release onwards, current ranges should be specified as strings. This means less typing, and makes the code more readable.

So instead of using:

```python
cv = ps.CyclicVoltammetry(
    current_range=ps.settings.CurrentRange(
        min=ps.settings.CURRENT_RANGE.cr_1_uA,
        max=ps.settings.CURRENT_RANGE.cr_10_mA,
    )
)
```

You can pass the current range directly as a dictionary of strings:

```python
cv = ps.CyclicVoltammetry(current_range={'min': '1uA', 'max': '10mA'})
```

A list of allowed values is available via
- [`ps.settings.AllowedCurrentRanges`](https://dev.palmsens.com/python/latest/_attachments/reference/methods/enums/#pypalmsens.settings.AllowedCurrentRanges)
- [`ps.settings.AllowedPotentialRanges`](https://dev.palmsens.com/python/latest/_attachments/reference/methods/enums/#pypalmsens.settings.AllowedPotentialRanges)

Thanks to how the methods are validated, a warning will be raised if an incorrect value is passed:

```python
>>> ps.CyclicVoltammetry(current_range={'start':'fail'})
ValidationError: 1 validation error for CyclicVoltammetry
current_range.start
  Input should be '100pA', '1nA', '10nA', '100nA', '1uA', '10uA', '100uA', '1mA', '10mA', '100mA', '2uA', '4uA', '8uA', '16uA', '32uA', '63uA', '125uA', '250uA', '500uA', '5mA', '6uA', '13uA', '25uA', '50uA', '200uA' or '1A' [type=literal_error, input_value='fail', input_type=str]
    For further information visit https://errors.pydantic.dev/2.12/v/literal_error
```

### What's Changed

* Forbid extra keys in structure by [@stefsmeets](https://github.com/stefsmeets) in [#201](https://github.com/PalmSens/PalmSens_SDK/pull/201)
* Improve firmware warning by [@stefsmeets](https://github.com/stefsmeets) in [#202](https://github.com/PalmSens/PalmSens_SDK/pull/202)
* Add regression test for aux input by [@stefsmeets](https://github.com/stefsmeets) in [#205](https://github.com/PalmSens/PalmSens_SDK/pull/205)
* Add validation to method classes by [@stefsmeets](https://github.com/stefsmeets) in [#210](https://github.com/PalmSens/PalmSens_SDK/pull/210)
* Use literal strings for config objects by [@stefsmeets](https://github.com/stefsmeets) in [#206](https://github.com/PalmSens/PalmSens_SDK/pull/206)


## PyPalmSens 1.4.0

> :fontawesome-brands-github: <a href="https://github.com/PalmSens/PalmSens_SDK/releases/tag/python-1.4.0">python-1.4.0</a>
| :fontawesome-brands-python: <a href="https://pypi.org/project/pypalmsens/1.4.0">pypalmsens-1.4.0</a>
| :fontawesome-solid-calendar: 2025-12-04

The goal for this release is to remove friction when you are getting started with `PyPalmSens`.

### New measurement command

We added a new top-level function `measure()` (and `measure_async()`) which will connect to the USB device and start a measurement:

```python
>>> import pypalmsens as ps

>>> method = ps.ChronoAmperometry(
...     interval_time=0.01,
...     potential=1.0,
...     run_time=10.0,
... )

>>> ps.measure(method)
Measurement(title=Chronoamperometry, timestamp=17-Nov-25 13:42:16, device=EmStat4HR)
```

### Easier to add a callback

The measure function takes a callback as an argument, so you can use this cool one-liner to impress your friends:

```python
>>> import pypalmsens as ps
>>> ps.measure(ps.CyclicVoltammetry(), callback=print)
```

This change also affects all other `measure()` methods, like `InstrumentManager.measure()` and `InstrumentPool.measure()`.

```python
>>> ...
>>> with ps.connect() as manager:
...     measurement = manager.measure(method, callback=new_data_callback)
```

As a result, passing the callback directly to these class instantiators has been deprecated.

### Scan for for FTDI devices by default

`pypalmsens.discover()` unexpectedly returning an empty list was a common source of confusion for Linux users . The reason is that some instruments (e.g. EmStat Pico or MultiPalmsens4) use an FTDI chip which require additional drivers. We now scan for FTDI devices by default, and instead show a warning message explaining what to do if drivers are missing.

You can turn this warning off with (`ps.discover(ftdi=False)`).

See the driver compatibility list [here](https://dev.palmsens.com/python/latest/_attachments/installation/#compatibility).

### Improved error handling and locking

We also refactored the `InstrumentManager` / `InstrumentManagerAsync` to reduce the amount of duplicated code to not silently swallow errors. The result is better error handling and management of instrument resources. This change won't be directly noticable, but makes the code easier to work with and maintain in the long run.

### Better support for linux

As a result of the above change, compatibility with linux also improved. All techniques should now work as expected. If you run into any issues, [let us know](https://github.com/PalmSens/PalmSens_SDK/issues/60).

### What's Changed

* Add `pypalmsens.measure` method and improve connection handling by [@stefsmeets](https://github.com/stefsmeets) in [#173](https://github.com/PalmSens/PalmSens_SDK/pull/173)
* Scan for ftdi devices by default by [@stefsmeets](https://github.com/stefsmeets) in [#183](https://github.com/PalmSens/PalmSens_SDK/pull/183)
* Add locking to InstrumentManager by [@stefsmeets](https://github.com/stefsmeets) in [#184](https://github.com/PalmSens/PalmSens_SDK/pull/184)
* Update docstrings for methods and method settings by [@stefsmeets](https://github.com/stefsmeets) in [#180](https://github.com/PalmSens/PalmSens_SDK/pull/180)
* Single-source measurement code by [@stefsmeets](https://github.com/stefsmeets) in [#188](https://github.com/PalmSens/PalmSens_SDK/pull/188)
* Generate python docs using mkdocs by [@stefsmeets](https://github.com/stefsmeets) in [#169](https://github.com/PalmSens/PalmSens_SDK/pull/169)
* Fix missing css in Python api reference by [@stefsmeets](https://github.com/stefsmeets) in [#177](https://github.com/PalmSens/PalmSens_SDK/pull/177)
* Fix method pages not showing up by [@stefsmeets](https://github.com/stefsmeets) in [#187](https://github.com/PalmSens/PalmSens_SDK/pull/187)


## PyPalmSens 1.3.3

> :fontawesome-brands-github: <a href="https://github.com/PalmSens/PalmSens_SDK/releases/tag/python-1.3.3">python-1.3.3</a>
| :fontawesome-brands-python: <a href="https://pypi.org/project/pypalmsens/1.3.3">pypalmsens-1.3.3</a>
| :fontawesome-solid-calendar: 2025-11-14

This release updates the PalmSens dotnet libraries to the latest version. This fixes a bug on Windows that caused measurements to hang when 'record_auxiliary_input' was enabled.

This release also adds [type stubs](https://mypy.readthedocs.io/en/stable/stubs.html) for the PalmSens .NET library, which helps with autocomplete and type checking in your IDE.

### What's Changed

* Add type stubs for PalmSens .NET library by [@stefsmeets](https://github.com/stefsmeets) in [#145](https://github.com/PalmSens/PalmSens_SDK/pull/145)
* Update PalmSens dlls to the latest version by [@stefsmeets](https://github.com/stefsmeets) in [#165](https://github.com/PalmSens/PalmSens_SDK/pull/165)
* Update type stubs by [@stefsmeets](https://github.com/stefsmeets) in [#167](https://github.com/PalmSens/PalmSens_SDK/pull/167)


## PyPalmSens 1.3.2

> :fontawesome-brands-github: <a href="https://github.com/PalmSens/PalmSens_SDK/releases/tag/python-1.3.2">python-1.3.2</a>
| :fontawesome-brands-python: <a href="https://pypi.org/project/pypalmsens/1.3.2">pypalmsens-1.3.2</a>
| :fontawesome-solid-calendar: 2025-11-07

This release adds the option to do potential and time scans with EIS.

Single frequency scan:

```python
method = ps.ElectrochemicalImpedanceSpectroscopy(
    scan_type = 'fixed',
    frequency_type = 'scan',
)
```

Multiple frequency scans repeated over a range of DC potential values:

```python
method = ps.ElectrochemicalImpedanceSpectroscopy(
    scan_type = 'potential',
    frequency_type = 'scan',
    begin_potential = -0.5,
    end_potential = 0.5,
    step_potential = 0.1,
)
```

Multiple frequency scans repeated over a time interval:

```python
method = ps.ElectrochemicalImpedanceSpectroscopy(
    scan_type = 'time',
    frequency_type = 'scan',
	run_time = 10.0,
    interval_time = 0.1,
)
```

Single frequency measurement repeated over a time interval:

```python
method = ps.ElectrochemicalImpedanceSpectroscopy(
    scan_type = 'time',
    frequency_type = 'fixed',
)
```

### What's Changed

* Expose Scan and Frequency scans in Python API by [@stefsmeets](https://github.com/stefsmeets) in [#153](https://github.com/PalmSens/PalmSens_SDK/pull/153)


## PyPalmSens 1.3.1

> :fontawesome-brands-github: <a href="https://github.com/PalmSens/PalmSens_SDK/releases/tag/python-1.3.1">python-1.3.1</a>
| :fontawesome-brands-python: <a href="https://pypi.org/project/pypalmsens/1.3.1">pypalmsens-1.3.1</a>
| :fontawesome-solid-calendar: 2025-10-31

This release focuses on improved support for Linux and MacOS. It contains new builds of the underlying PalmSens.Core .NET library for both x86-64 and arm. And the [documentation](https://dev.palmsens.com/python/latest/_attachments/installation.html) was updated with better installation instructions (e.g. for running the code on a Raspberry Pi).

### What's Changed

* Add MPAD technique by [@stefsmeets](https://github.com/stefsmeets) in [#125](https://github.com/PalmSens/PalmSens_SDK/pull/125)
* Fix pypalmsens arm linux builds by [@stefsmeets](https://github.com/stefsmeets) in [#134](https://github.com/PalmSens/PalmSens_SDK/pull/134)
* Refactor tests and add structure/unstructure methods by [@stefsmeets](https://github.com/stefsmeets) in [#141](https://github.com/PalmSens/PalmSens_SDK/pull/141)
* Fix default value for charge limits causing ChronoAmperometry to only collect 1 data point by [@stefsmeets](https://github.com/stefsmeets) in [#144](https://github.com/PalmSens/PalmSens_SDK/pull/144)

### Documentation
* Expand documentation for HW sync example by [@stefsmeets](https://github.com/stefsmeets) in [#137](https://github.com/PalmSens/PalmSens_SDK/pull/137)
* Update installation instructions for linux distros by [@stefsmeets](https://github.com/stefsmeets) in [#138](https://github.com/PalmSens/PalmSens_SDK/pull/138)


## PyPalmSens 1.2.2

> :fontawesome-brands-github: <a href="https://github.com/PalmSens/PalmSens_SDK/releases/tag/python-1.2.2">python-1.2.2</a>
| :fontawesome-brands-python: <a href="https://pypi.org/project/pypalmsens/1.2.2">pypalmsens-1.2.2</a>
| :fontawesome-solid-calendar: 2025-10-13

This release adds the following methods to PyPalmSens:

- Fast Cyclic Voltammetry
- AC Voltammetry
- Normal Pulse Voltammetry
- Fast Amperometry
- Pulsed Amperometric Detection
- Linear Sweep Potentiometry
- Multistep Potentiometry
- Stripping Chronopotentiometry
- Chronocoulometry
- Fast Impedance Spectroscopy
- Fast Galvanostatic Impedance Spectroscopy
- Mixed Mode

There is also a small backwards incompatible API change in some of the settings. Limits, triggers, and IR drop are now easier to define. See #117 for more information:

### Limits

```python
ps.settings.CurrentLimits(min=0, max=1)
ps.settings.PotentialLimits(min=0, max=1)
ps.settings.ChargeLimits(min=0, max=1)
```

### Ir Drop

```python
ps.settings.IrDropCompensation(resistance=0.5)
```

### Triggers

```python
ps.settings.EquilibrationTriggers(d1=True, d2=True)
ps.settings.MeasurementTriggers(d3=True)
ps.settings.DelayTriggers(delay=0.5, d0=True)
```

### What's Changed

* Add MixedMode python interface by [@stefsmeets](https://github.com/stefsmeets) in [#114](https://github.com/PalmSens/PalmSens_SDK/pull/114)
* Add methods by [@stefsmeets](https://github.com/stefsmeets) in [#109](https://github.com/PalmSens/PalmSens_SDK/pull/109)
* Simplify api triggers, limits, and ir drop settings by [@stefsmeets](https://github.com/stefsmeets) in [#117](https://github.com/PalmSens/PalmSens_SDK/pull/117)
* Improve testing for method reading / writing by [@stefsmeets](https://github.com/stefsmeets) in [#118](https://github.com/PalmSens/PalmSens_SDK/pull/118)
* Update mixed mode example with battery cycle by [@stefsmeets](https://github.com/stefsmeets) in [#119](https://github.com/PalmSens/PalmSens_SDK/pull/119)


## PyPalmSens 1.1.1

> :fontawesome-brands-github: <a href="https://github.com/PalmSens/PalmSens_SDK/releases/tag/python-1.1.1">python-1.1.1</a>
| :fontawesome-brands-python: <a href="https://pypi.org/project/pypalmsens/1.1.1">pypalmsens-1.1.1</a>
| :fontawesome-solid-calendar: 2025-10-06

This is a small patch release that adds support for the EMStat4X via the WinUSB protocol.

### What's Changed

* Add support for WinUSB devices (EMStat4X) by [@stefsmeets](https://github.com/stefsmeets) in [#110](https://github.com/PalmSens/PalmSens_SDK/pull/110)


## PyPalmSens 1.1.0

> :fontawesome-brands-github: <a href="https://github.com/PalmSens/PalmSens_SDK/releases/tag/python-1.1.0">python-1.1.0</a>
| :fontawesome-brands-python: <a href="https://pypi.org/project/pypalmsens/1.1.0">pypalmsens-1.1.0</a>
| :fontawesome-solid-calendar: 2025-09-23

The main change in this release is better support for multichannel experiments, making it simpler to manage a group of instruments. For example:

```python
import pypalmsens as ps

instruments = ps.discover()

with ps.InstrumentPool(instruments) as pool:
    measurements = pool.measure(method=method)
```

See the [documentation](https://palmsens.github.io/PalmSens_SDK/python/latest/measuring.html#_multichannel_measurements) for more information.

### What's Changed

* Add InstrumentPool class by [@stefsmeets](https://github.com/stefsmeets) in [#95](https://github.com/PalmSens/PalmSens_SDK/pull/95)
* Update requirements.txt by [@stefsmeets](https://github.com/stefsmeets) in [#96](https://github.com/PalmSens/PalmSens_SDK/pull/96)
* Simplify ELevel dataclass by [@stefsmeets](https://github.com/stefsmeets) in [#97](https://github.com/PalmSens/PalmSens_SDK/pull/97)
* Shorten pypalmsens imports and clean up examples by [@stefsmeets](https://github.com/stefsmeets) in [#104](https://github.com/PalmSens/PalmSens_SDK/pull/104)
* Add workflow for publishing to pypi by [@stefsmeets](https://github.com/stefsmeets) in [#86](https://github.com/PalmSens/PalmSens_SDK/pull/86)


## PyPalmSens 1.0.0

> :fontawesome-brands-github: <a href="https://github.com/PalmSens/PalmSens_SDK/releases/tag/python-1.0.0">python-1.0.0</a>
| :fontawesome-brands-python: <a href="https://pypi.org/project/pypalmsens/1.0.0">pypalmsens-1.0.0</a>
| :fontawesome-solid-calendar: 2025-08-28

PyPalmSens is a Python library for automating electrochemistry experiments with your PalmSens instruments. It provides an intuitive Python API, making it straightforward to integrate into your Python workflows.

With PyPalmSens, you can:

- Connect to one or more instruments/channels
- Automate electrochemistry measurements
- Access and process measured data
- Analyze and manipulate data
- Perform peak detection
- Do Equivalent Circuit Fitting on impedance data
- Take manual control the cell
- Read and write method and data files
