from __future__ import annotations

from collections.abc import Sequence
from typing import ClassVar, Self

import System
from instrument import InstrumentClaim, InstrumentRef
from measurement import Measurement, MeasurementRef
from PalmSens.Sdk.Lablink.Example import Lablink as PSLablink
from PalmSens.Sdk.Lablink.Example.Lablink import Models as PSModels

from pypalmsens._instruments.shared import create_future
from pypalmsens.types import MethodTypeCompatible


class Session:
    __slots__: ClassVar[tuple[str, ...]] = ('_inner',)
    _inner: PSLablink.Lablink  # pyright: ignore[reportUninitializedInstanceVariable]

    # Events
    # - _inner.OnInstrumentRefChanged

    def __init__(self):
        raise TypeError(
            'Lablink instance cannot be instantiated directly. '
            'Obtain instances through `Instance.login()`.'
        )

    def __repr__(self) -> str:
        return f'{type(self).__name__}(name={self.name}, address={self.address})'

    @classmethod
    def _wrap(cls, inner: PSLablink.Lablink) -> Self:
        obj = cls.__new__(cls)
        obj._inner = inner
        return obj

    @property
    def instruments(self) -> list[InstrumentRef]:
        """Instruments seen by the most recent `list_instruments()` call.

        May be stale or empty.
        """
        return [InstrumentRef._wrap(refs) for refs in self._inner.Instruments]

    async def list_instruments(self) -> list[InstrumentRef]:
        """List currently attached instruments

        Refreshes `self.instruments`."""
        raise NotImplementedError('Needs PalmSens.Sdk.Lablink update')
        return [
            InstrumentRef._wrap(refs)
            for refs in await create_future(self._inner.ListInstruments())
        ]

    async def claim(self, instruments: Sequence[InstrumentRef]) -> list[InstrumentClaim]:
        """Claims instrument."""
        lst = System.Collections.Generic.List[PSModels.LablinkInstrument]()

        for instrument in instruments:
            lst.Add(instrument._inner)

        ref = await create_future(self._inner.ConnectInstruments(lst))

        return [InstrumentClaim._wrap(ref) for ref in ref]

    async def list_measurements(self) -> list[MeasurementRef]:
        refs = await create_future(self._inner.GetMeasurements())
        return [MeasurementRef._wrap(ref, self) for ref in refs]

    async def fetch_measurement(self, measurement: MeasurementRef) -> Measurement:
        """Not working, error: `InvalidOperationException: Sequence contains no matching element`

        https://stackoverflow.com/questions/3994336/sequence-contains-no-matching-element
        """
        ref = await create_future(self._inner.GetMeasurement(measurement._inner.Id))
        return Measurement._wrap(ref)

    async def start_measurements(
        self, instruments: Sequence[InstrumentClaim], method: MethodTypeCompatible
    ) -> list[Measurement]:
        """Not working, error: `unknown CellModeAfterMeasurement CellModePotentiostatic`"""
        lst = System.Collections.Generic.List[PSLablink.LablinkInstrument]()

        for instrument in instruments:
            lst.Add(instrument._inner)

        refs = await create_future(self._inner.StartMeasurements(lst, method._to_psmethod()))
        return [Measurement._wrap(ref) for ref in refs]

    @property
    def address(self) -> str:
        return str(self._inner.Address)

    @property
    def name(self) -> str:
        return self._inner.Name

    @property
    def version(self) -> str:
        raise NotImplementedError
        return self._inner.Version

    @property
    def serial_number(self) -> str:
        return self._inner.Serial
