# Corrosion techniques

This section contains a listing of all available corrosion techniques in PyPalmSens.

The techniques below are identical to the other [electrochemistry techniques](../methods/), they generate the same signal and adhere to the same specifications. The only difference is that these expose additional material metadata.

- [Potentiostatic][pypalmsens.corrosion.Potentiostatic] (constant potential)
- [Galvanostatic][pypalmsens.corrosion.Galvanostatic] (constant current)
- [Linear Polarization][pypalmsens.corrosion.LinearPolarization] (potential sweep)
- [Cyclic Polarization][pypalmsens.corrosion.CyclicPolarization] (bi-directional potential sweep)
- [Corrosion Potential][pypalmsens.corrosion.CorrosionPotential] (OCP)
- [Impedance Spectroscopy][pypalmsens.corrosion.ImpedanceSpectroscopy]

For example to set up a CP experiment:

```python
>>> import pypalmsens as ps

>>> method = ps.CyclicPolarization(
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
...     material = {
...         'surface_area' = 0.5,
...         'density' = 30.0,
...         'weight' = 20.0,
...     }
... )
```

!!! note "Shared settings"

    Many configuration settings are shared between methods, like the current ranges above
    or _versus OCP_ or _material_ settings. These are listed in [Settings](../methods/settings.md).
