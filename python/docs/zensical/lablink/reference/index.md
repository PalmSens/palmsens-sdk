# Lablink API reference

The reference for the [pypalmsens.lablink][] module: connecting to Lablink instances, claiming instruments, running measurements, and fetching data. All methods that talk to the server are async. See [the lablink introduction](../index.md) for how to get started and [concepts](../concept.md) for the object model.

## Functions

- [`discover`][pypalmsens.lablink.discover] – Discover lablink instances on the network

## Classes

- [`Instance`][pypalmsens.lablink.Instance] – Lablink instance: address plus cached metadata
- [`Session`][pypalmsens.lablink.Session] – Authenticated Lablink connection
- [`Instrument`][pypalmsens.lablink.Instrument] – Reference to an attached instrument
- [`InstrumentClaim`][pypalmsens.lablink.InstrumentClaim] – Exclusive claim on an instrument
- [`InstrumentClaimBatch`][pypalmsens.lablink.InstrumentClaimBatch] – Group of instrument claims
- [`Measurement`][pypalmsens.lablink.Measurement] – Reference to a stored measurement
- [`MeasurementJob`][pypalmsens.lablink.MeasurementJob] – Handle to an active measurement

## Exceptions

- [`LablinkApiError`][pypalmsens.lablink.LablinkApiError] – Base class for API errors
- [`NoActiveMeasurementError`][pypalmsens.lablink.NoActiveMeasurementError] – No active measurement
- [`LablinkClientError`][pypalmsens.lablink.LablinkClientError] – Client errors (4xx)
- [`LablinkServerError`][pypalmsens.lablink.LablinkServerError] – Server errors (5xx)

::: pypalmsens.lablink.discover
