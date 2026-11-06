# Lablink API reference

The reference for the [pypalmsens.lablink][] module: connecting to Lablink instances, claiming instruments, running measurements, and fetching data. Everything that talks to the server is async. See [the lablink introduction](../index.md) for a walkthrough and [concepts](../concept.md) for the object model.

## Classes

- [Instance][pypalmsens.lablink.Instance] — a Lablink server: its address plus cached metadata
- [Session][pypalmsens.lablink.Session] — an authenticated connection; the root object
- [Instrument][pypalmsens.lablink.Instrument] — a reference to an attached instrument
- [InstrumentClaim][pypalmsens.lablink.InstrumentClaim] — an exclusive lease on an instrument
- [InstrumentClaimBatch][pypalmsens.lablink.InstrumentClaimBatch] — a group of claims that release together
- [Measurement][pypalmsens.lablink.Measurement] — a reference to a stored measurement
- [MeasurementJob][pypalmsens.lablink.MeasurementJob] — a handle to a running measurement

## Exceptions

- [LablinkApiError][pypalmsens.lablink.LablinkApiError] — base class for API errors
- [NoActiveMeasurementError][pypalmsens.lablink.NoActiveMeasurementError] — conflict: no active measurement
- [LablinkClientError][pypalmsens.lablink.LablinkClientError] — 4xx errors
- [LablinkServerError][pypalmsens.lablink.LablinkServerError] — 5xx errors

## Functions

### discover

::: pypalmsens.lablink.discover
