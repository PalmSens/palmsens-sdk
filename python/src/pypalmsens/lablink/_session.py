"""Submodule for managing sessions on a Lablink instance.

Use [Session][] for an authenticated connection to a Lablink
instance. Use [InstrumentClaimBatch][] to group several instrument claims so
they can be released together.

"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Self

import pandas as pd
import xarray as xr

from ..types import MethodTypeCompatible
from ._client import HttpClient
from ._instrument import Instrument, InstrumentClaim, InstrumentClaimBatch
from ._measurement import Measurement, MeasurementJob
from .models import LablinkInfo
from .models._method_mapper import to_payload
from .models._public import UserInfo
from .models._wire import (
    EmptyProperty,
    MeasurementListResult,
    MeasurementResult,
    SendWorkflowCommand,
    SimpleInstrumentsCommand,
)


class Session:
    """
    A session managing a connection to a Lablink instance.

    Use [Session.list_instruments][] to list instruments,
    [Session.claim][] to claim them, and
    [Session.start_measurement][] to run measurements.

    Parameters
    ----------
    host : str
        Base URL of the Lablink instance (e.g. 'lablink.example.com').
    token : str
        Token used to authenticate API calls.
    port : int, optional
        Port for the API server, defaults to 5000.
    """

    def __init__(
        self,
        host: str,
        token: str,
        port: int = 5000,
    ):
        self._init(HttpClient(f'{host}:{port}/api/v1', token=token))

    @classmethod
    def _from_http(cls, http: HttpClient) -> Self:
        obj = cls.__new__(cls)
        obj._init(http)
        return obj

    def _init(self, http: HttpClient) -> None:
        self._http = http
        self._info: LablinkInfo | None = None
        self._instruments: list[Instrument] = []
        self._instrument_info: dict[str, dict[str, Any]] = {}

    def __repr__(self) -> str:
        return f'{type(self).__name__}(host={self._http._client.base_url.host!r}, port={self._http._client.base_url.port})'

    @property
    def info(self) -> LablinkInfo | None:
        """Last fetched metadata, or `None` if not yet fetched.

        Use [get_info][] to (re)populate this.
        """
        return self._info

    async def get_info(self) -> LablinkInfo:
        """Fetch metadata for this instance."""
        data = await self._http.get('/Home/GetInfo')
        self._info = LablinkInfo.from_wire(data.json())
        return self._info

    @property
    def instrument_info(self) -> dict[str, dict[str, Any]]:
        """The instrument info from the most recent [get_instrument_info][] call.

        May be stale or empty. Use [list_instruments][] or
        [get_instrument_info][] to update the cache.
        """
        return self._instrument_info

    @property
    def instruments(self) -> list[Instrument]:
        """The instruments from the most recent [list_instruments][] call.

        May be stale or empty. Use [list_instruments][] or
        [get_instrument_info][] update the cache.
        """
        return self._instruments

    async def _get_instruments(self):
        """Helper function to get instrument data and populate caches."""
        data = await self._http.get('/Instruments')
        self._instrument_info = {info['Serial']['Serial']: info for info in data.json()}
        self._instruments = [
            Instrument(serial=serial, session=self) for serial in self._instrument_info
        ]

    async def get_instrument_info(self) -> dict[str, dict[str, Any]]:
        """Get info dictionary for currently attached instruments.

        Refreshes the [instrument_info][] dictionary and caches it in-place.

        Returns
        -------
        dict[str, dict[str, Any]]
            A mapping from serial number to instrument info for each currently
            attached instrument.
        """
        await self._get_instruments()
        return self._instrument_info

    async def list_instruments(self) -> list[Instrument]:
        """List currently attached instruments.

        Refreshes the [instruments][] list.

        Returns
        -------
        list of Instrument
            A list of currently attached instruments.
        """
        await self._get_instruments()
        return self._instruments

    async def claim(
        self, instruments: Sequence[Instrument], *, auto_release: bool = False
    ) -> InstrumentClaimBatch:
        """Claim multiple instruments.

        The claim is held until you release it, or until the enclosing
        `async with` block exits.

        Parameters
        ----------
        instruments : Sequence[Instrument]
            The instruments to claim.
        auto_release : bool, optional
            If True, the server releases the claims after measurement ends.

        Returns
        -------
        claims : ClaimBatch
            A batch containing the instrument claims.
        """
        method = 'Claim' if auto_release else 'ManualClaim'

        props = {instrument.serial_number: EmptyProperty() for instrument in instruments}
        payload = SimpleInstrumentsCommand(
            InstrumentProperties=props, AllInstrumentsMustSucceed=True
        )

        await self._http.post(f'/Instruments/{method}', json=payload.model_dump())

        claims = [InstrumentClaim(instrument.serial_number, self) for instrument in instruments]
        return InstrumentClaimBatch(claims)

    async def release(self, instruments: Sequence[InstrumentClaim]) -> None:
        """Release the given instruments back to Lablink.

        Parameters
        ----------
        instruments : Sequence[InstrumentClaim]
            Claimed instruments to release.
        """
        props = {instrument.serial_number: EmptyProperty() for instrument in instruments}
        payload = SimpleInstrumentsCommand(
            InstrumentProperties=props, AllInstrumentsMustSucceed=True
        )

        await self._http.post('/Instruments/UnClaim', json=payload.model_dump())

    async def list_measurements(self) -> list[Measurement]:
        """List all measurements.

        Returns
        -------
        list of MeasurementRef
            A list of measurement references.
        """
        data = await self._http.get('/Measurements')
        refs = [MeasurementListResult.model_validate(item) for item in data.json()]
        # TODO: Expose `MeasurementListResult` data via Measurement.info()
        return [Measurement(str(ref.Id), session=self) for ref in refs]

    async def get_measurement(self, measurement: Measurement | str) -> xr.Dataset | xr.DataTree:
        """Fetch a specific measurement by its reference ID.

        Parameters
        ----------
        measurement : MeasurementRef | str
            The measurement to fetch. Can be a MeasurementRef or its string ID.

        Returns
        -------
        xr.Dataset | xr.DataTree
            The parsed measurement data as an xarray object.
        """
        import numpy as np

        if isinstance(measurement, Measurement):
            guid = measurement.guid
        else:
            guid = measurement

        response = await self._http.get(f'/Measurements/{guid}')
        parsed = MeasurementResult.model_validate(response.json())

        # metadata = _to_measurement_metadata(parsed)

        datasets = []

        assert parsed.RawDataSets

        for dataset in parsed.RawDataSets:
            data_vars = {}
            attrs: dict[str, Any] = {}

            dataset, *_ = parsed.RawDataSets
            dataset_id = dataset.DataSetId

            assert dataset.DataArrays

            for array in dataset.DataArrays:
                assert array.DataValueType
                array_type = array.DataValueType.name
                # TODO, what is array ID used for?
                # array_id = array.DataArrayId
                values_id = array.DataValuesId

                response = await self._http.get(f'DataSets/{dataset_id}/{values_id}')
                raw = response.content

                if array_type == 'CurrentRange':
                    pairs = np.frombuffer(raw, dtype=np.int32).reshape(-1, 2)
                    data = pairs[:, 0]
                    # TODO: what is other? factor? exponent? How to store.
                    # other = pairs[:, 0]

                elif array_type in (
                    'AppliedPotential',
                    'Charge',
                    'MeasuredCurrent',
                    'AuxiliaryPotential',
                    'ReverseCurrent',
                    'ForwardCurrent',
                ):
                    data = np.frombuffer(raw, dtype=np.float64)  # little-endian float64

                elif array_type in (
                    'TimingStatus',
                    'CurrentReadingStatus',
                    'ForwardCurrentReadingStatus',
                    'ReverseCurrentReadingStatus',
                ):
                    data = np.frombuffer(raw, dtype=np.int8)  # int enum (8-bit signed integer)

                elif array_type in ('Index', 'CycleIndex', 'LevelIndex'):
                    data = np.frombuffer(raw, dtype=np.int32)  # int enum (32 bit signed)

                elif array_type == 'Timestamp':
                    ticks = np.frombuffer(raw, dtype=np.int64)  # 100-ns ticks
                    data = ticks * 1e-7  # seconds

                else:
                    print(f'Unknown data type: {array_type=}')
                    print('  len:', len(response.content))
                    print('  hex:', response.content[:32].hex())
                    continue

                data_vars[array_type] = ('point', data, {'unit': '...'})

            coords = {'point': range(len(data))}

            ds = xr.Dataset(data_vars=data_vars, coords=coords, attrs=attrs)
            datasets.append(ds)

        if len(datasets) > 1:
            data = xr.concat(datasets, pd.Index(len(datasets), name='new_dim'))
        else:
            data = datasets[0]

        return data

    async def start_measurement(
        self, instruments: Sequence[InstrumentClaim], *, method: MethodTypeCompatible
    ) -> list[MeasurementJob]:
        """Start a measurement on each of the claimed instruments.

        Parameters
        ----------
        instruments : Sequence[InstrumentClaim]
            Instruments (claimed) to start measuremeents on.
        method : MethodTypeCompatible
            The measurement method to apply.

        Returns
        -------
        list[MeasurementJob]
            One job per instrument, each with an associated MeasurementJob.
        """
        payload = {
            **to_payload(method),
            'AllInstrumentsMustSucceed': True,
            'InstrumentProperties': {
                instrument.serial_number: {} for instrument in instruments
            },
        }

        response = await self._http.post('/Instruments/StartMeasurement', json=payload)

        jobs = []
        claims = {claim.serial_number: claim for claim in instruments}

        for data in response.json():
            guid = data['result']
            serial = data['serial']
            claim = claims[serial]
            jobs.append(MeasurementJob(guid=guid, claim=claim))

        return jobs

    async def skip_pre_measurement_stage(self, jobs: Sequence[MeasurementJob]) -> None:
        """Skip the pre-measurement stage on the given measurement jobs.

        Parameters
        ----------
        jobs : Sequence[MeasurementJob]
            The running measurements to skip the pre-stage of.
        """
        payload = {
            'AllInstrumentsMustSucceed': True,
            'InstrumentProperties': {job.serial_number: {} for job in jobs},
        }

        await self._http.post('/Instrument/SkipPreMeasurementStage', json=payload)

    async def pause_measurement(self, jobs: Sequence[MeasurementJob]) -> None:
        """Pause running measurements on the given jobs.

        Parameters
        ----------
        jobs : Sequence[MeasurementJob]
            The measurement jobs to pause.
        """
        payload = {
            'AllInstrumentsMustSucceed': True,
            'InstrumentProperties': {job.serial_number: {} for job in jobs},
        }

        await self._http.post('/Instrument/PauseMeasurement', json=payload)

    async def resume_measurement(self, jobs: Sequence[MeasurementJob]) -> None:
        """Resume a measurement that was previously paused.

        Parameters
        ----------
        jobs : Sequence[MeasurementJob]
            The measurement jobs to resume.
        """
        payload = {
            'AllInstrumentsMustSucceed': True,
            'InstrumentProperties': {job.serial_number: {} for job in jobs},
        }

        await self._http.post('/Instrument/ResumeMeasurement', json=payload)

    async def abort_measurement(self, jobs: Sequence[MeasurementJob]) -> None:
        """Abort a running measurement and cancel job.

        Parameters
        ----------
        jobs : Sequence[MeasurementJob]
            The measurement to abort.
        """
        payload = {
            'AllInstrumentsMustSucceed': True,
            'InstrumentProperties': {job.serial_number: {} for job in jobs},
        }

        await self._http.post('/Instrument/AbortMeasurement', json=payload)

    async def start_workflow(
        self, instruments: Sequence[InstrumentClaim], *, workflow: str
    ) -> None:
        """Start a workflow on the given instruments.

        Parameters
        ----------
        instruments : Sequence[InstrumentClaim]
            The claimed instruments that will run the workflow.
        workflow : str
            Name of the workflow to start.
        """
        data = {
            'AllInstrumentsMustSucceed': True,
            'InstrumentProperties': {
                instrument.serial_number: workflow for instrument in instruments
            },
        }
        payload = SendWorkflowCommand.model_validate(data).model_dump()
        await self._http.post('/Instrument/SendScript', json=payload)

    async def list_users(self) -> list[UserInfo]:
        """Get list of users.

        Returns
        -------
        users : list[UserInfo]
            List of user info
        """
        data = await self._http.get('/Users')
        return [UserInfo.from_wire(item) for item in data.json()]

    async def delete_user(self, user: UserInfo | str) -> None:
        """Delete a user by their identifier.

        Users are deleted using their unique identifier (GUID),
        either using the `guid` attribute from the `UserInfo` instance or
        directly as a string.

        Parameters
        ----------
        user: UserInfo | str
            The identifier for the user to delete. This can be either an instance
            of UserInfo, or a GUID string.
        """
        if isinstance(user, UserInfo):
            guid = user.guid
        else:
            guid = user

        await self._http.delete(f'/Users/{guid}')

    async def delete_measurements(self, measurements: list[Measurement | str]) -> None:
        """Delete measurement data from Lablink.

        Measurements are deleted by their unique identifier (GUID),
        either using the `guid` attribute from the `Measurement` instance or
        directly as a string.

        Parameters
        ----------
        measurements : list[Measurement | str]
            A list of measurements to delete. Each item in the list can be
            either an instance of `Measurement` or a GUID string.
        """
        payload = [
            item.guid if isinstance(item, Measurement) else item for item in measurements
        ]

        await self._http.delete('/Measurements/BatchDelete', json=payload)
