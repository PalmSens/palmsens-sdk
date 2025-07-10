class Measurement:
    def __init__(
        self,
        title: str,
        timestamp,
        current_arrays,
        potential_arrays,
        time_arrays,
        freq_arrays,
        zre_arrays,
        zim_arrays,
        aux_input_arrays,
        peaks,
        eis_fit,
        curves=[],
        dotnet_measurement=None,
    ):
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
