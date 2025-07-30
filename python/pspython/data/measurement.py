from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from PalmSens import Measurement as PSMeasurement

from ..methods.method import Method
from .curve import Curve
from .dataset import DataSet
from .eisdata import EISData
from .fit_result import EISFitResult
from .peak import Peak


@dataclass(frozen=True)
class DeviceInfo:
    """Dataclass for device information.

    Attributes
    ----------
    type : str
        Device type
    firmware : str
        Firmware version
    serial : str
        Serial number
    id : int
        Device ID
    """

    type: str
    firmware: str
    serial: str
    id: int

    @classmethod
    def from_psmeasurement(cls, obj: PSMeasurement) -> DeviceInfo:
        return cls(
            type=obj.DeviceUsed.ToString(),
            firmware=obj.DeviceUsedFW,
            serial=obj.DeviceUsedSerial,
            id=int(obj.DeviceUsed),
        )


@dataclass
class Measurement:
    """Python wrapper for dotnet Measurement class."""

    def __init__(self, *, psmeasurement):
        self.psmeasurement = psmeasurement

    def __repr__(self):
        return f'{self.__class__.__name__}(title={self.title}, timestamp={self.timestamp})'

    @property
    def title(self) -> str:
        """Title for the measurement."""
        return self.psmeasurement.Title

    @property
    def timestamp(self) -> str:
        """Date and time of the start of this measurement.."""
        return str(self.psmeasurement.TimeStamp)

    @property
    def device(self) -> DeviceInfo:
        """Return dataclass with measurement device information."""
        return DeviceInfo.from_psmeasurement(self.psmeasurement)

    @property
    def blank_curve(self) -> Curve:
        """Blank curve.

        if Blank curve is present (not null) a new curve will be added after each measurement
        containing the result of the measured curve subtracted with the Blank curve.
        """
        return self.psmeasurement.BlankCurve

    @property
    def contains_blank_subtracted_curves(self) -> bool:
        """Return True if the curve collection contains a blank subtracted curve."""
        return self.psmeasurement.ContainsBlankSubtractedCurves

    @property
    def contains_eis_data(self) -> bool:
        """Return True if EIS data are is available."""
        return self.psmeasurement.ContainsEISData

    @property
    def dataset(self) -> DataSet:
        """Dataset containing multiple arrays of values.

        All values are related by means of their indices.
        Data arrays in a dataset should always have an equal amount of entries.
        """
        return DataSet(dotnet_dataset=self.psmeasurement.DataSet)

    @property
    def eis_data(self) -> Any:
        """EIS data in measurement."""
        return EISData(dotnet_eisdata=self.psmeasurement.EISdata)

    def get_curve_by_index(self, index: int) -> Curve:
        """Retrieve curve with given index."""
        dotnet_curve = self.psmeasurement.get_Item(index)
        return Curve(dotnet_curve=dotnet_curve)

    @property
    def method(self) -> Method:
        """Method related with this Measurement.

        The information from the Method is used when saving Curves."""
        return Method(psmethod=self.psmeasurement.Method)

    def ocp_value(self) -> float:
        """First OCP Value from either curves or EISData."""
        return self.psmeasurement.OcpValue

    def n_curves(self) -> int:
        """Number of curves that are part of the Measurement class."""
        return self.psmeasurement.nCurves

    def n_eis_data(self) -> int:
        """Number of EISdata curves that are part of the Measurement class."""
        return self.psmeasurement.nEISData

    @property
    def peaks(self) -> list[Peak]:
        """Get peaks from all curves.

        Returns
        -------
        peaks : list[Peak]
            List of peaks
        """
        peaks = []
        for curve in self.curves:
            peaks.extend(curve.peaks)
        return peaks

    @property
    def eis_fit(self) -> list[EISFitResult]:
        """Get all EIS fits from measurement

        Returns
        -------
        eis_fits : list[EISFitResults]
            Return list of EIS fits
        """
        eisdatas = self.psmeasurement.EISdata

        if not eisdatas:
            return []

        eis_fits = []

        for eisdata in eisdatas:
            if not eisdata:
                continue
            eis_fits.append(EISFitResult(eisdata.CDC, eisdata.CDCValues))

        return eis_fits

    @property
    def curves(self) -> list[Curve]:
        """Get all curves in measurement.

        Returns
        -------
        curves : list[Curve]
            List of curves
        """
        curves = self.psmeasurement.GetCurveArray()
        return [Curve(dotnet_curve=curve) for curve in curves]
