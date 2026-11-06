# Techniques

This section contains a listing of all available techniques in PyPalmSens.

For example to set up a [CV][pypalmsens.CyclicVoltammetry] experiment:

```python
import pypalmsens as ps

method = ps.CyclicVoltammetry(
    begin_potential = -1,
    vertex1_potential = -1,
    vertex2_potential = 1,
    step_potential = 0.25,
    scanrate = 5,
    n_scans = 2,
    current_range = {
        'max': '1mA',
        'min': '100nA',
        'start': '100uA',
    },
)
```

!!! note "Shared settings"

    Many configuration settings are shared between methods, like the current ranges above
    or _versus OCP_ or _trigger_ settings. These are listed in [Settings](settings.md).

## Classes

### Voltammetric

- [`pypalmsens.ACVoltammetry`][pypalmsens.ACVoltammetry]
- [`pypalmsens.CyclicVoltammetry`][pypalmsens.CyclicVoltammetry]
- [`pypalmsens.FastCyclicVoltammetry`][pypalmsens.FastCyclicVoltammetry]
- [`pypalmsens.LinearSweepVoltammetry`][pypalmsens.LinearSweepVoltammetry]

### Pulsed

- [`pypalmsens.DifferentialPulseVoltammetry`][pypalmsens.DifferentialPulseVoltammetry]
- [`pypalmsens.NormalPulseVoltammetry`][pypalmsens.NormalPulseVoltammetry]
- [`pypalmsens.SquareWaveVoltammetry`][pypalmsens.SquareWaveVoltammetry]

### Amperometric

- [`pypalmsens.ChronoAmperometry`][pypalmsens.ChronoAmperometry]
- [`pypalmsens.FastAmperometry`][pypalmsens.FastAmperometry]
- [`pypalmsens.MultiStepAmperometry`][pypalmsens.MultiStepAmperometry]
- [`pypalmsens.MultiplePulseAmperometry`][pypalmsens.MultiplePulseAmperometry]
- [`pypalmsens.PulsedAmperometricDetection`][pypalmsens.PulsedAmperometricDetection]

### Potentiometric

- [`pypalmsens.ChronoPotentiometry`][pypalmsens.ChronoPotentiometry]
- [`pypalmsens.LinearSweepPotentiometry`][pypalmsens.LinearSweepPotentiometry]
- [`pypalmsens.MultiStepPotentiometry`][pypalmsens.MultiStepPotentiometry]
- [`pypalmsens.OpenCircuitPotentiometry`][pypalmsens.OpenCircuitPotentiometry]
- [`pypalmsens.StrippingChronoPotentiometry`][pypalmsens.StrippingChronoPotentiometry]

### Impedance

- [`pypalmsens.ElectrochemicalImpedanceSpectroscopy`][pypalmsens.ElectrochemicalImpedanceSpectroscopy]
- [`pypalmsens.FastImpedanceSpectroscopy`][pypalmsens.FastImpedanceSpectroscopy]
- [`pypalmsens.GalvanostaticImpedanceSpectroscopy`][pypalmsens.GalvanostaticImpedanceSpectroscopy]
- [`pypalmsens.FastGalvanostaticImpedanceSpectroscopy`][pypalmsens.FastGalvanostaticImpedanceSpectroscopy]

### Other

- [`pypalmsens.ChronoCoulometry`][pypalmsens.ChronoCoulometry]
- [`pypalmsens.MethodScript`][pypalmsens.MethodScript]
- [`pypalmsens.MixedMode`][pypalmsens.MixedMode] ([`ConstantE`][pypalmsens.stages.ConstantE] | [`ConstantI`][pypalmsens.stages.ConstantI] | [`Impedance`][pypalmsens.stages.Impedance] | [`OpenCircuit`][pypalmsens.stages.OpenCircuit] | [`SweepE`][pypalmsens.stages.SweepE])

## Settings

- [`pypalmsens.settings.BiPot`][pypalmsens.settings.BiPot]
- [`pypalmsens.settings.ChargeLimits`][pypalmsens.settings.ChargeLimits]
- [`pypalmsens.settings.CurrentLimits`][pypalmsens.settings.CurrentLimits]
- [`pypalmsens.settings.CurrentRange`][pypalmsens.settings.CurrentRange]
- [`pypalmsens.settings.DataProcessing`][pypalmsens.settings.DataProcessing]
- [`pypalmsens.settings.ELevel`][pypalmsens.settings.ELevel]
- [`pypalmsens.settings.EquilibrationTriggers`][pypalmsens.settings.EquilibrationTriggers]
- [`pypalmsens.settings.General`][pypalmsens.settings.General]
- [`pypalmsens.settings.ILevel`][pypalmsens.settings.ILevel]
- [`pypalmsens.settings.IrDropCompensation`][pypalmsens.settings.IrDropCompensation]
- [`pypalmsens.settings.Material`][pypalmsens.settings.Material]
- [`pypalmsens.settings.MeasurementTriggers`][pypalmsens.settings.MeasurementTriggers]
- [`pypalmsens.settings.Multiplexer`][pypalmsens.settings.Multiplexer]
- [`pypalmsens.settings.PostMeasurement`][pypalmsens.settings.PostMeasurement]
- [`pypalmsens.settings.PotentialLimits`][pypalmsens.settings.PotentialLimits]
- [`pypalmsens.settings.PotentialRange`][pypalmsens.settings.PotentialRange]
- [`pypalmsens.settings.Pretreatment`][pypalmsens.settings.Pretreatment]
- [`pypalmsens.settings.VersusOCP`][pypalmsens.settings.VersusOCP]
