# Techniques

This section contains a listing of all available techniques in PyPalmSens.

For example to set up a CV experiment:

```python
>>> import pypalmsens as ps

>>> method = ps.CyclicVoltammetry(
...     begin_potential = -1,
...     vertex1_potential = -1,
...     vertex2_potential = 1,
...     step_potential = 0.25,
...     scanrate = 5,
...     n_scans = 2,
...     current_range = {
...         'max': '1mA',
...         'min': '100nA',
...         'start': '100uA',
...     },
... )
```

!!! note "Shared settings"

    Many configuration settings are shared between methods, like the current ranges above
    or _versus OCP_ or _trigger_ settings. These are listed in [Settings](./settings.md).
