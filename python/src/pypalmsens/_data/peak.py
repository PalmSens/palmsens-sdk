from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PalmSens.Analysis import Peak as PSPeak

    from .curve import Curve


class Peak:
    """Python wrapper for .NET Peak class.

    Parameters
    ----------
    pspeak : PalmSens.Analysis.Peak
        Reference to .NET Peak object.
    """

    def __init__(self, *, pspeak: PSPeak):
        self._pspeak = pspeak

        self._curve: Curve | None = None

    def __repr__(self):
        x_unit = self.x_unit
        y_unit = self.y_unit

        return (
            f'{self.__class__.__name__}('
            f'x={self.x:g} {x_unit}, '
            f'y={self.y:g} {y_unit}, '
            f'y_offset={self.y_offset:g} {y_unit}, '
            f'area={self.area:g} {x_unit}{y_unit}, '
            f'width={self.width:g} {x_unit})'
        )

    @property
    def curve(self) -> Curve:
        """Parent curve associated with Peak."""
        from .curve import Curve

        if not self._curve:
            self._curve = Curve(pscurve=self._pspeak.Curve)
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
        """Units for Y axis"""
        return self.curve.y_unit

    @property
    def analyte_name(self) -> str:
        """Name of analyte."""
        return self._pspeak.AnalyteName

    @analyte_name.setter
    def analyte_name(self, name: str):
        """Set name of analyte."""
        self._pspeak.set_AnalyteName(name)

    @property
    def area(self) -> float:
        """Area of the peak."""
        return self._pspeak.Area

    @property
    def label(self) -> str:
        """Formatted label for the peak value."""
        return self._pspeak.Label

    @property
    def left_index(self) -> int:
        """Left side of the peaks baseline as index number of the curve."""
        return self._pspeak.LeftIndex

    @property
    def left_x(self) -> float:
        """X of the left side of the peak baseline."""
        return self._pspeak.LeftX

    @property
    def left_y(self) -> float:
        """Y of the left side of the peak baseline."""
        return self._pspeak.LeftY

    @property
    def maximum_of_derivative_neg(self) -> float:
        """Maximum derivative of the negative slope of the peak."""
        return self._pspeak.MaximumOfDerivativeNeg

    @property
    def maximum_of_derivative_pos(self) -> float:
        """Maximum derivative of the positive slope of the peak."""
        return self._pspeak.MaximumOfDerivativePos

    @property
    def maximum_of_derivative_sum(self) -> float:
        """Sum of the absolute values for both the positive and negative maximum derivative."""
        return self._pspeak.MaximumOfDerivativeSum

    @property
    def notes(self) -> str:
        """User notes stored on this peak."""
        return self._pspeak.Notes

    @property
    def y_offset(self) -> float:
        """Offset of Y."""
        return self._pspeak.OffsetY

    @property
    def index(self) -> int:
        """Location of the peak as index number of the curve."""
        return self._pspeak.PeakIndex

    @property
    def type(self) -> str:
        """Used to determine if a peak is auto found."""
        return str(self._pspeak.PeakType)

    @property
    def value(self) -> float:
        """Value of the peak in units of the curve.
        This is the value of the peak height relative to the baseline of the peak."""
        return self._pspeak.PeakValue

    @property
    def x(self) -> float:
        """X value of the peak."""
        return self._pspeak.PeakX

    @property
    def y(self) -> float:
        """Y value of the peak."""
        return self._pspeak.PeakY

    @property
    def right_index(self) -> int:
        """Left side of the peaks baseline as index number of the curve."""
        return self._pspeak.RightIndex

    @property
    def right_x(self) -> float:
        """X of the right side of the peak baseline."""
        return self._pspeak.RightX

    @property
    def right_y(self) -> float:
        """Returns the Y of the right side of the peak baseline."""
        return self._pspeak.RightY

    @property
    def width(self) -> float:
        """Full width at half-height of the peak."""
        return self._pspeak.Width
