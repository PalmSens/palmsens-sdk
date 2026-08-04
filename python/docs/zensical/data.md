# Working with data

This page shows how to use `pypalmsens` to interface with your measurement data.

The [pypalmsens.data][] submodule contains wrappers for the PyPalmSens .NET SDK libraries.
These are the same libraries that power the [PSTrace](https://www.palmsens.com/software/ps-trace/) software.

## Measurement

```python
import pypalmsens as ps  # comment

measurements = ps.load_session_file('examples/Demo CV DPV EIS IS-C electrode.pssession')

print(measurements)
"""
[Measurement(title=Differential Pulse Voltammetry, timestamp=2017-07-12T14:28:58, device=PalmSens4), Measurement(title=Cyclic Voltammetry [1], timestamp=2017-07-12T14:33:10, device=PalmSens4), Measurement(title=Impedance Spectroscopy [2], timestamp=2017-07-12T14:48:42, device=PalmSens4)]
"""
```

A `.pssession` file always contains a list of measurements, so you can pick the first (DPV) one:

```python
measurement = measurements[0]
```

From there you can query the device info:

```python
print(measurement.device)
#> DeviceInfo(type='PalmSens4', firmware='', serial='PS4A16A000003', id=9)
```

As well as other measurement metadata:

```python
print(measurement.title)
#> Differential Pulse Voltammetry

print(measurement.timestamp)
#> 2017-07-12T14:28:58

print(measurement.channel) # (1)!
#> -1
```

1. For multichannel measurements

There are two ways to access the data.
`m.dataset` returns the raw data that were measured, analogous to the _Data_ tab in PSTrace.
`m.curves` returns a list of [Curve](#curve) objects, which represent the plots.

For more information, see the [pypalmsens.data.Measurement][].

## Curve

A measurement can contain multiple curves, this measurement has only 1 with 219 data points:

```python
curves = measurement.curves

print(curves)
#> [Curve(title=Curve, n_points=219)]
```

From here you can query some Curve metadata:

```python
curve = curves[0]

print(curve.title)
#> Curve

print(len(curve))
#> 219

print(curve.x_label, curve.x_unit)
#> Potential V

print(curve.y_label, curve.y_unit)
#> Current µA

```

Use the `.plot()` method to show a simple plot of the data.
This depends on [matplotlib](https://matplotlib.org/) being available.

```python
fig = curve.plot() # (1)!
fig.show()
```

1. This returns a [matplotlib.figure.Figure][].

This results in this plot:

![Image of DPV plot](assets/dpv_figure_1.png){ width="80%" }

The data has a single peak stored in the measurement. You can retrieve it using:

```python
print(curve.peaks)
"""
[Peak(x=0.179102 V, y=3.42442 µA, y_offset=0.501758 µA, area=0.647762 VµA, width=0.201485 V)]
"""
```

To find the peak, use `.find_peaks()`:

```python
peaks = curve.find_peaks()
print(peaks)
"""
[Peak(x=0.179102 V, y=3.42442 µA, y_offset=0.26371 µA, area=0.818265 VµA, width=0.216563 V)]
"""
```

An alternative method for CV and LSV is available under `curve.find_peaks_semiderivative()`.
For more info on this algorithm, see [this Wikipedia page](https://en.wikipedia.org/wiki/Neopolarogram).

!!! NOTE "Peak finding"

    Depending on your data, the peak finder may not always find peaks on the first try.
    Sometimes the parameters need to be tuned, see [pypalmsens.data.Curve.find_peaks][] for more information.

You can do filtering using [pypalmsens.data.Curve.smooth][]. Note that this updates the curve in-place.

```python
curve.smooth(smooth_level=1)
```

Or alternatively using a [Savitsky-Golay filter](https://en.wikipedia.org/wiki/Savitzky%E2%80%93Golay_filter):

```python
curve.savitsky_golay(window_size=3)
```

To make your own plot or run your own data processing or analytics script,
the raw x and y data can be accessed through `curve.x_array` and `curve.y_array`.
These both return [DataArray](#dataarray) objects, which can be converted to floats or numpy arrays.

```python
print(curve.x_array)
#> DataArray(name=potential, unit=V, n_points=219)

print(list(curve.x_array)[:5]) # (1)!
#> [-0.399962, -0.394962, -0.389884, -0.384884, -0.379806]

print(curve.y_array)
#> DataArray(name=current, unit=µA, n_points=219)

import numpy as np

print(np.array(curve.y_array)) # (2)!
"""
[0.352146   0.34988091 0.3476509  0.34582246 0.34427407 0.34355729
 0.34364791 0.34375704 0.34318542 0.3431818  0.34461797 0.34603591
 0.34648748 0.34762682 0.35085138 0.35402086 0.35607702 0.35820485
 0.36189888 0.36584161 0.36985445 0.37386234 0.37770955 0.38047076
 0.38306875 0.38654686 0.39139747 0.39720522 0.40283433 0.40812965
 0.41252083 0.41641709 0.42060948 0.42605971 0.43209123 0.43772928
 0.44317137 0.44890277 0.4545749  0.45954959 0.46418179 0.46924904
 0.47494217 0.48151673 0.48822595 0.49437915 0.49977325 0.50486027
 0.5100499  0.51617877 0.52325011 0.5303802  0.53669559 0.54218811
 0.54737342 0.55241193 0.5575417  0.56257908 0.56790851 0.57462359
 0.5817099  0.58850675 0.59419933 0.59960332 0.60569477 0.61256226
 0.6201726  0.62847388 0.6381549  0.64863483 0.65994481 0.67342529
 0.6881364  0.70298793 0.71876821 0.73717279 0.75913395 0.78422492
 0.81189445 0.84209503 0.87540466 0.91283996 0.95461731 1.00395215
 1.06319528 1.12830267 1.19192522 1.25255312 1.31655408 1.38810125
 1.46783631 1.55495563 1.64872827 1.74621239 1.84690562 1.95243757
 2.0626346  2.17454904 2.28628134 2.39824427 2.50995399 2.62028321
 2.72764035 2.83000948 2.92672581 3.01663662 3.0992618  3.17336951
 3.23887349 3.29463776 3.34066708 3.3770033  3.40358262 3.41966377
 3.42608557 3.42407953 3.41221235 3.38926046 3.35671625 3.31622216
 3.26576331 3.20559473 3.13942008 3.06976775 2.99542628 2.91671577
 2.83491439 2.75015959 2.66164916 2.57104664 2.47952722 2.38829587
 2.29745488 2.20812682 2.11936616 2.03043868 1.94174173 1.85442157
 1.76999591 1.68905714 1.61152205 1.53748776 1.46663701 1.39863564
 1.33219432 1.26824054 1.20801618 1.15100861 1.09657923 1.04497709
 0.99656809 0.9501664  0.90511562 0.86173302 0.82096753 0.78235679
 0.74569531 0.71166616 0.67991876 0.64963673 0.62043368 0.59242541
 0.56571789 0.54107916 0.51925308 0.49917088 0.47956541 0.45983016
 0.44041867 0.42187786 0.40514988 0.39049842 0.37725165 0.36483078
 0.35364147 0.34308262 0.33220003 0.3212318  0.31134687 0.30242063
 0.2935288  0.28516263 0.27863082 0.27266196 0.2646879  0.25585876
 0.24902276 0.24433023 0.23986889 0.23543113 0.23208289 0.22993475
 0.22778666 0.22419513 0.21962058 0.21569198 0.21341777 0.21204078
 0.21082809 0.20883522 0.20626839 0.20427504 0.20355066 0.20292564
 0.2017651  0.20068418 0.19959817 0.19814618 0.1965314  0.1960282
 0.19601016 0.19647393 0.19691793 0.19734872 0.19767972 0.19810595
 0.19856537 0.19905777 0.199557  ]
"""
```

1. Convert to list...
2. ...or numpy array

For more information, see [pypalmsens.data.Curve][].

## Peak

The peaks is a small dataclass containing peak propersies.

Stored peaks can be retrieved from a [Curve](#curve) (e.g. if PSTrace stored peaks in the `.pssession file).

```python
peaks = curve.peaks

print(peaks)
"""
[Peak(x=0.179102 V, y=3.42408 µA, y_offset=0.501758 µA, area=0.647762 VµA, width=0.201485 V), Peak(x=0.179102 V, y=3.42408 µA, y_offset=0.26371 µA, area=0.818265 VµA, width=0.216563 V)]
"""
# [Peak(x=0.179102 V, y=3.42442 µA, y_offset=0.26371 µA, area=0.818265 VµA, width=0.221563 V)]
```

Many peak properties are accessible from this object.

```python
peak = peaks[0]

print(peak.x, peak.y)
#> 0.179102 3.4240795300662503

print(peak.width)
#> 0.20148520000000003

print(peak.area)
#> 0.6477622406522667

print(peak.left_x), peak.right_x
#> -0.0626174

print(peak.value) # (1)!
#> 2.9223213475512604
```

1. The peak value is the height of the peak relative to the baseline

For more information, see [pypalmsens.data.Peak][].

## DataSet

The raw data are stored in a dataset. The dataset contains all the raw data, including the data for the curves.

```python
dataset = measurement.dataset

print(dataset)
#> DataSet(['Time', 'Potential', 'Current'])
```

A dataset is a mapping, so it acts like a Python dictionary:

```python
print(dataset['Time'])
#> DataArray(name=time, unit=s, n_points=219)

print(dataset['Potential'])
#> PotentialArray(name=potential, unit=V, n_points=219)
```

To list all arrays:

```python
print(dataset.arrays())
"""
[
    DataArray(name=time, unit=s, n_points=219),
    PotentialArray(name=potential, unit=V, n_points=219),
    CurrentArray(name=current, unit=µA, n_points=219),
]
"""
```

Arrays of the same type can be retrieved through a method:

```python
print(dataset.arrays(type='Current'))
#> [CurrentArray(name=current, unit=µA, n_points=219)]

print(dataset.arrays(type='Potential'))
#> [PotentialArray(name=potential, unit=V, n_points=219)]
```

Datasets can be quite large and contain many arrays.
Therefore, arrays can be selected by name...

```python
print(dataset.array_names)
#> {'current', 'potential', 'time'}

print(dataset.arrays(name='time'))
#> [DataArray(name=time, unit=s, n_points=219)]
```

...quantity...

```python
print(dataset.array_quantities)
#> {'Current', 'Potential', 'Time'}

print(dataset.arrays(quantity='Potential'))
#> [PotentialArray(name=potential, unit=V, n_points=219)]
```

...or type:

```python
print(dataset.array_types)
#> {'Current', 'Potential', 'Time'}

print(dataset.arrays(type='Current'))
#> [CurrentArray(name=current, unit=µA, n_points=219)]
```

Type and quantity may seem similar, but for methods with many quantities the difference will be visible.
For example, in EIS 'miDC' and 'Iac' are different array types, but have the same quantity 'Current'.

Note that for larger datasets these methods can return multiple DataArrays.
Data from a _Cyclic Voltammetry_ measurement can contain multiple scans and
can therefore the dataset can contain multiple arrays per array type.

If you have [pandas](https://pandas.pydata.org/) installed,
you can use easily convert the dataset into a
[DataFrame](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html):

```python
import pandas as pd
df = pd.DataFrame(dataset.to_dict())

print(df.head(5))
"""
   Time  Potential   Current    CR ReadingStatus
0   0.0  -0.399962  0.352146  10uA            OK
1   0.2  -0.394962  0.351192  10uA            OK
2   0.4  -0.389884  0.346900  10uA            OK
3   0.6  -0.384884  0.345947  10uA            OK
4   0.8  -0.379806  0.344516  10uA            OK
"""
#>
#> [219 rows x 5 columns]
```

Any new [Curve](#curve) can be generated by passing the x and y keys to use:

```python
print(list(dataset))
#> ['Time', 'Potential', 'Current']

curve = dataset.curve(x='Time', y='Potential', title='My curve')

print(curve)
#> Curve(title=My curve, n_points=219)
```

1. Any combination of these will work

For more information, see [pypalmsens.data.DataSet][].

## DataArray

Data arrays store a list of values, essentially representing a column in the PSTrace Data tab.

Let’s grab the first current array:

```python
array = dataset.arrays(type='Current')[0]

print(array)
#> CurrentArray(name=current, unit=µA, n_points=219)
```

An array stores some data about itself:

```python
print(array.name)
#> current

print(array.type)
#> Current

print(array.unit)
#> µA

print(array.quantity)
#> Current
```

Arrays act and behave like a
Python [Sequence](https://docs.python.org/3/glossary.html#term-sequence)
(e.g. a list).

```python
print(len(array))
#> 219

print(min(array))
#> 0.193358

print(max(array))
#> 3.42442

print(array[0])
#> 0.352146
```

Arrays support complex slicing, but note that this returns a list.

```python
print(array[:5])
#> [0.352146, 0.351192, 0.3469, 0.345947, 0.344516]

print(array[-5:])
#> [0.197411, 0.198127, 0.198544, 0.19908, 0.199557]

print(array[4::-1])  # (1)!
#> [0.344516, 0.345947, 0.3469, 0.351192, 0.352146]
```

1. `[::-1]` reverses list

Arrays can be converted to lists or numpy arrays:

```python
print(list(array))
"""
[
    0.352146,
    0.351192,
    0.3469,
    0.345947,
    0.344516,
    0.343086,
    0.343562,
    0.343086,
    0.345947,
    0.341178,
    0.344039,
    0.34547,
    0.350715,
    0.344039,
    0.350715,
    0.353099,
    0.360729,
    0.355007,
    0.361206,
    0.366451,
    0.371219,
    0.371696,
    0.378849,
    0.38171,
    0.38171,
    0.387909,
    0.388385,
    0.399353,
    0.401737,
    0.409366,
    0.41175,
    0.417949,
    0.41938,
    0.425579,
    0.431778,
    0.43893,
    0.443222,
    0.44799,
    0.454189,
    0.461819,
    0.462295,
    0.470402,
    0.47374,
    0.481846,
    0.487568,
    0.495674,
    0.499489,
    0.505211,
    0.509502,
    0.516655,
    0.521423,
    0.531437,
    0.537636,
    0.541451,
    0.54765,
    0.552895,
    0.555756,
    0.565293,
    0.565769,
    0.575306,
    0.580075,
    0.590565,
    0.59438,
    0.598671,
    0.607254,
    0.609639,
    0.622513,
    0.628712,
    0.635388,
    0.6516,
    0.65923,
    0.672105,
    0.688317,
    0.70453,
    0.719788,
    0.73457,
    0.759843,
    0.784162,
    0.811342,
    0.844243,
    0.874284,
    0.912431,
    0.957254,
    1.00112,
    1.06073,
    1.12415,
    1.20187,
    1.25385,
    1.31488,
    1.38307,
    1.47081,
    1.55283,
    1.64867,
    1.7469,
    1.8499,
    1.94908,
    2.06066,
    2.17749,
    2.28716,
    2.39588,
    2.51175,
    2.61761,
    2.73014,
    2.82837,
    2.92898,
    3.01434,
    3.10112,
    3.17265,
    3.23893,
    3.2952,
    3.3405,
    3.37769,
    3.40153,
    3.42299,
    3.42394,
    3.42442,
    3.40964,
    3.39533,
    3.35289,
    3.3157,
    3.26611,
    3.21127,
    3.13355,
    3.07013,
    2.99526,
    2.91992,
    2.83028,
    2.75303,
    2.661,
    2.57326,
    2.47551,
    2.39159,
    2.29526,
    2.208,
    2.11979,
    2.03062,
    1.94336,
    1.85323,
    1.76931,
    1.69016,
    1.60909,
    1.53995,
    1.46509,
    1.39785,
    1.33539,
    1.26672,
    1.20712,
    1.15085,
    1.0984,
    1.04309,
    0.997309,
    0.949148,
    0.907186,
    0.86141,
    0.819448,
    0.783208,
    0.746491,
    0.710252,
    0.679734,
    0.650647,
    0.620606,
    0.591519,
    0.567677,
    0.539066,
    0.519516,
    0.498058,
    0.481369,
    0.459911,
    0.440361,
    0.42176400000000003,
    0.405552,
    0.388385,
    0.378849,
    0.36502,
    0.352622,
    0.343086,
    0.333549,
    0.321151,
    0.310661,
    0.301601,
    0.294925,
    0.285865,
    0.275851,
    0.272513,
    0.268222,
    0.256301,
    0.24581,
    0.243426,
    0.242949,
    0.234366,
    0.231982,
    0.22864400000000001,
    0.22864400000000001,
    0.22483,
    0.221492,
    0.212909,
    0.213862,
    0.211478,
    0.211478,
    0.209094,
    0.207187,
    0.203372,
    0.202418,
    0.203372,
    0.203372,
    0.199557,
    0.198603,
    0.200511,
    0.195742,
    0.194312,
    0.198127,
    0.193358,
    0.19765,
    0.19765,
    0.197411,
    0.198127,
    0.198544,
    0.19908,
    0.199557,
]
"""

print(np.array(array))
"""
[0.352146 0.351192 0.3469   0.345947 0.344516 0.343086 0.343562 0.343086
 0.345947 0.341178 0.344039 0.34547  0.350715 0.344039 0.350715 0.353099
 0.360729 0.355007 0.361206 0.366451 0.371219 0.371696 0.378849 0.38171
 0.38171  0.387909 0.388385 0.399353 0.401737 0.409366 0.41175  0.417949
 0.41938  0.425579 0.431778 0.43893  0.443222 0.44799  0.454189 0.461819
 0.462295 0.470402 0.47374  0.481846 0.487568 0.495674 0.499489 0.505211
 0.509502 0.516655 0.521423 0.531437 0.537636 0.541451 0.54765  0.552895
 0.555756 0.565293 0.565769 0.575306 0.580075 0.590565 0.59438  0.598671
 0.607254 0.609639 0.622513 0.628712 0.635388 0.6516   0.65923  0.672105
 0.688317 0.70453  0.719788 0.73457  0.759843 0.784162 0.811342 0.844243
 0.874284 0.912431 0.957254 1.00112  1.06073  1.12415  1.20187  1.25385
 1.31488  1.38307  1.47081  1.55283  1.64867  1.7469   1.8499   1.94908
 2.06066  2.17749  2.28716  2.39588  2.51175  2.61761  2.73014  2.82837
 2.92898  3.01434  3.10112  3.17265  3.23893  3.2952   3.3405   3.37769
 3.40153  3.42299  3.42394  3.42442  3.40964  3.39533  3.35289  3.3157
 3.26611  3.21127  3.13355  3.07013  2.99526  2.91992  2.83028  2.75303
 2.661    2.57326  2.47551  2.39159  2.29526  2.208    2.11979  2.03062
 1.94336  1.85323  1.76931  1.69016  1.60909  1.53995  1.46509  1.39785
 1.33539  1.26672  1.20712  1.15085  1.0984   1.04309  0.997309 0.949148
 0.907186 0.86141  0.819448 0.783208 0.746491 0.710252 0.679734 0.650647
 0.620606 0.591519 0.567677 0.539066 0.519516 0.498058 0.481369 0.459911
 0.440361 0.421764 0.405552 0.388385 0.378849 0.36502  0.352622 0.343086
 0.333549 0.321151 0.310661 0.301601 0.294925 0.285865 0.275851 0.272513
 0.268222 0.256301 0.24581  0.243426 0.242949 0.234366 0.231982 0.228644
 0.228644 0.22483  0.221492 0.212909 0.213862 0.211478 0.211478 0.209094
 0.207187 0.203372 0.202418 0.203372 0.203372 0.199557 0.198603 0.200511
 0.195742 0.194312 0.198127 0.193358 0.19765  0.19765  0.197411 0.198127
 0.198544 0.19908  0.199557]
"""
```

For more information, see [pypalmsens.data.DataArray][].

### CurrentArray

Current readings have more data associated with them, such as the current range, reading status, etc.
[pypalmsens.data.CurrentArray][] derive from `DataArray` and contain additional methods:

```python
import pypalmsens as ps
measurement = ps.measure(ps.CyclicVoltammetry())
array = measurement.dataset['Current']

print(array)
#> CurrentArray(name=scan1, unit=µA, n_points=21)

print(array.current())  # in µA
"""
[
    -50.016895999999996,
    -40.017812,
    -30.02903,
    -20.032352,
    -10.027448999999999,
    -0.036653388,
    9.946921,
    19.972483999999998,
    29.963691999999998,
    39.93542,
    49.937332,
    39.932128,
    29.941201999999997,
    19.947091999999998,
    9.944965,
    -0.037074288000000004,
    -10.029439,
    -20.008104,
    -29.943654,
    -40.004872,
    -50.012328,
]
"""

print(array.current_in_range())
"""
[
    -0.50016896,
    -0.40017811999999997,
    -0.3002903,
    -0.20032352,
    -0.10027449,
    -0.00036653388,
    0.09946921,
    1.9972483999999997,
    2.9963691999999997,
    0.3993542,
    0.49937331999999995,
    0.39932128,
    0.29941201999999995,
    0.19947091999999997,
    0.09944965,
    -0.00037074288000000003,
    -0.10029439,
    -2.0008103999999998,
    -2.9943654,
    -0.40004871999999997,
    -0.50012328,
]
"""

print(array.current_range())
"""
[
    '100uA',
    '100uA',
    '100uA',
    '100uA',
    '100uA',
    '100uA',
    '100uA',
    '10uA',
    '10uA',
    '100uA',
    '100uA',
    '100uA',
    '100uA',
    '100uA',
    '100uA',
    '100uA',
    '100uA',
    '10uA',
    '10uA',
    '100uA',
    '100uA',
]
"""

print(array.reading_status())
"""
[
    'OK',
    'OK',
    'OK',
    'OK',
    'Underload',
    'Underload',
    'Underload',
    'OK',
    'Overload',
    'OK',
    'OK',
    'OK',
    'OK',
    'OK',
    'Underload',
    'Underload',
    'Underload',
    'OK',
    'Overload',
    'OK',
    'OK',
]
"""

print(array.timing_status())
"""
[
    'OK',
    'OK',
    'OK',
    'OK',
    'OK',
    'OK',
    'OK',
    'OK',
    'OK',
    'OK',
    'OK',
    'OK',
    'OK',
    'OK',
    'OK',
    'OK',
    'OK',
    'OK',
    'OK',
    'OK',
    'OK',
]
"""

print(pd.DataFrame(array.to_dict()))
"""
     Current  CurrentInRange     CR TimingStatus ReadingStatus
0 -50.016896       -0.500169  100uA           OK            OK
1 -40.017812       -0.400178  100uA           OK            OK
2 -30.029030       -0.300290  100uA           OK            OK
3 -20.032352       -0.200324  100uA           OK            OK
4 -10.027449       -0.100274  100uA           OK     Underload
"""
```

For more information, see [pypalmsens.data.DataArray][].

### PotentialArray

Like currents, potential readings also have more data associated with them.
[pypalmsens.data.PotentialArray][] derive from `DataArray` and can be used to query additional data:

```python
array = measurement.dataset['Potential']

print(array.potential())  # in V
"""
[
    -0.49998899999999996,
    -0.400011,
    -0.300033,
    -0.20005599999999998,
    -0.10007779200000001,
    -0.000100077792,
    0.09987763200000001,
    0.19985499999999998,
    0.29983299999999996,
    0.39981099999999997,
    0.499789,
    0.39981099999999997,
    0.29983299999999996,
    0.19985499999999998,
    0.09987763200000001,
    -0.000100077792,
    -0.10007779200000001,
    -0.20005599999999998,
    -0.300033,
    -0.400011,
    -0.49998899999999996,
]
"""

print(array.potential_in_range())
"""
[
    -0.49998899999999996,
    -0.400011,
    -0.300033,
    -0.20005599999999998,
    -0.10007779200000001,
    -0.000100077792,
    0.09987763200000001,
    0.19985499999999998,
    0.29983299999999996,
    0.39981099999999997,
    0.499789,
    0.39981099999999997,
    0.29983299999999996,
    0.19985499999999998,
    0.09987763200000001,
    -0.000100077792,
    -0.10007779200000001,
    -0.20005599999999998,
    -0.300033,
    -0.400011,
    -0.49998899999999996,
]
"""

print(array.potential_range())
"""
[
    '1V',
    '1V',
    '1V',
    '1V',
    '1V',
    '1V',
    '1V',
    '1V',
    '1V',
    '1V',
    '1V',
    '1V',
    '1V',
    '1V',
    '1V',
    '1V',
    '1V',
    '1V',
    '1V',
    '1V',
    '1V',
]
"""

print(array.reading_status())
"""
[
    'Unknown',
    'Unknown',
    'Unknown',
    'Unknown',
    'Unknown',
    'Unknown',
    'Unknown',
    'Unknown',
    'Unknown',
    'Unknown',
    'Unknown',
    'Unknown',
    'Unknown',
    'Unknown',
    'Unknown',
    'Unknown',
    'Unknown',
    'Unknown',
    'Unknown',
    'Unknown',
    'Unknown',
]
"""

print(array.timing_status())
"""
[
    'Unknown',
    'Unknown',
    'Unknown',
    'Unknown',
    'Unknown',
    'Unknown',
    'Unknown',
    'Unknown',
    'Unknown',
    'Unknown',
    'Unknown',
    'Unknown',
    'Unknown',
    'Unknown',
    'Unknown',
    'Unknown',
    'Unknown',
    'Unknown',
    'Unknown',
    'Unknown',
    'Unknown',
]
"""

print(pd.DataFrame(array.to_dict()).head(5))
"""
   Potential  PotentialInRange  CR TimingStatus ReadingStatus
0  -0.499989         -0.499989  1V      Unknown       Unknown
1  -0.400011         -0.400011  1V      Unknown       Unknown
2  -0.300033         -0.300033  1V      Unknown       Unknown
3  -0.200056         -0.200056  1V      Unknown       Unknown
4  -0.100078         -0.100078  1V      Unknown       Unknown
"""
```

For more information, see [pypalmsens.data.PotentialArray][].

## EISData

You can retrieve EIS data from an EIS measurement.

Note that the EIS measurement can be multichannel, so `.eisdata` returns a list.
If you don’t use a multiplexer, you can pick the first (and only) item from the list.

```python
eis_measurement = measurements[2]

print(eis_measurement)
"""
Measurement(title=Impedance Spectroscopy [2], timestamp=2017-07-12T14:48:42, device=PalmSens4)
"""

print(eis_measurement.eis_data) # (1)!
#> [EISData(title=FixedPotential at 71 freqs [2], n_points=71, n_frequencies=71)]
```

1. `.eis_data` returns a list

The EISData object can be queried for metadata:

```python
eis_data = eis_measurement.eis_data[0] # (1)!

print(eis_data.title)
#> FixedPotential at 71 freqs [2]

print(eis_data.scan_type)
#> fixed

print(eis_data.frequency_type)
#> scan

print(eis_data.n_points)
#> 71

print(eis_data.n_frequencies)
#> 71
```

1. Pick the first and only item

If you previously fitted a circuit model in PSTrace, you can retrieve the CDC values:

```python
print(eis_data.cdc)
#> R([RT]Q)

print(eis_data.cdc_values)
#> [132.146, 11009.9, 3710.55, 3.77887, 0.971414, 6.23791e-07, 0.961612]
```

And use these to [fit a circuit model](circuit_fitting.md):

```python
model = ps.fitting.CircuitModel(cdc=eis_data.cdc)
result = model.fit(eis_data, parameters=eis_data.cdc_values)

print(result)
"""
FitResult(
    cdc='R([RT]Q)',
    parameters=[
        132.14597573482914,
        11009.960398871117,
        3710.5012402266098,
        3.780788780211564,
        0.9714238919891629,
        6.237895257571337e-07,
        0.9616123965729131,
    ],
    error=[
        1.5100310284471883,
        4.600055852184849,
        37.556727628788636,
        165.04785164182704,
        25.814541664143285,
        7.221623047995394,
        0.9499742351252066,
    ],
    chisq=0.005418877355555921,
    n_iter=5,
    exit_code='MinimumDeltaErrorTerm',
)
"""
```

The raw data can be accessed via `.dataset`. This results in a [DataSet](#dataset) object.

```python
print(eis_data.dataset)
"""
DataSet(
    [
        'Current',
        'Potential',
        'Time',
        'Frequency',
        'ZRe',
        'ZIm',
        'Z',
        'Phase',
        'Iac',
        'nPointsAC',
        'realtintac',
        'ymean',
        'debugtext',
        'YRe',
        'YIm',
        'Y',
        'Cs',
        'CsRe',
        'CsIm',
    ]
)
"""
```

Likewise, you can retrieve all the arrays:

```python
print(eis_data.arrays()[:5])
"""
[
    CurrentArray(name=Idc, unit=µA, n_points=71),
    PotentialArray(name=potential, unit=V, n_points=71),
    DataArray(name=time, unit=s, n_points=71),
    DataArray(name=Frequency, unit=Hz, n_points=71),
    DataArray(name=ZRe, unit=Ω, n_points=71),
]
"""
```

### Subscans

If an EIS dataset has subscans, this is shown in the repr:

```python
print(eis_data)
#> EISData(title=FixedPotential at 71 freqs [2], n_points=71, n_frequencies=71)

print(eis_data.has_subscans)
#> False

print(eis_data.n_subscans)
#> 0
```

Subscans can be accessed via the `.subscans()` method.

```python
print(eis_data.subscans)
#> []
```

The subscans are themselves [EISData](#eisdata) objects.

For more information, see [pypalmsens.data.EISData][].
