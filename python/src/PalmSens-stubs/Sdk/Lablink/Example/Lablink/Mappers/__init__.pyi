import abc
from PalmSens import Method
from PalmSens.Sdk.Lablink.Example.Lablink.Models.Dtos.HttpClient import MethodResponseDto

class MethodMappers(abc.ABC):
    @staticmethod
    def FromDto(dto: MethodResponseDto) -> Method: ...
    @staticmethod
    def ToDto(method: Method) -> MethodResponseDto: ...
