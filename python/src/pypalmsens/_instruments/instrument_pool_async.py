from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, Awaitable, Protocol, Sequence

from .._methods import BaseTechnique
from .callback import Callback, CallbackEIS
from .instrument_manager_async import InstrumentManagerAsync
from .shared import Instrument

if TYPE_CHECKING:
    from .._data.measurement import Measurement


class SubmitCallable(Protocol):
    def __call__(self, manager: InstrumentManagerAsync, **kwargs) -> Awaitable[Any]: ...


class InstrumentPoolAsync:
    """Manages a set of instrument.

    Most calls are run asynchronously in the background,
    which means that measurements are running in parallel.

    Parameters
    ----------
    devices_or_managers : list[Instrument | InstrumentManagerAsync]
        List of devices or managers.
    """

    def __init__(
        self,
        devices_or_managers: Sequence[Instrument | InstrumentManagerAsync],
    ):
        self.managers: list[InstrumentManagerAsync] = []
        """List of instruments managers in the pool."""

        for item in devices_or_managers:
            if isinstance(item, Instrument):
                self.managers.append(InstrumentManagerAsync(item))
            else:
                self.managers.append(item)

    def __repr__(self):
        ids = [manager.instrument.id for manager in self.managers]
        return f'{self.__class__.__name__}({ids}, connected={self.is_connected()})'

    def __len__(self):
        return len(self.managers)

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
        await manager.connect()
        self.managers.append(manager)

    async def measure(
        self,
        method: BaseTechnique,
        callback: Sequence[Callback | CallbackEIS] | Callback | CallbackEIS | None = None,
        **kwargs,
    ) -> list[Measurement]:
        """Concurrently start measurement on all managers in the pool.

        For hardware synchronization, set `.general.use_hardware_sync` on the method.
        For MethodSCRIPT, use 'set_channel_sync 1'.

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
        callback : list[Callback] | Callback | CallbackEIS | None
            If specified, call these functions/this function on every new set of data points.
            New data points are batched, and contain all points since the last
            time it was called.

            Specify a sequence of callbacks to set a different function for every channel.
            The number of callbacks must match the number of channels.

            Specify a single callback to set the same function to all channels.
        **kwargs
            These keyword parameters are passed to the measure function.
        """
        tasks: list[Awaitable[Measurement]] = []

        callbacks: Sequence[Callback | CallbackEIS | None]

        if isinstance(callback, Sequence):
            if len(callback) != len(self.managers):
                raise IndexError('Number of callbacks does not match number of channels.')
            callbacks = callback
        else:
            callbacks = [callback or None for _ in self.managers]

        if method._use_hardware_sync:
            return await self._measure_hw_sync(method, callbacks=callbacks)

        for manager, callback in zip(self.managers, callbacks):
            tasks.append(manager.measure(method, callback=callback, **kwargs))

        results = await asyncio.gather(*tasks)
        return results

    async def _measure_hw_sync(
        self,
        method: BaseTechnique,
        callbacks: Sequence[Callback | CallbackEIS | None] | None = None,
        **kwargs,
    ) -> list[Measurement]:
        """Concurrently start measurement on all managers in the pool.

        Parameters
        ----------
        method : MethodSettings
            Method parameters for measurement.
        callbacks : list[Callback | CallbackEIS | None]
            List of callbacks, must match number of managers.
        **kwargs
            These keyword arguments are passed to the measurement function.
        """
        follower_sync_tasks = []
        tasks: list[Awaitable[Measurement]] = []

        if callbacks is None:
            callbacks = [None] * len(self)

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

        for manager, callback in zip(self.managers, callbacks):
            if manager.instrument.channel == 1:
                hw_sync_manager = manager
                hw_sync_callback = callback
                break
        else:
            raise ValueError(
                (
                    'Hardware synchronization requires the first channel '
                    'of the multi-channel instrument to be in the pool.'
                )
            )

        for manager in self.managers:
            manager.validate_method(method._to_psmethod())

        for manager, callback in zip(self.managers, callbacks):
            if manager is hw_sync_manager:
                continue

            sync_task, measure_task = manager._initiate_hardware_sync_follower_channel(
                method=method,
                callback=callback,
                **kwargs,
            )
            follower_sync_tasks.append(sync_task)
            tasks.append(measure_task)

        _ = await asyncio.gather(*follower_sync_tasks)

        tasks.append(
            hw_sync_manager.measure(method=method, callback=hw_sync_callback, **kwargs)
        )

        results = await asyncio.gather(*tasks)
        return results

    async def submit(self, func: SubmitCallable, **kwargs: Any) -> list[Any]:
        """Concurrently start measurement on all managers in the pool.

        This method does not support hardware sync.

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
