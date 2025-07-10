class Peak:
    """Python wrapper for dotnet Peak class."""

    def __init__(self, *, dotnet_peak):
        self.dotnet_peak = dotnet_peak

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
    def curve_title(self) -> str:
        return self.dotnet_peak.Curve.Title

    @property
    def x_unit(self) -> str:
        """Get units of X axis"""
        return self.dotnet_peak.Curve.get_XUnit()

    @property
    def y_unit(self) -> str:
        """Get units for Y axis"""
        return self.dotnet_peak.Curve.get_YUnit()

    @property
    def analyte_name(self) -> str:
        return self.dotnet_peak.AnalyteName

    @analyte_name.setter
    def analyte_name(self, name: str):
        self.dotnet_peak.set_AnalyteName(name)

    @property
    def area(self) -> float:
        return self.dotnet_peak.Area

    @property
    def label(self) -> str:
        return self.dotnet_peak.Label

    @property
    def left_index(self) -> int:
        return self.dotnet_peak.LeftIndex

    @property
    def left_x(self) -> float:
        return self.dotnet_peak.LeftX

    @property
    def left_y(self) -> float:
        return self.dotnet_peak.LeftY

    @property
    def maximum_of_derivative_neg(self) -> float:
        return self.dotnet_peak.MaximumOfDerivativeNeg

    @property
    def maximum_of_derivative_pos(self) -> float:
        return self.dotnet_peak.MaximumOfDerivativePos

    @property
    def maximum_of_derivative_sum(self) -> float:
        return self.dotnet_peak.MaximumOfDerivativeSum

    @property
    def notes(self) -> str:
        return self.dotnet_peak.Notes

    @property
    def offset_y(self) -> float:
        return self.dotnet_peak.OffsetY

    @property
    def index(self) -> int:
        return self.dotnet_peak.PeakIndex

    @property
    def type(self) -> str:
        return str(self.dotnet_peak.PeakType)

    @property
    def value(self) -> float:
        return self.dotnet_peak.PeakValue

    peak_height = value  # alias for backward compatibility

    @property
    def x(self) -> float:
        return self.dotnet_peak.PeakX

    @property
    def y(self) -> float:
        return self.dotnet_peak.PeakY

    @property
    def right_index(self) -> int:
        return self.dotnet_peak.RightIndex

    @property
    def right_x(self) -> float:
        return self.dotnet_peak.RightX

    @property
    def right_y(self) -> float:
        return self.dotnet_peak.RightY

    @property
    def width(self) -> float:
        return self.dotnet_peak.Width
