from __future__ import annotations

from typing import TYPE_CHECKING, Literal, NamedTuple, Self, final

import System
from PalmSens import Analysis as PSAnalysis
from PalmSens.Calculations import MathFunctions as PSMath
from PalmSens.Plottables import Curve as PSCurve
from pydantic import TypeAdapter
from pydantic.dataclasses import dataclass as pydantic_dataclass
from typing_extensions import override

from .data_array import DataArray
from .peak import Peak

if TYPE_CHECKING:
    from matplotlib import axes, figure


@pydantic_dataclass
class CurveMetadata:
    title: str
    """Measurement title."""
    columns: list[str]
    """Names for data values."""
    units: list[str]
    """Units for data values."""
    labels: list[str]
    """Labels for data values."""
    id: int
    """Curve identifier."""
    type: Literal['curve'] = 'curve'
    """Object type."""


@final
class Curve:
    """Curve class with X and Y data of a single curve.

    Parameters
    ----------
    x : DataArray
        Data values for the x axis
    y : DataArray
        Data values for the y axis
    title : str, optional
        Title for the curve

    Notes
    -----
    Supports arithmetic between curves. ``curve_a + curve_b`` and
    ``curve_a - curve_b`` return new curves.
    """

    __slots__ = ('_inner',)

    def __init__(self, x: DataArray, y: DataArray, *, title: str = 'Curve'):
        self._inner = PSCurve(x._inner, y._inner, title)

    @classmethod
    def _wrap(cls, inner: PSCurve) -> Self:
        obj = cls.__new__(cls)
        obj._inner = inner
        return obj

    def __add__(self, other: object) -> Self:
        if not isinstance(other, Curve):
            return NotImplemented

        operator = PSMath.enumOperator.Add
        new_curve = PSMath.AddSubtractCurves(self._inner, other._inner, operator)

        return type(self)._wrap(new_curve)

    __radd__ = __add__

    def __sub__(self, other: object) -> Self:
        if not isinstance(other, Curve):
            return NotImplemented

        operator = PSMath.enumOperator.Subtract
        new_curve = PSMath.AddSubtractCurves(self._inner, other._inner, operator)

        return type(self)._wrap(new_curve)

    def __rsub__(self, other: object) -> Self:
        if not isinstance(other, Curve):
            return NotImplemented

        operator = PSMath.enumOperator.Subtract
        new_curve = PSMath.AddSubtractCurves(other._inner, self._inner, operator)

        return type(self)._wrap(new_curve)

    @override
    def __repr__(self):
        return f'{type(self).__name__}(title={self.title}, n_points={self.n_points})'

    def concat(self, other: Curve) -> Self:
        """Concatenate the x and y arrays of this curve with another curve.

        Parameters
        ----------
        other: Curve
            Curve whose points are appended after this curve's points.

        Returns
        -------
        Curve
            New curve with the concatenated x and y arrays.
        """
        new_curve = PSMath.AppendCurves(self._inner, other._inner)

        return type(self)._wrap(new_curve)

    def copy(self) -> Curve:
        """Return a copy of this curve."""
        return Curve._wrap(PSCurve(self._inner, cloneData=True))

    def smooth(self, smooth_level: int = 0):
        """Smooth the .y_array using a Savitsky-Golay filter with the specified smooth
        level.

        Parameters
        ----------
        smooth_level : int
            The smooth level to be used. -1 = none, 0 = no smooth (spike rejection only),
            1 = 5 points, 2 = 9 points, 3 = 15 points, 4 = 25 points
        """
        success = self._inner.Smooth(smoothLevel=smooth_level)
        if not success:
            raise ValueError('Something went wrong.')

    def savitsky_golay(self, window_size: int = 3):
        """Smooth the .y_array using a Savitsky-Golay filter with the specified window
        size.

        (i.e. window size 2 will filter points based on the values of the next/previous 2 points)

        Parameters
        ----------
        window_size : int
            Size of the window
        """
        self._inner.SavitskyGolay(windowSize=window_size)

    def find_peaks(
        self,
        min_peak_width: float = 0.1,
        min_peak_height: float = 0.0,
        peak_shoulders: bool = False,
        merge_overlapping_peaks: bool = True,
    ) -> list[Peak]:
        """Find peaks in a curve in all directions.

        CV can have 1 or 2 direction changes.

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
        pspeaks = self._inner.FindPeaks(
            minPeakWidth=min_peak_width,
            minPeakHeight=min_peak_height,
            peakShoulders=peak_shoulders,
            mergeOverlappingPeaks=merge_overlapping_peaks,
        )

        peaks_list = [Peak._wrap(peak) for peak in pspeaks]

        return peaks_list

    def find_peaks_semiderivative(
        self,
        min_peak_height: float = 0.0,
    ) -> list[Peak]:
        """
        Find peaks in a curve using the semi-derivative algorithm.

        Used for detecting non-overlapping peaks in LSV and CV curves.
        The peaks are also assigned to the curve, updating `Curve.peaks`.
        Existing peaks are overwritten.

        For more info, see this
        [Wikipedia page](https://en.wikipedia.org/wiki/Neopolarogram).

        Parameters
        ----------
        min_peak_height : float
            Minimum height of the peak in uA

        Returns
        -------
        peak_list : list[Peak]
        """
        dct = System.Collections.Generic.Dictionary[PSCurve, System.Double]()
        dct[self._inner] = min_peak_height

        pd = PSAnalysis.SemiDerivativePeakDetection()
        pd.GetNonOverlappingPeaks(dct)

        return self.peaks

    def remove_baseline(
        self,
        max_sweeps: int = 1001,
        window_size: int = 2,
        mode: Literal['moving-average'] = 'moving-average',
    ) -> tuple[Curve, Curve]:
        """Perform the moving average baseline correction on a curve.

        This method calculates and applies a baseline correction using a specified
        moving average window size and a maximum number of sweeps allowed.

        Parameters
        ----------
        max_sweeps : int, optional
            The maximum number of sweeps allowed during the baseline correction process.
            Defaults to 1001.
        window_size : int, optional
            The size of the moving average window used for calculating the baseline.
            Defaults to 2.
        mode : str, optional
            The method used for baseline correction (e.g., 'moving-average').
            Defaults to 'moving-average'.

        Returns
        -------
        BaselineResult
            A named tuple containing:

            - `corrected` : The baseline-corrected curve.
            - `baseline` : The calculated baseline curve that was subtracted.

        Examples
        --------
        Unpacking as a tuple:
        >>> corrected, baseline = curve.remove_baseline(max_sweeps=500, window_size=2)

        Attribute access:
        >>> result = curve.remove_baseline(max_sweeps=500, window_size=2)
        >>> result.corrected, result.baseline
        """

        assert mode == 'moving-average'

        class BaselineResult(NamedTuple):
            corrected: Curve
            baseline: Curve

        _corrected = PSAnalysis.BaselineCorrection.GetMovingAverageBaselineCorrected(
            self._inner, nWindowSize=window_size, maxNSweeps=max_sweeps, baseline=False
        )
        _corrected.Title = self.title + ' (corrected)'
        _baseline = PSAnalysis.BaselineCorrection.GetMovingAverageBaselineCorrected(
            self._inner, nWindowSize=window_size, maxNSweeps=max_sweeps, baseline=True
        )
        _baseline.Title = self.title + ' (baseline)'

        return BaselineResult(
            corrected=Curve._wrap(_corrected), baseline=Curve._wrap(_baseline)
        )

    @property
    def max_x(self) -> float:
        """Maximum X value found in this curve."""
        return self._inner.MaxX

    @property
    def max_y(self) -> float:
        """Maximum Y value found in this curve."""
        return self._inner.MaxY

    @property
    def min_x(self) -> float:
        """Minimum X value found in this curve."""
        return self._inner.MinX

    @property
    def min_y(self) -> float:
        """Minimum Y value found in this curve."""
        return self._inner.MinY

    @property
    def mux_channel(self) -> int:
        """The corresponding MUX channel number with the curve starting at 0.
        Return -1 when no MUX channel used."""
        return self._inner.MuxChannel

    @property
    def n_points(self) -> int:
        """Number of points for this curve."""
        return len(self)

    def __len__(self):
        return self._inner.NPoints

    @property
    def ocp_value(self) -> float:
        """OCP value for curve."""
        return self._inner.OCPValue

    @property
    def x_unit(self) -> str:
        """Units for X dimension."""
        return self._inner.XUnit.ToString()

    @property
    def x_label(self) -> str:
        """Label for X dimension."""
        return self._inner.XUnit.Quantity

    @property
    def y_unit(self) -> str:
        """Units for Y dimension."""
        return self._inner.YUnit.ToString()

    @property
    def y_label(self) -> str:
        """Label for Y dimension."""
        return self._inner.YUnit.Quantity

    @property
    def z_unit(self) -> None | str:
        """Units for Z dimension. Returns None if not set."""
        if ret := self._inner.ZUnit:
            return ret.ToString()
        return None

    @property
    def z_label(self) -> None | str:
        """Units for Z dimension. Returns None if not set."""
        if ret := self._inner.ZUnit:
            return ret.Quantity
        return None

    @property
    def title(self) -> str:
        """Title for the curve."""
        return self._inner.Title

    @title.setter
    def title(self, title: str):
        """Set the title for the curve."""
        self._inner.Title = title

    @property
    def id(self) -> int:
        """Unique identifier for curve object."""
        return self._inner.GetHashCode()

    def metadata(self) -> CurveMetadata:
        """Generate curve metadata as dataclass."""
        return CurveMetadata(
            title=self.title,
            columns=['x', 'y'],
            units=[self.x_unit, self.y_unit],
            labels=[self.x_label, self.y_label],
            id=self.id,
        )

    def metadata_json(self) -> bytes:
        """Generate curve metadata as json."""
        return TypeAdapter(CurveMetadata).dump_json(self.metadata())

    @property
    def peaks(self) -> list[Peak]:
        """Return peaks stored on object."""
        try:
            peaks = [Peak._wrap(peak) for peak in self._inner.Peaks]
        except TypeError:
            peaks = []
        return peaks

    def clear_peaks(self):
        """Clear peaks stored on object."""
        self._inner.ClearPeaks()

    @property
    def x_array(self) -> DataArray:
        """Y data for the curve."""
        return DataArray._wrap_dispatched(self._inner.XAxisDataArray)

    @property
    def y_array(self) -> DataArray:
        """Y data for the curve."""
        return DataArray._wrap_dispatched(self._inner.YAxisDataArray)

    def linear_slope(
        self, start: None | int = None, stop: None | int = None
    ) -> tuple[float, float, float]:
        """Calculate linear line parameters for this curve between two indexes.

        current = a + b * x

        Parameters
        ----------
        start : int, optional
            begin index
        stop : int, optional
            end index

        Returns
        -------
        a : float
        b : float
        coefdet : float
            Coefficient of determination (R2)
        """
        if start and stop:
            return self._inner.LLS(start, stop)
        else:
            return self._inner.LLS()

    def plot(
        self,
        ax: None | axes.Axes = None,
        legend: bool = True,
        **plot_kwargs,
    ) -> figure.Figure | figure.SubFigure:
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
            _, ax = plt.subplots()

        _ = ax.plot(self.x_array, self.y_array, label=self.title, **plot_kwargs)
        _ = ax.set_xlabel(f'{self.x_label} ({self.x_unit})')
        _ = ax.set_ylabel(f'{self.y_label} ({self.y_unit})')

        if peaks := self.peaks:
            x, y = list(zip(*((peak.x, peak.y) for peak in peaks)))
            _ = ax.scatter(x, y, label='Peaks')

        if legend:
            _ = ax.legend()

        return ax.figure
