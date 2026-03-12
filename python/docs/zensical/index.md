<style>
  .md-typeset h1,
  .md-content__button {
    display: none;
  }
</style>

# PyPalmSens Documentation

<br/>

![Image title](./assets/banner.svg#only-light){ width="80%" }
![Image title](./assets/banner_dark.svg#only-dark){ width="80%" }

<br/>

PyPalmSens is a Python library for automating electrochemistry experiments with your PalmSens instruments.
It provides an intuitive Python API, making it straightforward to integrate into your Python workflows.

With PyPalmSens, you can:

- Connect to [one](measuring.md#connecting-to-a-device) or [more](measuring.md#multichannel-measurements) instruments/channels
- Automate [electrochemistry measurements](methods.md)
- [Access, process, and analyze](data.md) measured data
- Perform [peak detection][pypalmsens.data.Curve.find_peaks]
- Do [Equivalent Circuit Fitting](circuit_fitting.md) on impedance data
- Take [manual control](examples.md#manual-control) of the cell
- [Read and write method and data files](files.md)

To install:

```bash
pip install pypalmsens
```

PyPalmSens is built on top of the [PalmSens .NET libraries](https://dev.palmsens/dotnet),
and therefore requires the .NET runtime to be installed. See the [installation instructions](installation.md) for your platform for more information.

## Getting started

The following example shows how to set up and measure a simple chronoamperometry experiment:

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

!!! TIP

    Shorten the imported name from `pypalmsens` to `ps`. This widely adopted convention helps with better readability of code.

The following example shows how to discover devices and manually read out the current.

```python
>>> import pypalmsens as ps

>>> instruments = ps.discover()
>>> emstat4 = [inst for inst in instruments if inst.name.startswith('EmStat4')][0]

>>> with ps.connect(instrument=emstat4) as manager: # (1)!
...     manager.set_cell(True)
...     manager.set_potential(1)
...     manager.set_current_range('1mA')
...
...     current = manager.read_current()
...     print(f'{current=} µA')
...
...     manager.set_cell(False)
current=92.8065 µA
```

1. The context manager opens and closes the connection

Analyze a previous measurement with [pandas](https://pandas.pydata.org/):

```python
>>> import pandas as pd
>>> import pypalmsens as ps

>>> measurements = ps.load_session_file('Demo CV DPV EIS IS-C electrode.pssession')
>>> dpv = measurements[0]
>>> print(f'{dpv.title} ({dpv.timestamp})')
Impedance Spectroscopy [2] (7/12/2017 2:48:42 PM)

>>> dpv.dataset.to_dataframe() #(1)!
     Time Potential   Current    CR ReadingStatus
0     0.0 -0.399962  0.352146  10uA            OK
1     0.2 -0.394962  0.351192  10uA            OK
2     0.4 -0.389884    0.3469  10uA            OK
..    ...       ...       ...   ...           ...
216  43.2  0.687698  0.198544  10uA            OK
217  43.4  0.692698   0.19908  10uA            OK
218  43.6  0.697776  0.199557  10uA            OK
```

1. Extract all arrays from the dataset into a [pandas dataframe](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html).
