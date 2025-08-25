from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Union

from attrs import asdict
from PalmSens import Method as PSMethod
from PalmSens.Devices import PalmSens4Capabilities

from . import techniques

if TYPE_CHECKING:
    from .techniques import MethodSettings


class Method:
    """Wrapper for PalmSens.Method."""

    def __init__(self, *, psmethod: PSMethod):
        self.psmethod = psmethod

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(name={self.name!r}, id={self.id!r})'

    @property
    def id(self) -> str:
        """Unique id for method."""
        return self.psmethod.MethodID

    @property
    def name(self) -> str:
        """Name for the technique."""
        return self.psmethod.Name

    @property
    def short_name(self) -> str:
        """Short name for the technique."""
        return self.psmethod.ShortName

    @property
    def filename(self) -> Union[Path, None]:
        """Filename for the method if applicable."""
        fn = self.psmethod.MethodFilename
        if fn:
            return Path(fn)
        return None

    def get_estimated_duration(self, *, instrument_manager=None):
        """Get the estimated duration for this method.

        Parameters
        ----------
        instrument_manager : InstrumentManager
            Specifies the instrument manager to get the connected instruments capabilities from,
            If not specified it will use the PalmSens4 capabilities to determine the estimated duration.
        """
        if instrument_manager is None or instrument_manager.__comm is None:
            instrument_capabilities = PalmSens4Capabilities()
        else:
            instrument_capabilities = instrument_manager.__comm.Capabilities
        return self.psmethod.GetMinimumEstimatedMeasurementDuration(instrument_capabilities)

    @property
    def technique_number(self) -> int:
        """The technique number used in the firmware."""
        return self.psmethod.Technique

    def to_settings(self) -> MethodSettings:
        """Extract techniques parameters as dataclass."""
        return techniques.MethodSettings._from_psmethod(psmethod=self.psmethod)

    def to_dict(self) -> dict[str, Any]:
        """Return dictionary with technique parameters."""
        return asdict(self.to_settings())
