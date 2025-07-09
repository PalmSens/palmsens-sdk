from enum import Enum

class Measurement:
    def __init__(self, title: str, timestamp, current_arrays, potential_arrays, time_arrays, freq_arrays, zre_arrays, zim_arrays, aux_input_arrays, peaks, eis_fit, curves = [], dotnet_measurement = None):
        self.title = title
        self.timestamp = timestamp
        self.current_arrays = current_arrays
        self.potential_arrays = potential_arrays
        self.time_arrays = time_arrays
        self.freq_arrays = freq_arrays
        self.zre_arrays = zre_arrays
        self.zim_arrays = zim_arrays
        self.aux_input_arrays = aux_input_arrays
        self.peaks = peaks
        self.eis_fit = eis_fit
        self.dotnet_measurement = dotnet_measurement
        self.curves = curves


class Curve:
    def __init__(self, title, x_array, y_array, **kwargs):
        self.title = title
        self.x_array = x_array
        self.y_array = y_array
        self.peaks = kwargs.get('peaks', [])
        self.dotnet_curve = kwargs.get('dotnet_curve', [])

    def smooth(self, smooth_level: int):
        """Smooth the .y_array using a Savitsky-Golay filter with the specified smooth level.

        Parameters
        ----------
        smooth_level : int
            The smooth level to be used. -1 = none, 0 = no smooth (spike rejection only), 1 = 5 points, 2 = 9 points, 3 = 15 points, 4 = 25 points
        """
        success = self.dotnet_curve.Smooth(smoothLevel=smooth_level)
        assert success

        self.x_array = _get_values_from_NETArray(self.dotnet_curve.XAxisDataArray)
        self.y_array = _get_values_from_NETArray(self.dotnet_curve.YAxisDataArray)

    def savitsky_golay(self, window_size: int):
        """Smooth the .y_array using a Savitsky-Golay filter with the specified window size.

        (i.e. window size 2 will filter points based on the values of the next/previous 2 points)

        Parameters
        ----------
        window_size : int
            Size of the window
        """
        success = self.dotnet_curve.Smooth(windowSize=window_size)
        assert success

        self.x_array = _get_values_from_NETArray(self.dotnet_curve.XAxisDataArray)
        self.y_array = _get_values_from_NETArray(self.dotnet_curve.YAxisDataArray)


class Peak:
    def __init__(self, curve_title, peak_height, peak_x):
        self.curve_title = curve_title
        self.peak_height = peak_height
        self.peak_x = peak_x


class EISFitResult:
    def __init__(self, cdc, values):
        self.cdc = cdc
        self.values = self.__convert_values(values)

    def __convert_values(self, values):
        converted_values = []
        if values is not None:
            for value in values:
                converted_values.append(value)
        return converted_values


def convert_to_measurement(m, **kwargs) -> Measurement:
    # Get collection of arrays in the dataset (with the exception of the potential and current arrays
    # arrays contain a single value stored in the Value field.
    # Please note that measurements can contain multiple arrays of the same type,
    # i.e. for CVs or Mux measurements)

    load_peak_data = kwargs.get('load_peak_data', False)
    load_eis_fits = kwargs.get('load_eis_fits', False)
    return_dotnet_object = kwargs.get('return_dotnet_object', False)

    arrays = m.DataSet.GetDataArrays()
    curves = m.GetCurveArray()
    eisdatas = m.EISdata
    current_arrays = []
    potential_arrays = []
    time_arrays = []
    freq_arrays = []
    zre_arrays = []
    zim_arrays = []
    aux_input_arrays = []
    peaks = []
    eis_fits = []

    for n, array in enumerate(arrays):

        try:
            array_type = ArrayType(array.ArrayType)
        except:
            array_type = ArrayType.Unspecified  # arraytype not implemented in ArrayType enum

        if (array_type == ArrayType.Current):
            current_arrays.append(_get_values_from_NETArray(array))

            # # get the current range the current was measured in
            # currentranges = __getcurrentrangesfromcurrentarray(array)
            # # get the status of the meausured data point
            # currentstatus = __getstatusfromcurrentorpotentialarray(array)

        elif (array_type == ArrayType.Potential):
            potential_arrays.append(_get_values_from_NETArray(array))
            # # Get the status of the meausured data point
            # potentialStatus = __getstatusfromcurrentorpotentialarray(array)
        elif (array_type == ArrayType.Time):
            time_arrays.append(_get_values_from_NETArray(array))
            # # Get the status of the meausured data point
            # potentialStatus = __getstatusfromcurrentorpotentialarray(array)
        elif (array_type == ArrayType.Frequency):
            freq_arrays.append((_get_values_from_NETArray(array)))
        elif (array_type == ArrayType.ZRe):
            zre_arrays.append((_get_values_from_NETArray(array)))
        elif (array_type == ArrayType.ZIm):
            zim_arrays.append((_get_values_from_NETArray(array)))

        elif (array_type == ArrayType.AuxInput):
            aux_input_arrays.append((_get_values_from_NETArray(array)))


    if load_peak_data:
        for curve in curves:
            if curve.Peaks is not None:
                for peak in curve.Peaks:
                    peaks.append(Peak(str(curve.Title), peak.PeakValue, peak.PeakX))

    if load_eis_fits:
        if eisdatas is not None:
            for eisdata in eisdatas:
                if eisdata is not None:
                    eis_fits.append(EISFitResult(eisdata.CDC, eisdata.CDCValues))

    measurement = Measurement(m.Title, m.TimeStamp.ToString(),
                       current_arrays, potential_arrays, time_arrays, freq_arrays, zre_arrays, zim_arrays, aux_input_arrays,
                       peaks, eis_fits, convert_to_curves(m, return_dotnet_object=return_dotnet_object))

    if return_dotnet_object:
        measurement.dotnet_measurement = m

    return measurement


def convert_to_curves(m, **kwargs):
    return_dotnet_object = kwargs.get('return_dotnet_object', False)

    curves = []
    peaks = []

    curves_net = m.GetCurveArray()
    for c in curves_net:
        if c.Peaks is not None:
            for peak in c.Peaks:
                peaks.append(Peak(str(c.Title), peak.PeakValue, peak.PeakX))

        if return_dotnet_object:
            curve = Curve(c.Title, _get_values_from_NETArray(c.XAxisDataArray), _get_values_from_NETArray(c.YAxisDataArray), peaks=peaks, dotnet_curve=c)
        else:
            curve = Curve(c.Title, _get_values_from_NETArray(c.XAxisDataArray), _get_values_from_NETArray(c.YAxisDataArray), peaks=peaks)
        curves.append(curve)
    return curves


class ArrayType(Enum):
    Unspecified = -1
    Time = 0
    Potential = 1
    Current = 2
    Charge = 3
    ExtraValue = 4
    Frequency = 5
    Phase = 6
    ZRe = 7
    ZIm = 8
    Iac = 9
    Z = 10
    Y = 11
    YRe = 12
    YIm = 13
    Cs = 14
    CsRe = 15
    CsIm = 16
    Index = 17
    Admittance = 18
    Concentration = 19
    Signal = 20
    Func = 21
    Integral = 22
    AuxInput = 23
    BipotCurrent = 24
    BipotPotential = 25
    ReverseCurrent = 26
    CEPotential = 27
    DCCurrent = 28
    ForwardCurrent = 29
    PotentialExtraRE = 30
    CurrentExtraWE = 31
    InverseDerative_dtdE = 32
    mEdc = 33
    Eac = 34
    MeasuredStepStartIndex = 35
    miDC = 36


class Status(Enum):
    Unknown = -1
    OK = 0
    Overload = 1
    Underload = 2


def _get_values_from_NETArray(array, **kwargs):
    start = kwargs.get('start', 0)
    count = kwargs.get('count', array.Count)
    values = list()
    for i in range(start, start + count):
        value = array.get_Item(i)
        values.append(float(value.Value))
    return values


def __get_currentranges_from_currentarray(arraycurrents, **kwargs):
    start = kwargs.get('start', 0)
    count = kwargs.get('count', arraycurrents.Count)
    values = list()
    if (ArrayType(arraycurrents.ArrayType) == ArrayType.Current):
        for i in range(start, count):
            value = arraycurrents.get_Item(i)
            values.append(str(value.CurrentRange.ToString()))
    return values


def __get_status_from_current_or_potentialarray(array, **kwargs):
    start = kwargs.get('start', 0)
    count = kwargs.get('count', array.Count)
    values = list()
    for i in range(start, count):
        value = array.get_Item(i)
        values.append(str(Status(value.ReadingStatus)))
    return values

if __name__ == "__main__":
    pass
