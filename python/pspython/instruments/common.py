import asyncio

from System import Action


def create_future(clr_task):
    loop = asyncio.get_running_loop()
    future = asyncio.Future()
    callback = Action(lambda: on_completion(future, loop, clr_task))

    clr_task.GetAwaiter().OnCompleted(callback)
    return future


def on_completion(future, loop, task):
    if task.IsFaulted:
        clr_error = task.Exception.GetBaseException()
        future.set_exception(clr_error)
    else:
        loop.call_soon_threadsafe(lambda: future.set_result(task.GetAwaiter().GetResult()))


class Instrument:
    def __init__(self, name, conn, device):
        self.name = name
        self.connection = conn
        self.device = device
