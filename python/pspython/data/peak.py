from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .curve import Curve


class Peak:
    """Python wrapper for dotnet Peak class."""

    def __init__(self, *, dotnet_peak):
        self.dotnet_peak = dotnet_peak
        self._curve = None

    def __str__(self):
        x_unit = self.x_unit
        y_unit = self.y_unit

        return (
            f'{self.__class__.__name__}('
            f'Potential={self.x:g} {x_unit}, '
            f'Height={self.y:g} {y_unit}, '
            f'Y_Offset={self.offset_y:g} {y_unit}, '
            f'Area={self.area:g} {x_unit}{y_unit}, '
            f'Width={self.width:g} {x_unit})'
        )

    @property
    def curve(self) -> Curve:
        """Parent curve associated with Peak."""
        from .curve import Curve

        if not self._curve:
            self._curve = Curve(dotnet_curve=self.dotnet_peak.Curve)
        return self._curve

    @property
    def curve_title(self) -> str:
        """Title of parent curve."""
        return self.curve.title

    @property
    def x_unit(self) -> str:
        """Units of X axis"""
        return self.curve.x_unit

    @property
    def y_unit(self) -> str:
        """Unitss for Y axis"""
        return self.curve.y_unit

    @property
    def analyte_name(self) -> str:
        """Name of analyte."""
        return self.dotnet_peak.AnalyteName

    @analyte_name.setter
    def analyte_name(self, name: str):
        """Set name of analyte."""
        self.dotnet_peak.set_AnalyteName(name)

    @property
    def area(self) -> float:
        """Area of the peak."""
        return self.dotnet_peak.Area

    @property
    def label(self) -> str:
        """Formatted label for the peak value."""
        return self.dotnet_peak.Label

    @property
    def left_index(self) -> int:
        """Left side of the peaks baseline as index number of the curve."""
        return self.dotnet_peak.LeftIndex

    @property
    def left_x(self) -> float:
        """X of the left side of the peak baseline."""
        return self.dotnet_peak.LeftX

    @property
    def left_y(self) -> float:
        """Y of the left side of the peak baseline."""
        return self.dotnet_peak.LeftY

    @property
    def maximum_of_derivative_neg(self) -> float:
        """Maximum derivative of the negative slope of the peak."""
        return self.dotnet_peak.MaximumOfDerivativeNeg

    @property
    def maximum_of_derivative_pos(self) -> float:
        """Maximum derivative of the positive slope of the peak."""
        return self.dotnet_peak.MaximumOfDerivativePos

    @property
    def maximum_of_derivative_sum(self) -> float:
        """Sum of the absolute values for both the positive and negative maximum derivative."""
        return self.dotnet_peak.MaximumOfDerivativeSum

    @property
    def notes(self) -> str:
        """User notes stored on this peak."""
        return self.dotnet_peak.Notes

    @property
    def offset_y(self) -> float:
        """Offset of Y."""
        return self.dotnet_peak.OffsetY

    @property
    def index(self) -> int:
        """Location of the peak as index number of the curve."""
        return self.dotnet_peak.PeakIndex

    @property
    def type(self) -> str:
        """Used to determine if a peak is auto found."""
        return str(self.dotnet_peak.PeakType)

    @property
    def value(self) -> float:
        """Value of the peak in units of the curve.
        This is the value of the peak height relative to the baseline of the peak."""
        return self.dotnet_peak.PeakValue

    peak_height = value  # alias for backward compatibility

    @property
    def x(self) -> float:
        """X value of the peak."""
        return self.dotnet_peak.PeakX

    @property
    def y(self) -> float:
        """Y value of the peak."""
        return self.dotnet_peak.PeakY

    @property
    def right_index(self) -> int:
        """Left side of the peaks baseline as index number of the curve."""
        return self.dotnet_peak.RightIndex

    @property
    def right_x(self) -> float:
        """X of the right side of the peak baseline."""
        return self.dotnet_peak.RightX

    @property
    def right_y(self) -> float:
        """Returns the Y of the right side of the peak baseline."""
        return self.dotnet_peak.RightY

    @property
    def width(self) -> float:
        """Full width at half-height of the peak."""
        return self.dotnet_peak.Width
