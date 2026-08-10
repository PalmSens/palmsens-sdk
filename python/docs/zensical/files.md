# Working with Files

pypalmsens and PSTrace store measurements and their corresponding methods in `.pssession` files. Methods can also be stored separately in `.psmethod` files. `pypalmsens` contains all the functions needed to work with session and method files.

## Loading a Method

[pypalmsens.load_method_file][] is used to load method files (with the `.psmethod` extension). This returns a [Technique](./reference/methods/index.md) object containing all technique parameters.

```pycon
>>> import pypalmsens as ps

>>> method = ps.load_method_file('examples/PSDummyCell_LSV.psmethod')
>>> method
LinearSweepVoltammetry(..., current_range=CurrentRange(max='1mA', min='100nA', start='100uA'), equilibration_time=2.0, begin_potential=-5.0, end_potential=5.0, step_potential=0.01, scanrate=1.0, ...)

```

## Saving a Method

Save the method using [pypalmsens.save_method_file][]. The `.psmethod` file can be opened with PSTRace.

```pycon
>>> ps.save_method_file('lsv.psmethod', method)

```

## Loading Data

Measurement data can be loaded from `.pssession` files. This contains one or more measurements that include both methods, metadata, and data.

[pypalmsens.load_session_file][] is used to load session files. It returns a list of measurements containing the dataset (raw data in array form) and curves (plot data). The equivalent in PSTrace or PSTrace Express would be the 'Data' and the 'Plot' tabs, respectively.

For example, loading a collection of measurements from a session file:

```pycon
>>> measurements = ps.load_session_file('examples/Demo CV DPV EIS IS-C electrode.pssession')
>>> measurements
[Measurement(title=Differential Pulse Voltammetry, timestamp=2017-07-12T14:28:58, device=PalmSens4),
 Measurement(title=Cyclic Voltammetry [1], timestamp=2017-07-12T14:33:10, device=PalmSens4),
 Measurement(title=Impedance Spectroscopy [2], timestamp=2017-07-12T14:48:42, device=PalmSens4)]

```

If you know that your session file only contains a single measurement, you can use the [pypalmsens.load_measurement][] function:

```pycon
>>> measurement = ps.load_measurement('examples/CV example.pssession')  #(1)!
>>> measurement
Measurement(title=Cyclic Voltammetry, timestamp=2017-07-12T14:33:10, device=PalmSens4)

```

1. This is equivalent to `ps.load_session_file(...)[0]`

The measurement data and curve classes are defined in the `.curves` attribute:

- Curves: `.curves`
- Raw data: `.dataset`
- EIS data: `.eis_data`

See the [Measurement documentation](../data.md#measurement) for how to work with the data classes.

## Saving Data

For single measurements, use [pypalmsens.save_measurement][]:

```pycon
>>> ps.save_measurement('cv_measurement.pssession', measurement)  #(1)!

```

1. This is equivalent to `ps.save_session_file(..., [measurement])`.

Note that session files can contain multiple measurements, so to store multiple measurements, use [pypalmsens.save_session_file][]:

```pycon
>>> ps.save_session_file(
...     'CV DPV EIS measurements.pssession',
...     measurements  #(1)!
... )

```

1. A list of measurements
