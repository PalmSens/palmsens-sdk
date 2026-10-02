"""Submodule for instrument references and claims.

[InstrumentRef][] holds an instrument's metadata and status. Use
[InstrumentClaim][] as an async context manager for a claimed
instrument. The claim is released when the context exits.

"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, Literal, Self

if TYPE_CHECKING:
    from ._session import Session


class InstrumentRef:
    """
    A reference to an instrument.
    """

    __slots__: ClassVar[tuple[str, ...]] = ('_inner',)
    _inner: dict[str, Any]

    def __init__(self):
        raise TypeError(
            'InstrumentRef cannot be instantiated directly. '
            'Obtain instances through Session.list_instruments().'
        )

    def __repr__(self) -> str:
        return f'{type(self).__name__}(name={self.name!r}, serial={self.serial_number!r})'

    @classmethod
    def _wrap(cls, inner: dict[str, Any]) -> Self:
        obj = cls.__new__(cls)
        obj._inner = inner
        return obj

    @property
    def name(self) -> str:
        """The name of the instrument."""
        return self.custom_name or self.default_name

    @property
    def custom_name(self) -> str | None:
        """The custom name assigned to the instrument, if any."""
        return self._inner['CustomInstrumentName']

    @property
    def default_name(self) -> str:
        """The default name of the instrument."""
        return self._inner['DefaultInstrumentName']

    @property
    def is_claimed(self) -> bool:
        """Whether the instrument is currently claimed."""
        return self._inner['IsClaimed']

    @property
    def claim_owner(self) -> str | None:
        """The username of the person who claimed the instrument, if any."""
        return self._inner['ClaimOwnerUsername']

    @property
    def status(self) -> Literal['Idle', 'Measuring', 'Error']:
        """The current status of the instrument."""
        if self.is_in_error:
            return 'Error'
        elif self.is_measuring:
            return 'Measuring'
        else:
            return 'Idle'

    @property
    def is_in_error(self) -> bool:
        """Whether the instrument is in an error state."""
        return self._inner['IsInErrorState']

    @property
    def is_measuring(self) -> bool:
        """Whether the instrument is currently measuring."""
        return self._inner['IsMeasuring']

    @property
    def model(self) -> str:
        """The model name of the instrument."""
        return self._inner['Model']

    @property
    def multichannel_id(self) -> str:
        """The ID of the multichannel device."""
        return self._inner['MultiChannelId']

    @property
    def multichannel_index(self) -> int:
        """The index of the channel within the multichannel device."""
        return self._inner['MultiChannelIndex']

    @property
    def in_multichannel_group(self) -> bool:
        """Whether the instrument belongs to a multichannel group."""
        return self._inner['BelongsToMultiChannelInstrument']

    @property
    def serial_number(self) -> str:
        """The serial number of the instrument."""
        return self._inner['Serial']['Serial']


class InstrumentClaim:
    """
    A context manager for claiming an instrument.
    """

    __slots__: ClassVar[tuple[str, ...]] = ('_serial', '_session')
    _serial: str
    _session: Session

    def __init__(self):
        raise TypeError(
            'InstrumentClaim cannot be instantiated directly. '
            'Obtain instances through Session.claim() or claim_many().'
        )

    def __repr__(self) -> str:
        return f'{type(self).__name__}(serial_number={self.serial_number!r})'

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *exc) -> None:
        await self.release()

    @classmethod
    def _wrap(cls, serial: str, session: Session) -> Self:
        obj = object.__new__(cls)
        obj._serial = serial
        obj._session = session
        return obj

    @property
    def serial_number(self) -> str:
        """The serial number of the claimed instrument."""
        return self._serial

    async def release(self) -> None:
        """Release the instrument claim."""
        await self._session.release(self)
