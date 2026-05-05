# Techniques

This section contains a listing of all available techniques in PyPalmSens.

For example to set up a [CV][pypalmsens.CyclicVoltammetry] experiment:

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

## Classes

- [`pypalmsens.CyclicVoltammetry`][pypalmsens.CyclicVoltammetry]
- [`pypalmsens.SquareWaveVoltammetry`][pypalmsens.SquareWaveVoltammetry]
- [`pypalmsens.LinearSweepVoltammetry`][pypalmsens.LinearSweepVoltammetry]
- [`pypalmsens.FastCyclicVoltammetry`][pypalmsens.FastCyclicVoltammetry]
- [`pypalmsens.ACVoltammetry`][pypalmsens.ACVoltammetry]
- [`pypalmsens.DifferentialPulseVoltammetry`][pypalmsens.DifferentialPulseVoltammetry]
- [`pypalmsens.NormalPulseVoltammetry`][pypalmsens.NormalPulseVoltammetry]
- [`pypalmsens.ChronoAmperometry`][pypalmsens.ChronoAmperometry]
- [`pypalmsens.MultiStepAmperometry`][pypalmsens.MultiStepAmperometry]
- [`pypalmsens.FastAmperometry`][pypalmsens.FastAmperometry]
- [`pypalmsens.PulsedAmperometricDetection`][pypalmsens.PulsedAmperometricDetection]
- [`pypalmsens.MultiplePulseAmperometry`][pypalmsens.MultiplePulseAmperometry]
- [`pypalmsens.OpenCircuitPotentiometry`][pypalmsens.OpenCircuitPotentiometry]
- [`pypalmsens.ChronoPotentiometry`][pypalmsens.ChronoPotentiometry]
- [`pypalmsens.LinearSweepPotentiometry`][pypalmsens.LinearSweepPotentiometry]
- [`pypalmsens.MultiStepPotentiometry`][pypalmsens.MultiStepPotentiometry]
- [`pypalmsens.StrippingChronoPotentiometry`][pypalmsens.StrippingChronoPotentiometry]
- [`pypalmsens.ChronoCoulometry`][pypalmsens.ChronoCoulometry]
- [`pypalmsens.ElectrochemicalImpedanceSpectroscopy`][pypalmsens.ElectrochemicalImpedanceSpectroscopy]
- [`pypalmsens.FastImpedanceSpectroscopy`][pypalmsens.FastImpedanceSpectroscopy]
- [`pypalmsens.GalvanostaticImpedanceSpectroscopy`][pypalmsens.GalvanostaticImpedanceSpectroscopy]
- [`pypalmsens.FastGalvanostaticImpedanceSpectroscopy`][pypalmsens.FastGalvanostaticImpedanceSpectroscopy]
- [`pypalmsens.MixedMode`][pypalmsens.MixedMode] ([`ConstantE`][pypalmsens.stages.ConstantE] | [`ConstantI`][pypalmsens.stages.ConstantI] | [`Impedance`][pypalmsens.stages.Impedance] | [`OpenCircuit`][pypalmsens.stages.OpenCircuit] | [`SweepE`][pypalmsens.stages.SweepE])
- [`pypalmsens.MethodScript`][pypalmsens.MethodScript]
