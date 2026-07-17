
import typing
from typing import Final

if typing.TYPE_CHECKING:
    from .instrument_manager import InstrumentManager


class InternalStorageManager:
    def __init__(self, manager:InstrumentManager):
        self.manager: Final = manager
