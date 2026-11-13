# Instrument

An [Instrument][pypalmsens.lablink.Instrument] is a reference to an instrument attached to your session, uniquely identified by its serial number (GUID).
[Instrument][pypalmsens.lablink.Instrument] gives read access to an instrument's metadata, status, and configuration.

To start a measurement or configure parameters, you must first claim an instrument.
An active [InstrumentClaim][pypalmsens.lablink.InstrumentClaim] locks the instrument to your session. All control operations (`start_measurement`, `set_potential`, `configure`, `pause` / `resume` / `abort`, ...) are only accessible on a claimed instrument.

You can use the claim as a context manager. The instrument is released when the block exits, even if it raises an exception:

```python
async with await instrument.claim() as claim:
    await claim.set_current_range('1 mA')
    job = await claim.start_measurement(method=method)
    measurement = await job  # claim released here
```

To claim several instruments at once, use [Session.claim][pypalmsens.lablink.Session.claim]. This returns [InstrumentClaimBatch][pypalmsens.lablink.InstrumentClaimBatch] that releases every claim when its block exits.

**Classes:**

- [`Instrument`][pypalmsens.lablink.Instrument]
- [`InstrumentClaim`][pypalmsens.lablink.InstrumentClaim]
- [`InstrumentClaimBatch`][pypalmsens.lablink.InstrumentClaimBatch]

::: pypalmsens.lablink.Instrument
::: pypalmsens.lablink.InstrumentClaim
::: pypalmsens.lablink.InstrumentClaimBatch
