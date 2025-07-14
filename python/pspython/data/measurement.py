from ._shared import ArrayType
from .curve import Curve
from .fit_result import EISFitResult
from .peak import Peak


class Measurement:
    def __init__(
        self,
        *,
        dotnet_measurement,
    ):
        self.dotnet_measurement = dotnet_measurement

    @property
    def title(self) -> str:
        return self.dotnet_measurement.Title

    @property
    def timestamp(self) -> str:
        return str(self.dotnet_measurement.TimeStamp)

    @property
    def current_arrays(self) -> list:
        # # get the current range the current was measured in
        # currentranges = __getcurrentrangesfromcurrentarray(array)
        # # get the status of the meausured data point
        # currentstatus = __getstatusfromcurrentorpotentialarray(array)
        return [
            list(array.GetValues())
            for array in self.dotnet_measurement.DataSet.GetDataArrays()
            if ArrayType(array.ArrayType) == ArrayType.Current
        ]

    @property
    def potential_arrays(self) -> list:
        # # Get the status of the meausured data point
        # potentialStatus = __getstatusfromcurrentorpotentialarray(array)
        return [
            list(array.GetValues())
            for array in self.dotnet_measurement.DataSet.GetDataArrays()
            if ArrayType(array.ArrayType) == ArrayType.Potential
        ]

    @property
    def time_arrays(self) -> list:
        return [
            list(array.GetValues())
            for array in self.dotnet_measurement.DataSet.GetDataArrays()
            if ArrayType(array.ArrayType) == ArrayType.Time
        ]

    @property
    def freq_arrays(self) -> list:
        return [
            list(array.GetValues())
            for array in self.dotnet_measurement.DataSet.GetDataArrays()
            if ArrayType(array.ArrayType) == ArrayType.Frequency
        ]

    @property
    def zre_arrays(self) -> list:
        return [
            list(array.GetValues())
            for array in self.dotnet_measurement.DataSet.GetDataArrays()
            if ArrayType(array.ArrayType) == ArrayType.ZRe
        ]

    @property
    def zim_arrays(self) -> list:
        return [
            list(array.GetValues())
            for array in self.dotnet_measurement.DataSet.GetDataArrays()
            if ArrayType(array.ArrayType) == ArrayType.ZIm
        ]

    @property
    def aux_input_arrays(self) -> list:
        return [
            list(array.GetValues())
            for array in self.dotnet_measurement.DataSet.GetDataArrays()
            if ArrayType(array.ArrayType) == ArrayType.AuxInput
        ]

    @property
    def peaks(self) -> list[Peak]:
        peaks = []
        for curve in self.curves:
            peaks.extend(curve.peaks)
        return peaks

    @property
    def eis_fit(self) -> list:
        eisdatas = self.dotnet_measurement.EISdata
        eis_fits = []
        if eisdatas is not None:
            for eisdata in eisdatas:
                if eisdata is not None:
                    eis_fits.append(EISFitResult(eisdata.CDC, eisdata.CDCValues))
        return eis_fits

    @property
    def curves(self) -> list[Curve]:
        curves = self.dotnet_measurement.GetCurveArray()
        return [Curve(dotnet_curve=curve) for curve in curves]
