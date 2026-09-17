from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Literal, Self

from PalmSens.Sdk.Lablink.Example import Lablink as PSLablink
from PalmSens.Sdk.Lablink.Example.Lablink import Models as PSModels

from pypalmsens._instruments.shared import create_future

if TYPE_CHECKING:
    from lablink import Lablink


class InstrumentInfo:
    __slots__: ClassVar[tuple[str, ...]] = ('_inner',)
    _inner: PSModels.LablinkInstrumentInfo  # pyright: ignore[reportUninitializedInstanceVariable]

    def __init__(self):
        raise TypeError(
            'InstrumentInfo cannot be instantiated directly. '
            'Obtain instances through Lablink class.'
        )

    def __repr__(self) -> str:
        return f'{type(self).__name__}(name={self.name!r}, serial={self.serial_number!r})'

    @classmethod
    def _wrap(cls, inner: PSLablink.LablinkInstrumentInfo) -> Self:
        obj = cls.__new__(cls)
        obj._inner = inner
        return obj

    @property
    def name(self) -> str:
        return self.custom_name or self.default_name

    @property
    def custom_name(self) -> str | None:
        return self._inner.CustomInstrumentName

    @property
    def default_name(self) -> str:
        return self._inner.DefaultInstrumentName

    @property
    def is_claimed(self) -> bool:
        return self._inner.IsClaimed

    @property
    def claim_owner(self) -> str | None:
        return self._inner.ClaimOwnerUsername

    @property
    def status(self) -> Literal['Idle', 'Measuring', 'Error']:
        if self.is_in_error:
            return 'Error'
        elif self.is_measuring:
            return 'Measuring'
        else:
            return 'Idle'

    @property
    def is_in_error(self) -> bool:
        return self._inner.IsInErrorState

    @property
    def is_measuring(self) -> bool:
        return self._inner.IsMeasuring

    @property
    def model(self) -> str:
        return self._inner.Model

    @property
    def multichannel_id(self) -> str:
        return self._inner.MultiChannelId

    @property
    def multichannel_index(self) -> int:
        return self._inner.MultiChannelIndex

    @property
    def in_multichannel_group(self) -> bool:
        return self._inner.BelongsToMultiChannelInstrument

    @property
    def serial_number(self) -> str:
        return self._inner.Serial


class InstrumentHandle:
    __slots__: ClassVar[tuple[str, ...]] = ('_inner',)
    _inner: PSLablink.LablinkInstrument  # pyright: ignore[reportUninitializedInstanceVariable]

    def __init__(self):
        raise TypeError(
            'LablinkInstrument cannot be instantiated directly. '
            'Obtain instances through Lablink class.'
        )

    def __repr__(self) -> str:
        return f'{type(self).__name__}(serial_number={self.serial_number})'

    @classmethod
    def _wrap(cls, inner: PSLablink.LablinkInstrument) -> Self:
        obj = cls.__new__(cls)
        obj._inner = inner
        return obj

    @property
    def lablink(self) -> Lablink:
        from lablink import Lablink

        return Lablink._wrap(self._inner.Parent)

    @property
    def serial_number(self) -> str:
        return self._inner.Serial

    async def unclaim(self) -> None:
        await create_future(self._inner.DisposeAsync())
