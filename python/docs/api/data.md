# Data

The main entry point for the data is the `Measurement` class. These
can be loaded from a .pssession file or directly returned as a result
from an expirement.

These classes are wrappers for the underlying .NET code. Each Python
wrapper in this module holds a reference to the underlying .NET SDK
object, usually prefixed `ps...` like `Measurement.psmeasurement`.
These .NET classes are instantiated by the measurement or data loading
code. These wrappers are intended to be used for data processing and
exploration and not to be directly instantiated.

The raw data is stored in a `DataSet` under `Measurement.dataset`. A
_dataset_ in turn consist of a series of `DataArray`'`s. These would
be analogous to the ’Data`' tab in the PSTrace software. A _data array_
would be the equivalent of a column, with a title, array type, and
units.

The `Curve` objects (retrieved via `Measurement.curves`) are
interpretations of the data, much like the plots in the PSTrace
software. These can be used for plots or data processing like smoothing
the data and peak finding.

::: pypalmsens.data
