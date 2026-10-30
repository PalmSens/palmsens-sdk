import typing
from PalmSens.Sdk.Lablink.Example.Lablink.Services.Client import LablinkHttpClientFactory, LablinkSignalRHubFactory
from System.Threading.Tasks import Task_1
from PalmSens.Sdk.Lablink.Example.Lablink.Models import LablinkInfo
from System import Uri
from System.Threading import CancellationToken
from PalmSens.Sdk.Lablink.Example.Lablink import Lablink

class LablinkFactory:
    def __init__(self, lablinkHttpClientFactory: LablinkHttpClientFactory, lablinkSignalRHubFactory: LablinkSignalRHubFactory) -> None: ...
    def GetLablinkInfo(self, lablinkAddress: Uri, cancellationToken: CancellationToken = ...) -> Task_1[LablinkInfo]: ...
    def RegisterNewUserAndLogin(self, lablinkInfo: LablinkInfo, userName: str, password: str, cancellationToken: CancellationToken = ...) -> Task_1[Lablink]: ...
    # Skipped Login due to it being static, abstract and generic.

    Login : Login_MethodGroup
    class Login_MethodGroup:
        @typing.overload
        def __call__(self, lablinkInfo: LablinkInfo, bearerToken: str, cancellationToken: CancellationToken = ...) -> Task_1[Lablink]:...
        @typing.overload
        def __call__(self, lablinkInfo: LablinkInfo, userName: str, password: str, cancellationToken: CancellationToken = ...) -> Task_1[Lablink]:...
