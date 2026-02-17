# Examples

The following examples are also available in the [examples directory](https://github.com/PalmSens/PalmSens_SDK/tree/main/python).

## Load and save data

This example shows how to load/save [methods][pypalmsens.load_method_file] and [measurements][pypalmsens.load_session_file], and how to [work with the the data](files.md).

```python title="load_save_data.py"
--8<-- "examples/load_save_data.py"
```

[:fontawesome-solid-download: load_save_data.py](https://raw.githubusercontent.com/PalmSens/PalmSens_SDK/refs/heads/main/python/examples/load_save_data.py){ .md-button .md-button--primary} [:fontawesome-solid-download: Demo CV DPV EIS.pssession](https://raw.githubusercontent.com/PalmSens/PalmSens_SDK/refs/heads/main/python/examples/Demo CV DPV EIS IS-C electrode.pssession){ .md-button } [:fontawesome-solid-download: LSV.psmethod](https://raw.githubusercontent.com/PalmSens/PalmSens_SDK/refs/heads/main/python/examples/PSDummyCell_LSV.psmethod){ .md-button }

## Manual control

This example shows how to [discover][pypalmsens.discover] devices, [establish a connection][pypalmsens.connect] and control an instrument manually using the [instrument manager][pypalmsens.InstrumentManager].

```python title="manual_control.py"
--8<-- "examples/manual_control.py"
```

[:fontawesome-solid-download: manual_control.py](https://raw.githubusercontent.com/PalmSens/PalmSens_SDK/refs/heads/main/python/examples/manual_control.py){ .md-button .md-button--primary}

## Manual control async

This example shows how to [discover][pypalmsens.discover] devices, [establish a connection][pypalmsens.connect] and control an instrument manually using the [asynchronous instrument manager][pypalmsens.InstrumentManagerAsync].

```python title="manual_control_async.py"
--8<-- "examples/manual_control_async.py"
```

[:fontawesome-solid-download: manual_control_async.py](https://raw.githubusercontent.com/PalmSens/PalmSens_SDK/refs/heads/main/python/examples/manual_control_async.py){ .md-button .md-button--primary}

## Measure CA

This example shows how to set up and run a [chronoamperometry][pypalmsens.ChronoAmperometry] measurement.

For more information, see [Methods](Methods.md).

```python title="measurement_CA.py"
--8<-- "examples/measurement_CA.py"
```

[:fontawesome-solid-download: measurement_CA.py](https://raw.githubusercontent.com/PalmSens/PalmSens_SDK/refs/heads/main/python/examples/measurement_CA.py){ .md-button .md-button--primary}

## Measure CA async

This example shows how to set up and run a [chronoamperometry][pypalmsens.ChronoAmperometry] measurement using the asynchronous instrument manager.

For more information, see [Methods](Methods.md).

```python title="measurement_CA_async.py"
--8<-- "examples/measurement_CA_async.py"
```

[:fontawesome-solid-download: measurement_CA_async.py](https://raw.githubusercontent.com/PalmSens/PalmSens_SDK/refs/heads/main/python/examples/measurement_CA_async.py){ .md-button .md-button--primary}

## Measure CV

This example shows how to set up and run a [cyclic voltammetry][pypalmsens.CyclicVoltammetry] measurement.

For more information, see [Methods](Methods.md).

```python title="measurement_CV.py"
--8<-- "examples/measurement_CV.py"
```

[:fontawesome-solid-download: measurement_CV.py](https://raw.githubusercontent.com/PalmSens/PalmSens_SDK/refs/heads/main/python/examples/measurement_CV.py){ .md-button .md-button--primary}

## Measure EIS

This example shows how to set up and run a [EIS measurement][pypalmsens.ElectrochemicalImpedanceSpectroscopy].

For more information, see [Methods](Methods.md).

```python title="measurement_EIS.py"
--8<-- "examples/measurement_EIS.py"
```

[:fontawesome-solid-download: measurement_EIS.py](https://raw.githubusercontent.com/PalmSens/PalmSens_SDK/refs/heads/main/python/examples/measurement_EIS.py){ .md-button .md-button--primary}

## Mixed Mode

This example shows how to set up a [Mixed Mode][pypalmsens.mixed_mode.MixedMode] measurement for a typicial charge / discharge cycle of a common Lithium battery.
Note that the example has a reduced number of cycles and maximum run time.

```python title="mixed_mode.py"
--8<-- "examples/mixed_mode.py"
```

[:fontawesome-solid-download: mixed_mode.py](https://raw.githubusercontent.com/PalmSens/PalmSens_SDK/refs/heads/main/python/examples/mixed_mode.py){ .md-button .md-button--primary}

## MethodSCRIPT sandbox

This example shows how to set up and run a [MethodSCRIPT Sandbox measurement](measuring/#methodscripttm).

For more information, see [pypalmsens.MethodScript][].

```python title="measurement_MethodSCRIPT_sandbox.py"
--8<-- "examples/measurement_MethodSCRIPT_sandbox.py"
```

[:fontawesome-solid-download: measurement_MethodSCRIPT_sandbox.py](https://raw.githubusercontent.com/PalmSens/PalmSens_SDK/refs/heads/main/python/examples/measurement_MethodSCRIPT_sandbox.py){ .md-button .md-button--primary}

## Status callback

This example shows how to set up a callback to read out the [Status][pypalmsens.data.Status] (current/potential) and store the pretreatment data using the [idle status events](measuring/#idle-status-updates).

```python title="measurement_status_callback.py"
--8<-- "examples/measurement_status_callback.py"
```

[:fontawesome-solid-download: measurement_status_callback.py](https://raw.githubusercontent.com/PalmSens/PalmSens_SDK/refs/heads/main/python/examples/measurement_status_callback.py){ .md-button .md-button--primary}

## Stream data to CSV

This example shows how to set up and run a [chronoamperometry][pypalmsens.ChronoAmperometry] measurement and write the results to a CSV file in real-time using [callbacks][pypalmsens.data.CallbackData].

```python title="measurement_stream_to_csv.py"
--8<-- "examples/measurement_stream_to_csv.py"
```

[:fontawesome-solid-download: measurement_stream_to_csv.py](https://raw.githubusercontent.com/PalmSens/PalmSens_SDK/refs/heads/main/python/examples/measurement_stream_to_csv.py){ .md-button .md-button--primary}

## SWV versus OCP

This example shows how to set up and run a [square wave voltammetry][pypalmsens.SquareWaveVoltammetry] measurement [versus OCP][pypalmsens.settings.VersusOCP].

```python title="measurement_SWV_vs_OCP.py"
--8<-- "examples/measurement_SWV_vs_OCP.py"
```

[:fontawesome-solid-download: measurement_SWV_vs_OCP.py](https://raw.githubusercontent.com/PalmSens/PalmSens_SDK/refs/heads/main/python/examples/measurement_SWV_vs_OCP.py){ .md-button .md-button--primary}

## Multiplexer

This example shows how to [set up and control a multiplexer][pypalmsens.settings.Multiplexer] and run consecutive and alternating multiplexer measurments.

```python title="multiplexer.py"
--8<-- "examples/multiplexer.py"
```

[:fontawesome-solid-download: multiplexer.py](https://raw.githubusercontent.com/PalmSens/PalmSens_SDK/refs/heads/main/python/examples/multiplexer.py){ .md-button .md-button--primary}

## Multichannel measurement   { #multichannel_basic }

This example shows how to [manage a pool of of instruments](measuring/#multichannel-measurements) and run a [chronoamperometry][pypalmsens.ChronoAmperometry] measurement on all channels simultaneously.

```python title="multichannel_measurement.py"
--8<-- "examples/multichannel_measurement.py"
```

[:fontawesome-solid-download: multichannel_measurement.py](https://raw.githubusercontent.com/PalmSens/PalmSens_SDK/refs/heads/main/python/examples/multichannel_measurement.py){ .md-button .md-button--primary}

## Multichannel CSV writer  { #multichannel_csv_writer }

This example shows how to connect to a set up a [manage a pool of of instruments](measuring/#multichannel-measurements) using [pypalmsens.InstrumentPoolAsync][], and use a custom callback to automatically store data to a csv file in parallel.

```python title="multichannel_csv_callback.py"
--8<-- "examples/multichannel_csv_callback.py"
```

[:fontawesome-solid-download: multichannel_csv_callback.py](https://raw.githubusercontent.com/PalmSens/PalmSens_SDK/refs/heads/main/python/examples/multichannel_csv_callback.py){ .md-button .md-button--primary}

## Multichannel custom loop  { #multichannel_custom_loop }

This example shows how to run and set up a sequence of measurements on a [collection of channels](measuring.md#multichannel-measurements) simultaneously.

```python title="multichannel_custom_loop.py"
--8<-- "examples/multichannel_custom_loop.py"
```

[:fontawesome-solid-download: multichannel_custom_loop.py](https://raw.githubusercontent.com/PalmSens/PalmSens_SDK/refs/heads/main/python/examples/multichannel_custom_loop.py){ .md-button .md-button--primary}

## Multichannel HW sync  { #multichannel_hw_sync }

On multi-channel devices that support it, hardware sync can be used to [synchronize measurements between multiple channels](measuring.md#multichannel-measurements).
When synchronization is enabled the follower device will wait until the main channel enables synchronisation.
After that, the follower and main will synchronize their measurement loop start and iterations.

This example shows how to connect to a [pool of instruments][pypalmsens.InstrumentPoolAsync] and run a [chronopotentiometry][pypalmsens.ChronoPotentiometry] measurement on all channels simultaneously using hardware synchronization.

For hardware synchronization, you set [`use_hardware_sync = True`][pypalmsens.settings.General.use_hardware_sync] on the method.
If you use MethodSCRIPT, use `set_channel_sync 1` in your script. PyPalmSens checks for this string to check if it is necessary to set up the main/follower channels.

In addition, your pool of instruments must contain:

* channels from a single [multi-channel instrument](https://www.palmsens.com/knowledgebase-article/multichannel-potentiostat/)
* the first (main) channel of the instrument
* at least one follower channel

All instruments are prepared and put in a waiting state.
The measurements are started via a hardware sync trigger on channel 1.
Only channel 1 (the main channel) has hardware required to trigger the other channels.

```python title="multichannel_HW_sync.py"
--8<-- "examples/multichannel_HW_sync.py"
```

[:fontawesome-solid-download: multichannel_HW_sync.py](https://raw.githubusercontent.com/PalmSens/PalmSens_SDK/refs/heads/main/python/examples/multichannel_HW_sync.py){ .md-button .md-button--primary}
