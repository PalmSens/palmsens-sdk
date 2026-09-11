from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Self, final

from typing_extensions import override

from .._converters import single_to_double

if TYPE_CHECKING:
    from PalmSens.Analysis import Peak as PSPeak

    from .curve import Curve


@final
class Peak:
    """Contains the peak data of one peak in a curve.

    Notes
    -----
    Obtain internal instances via `_wrap`.
    """

    __slots__: ClassVar[tuple[str, ...]] = ('_inner',)
    _inner: PSPeak  # pyright: ignore[reportUninitializedInstanceVariable]

    def __init__(self):
        raise TypeError(
            'Peak cannot be instantiated directly. Obtain instances through the Curve methods.'
        )

    @classmethod
    def _wrap(cls, pspeak: PSPeak) -> Self:
        obj = cls.__new__(cls)
        obj._inner = pspeak
        return obj

    @override
    def __repr__(self):
        x_unit = self.x_unit
        y_unit = self.y_unit

        return (
            f'{type(self).__name__}('
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

        return Curve._wrap(self._inner.Curve)

    @property
    def analyte_name(self) -> str:
        """Name of analyte."""
        return self._inner.AnalyteName

    @analyte_name.setter
    def analyte_name(self, name: str):
        """Set name of analyte."""
        self._inner.set_AnalyteName(name)

    @property
    def area(self) -> float:
        """Area of the peak."""
        return single_to_double(self._inner.Area)

    @property
    def label(self) -> str:
        """Formatted label for the peak value."""
        return self._inner.Label

    @property
    def left_index(self) -> int:
        """Left side of the peaks baseline as index number of the curve."""
        return self._inner.LeftIndex

    @property
    def left_x(self) -> float:
        """X of the left side of the peak baseline."""
        return single_to_double(self._inner.LeftX)

    @property
    def left_y(self) -> float:
        """Y of the left side of the peak baseline."""
        return single_to_double(self._inner.LeftY)

    @property
    def maximum_of_derivative_neg(self) -> float:
        """Maximum derivative of the negative slope of the peak."""
        return single_to_double(self._inner.MaximumOfDerivativeNeg)

    @property
    def maximum_of_derivative_pos(self) -> float:
        """Maximum derivative of the positive slope of the peak."""
        return single_to_double(self._inner.MaximumOfDerivativePos)

    @property
    def maximum_of_derivative_sum(self) -> float:
        """Sum of the absolute values for both the positive and negative maximum derivative."""
        return single_to_double(self._inner.MaximumOfDerivativeSum)

    @property
    def notes(self) -> str:
        """User notes stored on this peak."""
        return self._inner.Notes

    @property
    def y_offset(self) -> float:
        """Offset of Y."""
        return single_to_double(self._inner.OffsetY)

    @property
    def index(self) -> int:
        """Location of the peak as index number of the curve."""
        return self._inner.PeakIndex

    @property
    def type(self) -> str:
        """Used to determine if a peak is auto found."""
        return str(self._inner.PeakType)

    @property
    def value(self) -> float:
        """Value of the peak in units of the curve.
        This is the value of the peak height relative to the baseline of the peak."""
        return single_to_double(self._inner.PeakValue)

    @property
    def x(self) -> float:
        """X value of the peak."""
        return single_to_double(self._inner.PeakX)

    @property
    def y(self) -> float:
        """Y value of the peak."""
        return single_to_double(self._inner.PeakY)

    @property
    def right_index(self) -> int:
        """Left side of the peaks baseline as index number of the curve."""
        return self._inner.RightIndex

    @property
    def right_x(self) -> float:
        """X of the right side of the peak baseline."""
        return single_to_double(self._inner.RightX)

    @property
    def right_y(self) -> float:
        """Returns the Y of the right side of the peak baseline."""
        return single_to_double(self._inner.RightY)

    @property
    def width(self) -> float:
        """Full width at half-height of the peak."""
        return single_to_double(self._inner.Width)
