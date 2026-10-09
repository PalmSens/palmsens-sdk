import typing, abc
from System import IDisposable, Action_2, Func_3, Func_1, Action, Action_1, Func_2, Action_3, Func_4
from Microsoft.AspNetCore.SignalR.Client import HubConnection
from PalmSens.Sdk.Lablink.Example.Lablink.Models.Dtos.SignalR import InstrumentSerialDto, UserDetailsDto, DataSetLayoutDto
from System.Threading.Tasks import Task
from System.Collections.Generic import List_1
from System.Text.Json import JsonElement

class LablinkHubConnectionBase(abc.ABC):
    pass


class LablinkHubConnectionGeneral(abc.ABC):
    # Skipped OnInstrumentClaimChanged due to it being static, abstract and generic.

    OnInstrumentClaimChanged : OnInstrumentClaimChanged_MethodGroup
    class OnInstrumentClaimChanged_MethodGroup:
        @typing.overload
        def __call__(self, connection: HubConnection, callbackAction: Action_2[InstrumentSerialDto, UserDetailsDto]) -> IDisposable:...
        @typing.overload
        def __call__(self, connection: HubConnection, callbackFunc: Func_3[InstrumentSerialDto, UserDetailsDto, Task]) -> IDisposable:...

    # Skipped OnInstrumentConnected due to it being static, abstract and generic.

    OnInstrumentConnected : OnInstrumentConnected_MethodGroup
    class OnInstrumentConnected_MethodGroup:
        @typing.overload
        def __call__(self, connection: HubConnection, callbackFunc: Func_1[Task]) -> IDisposable:...
        @typing.overload
        def __call__(self, connection: HubConnection, callbackAction: Action) -> IDisposable:...

    # Skipped OnInstrumentDisconnected due to it being static, abstract and generic.

    OnInstrumentDisconnected : OnInstrumentDisconnected_MethodGroup
    class OnInstrumentDisconnected_MethodGroup:
        @typing.overload
        def __call__(self, connection: HubConnection, callbackFunc: Func_1[Task]) -> IDisposable:...
        @typing.overload
        def __call__(self, connection: HubConnection, callbackAction: Action) -> IDisposable:...

    # Skipped OnInstrumentIdle due to it being static, abstract and generic.

    OnInstrumentIdle : OnInstrumentIdle_MethodGroup
    class OnInstrumentIdle_MethodGroup:
        @typing.overload
        def __call__(self, connection: HubConnection, callbackAction: Action_1[InstrumentSerialDto]) -> IDisposable:...
        @typing.overload
        def __call__(self, connection: HubConnection, callbackFunc: Func_2[InstrumentSerialDto, Task]) -> IDisposable:...

    # Skipped OnInstrumentMeasuring due to it being static, abstract and generic.

    OnInstrumentMeasuring : OnInstrumentMeasuring_MethodGroup
    class OnInstrumentMeasuring_MethodGroup:
        @typing.overload
        def __call__(self, connection: HubConnection, callbackAction: Action_1[InstrumentSerialDto]) -> IDisposable:...
        @typing.overload
        def __call__(self, connection: HubConnection, callbackFunc: Func_2[InstrumentSerialDto, Task]) -> IDisposable:...



class LablinkHubConnectionMeasurement(abc.ABC):
    # Skipped OnMeasurementAborted due to it being static, abstract and generic.

    OnMeasurementAborted : OnMeasurementAborted_MethodGroup
    class OnMeasurementAborted_MethodGroup:
        @typing.overload
        def __call__(self, connection: HubConnection, callbackFunc: Func_1[Task]) -> IDisposable:...
        @typing.overload
        def __call__(self, connection: HubConnection, callbackAction: Action) -> IDisposable:...

    # Skipped OnMeasurementDataReceived due to it being static, abstract and generic.

    OnMeasurementDataReceived : OnMeasurementDataReceived_MethodGroup
    class OnMeasurementDataReceived_MethodGroup:
        @typing.overload
        def __call__(self, connection: HubConnection, callbackAction: Action_3[int, int, List_1[JsonElement]]) -> IDisposable:...
        @typing.overload
        def __call__(self, connection: HubConnection, callbackFunc: Func_4[int, int, List_1[JsonElement], Task]) -> IDisposable:...

    # Skipped OnMeasurementDataSetLayout due to it being static, abstract and generic.

    OnMeasurementDataSetLayout : OnMeasurementDataSetLayout_MethodGroup
    class OnMeasurementDataSetLayout_MethodGroup:
        @typing.overload
        def __call__(self, connection: HubConnection, callbackAction: Action_2[int, DataSetLayoutDto]) -> IDisposable:...
        @typing.overload
        def __call__(self, connection: HubConnection, callbackFunc: Func_3[int, DataSetLayoutDto, Task]) -> IDisposable:...

    # Skipped OnMeasurementFinished due to it being static, abstract and generic.

    OnMeasurementFinished : OnMeasurementFinished_MethodGroup
    class OnMeasurementFinished_MethodGroup:
        @typing.overload
        def __call__(self, connection: HubConnection, callbackFunc: Func_1[Task]) -> IDisposable:...
        @typing.overload
        def __call__(self, connection: HubConnection, callbackAction: Action) -> IDisposable:...

    # Skipped OnMeasurementPaused due to it being static, abstract and generic.

    OnMeasurementPaused : OnMeasurementPaused_MethodGroup
    class OnMeasurementPaused_MethodGroup:
        @typing.overload
        def __call__(self, connection: HubConnection, callbackAction: Action_1[bool]) -> IDisposable:...
        @typing.overload
        def __call__(self, connection: HubConnection, callbackFunc: Func_2[bool, Task]) -> IDisposable:...

    # Skipped OnMeasurementStarted due to it being static, abstract and generic.

    OnMeasurementStarted : OnMeasurementStarted_MethodGroup
    class OnMeasurementStarted_MethodGroup:
        @typing.overload
        def __call__(self, connection: HubConnection, callbackFunc: Func_1[Task]) -> IDisposable:...
        @typing.overload
        def __call__(self, connection: HubConnection, callbackAction: Action) -> IDisposable:...
