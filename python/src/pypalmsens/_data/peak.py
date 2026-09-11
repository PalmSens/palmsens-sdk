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

    __slots__: ClassVar[tuple[str, ...]] = ('_internal',)
    _internal: PSPeak  # pyright: ignore[reportUninitializedInstanceVariable]

    def __init__(self):
        raise TypeError(
            'Peak cannot be instantiated directly. Obtain instances through the Curve methods.'
        )

    @classmethod
    def _wrap(cls, pspeak: PSPeak) -> Self:
        obj = cls.__new__(cls)
        obj._internal = pspeak
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

        return Curve._wrap(self._internal.Curve)

    @property
    def analyte_name(self) -> str:
        """Name of analyte."""
        return self._internal.AnalyteName

    @analyte_name.setter
    def analyte_name(self, name: str):
        """Set name of analyte."""
        self._internal.set_AnalyteName(name)

    @property
    def area(self) -> float:
        """Area of the peak."""
        return single_to_double(self._internal.Area)

    @property
    def label(self) -> str:
        """Formatted label for the peak value."""
        return self._internal.Label

    @property
    def left_index(self) -> int:
        """Left side of the peaks baseline as index number of the curve."""
        return self._internal.LeftIndex

    @property
    def left_x(self) -> float:
        """X of the left side of the peak baseline."""
        return single_to_double(self._internal.LeftX)

    @property
    def left_y(self) -> float:
        """Y of the left side of the peak baseline."""
        return single_to_double(self._internal.LeftY)

    @property
    def maximum_of_derivative_neg(self) -> float:
        """Maximum derivative of the negative slope of the peak."""
        return single_to_double(self._internal.MaximumOfDerivativeNeg)

    @property
    def maximum_of_derivative_pos(self) -> float:
        """Maximum derivative of the positive slope of the peak."""
        return single_to_double(self._internal.MaximumOfDerivativePos)

    @property
    def maximum_of_derivative_sum(self) -> float:
        """Sum of the absolute values for both the positive and negative maximum derivative."""
        return single_to_double(self._internal.MaximumOfDerivativeSum)

    @property
    def notes(self) -> str:
        """User notes stored on this peak."""
        return self._internal.Notes

    @property
    def y_offset(self) -> float:
        """Offset of Y."""
        return single_to_double(self._internal.OffsetY)

    @property
    def index(self) -> int:
        """Location of the peak as index number of the curve."""
        return self._internal.PeakIndex

    @property
    def type(self) -> str:
        """Used to determine if a peak is auto found."""
        return str(self._internal.PeakType)

    @property
    def value(self) -> float:
        """Value of the peak in units of the curve.
        This is the value of the peak height relative to the baseline of the peak."""
        return single_to_double(self._internal.PeakValue)

    @property
    def x(self) -> float:
        """X value of the peak."""
        return single_to_double(self._internal.PeakX)

    @property
    def y(self) -> float:
        """Y value of the peak."""
        return single_to_double(self._internal.PeakY)

    @property
    def right_index(self) -> int:
        """Left side of the peaks baseline as index number of the curve."""
        return self._internal.RightIndex

    @property
    def right_x(self) -> float:
        """X of the right side of the peak baseline."""
        return single_to_double(self._internal.RightX)

    @property
    def right_y(self) -> float:
        """Returns the Y of the right side of the peak baseline."""
        return single_to_double(self._internal.RightY)

    @property
    def width(self) -> float:
        """Full width at half-height of the peak."""
        return single_to_double(self._internal.Width)
