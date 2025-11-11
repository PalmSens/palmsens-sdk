from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Callable, Sequence

from .._methods import BaseTechnique
from ._common import Instrument
from .instrument_manager_async import InstrumentManagerAsync
from .instrument_pool_async import InstrumentPoolAsync

if TYPE_CHECKING:
    from .._data.measurement import Measurement


class InstrumentPool:
    """Manages a set of instrument.

    Most calls are run asynchronously in the background,
    which means that measurements are running in parallel.

    This is a thin wrapper around the `InstrumentManagerAsync`.


    Parameters
    ----------
    devices_or_managers : list[Instrument | InstrumentManagerAsync]
        List of devices or managers.
    callback : Callable, optional
        Optional callable to set on instrument managers
    """

    def __init__(
        self,
        devices_or_managers: Sequence[Instrument | InstrumentManagerAsync],
        *,
        callback: None | Callable = None,
    ):
        self._async: InstrumentPoolAsync = InstrumentPoolAsync(
            devices_or_managers, callback=callback
        )
        self._loop = asyncio.new_event_loop()

        self.managers: list[InstrumentManagerAsync] = self._async.managers
        """List of instruments managers in the pool."""

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return self.disconnect()

    def __iter__(self):
        yield from self.managers

    def connect(self) -> None:
        """Connect all instrument managers in the pool."""
        self._loop.run_until_complete(self._async.connect())

    def disconnect(self) -> None:
        """Disconnect all instrument managers in the pool."""
        self._loop.run_until_complete(self._async.disconnect())

    def is_connected(self) -> bool:
        """Return true if all managers in the pool are connected."""
        return self._async.is_connected()

    def is_disconnected(self) -> bool:
        """Return true if all managers in the pool are disconnected."""
        return self._async.is_disconnected()

    def remove(self, manager: InstrumentManagerAsync) -> None:
        """Close and remove manager from pool.

        Parameters
        ----------
        manager : InstrumentManagerAsync
            Instance of an instrument manager.
        """
        self._loop.run_until_complete(self._async.remove(manager))

    def add(self, manager: InstrumentManagerAsync) -> None:
        """Open and add manager to the pool.

        Parameters
        ----------
        manager : InstrumentManagerAsync
            Instance of an instrument manager.
        """
        self._loop.run_until_complete(self._async.add(manager))

    def measure(self, method: BaseTechnique) -> list[Measurement]:
        """Concurrently run measurement on all managers in the pool.

        For hardware synchronization, set `use_hardware_sync` on the method.
        In addition, the pool must contain:
        - channels from a single multi-channel instrument only
        - the first channel of the multi-channel instrument
        - at least two channels

        All instruments are prepared and put in a waiting state.
        The measurements are started via a hardware sync trigger on channel 1.

        Parameters
        ----------
        method : MethodSettings
            Method parameters for measurement.
        """
        return self._loop.run_until_complete(self._async.measure(method=method))
