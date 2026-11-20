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
| [ElectrochemicalImpedanceSpectroscopy][pypalmsens.ElectrochemicalImpedanceSpectroscopy] | **Partial** | Base `eis` ok in Lablink. Time/Potential scans, and fixed frequency not implemented in Lablink (`scan_type`, `frequency_type`). See Table 2. |
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
| [Corrosion methods](../reference/corrosion/index.md) | **No** | Missing in Lablink. |

## Not yet supported by Lablink

These features are still pending support or missing in Lablink.

| Area | Missing / unsupported |
|---|---|
| Methods | - [FastCyclicVoltammetry][pypalmsens.FastCyclicVoltammetry]<br/>- [FastImpedanceSpectroscopy][pypalmsens.FastImpedanceSpectroscopy]<br/>- [FastGalvanostaticImpedanceSpectroscopy][pypalmsens.FastGalvanostaticImpedanceSpectroscopy]<br/>- Impedance stage in [MixedMode][pypalmsens.MixedMode] (other stages ok)<br/>- Corrosion methods |
| EIS / GEIS parameters | - `MaxEqTime`<br/>- scan types "Time scan" and "Potential scan"<br/>- frequency type "Fixed current" |
| Settings | - Multiplexer<br/>- Bipot<br/>- Save to internal storage<br/>- Triggers<br/>- Data processing<br/>- Corrosion (Materials metadata)<br/>- Notes support (unconfirmed) |

## Behaviour changes

### Mains frequency

Lablink does not support the setting the [mains/power frequency][pypalmsens.settings.General.power_frequency] on the method. Setting the mains frequency is now handled by the session via [InstrumentClaim.configure][pypalmsens.lablink.InstrumentClaim.configure].

## Lablink API endpoints

Base route: `api/v1`. `Internal` / `Stable` / `Python` track implementation status.

**Total: 67 endpoints.** All endpoints except `Auth` and `Home` require a JWT bearer token.

### Auth

Path: `/Auth` (anonymous)

| Method | Path | Action | Internal | Python |
|---|---|---|---|---|
| POST | `/Auth/Register` | `Register` |  | ✓ |
| POST | `/Auth/ApiKey`   | `ApiKey` |  | ✓ |

### Home

Path: `/Home` (anonymous)

| Method | Path | Action | Internal | Python |
|---|---|---|---|---|
| GET | `/Home/GetInfo` | `GetInfo` |  | ✓ |
| GET | `/Home/GetConnectionType` | `GetConnectionType` | ✓ | n/a |
| GET | `/Home/DiscoverLablinkList` | `DiscoverLablinkList` | ✓ | n/a |

### DataSets

Path: /DataSets

| Method | Path | Action | Internal | Python |
|---|---|---|---|---|
| GET | `/DataSets/{dataSetId:guid}/{dataValuesId:guid}` | `GetDataValues` (`FileStreamResult`, range processing enabled) |  | wip |

### Instruments

Path: `/Instruments`

| Method | Path | Action | Internal | Python |
|---|---|---|---|---|
| GET | `/Instruments` | `Get` (all instruments) |  | ✓ |
| POST | `/Instruments/State` | `GetInstrumentState` |  | todo |
| POST | `/Instruments/Claim` | `Claim` |  | ✓ |
| POST | `/Instruments/ManualClaim` | `ForceClaim` |  | ✓ |
| POST | `/Instruments/Unclaim` | `Unclaim` |  | ✓ |
| POST | `/Instruments/StartMeasurement` | `Start` |  | ✓ |
| POST | `/Instruments/SkipPreMeasurementStage` | `SkipPreMeasurementStage` |  | ✓ |
| POST | `/Instruments/PauseMeasurement` | `Pause` |  | ✓ |
| POST | `/Instruments/ResumeMeasurement` | `Resume` |  | ✓ |
| POST | `/Instruments/AbortMeasurement` | `Abort` |  | ✓ |
| POST | `/Instruments/SetCustomName` | `SetCustomName` | ✓ | remove |
| POST | `/Instruments/ConfigureInstrument` | `ConfigureInstrument` |  | ✓ |
| POST | `/Instruments/SendWorkflow` | `SendWorkflow` |  | later (workflows) |
| POST | `/Instruments/Configuration` | `GetConfiguration` |  | todo |
| POST | `/Instruments/Instrument2Configuration` | `GetInstrument2Configuration` | ✓ | n/a |

### Instrument

Path: `/Instrument` (single instrument)

| Method | Path | Action | Internal | Python |
|---|---|---|---|---|
| GET | `/Instrument/{serial}/GetSignalRUrl` | `GetSignalRUrl` | ✓ | n/a |
| GET | `/Instrument/{serial}/Capabilities` | `GetCapabilities` | ✓ | n/a |
| GET | `/Instrument/{serial}/Configuration` | `GetConfiguration` |  | todo |
| GET | `/Instrument/{serial}/Instrument2Configuration` | `GetInstrument2Configuration` | ✓ | n/a |
| GET | `/Instrument/{serial}/CurrentMeasurement` | `CurrentMeasurement` |  | ✓ |
| GET | `/Instrument/{serial}/State` | `GetInstrumentState` |  | later |
| POST | `/Instrument/{serial}/Claim` | `Claim` |  | ✓ |
| POST | `/Instrument/{serial}/ManualClaim` | `ManualClaim` |  | ✓ |
| POST | `/Instrument/{serial}/Unclaim` | `Unclaim` |  | ✓ |
| POST | `/Instrument/{serial}/SetCellMode` | `SetCellMode` |  | ✓ |
| POST | `/Instrument/{serial}/SetCellState` | `SetCellSate` (sic in code) |  | ✓ |
| POST | `/Instrument/{serial}/StartMeasurement` | `StartMeasurement` |  | ✓ |
| POST | `/Instrument/{serial}/SkipPreMeasurementStage` | `SkipPretreatment` |  | ✓ |
| POST | `/Instrument/{serial}/PauseMeasurement` | `Pause` |  | ✓ |
| POST | `/Instrument/{serial}/ResumeMeasurement` | `Resume` |  | ✓ |
| POST | `/Instrument/{serial}/AbortMeasurement` | `Abort` |  | ✓ |
| POST | `/Instrument/{serial}/SetCustomName` | `SetCustomName` |  | ✓ |
| POST | `/Instrument/{serial}/ConfigureInstrument` | `ConfigureInstrument` |  | ✓ |
| POST | `/Instrument/{serial}/SendWorkflow` | `SendScript` |  | later (workflows) |
| GET | `/Instrument/{serial}/CurrentWorkflow` | `CurrentWorkflow` |  | later (workflows) |

### Instrument

Path: `/Instrument` (manual control)

| Method | Path | Action | Internal | Python |
|---|---|---|---|---|
| POST | `/Instrument/{serial}/SetCurrentRange` | `SetCurrentRangeAsync` |  | ✓ |
| POST | `/Instrument/{serial}/SetPotentialRange` | `SetPotentialRangeAsync` |  | ✓ |
| POST | `/Instrument/{serial}/SetCurrent` | `SetCurrentAsync` |  | ✓ |
| POST | `/Instrument/{serial}/SetPotential` | `SetPotentialAsync` |  | ✓ |
| POST | `/Instrument/{serial}/SetBiPotState` | `SetBiPotStateAsync` |  | ✓ |
| POST | `/Instrument/{serial}/SetBiPotCurrentRange` | `SetBiPotCurrentRangeAsync` |  | ✓ |
| POST | `/Instrument/{serial}/SetBiPotMode` | `SetBiPotModeAsync` |  | ✓ |
| POST | `/Instrument/{serial}/SetBiPotPotential` | `SetBiPotPotentialAsync` |  | ✓ |

### Measurements

Path: /Measurements

| Method | Path | Action | Internal | Python |
|---|---|---|---|---|
| GET | `/Measurements` | `Get` (list) |  | ✓ |
| GET | `/Measurements/{id:guid}` | `Get` (single) |  | ✓ |
| POST | `/Measurements/Upload/Start` | `StartMeasurementUpload` | ✓ | n/a |
| POST | `/Measurements/{measurementId:guid}/Upload/{dataValuesId:guid}` | `UploadDataValuesStream` (raw body stream, no form binding) | ✓ | n/a |
| POST | `/Measurements/{measurementId:guid}/Upload/Finish` | `FinishMeasurementUpload` | ✓ | n/a |
| POST | `/Measurements/{measurementId:guid}/Upload/Abort` | `AbortMeasurementUpload` | ✓ | n/a |
| DELETE | `/Measurements/{measurementId:guid}/Delete` | `DeleteMeasurement` |  | ✓ |
| DELETE | `/Measurements/BatchDelete` | `DeleteMultipleMeasurements` (JSON body of GUIDs) |  | ✓ |

### Methods

Path: `/Methods`

| Method | Path | Action | Internal | Python |
|---|---|---|---|---|
| GET | `/Methods` | `Get` (list) |  | not planned |
| GET | `/Methods/{id}` | `Get` (single) |  | not planned |
| POST | `/Methods/Upload` | `Upload` |  | not planned |
| DELETE | `/Methods/{id}` | `Delete` |  | not planned |
| DELETE | `/Methods` | `DeleteMultiple` (JSON body of GUIDs) |  | not planned |

### Update

Path: /Update

| Method | Path | Action | Internal | Python |
|---|---|---|---|---|
| POST | `/Update/ApplyUpdatePackage` | `ApplyUpdatePackage` (`IFormFile`, 2 GB body limit, 10 min timeout) | ✓ | n/a |

### Users

Path: `/Users`

| Method | Path | Action | Internal | Python |
|---|---|---|---|---|
| GET | `/Users` | `Get` |  | ✓ |
| DELETE | `/Users/{userId}` | `Delete` |  | ✓ |

### Workflows

Path: /Workflows

| Method | Path | Action | Internal | Python |
|---|---|---|---|---|
| POST | `/Workflows/Start` | `StartWorkflows` |  | later (workflows) |
| POST | `/Workflows/{serial}/Abort` | `AbortWorkflow` |  | later (workflows) |
