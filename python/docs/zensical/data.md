# Working with Data

This page shows how to use `pypalmsens` to interface with your measurement data.

The [pypalmsens.data][] submodule contains wrappers for the data structure in the underlying PalmSens .NET SDK libraries.

## Measurement

The top level object is a [Measurement][pypalmsens.data.Measurement].
The Measurement class contains information about the method, data, and experiment metadata.


```pycon
>>> import pypalmsens as ps
>>> measurements = ps.load_session_file('Demo CV DPV EIS IS-C electrode.pssession')
>>> measurements
[Measurement(title=Differential Pulse Voltammetry, timestamp=12-Jul-17 14:28:58, device=PalmSens4),
 Measurement(title=Cyclic Voltammetry [1], timestamp=12-Jul-17 14:33:10, device=PalmSens4),
 Measurement(title=Impedance Spectroscopy [2], timestamp=12-Jul-17 14:48:42, device=PalmSens4)]
```

Note that a session file (`.pssession`) can contain multiple measurements.
Therefore, [pypalmsens.load_session_file][] always returns a list of measurements. You can select the first measurement (DPV) using index `[0]`:

```pycon
>>> measurement = measurements[0]
```

From there, you can query device information and other metadata:

```pycon
>>> measurement.device
DeviceInfo(type='PalmSens4', firmware='', serial='PS4A16A000003', id=9)
```

And measurement details like title and timestamp:

```pycon
>>> measurement.title
'Differential Pulse Voltammetry'
>>> measurement.timestamp
'12-Jul-17 14:28:58'
>>> measurement.channel # (1)!
-1
```

1. For multichannel measurements

You have two main ways to access the data:

*   `measurement.dataset` returns the raw data that were measured, analogous to the _Data_ tab in PSTrace.
*   `measurement.curves` returns a list of [Curve](#curve) objects, which represent the plots.

For more information, see the [pypalmsens.data.Measurement][].

## Curve

A measurement can contain multiple curves, therefore `measurement.curves` returns a list.
The example below has only one curve with 219 data points:

```pycon
>>> curves = measurement.curves
>>> curves
[Curve(title=Curve, n_points=219)]
>>> curve = curves[0]
```

You can query some [Curve][pypalmsens.data.Curve] metadata like this:

```pycon
>>> curve.title
Curve
>>> len(curve)
219
>>> curve.x_label, curve.x_unit
('Potential', 'V')
>>> curve.y_label, curve.y_unit
('Current', 'µA')
```

Use the `.plot()` method to visualize the data. This requires [matplotlib](https://matplotlib.org/) to be installed:

```pycon
>>> fig = curve.plot() # (1)!
>>> fig.show()
```

1. This returns a [matplotlib.figure.Figure][].

The resulting plot looks like this:

![Image of DPV plot](assets/dpv_figure_1.png){ width="80%" }

The measurement stores a single peak. You can retrieve it using:

```pycon
>>> curve.peaks
>>> peaks
[Peak(x=0.179102 V, y=3.42442 µA, y_offset=0.26371 µA, area=0.818265 VµA, width=0.221563 V)]
```

To programmatically find peaks, use `.find_peaks()`:

```pycon
>>> peaks = curve.find_peaks()
>>> peaks
[Peak(x=0.179102 V, y=3.42442 µA, y_offset=0.26371 µA, area=0.818265 VµA, width=0.221563 V)]
```

Alternatively, for Cyclic Voltammetry (CV) and Linear Sweep Voltammetry (LSV), you can use `curve.find_peaks_semiderivative()`. For more information on this algorithm, see [this Wikipedia page](https://en.wikipedia.org/wiki/Neopolarogram).

!!! NOTE "Peak finding"

    The peak finder may not always find peaks on the first attempt depending on your data. You may need to tune parameters for better results.
    See [pypalmsens.data.Curve.find_peaks][] for more information.

You can also filter data using [pypalmsens.data.Curve.smooth][]. Note that this method updates the curve in-place:

```pycon
>>> curve.smooth(smooth_level=1)
```

Or, you can use a [Savitsky-Golay filter](https://en.wikipedia.org/wiki/Savitzky%E2%80%93Golay_filter):

```pycon
>>> curve.savitsky_golay(window_size=3)
```

Curve data are devived from the underlying [Dataset](#dataset), where variable data are stored in [DataArray](#dataarray)'s.
To access the raw x and y data for custom plotting or analysis, use `curve.x_array` and `curve.y_array`.
Both return [DataArray](#dataarray) objects that can be converted to standard Python floats or numpy arrays:

```pycon
>>> curve.x_array
DataArray(name=potential, unit=V, n_points=219)
>>> list(curve.x_array)
[-0.399962, -0.394962, ..., 0.692698, 0.697776]

>>> curve.y_array
DataArray(name=current, unit=µA, n_points=219)
>>> np.array(curve.y_array)
array([0.352146, 0.351192, ..., 0.19908 , 0.199557])
```

For more details on array manipulation, see [pypalmsens.data.Curve][].

## Peak

[Peak][pypalmsens.data.Peak] is a small dataclass containing peak properties.
Stored peaks can be retrieved from a [Curve](#curve) (for example, if PSTrace stored peaks in the `.pssession` file):

```pycon
>>> peaks = curve.peaks
>>> peaks
[Peak(x=0.179102 V, y=3.42442 µA, y_offset=0.26371 µA, area=0.818265 VµA, width=0.221563 V)]
```

Many peak properties are accessible from this object:

```pycon
>>> peak.x, peak.y
(0.179102, 3.42442)
>>> peak.width
0.2215
>>> peak.area
0.8182
>>> peak.left_x, peak.right_x
(-0.35465, 0.647385)
>>> peak.value # (1)!
3.1607
```

1. The `peak.value` represents the height of the peak relative to the baseline.

For more information on peak properties, see [pypalmsens.data.Peak][].

## DataSet

Raw data are stored in a [DataSet](#dataset). The dataset contains all raw measurement data, including the data for the curves.

```pycon
>>> dataset = measurement.dataset
>>> dataset
DataSet(['Time', 'Potential', 'Current'])
```

Since a `DataSet` acts like a Python dictionary (a mapping), you can access arrays by name:

```pycon
>>> dataset['Time']
DataArray(name=time, unit=s, n_points=219)
>>> dataset['Potential']
PotentialArray(name=potential, unit=V, n_points=219)
```

To list all available arrays:

```pycon
>>> dataset.arrays()
[DataArray(name=time, unit=s, n_points=219),
 PotentialArray(name=potential, unit=V, n_points=219),
 CurrentArray(name=current, unit=µA, n_points=219)]
```

You can retrieve arrays of a specific type using:

```pycon
>>> dataset.array_types
{'Current', 'Potential', 'Time'}
>>> dataset.arrays(type='Current')
[CurrentArray(name=current, unit=µA, n_points=219)]
```

Alternatively, you can query by name:

```pycon
>>> dataset.array_names
{'current', 'potential', 'time'}
>>> dataset.arrays(name='time')
[DataArray(name=time, unit=s, n_points=219)]
```

You can also filter by quantity:

```pycon
>>> dataset.array_quantities
{'Current', 'Potential', 'Time'}
>>> dataset.arrays(quantity='Potential')
[PotentialArray(name=potential, unit=V, n_points=219)]
```

Type and quantity may seem similar, but for methods with many quantities the difference will be visible.
For example, in impedimetric measurements (EIS/GEIS), 'miDC' and 'Iac' are different array types, but have the same quantity: 'Current'.

Note that for larger datasets, these methods might return multiple `DataArray` objects. Data from a _Cyclic Voltammetry_ measurement can contain multiple scans, meaning the dataset might hold multiple arrays per array type.

If you have [pandas](https://pandas.pydata.org/) installed, you can easily convert the entire dataset into a [DataFrame](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html):

```pycon
>>> df = pd.DataFrame(dataset.to_dict())
>>> df
     Time Potential   Current     CR ReadingStatus
0     0.0 -0.399962  0.352146  10 uA            OK
1     0.2 -0.394962  0.351192  10 uA            OK
2     0.4 -0.389884    0.3469  10 uA            OK
..    ...       ...       ...    ...           ...
216  43.2  0.687698  0.198544  10 uA            OK
217  43.4  0.692698   0.19908  10 uA            OK
218  43.6  0.697776  0.199557  10 uA            OK

[219 rows x 5 columns]
```

Any new [Curve](#curve) can be generated by passing the desired x and y keys:

```pycon
>>> list(dataset)
['Time', 'Potential', 'Current']
>>> curve = dataset.curve(x='Time', y='Potential', title='My curve')
>>> curve
Curve(title=My curve, n_points=219)
```

For more information on Dataset, see [pypalmsens.data.DataSet][].

## DataArray

Data arrays store a list of values, essentially representing a single column in the PSTrace *Data* tab.
A [Dataset](#dataset) contains multiple data arrays.

Let's examine the first current array:

```pycon
>>> array = dataset.arrays(type='Current')[0]
>>> array
CurrentArray(name=current, unit=µA, n_points=219)
```

An array stores metadata about itself:

```pycon
>>> array.name
'current'
>>> array.type
'Current'
>>> array.unit
'µA'
>>> array.quantity
'Current'
```

Arrays behave like a Python [Sequence](https://docs.python.org/3/glossary.html#term-sequence) (e.g., a list):

```pycon
>>> len(array)
219
>>> min(array)
0.193358
>>> max(array)
3.42442
>>> array[0]
0.352146
```

Arrays support complex slicing, but remember that this operation returns a standard Python list:

```pycon
>>> array[:5]
[0.352146, 0.351192, 0.3469, 0.345947, 0.344516]
>>> array[-5:]
[0.197411, 0.198127, 0.198544, 0.19908, 0.199557]
>>> array[::-1]  # (1)!
[0.199557, 0.19908, ..., 0.351192, 0.352146]
```

1. reverse list

You can convert arrays into lists or numpy arrays:

```pycon
>>> list(array)
[0.352146, 0.351192, ..., 0.19908, 0.199557]
>>> np.array(array)
array([0.352146, 0.351192, ..., 0.19908 , 0.199557])
```

For more information on array structures, see [pypalmsens.data.DataArray][].

### CurrentArray

`CurrentArray` derives from `DataArray` and includes additional methods for analyzing current readings, such as the current range, reading status, etc.:

```pycon
>>> import pypalmsens as ps
>>> measurement = ps.measure(ps.CyclicVoltammetry())
>>> array = measurement['Current']
>>> array
CurrentArray(name=scan1, unit=µA, n_points=21)
>>> array.current()  # (1)!
[-304.951, -301.55, -291.406, ...]
>>> array.current_in_range()  # (2)!
[-3.04951, -0.30155, -0.291406,  ... ]
>>> array.current_range()  # (3)!
['100uA', '1mA',  '1mA', ...]
>>> array.reading_status()  # (4)!
['Overload', 'OK', 'OK', 'OK']
>>> array.timing_status()  # (5)!
['OK', 'OK', 'OK', ...]
>>> pd.DataFrame(array.to_dict())
    Current  CurrentInRange     CR TimingStatus ReadingStatus
0  -304.951       -3.049510  100uA           OK      Overload
1  -301.550       -0.301550    1mA           OK            OK
2  -291.406       -0.291406    1mA           OK            OK
...
```

1. returns current readings in µA
2. returns values within a specified range
3. returns the current range bins (e.g., '100uA', '1mA')
4. returns status for each reading
5. returns timing status

For more information, see [pypalmsens.data.CurrentArray][].

### PotentialArray

Similar to currents, `PotentialArray` also derives from `DataArray` and provides methods to query associated data:

```pycon
>>> array = measurement.dataset['Potential']
>>> array.potential()  # (1)!
[-0.50, -0.40, 0.30, ...]
>>> array.potential_in_range()  # (2)!
[-0.50, -0.40, -0.30, ...]
>>> array.potential_range()  # (3)!
['1V', '1V', '1V', ...]
>>> array.reading_status()  # (4)!
['Unknown', 'Unknown', 'Unknown', ...]
>>> array.timing_status()  # (5)!
['Unknown', 'Unknown', 'Unknown', ...]
>>> pd.DataFrame(array.to_dict())
    Potential  PotentialInRange  CR TimingStatus ReadingStatus
0       -0.50             -0.50  1V      Unknown       Unknown
1       -0.40             -0.40  1V      Unknown       Unknown
2       -0.30             -0.30  1V      Unknown       Unknown
...
```

1. returns potential readings in V
2. returns values within a specified range
3. returns potential range bins (e.g., '1V')
4. returns status for each reading
5. returns timing status

For more information, see [pypalmsens.data.PotentialArray][].

## EISData

You can retrieve impedance data from an impedance (EIS/GEIS) measurement.

Since an EIS measurement might be multichannel, `.eis_data` returns a list of results.
If you are not using a multiplexer, you can select the first (and only) item from this list:

```pycon
>>> eis_measurement = measurements[2]
>>> eis_measurement
Measurement(title=Impedance Spectroscopy [2], timestamp=12-Jul-17 14:48:42, device=PalmSens4)
>>> eis_measurement.eis_data # (1)!
[EISData(title=FixedPotential at 71 freqs [2], n_points=71, n_frequencies=71)]
>>> eis_data = eis_measurement.eis_data[0] # (2)!
```

1. `.eis_data` returns a list
2. pick the first and only item

The `EISData` object can be queried for metadata:

```pycon
>>> eis.title
'FixedPotential at 71 freqs [2]'
>>> eis.scan_type
'fixed'
>>> eis.frequency_type
'scan'
>>> eis.n_points
5
>>> eis.n_frequencies
5
```

If you previously fitted a circuit model in PSTrace, you can retrieve the CDC values:

```pycon
>>> eis_data.cdc
'R([RT]Q)'
>>> eis_data.cdc_values
[132.146, 11009.9, 3710.55, 3.77887, 0.971414, 6.23791e-07, 0.961612]
```

You can use these values to [fit a circuit model](circuit_fitting.md):

```pycon
>>> model = ps.fitting.CircuitModel(cdc=eis_data.cdc)
>>> result = model.fit(eis_data, parameters=eis_data.cdc_values)
>>> result
FitResult(
    cdc='R([RT]Q)',
    parameters=[132.14, 11009.96, 3710.50, 3.78, 0.97, 6.23e-07, 0.96],
    error=[1.51, 4.60, 37.55, 165.04, 25.81, 7.22, 0.94],
    chisq=0.0054,
    n_iter=5,
    exit_code='MinimumDeltaErrorTerm',
)
```

The raw data can be accessed via `.dataset`, which returns a [DataSet](#dataset) object:

```pycon
>>> eis_data.dataset
DataSet(['Current', 'Potential', 'Time', 'Frequency', 'ZRe', 'ZIm', 'Z', 'Phase', 'Iac', 'Unspecified_1', 'Unspecified_2', 'Unspecified_3', 'Unspecified_4', 'YRe', 'YIm', 'Y', 'Cs', 'CsRe', 'CsIm'])
```

You can retrieve all arrays from the EIS data:

```pycon
>>> eis_data.arrays()
[CurrentArray(name=Idc, unit=µA, n_points=71),
 PotentialArray(name=potential, unit=V, n_points=71),
 DataArray(name=time, unit=s, n_points=71),
 ...
 DataArray(name=Capacitance, unit=F, n_points=71),
 DataArray(name=Capacitance', unit=F, n_points=71),
 DataArray(name=Capacitance'', unit=F, n_points=71)]
```

For more information on EIS datasets, see [pypalmsens.data.EISData][].

### Subscans

If an EIS dataset contains subscans, this will be shown in the object's representation:

```pycon
>>> eis
EISData(title=CH 3: E dc scan at 5 freqs, n_points=20, n_frequencies=5, n_subscans=4)
>>> eis.has_subscans
True
>>> eis.n_subscans
4
```

Subscans can be accessed via the `.subscans()` method:

```pycon
>>> eis.subscans
[EISData(title=E=0.000 V, n_points=5, n_frequencies=5),
 EISData(title=E=0.200 V, n_points=5, n_frequencies=5),
 EISData(title=E=0.400 V, n_points=5, n_frequencies=5),
 EISData(title=E=0.600 V, n_points=5, n_frequencies=5)]
```

Subscans are themselves `EISData` objects.
