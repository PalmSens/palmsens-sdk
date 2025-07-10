from ._shared import ArrayType, _get_values_from_NETArray
from .curve import Curve
from .fit_result import EISFitResult
from .measurement import Measurement
from .peak import Peak


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
        except Exception:
            array_type = ArrayType.Unspecified  # arraytype not implemented in ArrayType enum

        if array_type == ArrayType.Current:
            current_arrays.append(_get_values_from_NETArray(array))

            # # get the current range the current was measured in
            # currentranges = __getcurrentrangesfromcurrentarray(array)
            # # get the status of the meausured data point
            # currentstatus = __getstatusfromcurrentorpotentialarray(array)

        elif array_type == ArrayType.Potential:
            potential_arrays.append(_get_values_from_NETArray(array))
            # # Get the status of the meausured data point
            # potentialStatus = __getstatusfromcurrentorpotentialarray(array)
        elif array_type == ArrayType.Time:
            time_arrays.append(_get_values_from_NETArray(array))
            # # Get the status of the meausured data point
            # potentialStatus = __getstatusfromcurrentorpotentialarray(array)
        elif array_type == ArrayType.Frequency:
            freq_arrays.append(_get_values_from_NETArray(array))
        elif array_type == ArrayType.ZRe:
            zre_arrays.append(_get_values_from_NETArray(array))
        elif array_type == ArrayType.ZIm:
            zim_arrays.append(_get_values_from_NETArray(array))

        elif array_type == ArrayType.AuxInput:
            aux_input_arrays.append(_get_values_from_NETArray(array))

    if load_peak_data:
        for curve in curves:
            if curve.Peaks is not None:
                peaks.extend([Peak(dotnet_peak=peak) for peak in curve.Peaks])

    if load_eis_fits:
        if eisdatas is not None:
            for eisdata in eisdatas:
                if eisdata is not None:
                    eis_fits.append(EISFitResult(eisdata.CDC, eisdata.CDCValues))

    measurement = Measurement(
        m.Title,
        m.TimeStamp.ToString(),
        current_arrays,
        potential_arrays,
        time_arrays,
        freq_arrays,
        zre_arrays,
        zim_arrays,
        aux_input_arrays,
        peaks,
        eis_fits,
        convert_to_curves(m, return_dotnet_object=return_dotnet_object),
    )

    if return_dotnet_object:
        measurement.dotnet_measurement = m

    return measurement


def convert_to_curves(m, return_dotnet_object: bool = False):
    curves = []
    peaks = []

    curves_net = m.GetCurveArray()
    for curve in curves_net:
        if curve.Peaks is not None:
            peaks.extend([Peak(dotnet_peak=peak) for peak in curve.Peaks])

        if return_dotnet_object:
            curve = Curve(
                curve.Title,
                _get_values_from_NETArray(curve.XAxisDataArray),
                _get_values_from_NETArray(curve.YAxisDataArray),
                peaks=peaks,
                dotnet_curve=curve,
            )
        else:
            curve = Curve(
                curve.Title,
                _get_values_from_NETArray(curve.XAxisDataArray),
                _get_values_from_NETArray(curve.YAxisDataArray),
                peaks=peaks,
            )
        curves.append(curve)

    return curves
