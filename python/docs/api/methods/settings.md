# Settings

This page lists the shared settings for the techniques.

There are two ways to adjust these settings, either via the method constructor.

For example, adjusting the post measurement settings:

```python
import pypalmsens as ps

cv = ps.LinearSweepVoltammetry(
    ...,
    post_measurement = {
        'cell_on_after_measurement': True,
        'standby_potential': 0.5,
        'standby_time': 30,
    } # <1>
)
```
<1> Note that you can either pass a dictionary or the assosiated `ps.settings.PostMeasurement` class.

Or by setting the values on the attribute:

```python
lsv = ps.LinearSweepVoltammetry()

lsv.post_measurement.cell_on_after_measurement = True
lsv.post_measurement.standby_potential = 0.5
lsv.post_measurement.standby_time = 30
```

See the technique reference pages to see which settings are supported.

::: pypalmsens.settings.CurrentRange
::: pypalmsens.settings.PotentialRange
::: pypalmsens.settings.Pretreatment
::: pypalmsens.settings.VersusOCP
::: pypalmsens.settings.BiPot
::: pypalmsens.settings.ELevel
::: pypalmsens.settings.ILevel
::: pypalmsens.settings.PostMeasurement
::: pypalmsens.settings.CurrentLimits
::: pypalmsens.settings.PotentialLimits
::: pypalmsens.settings.ChargeLimits
::: pypalmsens.settings.IrDropCompensation
::: pypalmsens.settings.EquilibrationTriggers
::: pypalmsens.settings.MeasurementTriggers
::: pypalmsens.settings.Multiplexer
::: pypalmsens.settings.DataProcessing
::: pypalmsens.settings.General
