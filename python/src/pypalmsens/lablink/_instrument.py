"""Submodule for instrument references and claims.

[InstrumentRef][] holds an instrument's metadata and status. Use
[InstrumentClaim][] as an async context manager for a claimed
instrument. The claim is released when the context exits.

"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Self

from .models import InstrumentInfo

if TYPE_CHECKING:
    from ._session import Session


class InstrumentRef:
    """
    A reference to an instrument.
    """

    __slots__: ClassVar[tuple[str, ...]] = (
        '_info',
        '_serial',
    )
    _serial: str
    _info: InstrumentInfo

    def __init__(self, serial: str):
        self._serial: str = serial

    def __repr__(self) -> str:
        return f'{type(self).__name__}(serial={self.serial_number!r})'

    def metadata(self) -> InstrumentInfo:
        return self._info

    @property
    def serial_number(self) -> str:
        """The serial number of the instrument."""
        return self._serial


class InstrumentClaim:
    """
    A context manager for claiming an instrument.
    """

    __slots__: ClassVar[tuple[str, ...]] = ('_serial', '_session')
    _serial: str
    _session: Session

    def __init__(self, serial: str, session: Session):
        self._serial = serial
        self._session = session

    def __repr__(self) -> str:
        return f'{type(self).__name__}(serial_number={self.serial_number!r})'

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *exc) -> None:
        await self.release()

    @property
    def serial_number(self) -> str:
        """The serial number of the claimed instrument."""
        return self._serial

    async def release(self) -> None:
        """Release the instrument claim."""
        await self._session.release(self)
