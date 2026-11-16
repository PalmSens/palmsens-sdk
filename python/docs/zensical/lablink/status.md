# Support status

The latest version of PyPalmSens supports Lablink version 1.2.

This page documents what is currently supported.

## Method mapper status

This table documents the status of the method mappers.
This layer translates PyPalmSens methods to serialization format that Lablink expects. Note that some methods are not yet (fully) implemented on the Lablink side.

| Method | Mapper completed | Notes |
|---|---|---|
| [ACVoltammetry][pypalmsens.ACVoltammetry] | Yes | `acv` |
| [ChronoAmperometry][pypalmsens.ChronoAmperometry] | Yes | `ca` |
| [ChronoCoulometry][pypalmsens.ChronoCoulometry] | Yes | `cc` |
| [ChronoPotentiometry][pypalmsens.ChronoPotentiometry] | Yes | `cp` |
| [CyclicVoltammetry][pypalmsens.CyclicVoltammetry] | Yes | `cv` |
| [DifferentialPulseVoltammetry][pypalmsens.DifferentialPulseVoltammetry] | Yes | `dpv` |
| [ElectrochemicalImpedanceSpectroscopy][pypalmsens.ElectrochemicalImpedanceSpectroscopy] | **Partial** | Base `eis` ok in Lablink. Time/Potential scans, and fixed frequency not implemented in Lablink (`scan_type`, `frequency_type`). See Table 2. See Table 2. |
| [FastAmperometry][pypalmsens.FastAmperometry] | Yes | `fam` |
| [GalvanostaticImpedanceSpectroscopy][pypalmsens.GalvanostaticImpedanceSpectroscopy] | **Partial** | Base `gis` ok in Lablink. Time/Potential scans, and fixed frequency not implemented in Lablink (`scan_type`, `frequency_type`). See Table 2. |
| [LinearSweepPotentiometry][pypalmsens.LinearSweepPotentiometry] | Yes | `lsp` |
| [LinearSweepVoltammetry][pypalmsens.LinearSweepVoltammetry] | Yes | `lsv` `lsv_aux` |
| [MethodScript][pypalmsens.MethodScript] | Yes | `ms` |
| [MultiplePulseAmperometry][pypalmsens.MultiplePulseAmperometry] | Yes | `mpad`. Untested, maybe ok. Gives "The Command Is Unsupported", because it is not supported by ES4 |
| [MultiStepAmperometry][pypalmsens.MultiStepAmperometry] | Yes | `ma` |
| [MultiStepPotentiometry][pypalmsens.MultiStepPotentiometry] | Yes | `mp` |
| [NormalPulseVoltammetry][pypalmsens.NormalPulseVoltammetry] | Yes | `npv` |
| [OpenCircuitPotentiometry][pypalmsens.OpenCircuitPotentiometry] | Yes | `ocp` |
| [PulsedAmperometricDetection][pypalmsens.PulsedAmperometricDetection] | Yes | `pad` |
| [SquareWaveVoltammetry][pypalmsens.SquareWaveVoltammetry] | Yes | `swv` |
| [StrippingChronoPotentiometry][pypalmsens.StrippingChronoPotentiometry] | **Partial** | `scp`. `potential_range` not yet supported by Lablink. Untested, because `scp` is not supported by ES4 |
| [FastCyclicVoltammetry][pypalmsens.FastCyclicVoltammetry] | **No** | Lablink does not yet support this method. |
| [FastImpedanceSpectroscopy][pypalmsens.FastImpedanceSpectroscopy] | **No** | Lablink does not yet support this method. |
| [FastGalvanostaticImpedanceSpectroscopy][pypalmsens.FastGalvanostaticImpedanceSpectroscopy] | **No** | Lablink does not yet support this method. |
| [MixedMode][pypalmsens.MixedMode] | **Partial** | Lablink does not yet support the `Impedance` stage. Other stages ok. |
| [Corrosion methods](../reference/corrosion.md) | **No** | Missing in Lablink. |

## Not yet supported by Lablink

These features are still pending support or missing in Lablink.

| Area | Missing / unsupported |
|---|---|
| Methods | - [FastCyclicVoltammetry][pypalmsens.FastCyclicVoltammetry]<br/>- [FastImpedanceSpectroscopy][pypalmsens.FastImpedanceSpectroscopy]<br/>- [FastGalvanostaticImpedanceSpectroscopy][pypalmsens.FastGalvanostaticImpedanceSpectroscopy]<br/>- [MixedMode][pypalmsens.MixedMode] (Impedance stage)<br/>- Corrosion methods |
| EIS / GEIS parameters | - `MaxEqTime`<br/>- scan types "Time scan" and "Potential scan"<br/>- frequency type "Fixed current" |
| Settings | - Multiplexer<br/>- Bipot<br/>- Save to internal storage<br/>- Triggers<br/>- Data processing<br/>- Corrosion (Materials metadata)<br/>- Notes support (unconfirmed) |

## Behavioral change

[Hardware sync][pypalmsens.settings.General.use_hardware_sync] and [mains/power frequency][pypalmsens.settings.General.power_frequency] have been moved out of the method settings. They are now handled by the session via [InstrumentClaim.configure][pypalmsens.lablink.InstrumentClaim.configure]. Any code that read these from a method object should be updated accordingly.
