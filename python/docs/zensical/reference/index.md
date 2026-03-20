# PyPalmSens API reference

PyPalmSens is a Python library that lets you control your PalmSens device using Python.

[pypalmsens][]

:   The most-used functions and classes are available from the root module.

    - [Data reading/writing](./io.md)
    - [Technique parameters](./methods/index.md)
    - [Instrument management](./instrument.md)
    - [Instrument management (async)](./instrument.md)

[pypalmsens.settings][]

:   Contains additional classes for method configuration (e.g. general settings, current ranges, etc).

[pypalmsens.fitting][]

:   Contains classes for equivalent circuit fitting.

[pypalmsens.data][]

:   Contains the data structures for working with measurement data.

    `PyPalmSens` will typically construct these dataclasses for you,
    either when loading a `.pssession` file or after a measurement.
    This page documents the attributes and methods available on these classes.
