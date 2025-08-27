from __future__ import annotations

from dataclasses import dataclass

from PalmSens import Measurement as PSMeasurement

from .._fitting import FitResult
from .._methods.method import Method
from .curve import Curve
from .dataset import DataSet
from .eisdata import EISData
from .peak import Peak


@dataclass(frozen=True)
class DeviceInfo:
    """Dataclass for device information."""

    type: str
    """Device type"""
    firmware: str
    """Firmware version"""
    serial: str
    """Serial number"""
    id: int
    """Device ID"""

    @classmethod
    def _from_psmeasurement(cls, obj: PSMeasurement) -> DeviceInfo:
        """Construct device dataclass from SDK measurement object."""
        return cls(
            type=obj.DeviceUsed.ToString(),
            firmware=obj.DeviceUsedFW,
            serial=obj.DeviceUsedSerial,
            id=int(obj.DeviceUsed),
        )


@dataclass
class Measurement:
    """Python wrapper for .NET Measurement class.

    Parameters
    ----------
    psmeasurement
        Reference to .NET measurement object.
    """

    def __init__(self, *, psmeasurement: PSMeasurement):
        self._psmeasurement = psmeasurement

    def __repr__(self):
        return f'{self.__class__.__name__}(title={self.title}, timestamp={self.timestamp}, device={self.device.type})'

    @property
    def title(self) -> str:
        """Title for the measurement."""
        return self._psmeasurement.Title

    @property
    def timestamp(self) -> str:
        """Date and time of the start of this measurement.."""
        return str(self._psmeasurement.TimeStamp)

    @property
    def device(self) -> DeviceInfo:
        """Return dataclass with measurement device information."""
        return DeviceInfo._from_psmeasurement(self._psmeasurement)

    @property
    def blank_curve(self) -> Curve | None:
        """Blank curve.

        if Blank curve is present (not null) a new curve will be added after each measurement
        containing the result of the measured curve subtracted with the Blank curve.
        """
        curve = self._psmeasurement.BlankCurve
        if curve:
            return Curve(pscurve=curve)
        return None

    @property
    def has_blank_subtracted_curves(self) -> bool:
        """Return True if the curve collection contains a blank subtracted curve."""
        return self._psmeasurement.ContainsBlankSubtractedCurves

    @property
    def has_eis_data(self) -> bool:
        """Return True if EIS data are is available."""
        return self._psmeasurement.ContainsEISData

    @property
    def dataset(self) -> DataSet:
        """Dataset containing multiple arrays of values.

        All values are related by means of their indices.
        Data arrays in a dataset should always have an equal amount of entries.
        """
        return DataSet(psdataset=self._psmeasurement.DataSet)

    @property
    def eis_data(self) -> list[EISData]:
        """EIS data in measurement."""
        lst = [EISData(pseis=pseis) for pseis in self._psmeasurement.EISdata]

        return lst

    @property
    def method(self) -> Method:
        """Method related with this Measurement.

        The information from the Method is used when saving Curves."""
        return Method(psmethod=self._psmeasurement.Method)

    @property
    def channel(self) -> float:
        """Get the channel that the measurement was measured on."""
        return self._psmeasurement.Channel

    @property
    def ocp_value(self) -> float:
        """First OCP Value from either curves or EISData."""
        return self._psmeasurement.OcpValue

    @property
    def n_curves(self) -> int:
        """Number of curves that are part of the Measurement class."""
        return self._psmeasurement.nCurves

    @property
    def n_eis_data(self) -> int:
        """Number of EISdata curves (channels) that are part of the Measurement class."""
        return self._psmeasurement.nEISdata

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
    def eis_fit(self) -> list[FitResult]:
        """Get all EIS fits from measurement

        Returns
        -------
        eis_fits : list[EISFitResults]
            Return list of EIS fits
        """
        eisdatas = self.eis_data
        eis_fits = [FitResult.from_eisdata(eisdata) for eisdata in eisdatas]
        return eis_fits

    @property
    def curves(self) -> list[Curve]:
        """Get all curves in measurement.

        Returns
        -------
        curves : list[Curve]
            List of curves
        """
        curves = self._psmeasurement.GetCurveArray()
        return [Curve(pscurve=curve) for curve in curves]
