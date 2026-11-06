# Instrument

An [Instrument][pypalmsens.lablink.Instrument] is a reference to an instrument attached to your instance, identified by its serial number. It gives read access: info, state, configuration, capabilities, and the active measurement.

An An [InstrumentClaim][pypalmsens.lablink.InstrumentClaim] is the write side. Before an instrument can be used for a measurement you must claim it — claiming locks the instrument to your session. All control operations (`start_measurement`, `set_potential`, `configure`, `pause`/`resume`/`abort`, ...) live on the claim, not the instrument.

Use the claim as an async context manager; the instrument is released when the block exits, even if it raises:

```python
async with await instrument.claim() as claim:
    await claim.set_current_range('1 mA')
    job = await claim.start_measurement(method=method)
    measurement = await job
# claim released here
```

To claim several instruments at once, `session.claim(instruments)` returns an [InstrumentClaimBatch][pypalmsens.lablink.InstrumentClaimBatch] that releases every claim when its block exits.

::: pypalmsens.lablink.Instrument
::: pypalmsens.lablink.InstrumentClaim
::: pypalmsens.lablink.InstrumentClaimBatch
