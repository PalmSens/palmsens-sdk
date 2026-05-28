from __future__ import annotations

from datetime import datetime
from typing import Literal

import PalmSens
from jinja2 import Environment, PackageLoader, select_autoescape
from pydantic import BaseModel, Field

from .. import __version__
from .techniques import MethodScript

env = Environment(
    loader=PackageLoader('pypalmsens'),
    autoescape=select_autoescape(),
    keep_trailing_newline=True,
)


class experimental_BatteryCycling(BaseModel):
    """Battery cycling method parameters.

    Note: This method is experimental and may be subject to change.

    Supported devices:

    - Nexus
    - EmStat4 series (EmStat4S, EmStat4X, MultiEmStat4)

    This method implements CC-CV-CC Cycling with Delta-I-V and Qpass:

    1. With Chronopotentiometry and Chronoamperometry to charge a cell and a Constant
       current followed by Constant Coltage (CC-CV).
    2. With Chronopotentiometry discharge the cell at a constant current (CC).
    3. Store the charge transferred during each charge and discharge step.
    4. Send I-V verus time data, and the capacity per charge-discharge step (Qpass).
       The charge values are absolute and are converted to mAh.

    The underlying methodscript is described in this application note:
    https://www.palmsens.com/knowledgebase-article/advanced-battery-cycling-with-methodscript/
    """

    id: Literal['bc'] = 'bc'
    """Unique method identifier."""

    potential_max: int = 4300
    """Maximum potential to charge to (units: mV)."""

    current_min: int = 5
    """Minimum current to stop the CV charge step (units: μA)."""

    potential_min: int = 2500
    """Minimum potential to discharge to (units: mV)."""

    current_charge: int = 100
    """Constant current to charge with (units: μA)."""

    current_discharge: int = -100
    """Constant current to discharge with (units: μA)."""

    cycles: int = Field(default=100, gt=0)
    """Number of charge and discharge cycles."""

    interval: int = Field(default=100, ge=0)
    """Interval time of each measurement point (units: s)."""

    max_time: int = Field(default=3, ge=0)
    """Maximum duration of each step (if the cut-off is not met) (units: s)."""

    delta_v: int = Field(default=100, gt=0)
    """Minimum potential variation required for plotting data in CC steps (units: μV)."""

    delta_i: int = Field(default=500, gt=0)
    """Minimum current variation reuqired for plotting data in the CV step (units: nA)."""

    delta_t: int = Field(default=100, ge=0)
    """Maximum time without plotting data (units: ms)."""

    cell_on_ocp: bool = False
    """Turns cell on with the measured OCP (Nexus only)."""

    power_frequency: Literal[50, 60] = 50
    """Set the DC mains filter in Hz.

    Adjusts sampling on instrument to account for mains frequency.
    Set to 50 Hz or 60 Hz depending on your region (default: 50)."""

    _name: str = 'Battery Cycling (experimental)'

    def render(self) -> str:
        """Render the template with model parameters.

        Returns
        -------
        script : str
            Complete MethodScript code for this method.
        """
        template = env.get_template('battery_cycling.mscr')
        return template.render(model=self, timestamp=datetime.today(), version=__version__)

    def to_methodscript(self) -> MethodScript:
        """Convert to MethodSCRIPT class.

        Returns
        -------
        method: MethodScript
            MethodScript class.
        """
        script = self.render()
        return MethodScript(script=script)

    def _to_psmethod(self) -> PalmSens.Method:
        """Convert parameters to dotnet method."""
        method = self.to_methodscript()
        return method._to_psmethod()
