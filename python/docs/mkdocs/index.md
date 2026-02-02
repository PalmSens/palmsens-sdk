# PyPalmSens Documentation

<br/>

![Image title](https://raw.githubusercontent.com/PalmSens/PalmSens_SDK/refs/heads/main/python/docs/modules/ROOT/images/banner.svg#only-light){ width="80%" }
![Image title](https://raw.githubusercontent.com/PalmSens/PalmSens_SDK/refs/heads/main/python/docs/modules/ROOT/images/banner_dark.svg#only-dark){ width="80%" }

<br/>

PyPalmSens is a Python library for automating electrochemistry experiments with your PalmSens instruments.
It provides an intuitive Python API, making it straightforward to integrate into your Python workflows.

With PyPalmSens, you can:

- Connect to one or more instruments/channels
- Automate electrochemistry measurements
- Access and process measured data
- Analyze and manipulate data
- Perform peak detection
- Do Equivalent Circuit Fitting on impedance data
- Take manual control of the cell
- Read and write method and data files

To install:

```bash
pip install pypalmsens
```

PyPalmSens is built on top of the [PalmSens .NET libraries](https://sdk.palmsens/dotnet),
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

>>> frames = []
>>> frame_names = []

>>> for measurement in measurements:
...     frames.append(measurement.dataset.to_dataframe()) # (1)!
...     frame_names.append(measurement.title)

>>> df = pd.concat(frames, keys=frame_names)
>>> print(df)
```

1. Extract all arrays from the dataset into a [pandas dataframe](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html).
