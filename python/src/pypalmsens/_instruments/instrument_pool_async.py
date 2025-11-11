from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Sequence

from .._methods import BaseTechnique
from ._common import Instrument
from .instrument_manager_async import InstrumentManagerAsync

if TYPE_CHECKING:
    from .._data.measurement import Measurement


class InstrumentPoolAsync:
    """Manages a set of instrument.

    Most calls are run asynchronously in the background,
    which means that measurements are running in parallel.

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
        self.managers: list[InstrumentManagerAsync] = []
        """List of instruments managers in the pool."""

        for item in devices_or_managers:
            if isinstance(item, Instrument):
                self.managers.append(InstrumentManagerAsync(item, callback=callback))
            else:
                if callback:
                    item.callback = callback
                self.managers.append(item)

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        return await self.disconnect()

    def __iter__(self):
        yield from self.managers

    async def connect(self) -> None:
        """Connect all instrument managers in the pool."""
        tasks = [manager.connect() for manager in self.managers]
        await asyncio.gather(*tasks)

    async def disconnect(self) -> None:
        """Disconnect all instrument managers in the pool."""
        tasks = [manager.disconnect() for manager in self.managers]
        await asyncio.gather(*tasks)

    def is_connected(self) -> bool:
        """Return true if all managers in the pool are connected."""
        return all(manager.is_connected() for manager in self.managers)

    def is_disconnected(self) -> bool:
        """Return true if all managers in the pool are disconnected."""
        return not any(manager.is_connected() for manager in self.managers)

    async def remove(self, manager: InstrumentManagerAsync) -> None:
        """Close and remove manager from pool.

        Parameters
        ----------
        manager : InstrumentManagerAsync
            Instance of an instrument manager.
        """
        self.managers.remove(manager)
        _ = await manager.disconnect()

    async def add(self, manager: InstrumentManagerAsync) -> None:
        """Open and add manager to the pool.

        Parameters
        ----------
        manager : InstrumentManagerAsync
            Instance of an instrument manager.
        """
        _ = await manager.connect()
        self.managers.append(manager)

    async def measure(self, method: BaseTechnique) -> list[Measurement]:
        """Concurrently start measurement on all managers in the pool.

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
        tasks: list[Awaitable[Measurement]] = []

        if hasattr(method, 'general') and method.general.use_hardware_sync:
            tasks = await self._measure_hw_sync(method)
        else:
            for manager in self.managers:
                tasks.append(manager.measure(method))

        results = await asyncio.gather(*tasks)
        return results

    async def _measure_hw_sync(
        self,
        method: BaseTechnique,
    ) -> list[Awaitable[Measurement]]:
        """Concurrently start measurement on all managers in the pool.

        Parameters
        ----------
        method : MethodSettings
            Method parameters for measurement.
        """
        follower_sync_tasks = []
        tasks = []

        for manager in self.managers:
            _ = manager.validate_method(method._to_psmethod())

        if len(self.managers) < 2:
            raise ValueError(
                'Hardware synchronization requires two channels or more in the pool'
            )

        if len(set(manager.instrument.name for manager in self.managers)) > 1:
            raise ValueError(
                (
                    'Hardware synchronization is only supported when '
                    'a single multi-channel instrument is selected.'
                )
            )

        for manager in self.managers:
            if manager.instrument.channel == 1:
                hw_sync_manager = manager
                break
        else:
            raise ValueError(
                (
                    'Hardware synchronization requires the first channel '
                    'of the multi-channel instrument to be in the pool.'
                )
            )

        for manager in self.managers:
            if manager is hw_sync_manager:
                continue

            sync_task, measure_task = manager.initiate_hardware_sync_follower_channel(method)  # type: ignore
            follower_sync_tasks.append(sync_task)
            tasks.append(measure_task)

        await asyncio.gather(*follower_sync_tasks)

        tasks.append(hw_sync_manager.measure(method))
        return tasks

    async def submit(self, func: Callable, **kwargs: Any) -> list[Any]:
        """Concurrently start measurement on all managers in the pool.

        Parameters
        ----------
        func : Callable
            This function gets called with an instance of
            `InstrumentManagerAsync` as the argument.
        **kwargs
            These keyword arguments are passed on to the submitted function.
        """
        tasks: list[Awaitable[Any]] = []
        for manager in self.managers:
            tasks.append(func(manager, **kwargs))

        results = await asyncio.gather(*tasks)
        return results
