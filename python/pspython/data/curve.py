from ._shared import _get_values_from_NETArray
from .peak import Peak


class Curve:
    def __init__(self, title, x_array, y_array, **kwargs):
        self.title = title
        self.x_array = x_array
        self.y_array = y_array
        self.peaks = kwargs.get('peaks', [])
        self.dotnet_curve = kwargs.get('dotnet_curve', [])

    def smooth(self, smooth_level: int):
        """Smooth the .y_array using a Savitsky-Golay filter with the specified smooth
        level.

        Parameters
        ----------
        smooth_level : int
            The smooth level to be used. -1 = none, 0 = no smooth (spike rejection only),
            1 = 5 points, 2 = 9 points, 3 = 15 points, 4 = 25 points
        """
        success = self.dotnet_curve.Smooth(smoothLevel=smooth_level)
        assert success

        self.x_array = _get_values_from_NETArray(self.dotnet_curve.XAxisDataArray)
        self.y_array = _get_values_from_NETArray(self.dotnet_curve.YAxisDataArray)

    def savitsky_golay(self, window_size: int):
        """Smooth the .y_array using a Savitsky-Golay filter with the specified window
        size.

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

    def find_peaks(
        self,
        min_peak_width: float,
        min_peak_height: float,
        peak_shoulders: bool = False,
        merge_overlapping_peaks: bool = True,
    ) -> list[Peak]:
        """
        Find peaks in a curve in all directions; CV can have 1 or 2 direction changes

        Parameters
        ----------
        min_peak_width : float
            Minimum width of the peak in V
        min_peak_height : float
            Minimum height of the peak in uA
        peak_shoulders : bool, optional
            ...
        merge_overlapping_peaks : bool, optional
            ...

        Returns
        -------
        peak_list : list[Peak]
        """
        dotnet_peaks = self.dotnet_curve.FindPeaks(
            minPeakWidth=min_peak_width,
            minPeakHeight=min_peak_height,
            peakShoulders=peak_shoulders,
            mergeOverlappingPeaks=merge_overlapping_peaks,
        )

        peaks_list = [Peak(dotnet_peak=peak) for peak in dotnet_peaks]

        return peaks_list
