from typing import Optional, Union

from .peak import Peak


class Curve:
    """Python wrapper for dotnet Curve class."""

    def __init__(self, *, dotnet_curve):
        self.dotnet_curve = dotnet_curve

    def __str__(self):
        return f'{self.__class__.__name__}(n_points={self.n_points})'

    def smooth(self, smooth_level: int):
        """Smooth the .y_array using a Savitsky-Golay filter with the specified smooth
        level.

        Parameters
        ----------
        smooth_level : int
            The smooth level to be used. -1 = none, 0 = no smooth (spike rejection only),
            1 = 5 points, 2 = 9 points, 3 = 15 points, 4 = 25 points
        """
        return self.dotnet_curve.Smooth(smoothLevel=smooth_level)

    def savitsky_golay(self, window_size: int):
        """Smooth the .y_array using a Savitsky-Golay filter with the specified window
        size.

        (i.e. window size 2 will filter points based on the values of the next/previous 2 points)

        Parameters
        ----------
        window_size : int
            Size of the window
        """
        return self.dotnet_curve.SavitskyGolay(windowSize=window_size)

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
            Use alternative peak search algorithm optimized for finding peaks on slopes
        merge_overlapping_peaks : bool, optional
            Two or more peaks that overlap will be identified as a single
            base peak and as shoulder peaks on the base peak.

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

    @property
    def max_x(self) -> float:
        """Maximum X value found in this curve."""
        return self.dotnet_curve.MaxX

    @property
    def max_y(self) -> float:
        """Maximum Y value found in this curve."""
        return self.dotnet_curve.MaxY

    @property
    def min_x(self) -> float:
        """Minimum X value found in this curve."""
        return self.dotnet_curve.MinX

    @property
    def min_y(self) -> float:
        """Minimum Y value found in this curve."""
        return self.dotnet_curve.MinY

    @property
    def mux_channel(self) -> int:
        """The corresponding MUX channel number with the curve starting at 0.
        Return -1 when no MUX channel used."""
        return self.dotnet_curve.MuxChannel

    @property
    def n_points(self) -> int:
        """Number of points for this curve."""
        return len(self)

    def __len__(self):
        return self.dotnet_curve.NPoints

    @property
    def reference_electrode_name(self) -> Union[None, str]:
        """The name of the reference electrode. Return None if not set."""
        if ret := self.dotnet_curve.ReferenceElectrodeName:
            return str(ret)
        return None

    @property
    def reference_electrode_potential(self) -> Union[None, str]:
        """The reference electrode potential offset. Return None if not set."""
        if ret := self.dotnet_curve.ReferenceElectrodePotential:
            return str(ret)
        return None

    @property
    def x_unit(self) -> str:
        """Units for X dimension."""
        return self.dotnet_curve.XUnit.ToString()

    @property
    def x_label(self) -> str:
        """Label for X dimension."""
        return self.dotnet_curve.XUnit.Quantity

    @property
    def y_unit(self) -> str:
        """Units for Y dimension."""
        return self.dotnet_curve.YUnit.ToString()

    @property
    def y_label(self) -> str:
        """Label for Y dimension."""
        return self.dotnet_curve.YUnit.Quantity

    @property
    def z_unit(self) -> Union[None, str]:
        """Units for Z dimension. Returns None if not set."""
        if ret := self.dotnet_curve.ZUnit:
            return ret.ToString()
        return None

    @property
    def z_label(self) -> Union[None, str]:
        """Units for Z dimension. Returns None if not set."""
        if ret := self.dotnet_curve.ZUnit:
            return ret.Quantity
        return None

    @property
    def title(self) -> str:
        """Title for the curve."""
        return self.dotnet_curve.Title

    @title.setter
    def title(self, title: str):
        """Set the title for the curve."""
        self.dotnet_curve.Title = title

    @property
    def peaks(self) -> list[Peak]:
        """Return peaks stored on object."""
        return [Peak(dotnet_peak=peak) for peak in self.dotnet_curve.Peaks]

    def clear_peaks(self):
        """Clear peaks stored on object."""
        self.dotnet_curve.ClearPeaks()

    @property
    def x_array(self) -> list[float]:
        """Y data for the curve"""
        return list(self.dotnet_curve.GetXValues())

    @property
    def y_array(self) -> list[float]:
        """Y data for the curve."""
        return list(self.dotnet_curve.GetYValues())

    def linear_slope(
        self, start: Optional[int] = None, stop: Optional[int] = None
    ) -> tuple[float, float, float]:
        """Calculate linear line parameters for this curve between two indexes.

        current = a + b * x

        Parameters
        ----------
        from : int, optional
            begin index
        to : int, optional
            end index

        Returns
        -------
        a : float
        b : float
        coefdet : float
            Coefficient of determination (R2)
        """
        if start and stop:
            return self.dotnet_curve.LLS(start, stop)
        else:
            return self.dotnet_curve.LLS()

    # FindLevels
    # ClearLevels
    # Levels

    def plot(self):
        """Generate simple plot for this curve using matplotlib."""
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        ax.plot(self.x_array, self.y_array, label=self.title)
        ax.set_xlabel(f'{self.x_label} / {self.x_label}')
        ax.set_xlabel(f'{self.y_label} / {self.y_label}')

        if peaks := self.peaks:
            x, y = list(zip(*((peak.x, peak.y) for peak in peaks)))
            ax.scatter(x, y, label='Peaks')

        plt.legend()
