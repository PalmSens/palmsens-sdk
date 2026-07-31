# Working with Files

pypalmsens and PSTrace store measurements and their corresponding methods in `.pssession` files. Methods can also be stored separately in `.psmethod` files. `pypalmsens` contains all the functions needed to work with session and method files.

## Loading a Method

[pypalmsens.load_method_file][] is used to load method files (with the `.psmethod` extension). This returns a [Technique](./reference/methods/index.md) object containing all technique parameters.

```python
>>> import pypalmsens as ps

>>> method = ps.load_method_file('PSDummyCell_LSV.psmethod')
>>> method
LinearSweepVoltammetry(
    'conditioning_time': 0.0,
    'begin_potential': -5.0,
    'end_potential': 5.0,
    'step_potential': 0.01,
    'scanrate': 1.0,
)
```

## Saving a Method

Save the method using [pypalmsens.save_method_file][]. The `.psmethod` file can be opened with PSTRace.

```python
>>> ps.save_method_file(method, 'lsv.psmethod')
```

## Loading Data

Measurement data can be loaded from `.pssession` files. This contains one or more measurements that include both methods, metadata, and data.

[pypalmsens.load_session_file][] is used to load session files. It returns a list of measurements containing the dataset (raw data in array form) and curves (plot data). The equivalent in PSTrace or PSTrace Express would be the 'Data' and the 'Plot' tabs, respectively.

For example, loading a collection of measurements from a session file and showing the first one:

```python
>>> from pypalmsens import load_session_file

>>> measurement = load_session_file('my_measurement.pssession')[0]
>>> measurement
Measurement(title=Cyclic Voltammetry, timestamp=2026-07-31T10:25:15, device=EmStat4LR)
```

The measurement data and curve classes are defined in the `.curves` attribute:

- Curves: `.curves`
- Raw data: `.dataset`
- EIS data: `.eis_data`

See the [Measurement documentation](../data.md#measurement) for how to work with the data classes.

## Saving Data

Likewise, save your data using [pypalmsens.save_session_file][]. Note that session files can contain multiple measurements, therefore

```python
>>> import pypalmsens as ps

>>> measurement = ps.measure(ps.CyclicVoltammetry())

>>> ps.save_session_file(
...     'my_measurement_copy.pssession',
...     [measurement]
... )
```
