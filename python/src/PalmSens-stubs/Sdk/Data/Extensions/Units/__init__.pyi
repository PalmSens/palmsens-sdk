import typing, abc
from PalmSens.Sdk.Data.Models.Entities import Prefix, TimeUnitType, Quantity
from System import ValueTuple_2

class PrefixExtensions(abc.ABC):
    @staticmethod
    def DetermineNewPrefix(oldPrefix: Prefix, value: float) -> Prefix: ...
    @staticmethod
    def ParsePrefix(str: str) -> ValueTuple_2[Prefix, int]: ...
    # Skipped ToScaleFactor due to it being static, abstract and generic.

    ToScaleFactor : ToScaleFactor_MethodGroup
    class ToScaleFactor_MethodGroup:
        @typing.overload
        def __call__(self, prefix: Prefix) -> float:...
        @typing.overload
        def __call__(self, timeUnitType: TimeUnitType) -> float:...

    # Skipped ToSymbol due to it being static, abstract and generic.

    ToSymbol : ToSymbol_MethodGroup
    class ToSymbol_MethodGroup:
        @typing.overload
        def __call__(self, prefix: Prefix) -> str:...
        @typing.overload
        def __call__(self, timeUnitType: TimeUnitType) -> str:...



class QuantityExtensions(abc.ABC):
    @staticmethod
    def ParseUnitSymbol(str: str) -> Quantity: ...
    @staticmethod
    def ToUnitSymbol(quantity: Quantity) -> str: ...
