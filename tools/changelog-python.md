PyPalmSens python-1.9.0 is now available on PyPi.

To upgrade: `pip install pypalmsens -U`.

For more information, see: https://dev.palmsens.com/python/latest/_attachments/releases/#pypalmsens-python-190

## Corrosion methods

This release adds support for corrosion methods to PyPalmSens. This is mostly a compatibilitey update, so that corrosion data can be read into PyPalmSens. Functionally these methods are exactly the same as the corresponding regular classes. See the [documentation](https://dev.palmsens.com/python/latest/_attachments/reference/corrosion/) for more information.

- `pypalmsens.corrosion.CorrosionPotential`
- `pypalmsens.corrosion.CyclicPolarization`
- `pypalmsens.corrosion.Galvanostatic`
- `pypalmsens.corrosion.LinearPolarization`
- `pypalmsens.corrosion.Potentiostatic`
- `pypalmsens.corrosion.ElectrochemicalImpedanceSpectroscopy`

## Capabilities

You can now retrieve instrument capabilities using [`InstrumentManager.capabilities`](https://dev.palmsens.com/python/latest/_attachments/reference/instrument/#pypalmsens.InstrumentManager.capabilities).
This provides information on device features, firmware versions, supported current and potential ranges, and other information.

```python
>>> import pypalmsens as ps

>>> with ps.connect() as manager:
...     capabilities = manager.capabilities

>>> capabilities
Capabilities(device_type='EmStat4LR', firmware_version=1.5, ...)
```

## Estimated duration

Get the estimated measurement duration using [`InstrumentManager.get_estimated_duration()`](https://dev.palmsens.com/python/latest/_attachments/reference/instrument/#pypalmsens.InstrumentManager.get_estimated_duration):

```python
>>> import pypalmsens as ps

>>> method = ps.CyclicVoltammetry()

>>> with ps.connect() as manager:
...     print(manager.get_estimated_duration(method))
2.099
```

## Mixed Mode API changes

This release makes a few changes to the API for Mixed Mode.

- `pypalmsens.mixed_mode.MixedMode` is available from the root level (`pypalmsens.MixedMode`) for consistency with other techniques. Stages are available from `pypalmsens.stages`.

```python
import pypalmsens as ps
# old
ps.mixed_mode.MixedMode(stages=[ps.mixed_mode.ConstantE()])
# new
ps.MixedMode(stages=[ps.stages.ConstantE()])
```

See https://dev.palmsens.com/python/latest/_attachments/reference/methods/mixed_mode/

The old paths now emit `DeprecationWarnings`. They will be removed in a later version.

## What's changed

- Add wrappers for corrosion methods ([#341](https://github.com/PalmSens/PalmSens_SDK/pull/341))
- Move `get_estimated_duration` to instrument manager ([#342](https://github.com/PalmSens/PalmSens_SDK/pull/342))
- Add support for capabilities ([#346](https://github.com/PalmSens/PalmSens_SDK/pull/346))
- Work around page validation warnings in zensical 0.0.38 ([#348](https://github.com/PalmSens/PalmSens_SDK/pull/348))
- Add requirements.txt to docs directory ([#350](https://github.com/PalmSens/PalmSens_SDK/pull/350))
- Use EILevel for MSP methods ([#351](https://github.com/PalmSens/PalmSens_SDK/pull/351))
- Add paragraph about saving for previous versions in LabVIEW ([#352](https://github.com/PalmSens/PalmSens_SDK/pull/352))
- Min sampling time must be greater than 0 for Impedance ([#354](https://github.com/PalmSens/PalmSens_SDK/pull/354))
- Add __getitem__ and __contains__ magic methods to pool ([#355](https://github.com/PalmSens/PalmSens_SDK/pull/355))
- Move converters and types to root module ([#356](https://github.com/PalmSens/PalmSens_SDK/pull/356))
- Update user API (types and mixed mode) ([#357](https://github.com/PalmSens/PalmSens_SDK/pull/357))
- Update mixed mode method listing ([#360](https://github.com/PalmSens/PalmSens_SDK/pull/360))
- Add `status()` method for `IntrumentPool` ([#361](https://github.com/PalmSens/PalmSens_SDK/pull/361))
- Update matlab documentation with class and function reference ([#362](https://github.com/PalmSens/PalmSens_SDK/pull/362))
- Update release script ([#363](https://github.com/PalmSens/PalmSens_SDK/pull/363))
- Minor fixes in release script ([#364](https://github.com/PalmSens/PalmSens_SDK/pull/364))
- Minor fix in release script ([#365](https://github.com/PalmSens/PalmSens_SDK/pull/365))

**Full Changelog**: https://github.com/PalmSens/PalmSens_SDK/compare/python-1.8.1...python-1.9.0
