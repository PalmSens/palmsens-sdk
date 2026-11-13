# Support status

PyPalmSens is compatible with Lablink 1.2.

## Method mapper status

| Method name | Mapper completed | Notes |
|---|---|---|
| ACVoltammetry | Yes | `acv` |
| ChronoAmperometry | Yes | `ca` |
| ChronoCoulometry | Yes | `cc` |
| ChronoPotentiometry | Yes | `cp` |
| CyclicVoltammetry | Yes | `cv` |
| DifferentialPulseVoltammetry | Yes | `dpv` |
| ElectrochemicalImpedanceSpectroscopy | Yes | Base `eis` ok. Time/Potential scans, and fixed frequency not implemented in C# and blocked in Lablink (`scan_type`, `frequency_type`). See Table 2 |
| FastAmperometry | Yes | `fam` |
| GalvanostaticImpedanceSpectroscopy | Yes | Base `gis` ok in C#. Time/Potential scans, and fixed frequency not implemented in C# and blocked in Lablink (`scan_type`, `frequency_type`). See Table 2 |
| LinearSweepPotentiometry | Yes | `lsp` |
| LinearSweepVoltammetry | Yes | `lsv` `lsv_aux`) |
| MethodScript | Yes | `ms` |
| MultiplePulseAmperometry | Yes | `mpad`; Probably ok. "The Command Is Unsupported", because not supported by ES4 |
| MultiStepAmperometry | Yes | `ma` |
| MultiStepPotentiometry | Yes | `mp` |
| NormalPulseVoltammetry | Yes | `npv` |
| OpenCircuitPotentiometry | Yes | `ocp` |
| PulsedAmperometricDetection | Yes | `pad` |
| SquareWaveVoltammetry | Yes | `swv` |
| StrippingChronoPotentiometry | Yes | `scp`; Lablink test fails: `potential_range` not yet supported (also not supported by ES4) |
| FastCyclicVoltammetry | No | Lablink does not support technique id `fcv`: not implemented in C# |
| FastImpedanceSpectroscopy | No | Lablink does not support technique id `fis`: not implemented in C# |
| FastGalvanostaticImpedanceSpectroscopy | No | Lablink does not support technique id `fgis`: not implemented in C# |
| MixedMode | No | Lablink does not support the `Impedance` stage. Other stages ok. |
| Corrosion methods | No | Missing |

## Not yet supported by Lablink

| Area | Missing / unsupported |
|---|---|
| Methods | [FastCyclicVoltammetry][pypalmsens.FastCyclicVoltammetry], [FastImpedanceSpectroscopy][pypalmsens.FastImpedanceSpectroscopy], [FastGalvanostaticImpedanceSpectroscopy][pypalmsens.FastGalvanostaticImpedanceSpectroscopy], [MixedMode][pypalmsens.MixedMode] (Impedance stage), Corrosion methods |
| EIS / GEIS parameters | `MaxEqTime`, scan types "Time scan" and "Potential scan", frequency type "Fixed current" |
| Settings | Multiplexer, Bipot, Save to internal storage, Triggers, Data processing, Corrosion (Materials metadata), Notes support (unconfirmed) |

## Behavioral change

Hardware sync and mains frequency have been moved out of the methods. They are now handled by the session via [InstrumentClaim.configure][pypalmsens.lablink.InstrumentClaim.configure]. Any code that read these from a method object should be updated accordingly.
