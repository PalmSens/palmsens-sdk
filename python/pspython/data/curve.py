from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Union

from .peak import Peak

if TYPE_CHECKING:
    from matplotlib import axes, fig


class Curve:
    """Python wrapper for dotnet Curve class."""

    def __init__(self, *, pscurve):
        self.pscurve = pscurve

    def __str__(self):
        return f'{self.__class__.__name__}(title={self.title}, n_points={self.n_points})'

    def smooth(self, smooth_level: int):
        """Smooth the .y_array using a Savitsky-Golay filter with the specified smooth
        level.

        Parameters
        ----------
        smooth_level : int
            The smooth level to be used. -1 = none, 0 = no smooth (spike rejection only),
            1 = 5 points, 2 = 9 points, 3 = 15 points, 4 = 25 points
        """
        return self.pscurve.Smooth(smoothLevel=smooth_level)

    def savitsky_golay(self, window_size: int):
        """Smooth the .y_array using a Savitsky-Golay filter with the specified window
        size.

        (i.e. window size 2 will filter points based on the values of the next/previous 2 points)

        Parameters
        ----------
        window_size : int
            Size of the window
        """
        return self.pscurve.SavitskyGolay(windowSize=window_size)

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
        pspeaks = self.pscurve.FindPeaks(
            minPeakWidth=min_peak_width,
            minPeakHeight=min_peak_height,
            peakShoulders=peak_shoulders,
            mergeOverlappingPeaks=merge_overlapping_peaks,
        )

        peaks_list = [Peak(pspeak=peak) for peak in pspeaks]

        return peaks_list

    @property
    def max_x(self) -> float:
        """Maximum X value found in this curve."""
        return self.pscurve.MaxX

    @property
    def max_y(self) -> float:
        """Maximum Y value found in this curve."""
        return self.pscurve.MaxY

    @property
    def min_x(self) -> float:
        """Minimum X value found in this curve."""
        return self.pscurve.MinX

    @property
    def min_y(self) -> float:
        """Minimum Y value found in this curve."""
        return self.pscurve.MinY

    @property
    def mux_channel(self) -> int:
        """The corresponding MUX channel number with the curve starting at 0.
        Return -1 when no MUX channel used."""
        return self.pscurve.MuxChannel

    @property
    def n_points(self) -> int:
        """Number of points for this curve."""
        return len(self)

    def __len__(self):
        return self.pscurve.NPoints

    @property
    def ocp_value(self) -> float:
        """OCP value for curve."""
        return self.pscurve.OCPValue

    @property
    def reference_electrode_name(self) -> Union[None, str]:
        """The name of the reference electrode. Return None if not set."""
        if ret := self.pscurve.ReferenceElectrodeName:
            return str(ret)
        return None

    @property
    def reference_electrode_potential(self) -> Union[None, str]:
        """The reference electrode potential offset. Return None if not set."""
        if ret := self.pscurve.ReferenceElectrodePotential:
            return str(ret)
        return None

    @property
    def x_unit(self) -> str:
        """Units for X dimension."""
        return self.pscurve.XUnit.ToString()

    @property
    def x_label(self) -> str:
        """Label for X dimension."""
        return self.pscurve.XUnit.Quantity

    @property
    def y_unit(self) -> str:
        """Units for Y dimension."""
        return self.pscurve.YUnit.ToString()

    @property
    def y_label(self) -> str:
        """Label for Y dimension."""
        return self.pscurve.YUnit.Quantity

    @property
    def z_unit(self) -> Union[None, str]:
        """Units for Z dimension. Returns None if not set."""
        if ret := self.pscurve.ZUnit:
            return ret.ToString()
        return None

    @property
    def z_label(self) -> Union[None, str]:
        """Units for Z dimension. Returns None if not set."""
        if ret := self.pscurve.ZUnit:
            return ret.Quantity
        return None

    @property
    def title(self) -> str:
        """Title for the curve."""
        return self.pscurve.Title

    @title.setter
    def title(self, title: str):
        """Set the title for the curve."""
        self.pscurve.Title = title

    @property
    def peaks(self) -> list[Peak]:
        """Return peaks stored on object."""
        try:
            peaks = [Peak(pspeak=peak) for peak in self.pscurve.Peaks]
        except TypeError:
            peaks = []
        return peaks

    def clear_peaks(self):
        """Clear peaks stored on object."""
        self.pscurve.ClearPeaks()

    @property
    def x_array(self) -> list[float]:
        """Y data for the curve"""
        return list(self.pscurve.GetXValues())

    @property
    def y_array(self) -> list[float]:
        """Y data for the curve."""
        return list(self.pscurve.GetYValues())

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
            return self.pscurve.LLS(start, stop)
        else:
            return self.pscurve.LLS()

    def plot(
        self,
        ax: Optional[axes.Axes] = None,
        legend: bool = True,
        **plot_kwargs,
    ) -> fig.Figure:
        """Generate simple plot for this curve using matplotlib.

        Parameters
        ----------
        ax : Optional[axes.Axes]
            Add plot to this ax if specified.
        legend : bool
            If True, add legend.
        plot_kwargs
            These keyword arguments are passed to `ax.plot`.

        Returns
        -------
        fig : fig.Figure
            Matplotlib figure. Use `fig.show()` to render plot.
        """
        import matplotlib.pyplot as plt

        if not ax:
            fig, ax = plt.subplots()

        ax.plot(self.x_array, self.y_array, label=self.title, **plot_kwargs)
        ax.set_xlabel(f'{self.x_label} ({self.x_unit})')
        ax.set_ylabel(f'{self.y_label} ({self.y_unit})')

        if peaks := self.peaks:
            x, y = list(zip(*((peak.x, peak.y) for peak in peaks)))
            ax.scatter(x, y, label='Peaks')

        if legend:
            ax.legend()

        return ax.figure
