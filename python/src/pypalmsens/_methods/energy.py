from __future__ import annotations

from datetime import datetime
from typing import Literal

import PalmSens
from jinja2 import Environment, PackageLoader, StrictUndefined, select_autoescape
from pydantic import BaseModel, Field

from .. import __version__
from .techniques import MethodScript

env = Environment(
    loader=PackageLoader('pypalmsens'),
    autoescape=select_autoescape(),
    keep_trailing_newline=True,
    undefined=StrictUndefined,
)


class BaseMethodScriptTechnique(BaseModel):
    _template: str = ''

    def render(self) -> str:
        """Render the template with model parameters.

        Returns
        -------
        script : str
            Complete MethodScript code for this method.
        """
        template = env.get_template(self._template)
        return template.render(
            model=self,
            timestamp=datetime.today().replace(microsecond=0),
            version=__version__,
        )

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


class BatteryCycling(BaseMethodScriptTechnique):
    """Battery cycling CC-CV-CC.

    Note: This method is experimental and may be subject to change.

    This method implements CC-CV-CC Cycling with Delta-I-V and Passed Charge.

    Each cycle consist of:

    1. Charge at a CC (Constant Current) using Chronopotentiometry.
       When the target voltage is reached (the upper cut-off voltage limit),
       switch to CV (Constant Voltage) using Chronoamperometry and maintain
       the applied voltage for a defined period time or until the minimum
       current is reached (the lower cut-off current limit).
    2. Discharge at a Constant Current (using Chronopotentiometry) until
       the lower target voltage is reached (the lower cut-off voltage limit).
    3. Plot a point at defined time intervals.
    4. Send I-V versus time data
    5. Send the capacity per charge / discharge step, also known as passed charge (Qpass).
       The capacity values are absolute and are converted to mAh.

    Alternatively for point 3, use "deltas" to reduce data transfer and optimize points.

    The time interval will be used for controlling, but some points may be skipped:

    - Delta V: when voltage is being measured, plot a point only when a certain variation is reached.
    - Delta I: when current is being measured, plot a point only when a certain variation is reached.
    - Delta t: plot a point at this defined interval anyway, even if the variation is not met.

    The underlying methodscript is described in this application note:
    https://www.palmsens.com/knowledgebase-article/advanced-battery-cycling-with-methodscript/

    Supported devices:

    - Nexus
    - EmStat4 series (EmStat4S, EmStat4X, MultiEmStat4)
    """

    _name: str = 'Battery Cycling'
    _template: str = 'battery_cycling.mscr'

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

    mains_frequency: Literal[50, 60] = 50
    """Set the DC mains filter in Hz.

    Adjusts sampling on instrument to account for mains frequency.
    Set to 50 Hz or 60 Hz depending on your region (default: 50)."""


class ConstantResistance(BaseMethodScriptTechnique):
    """Discharge at Constant Resistance load.

    Note: This method is experimental and may be subject to change.

    This method implements a single step for discharging a battery or
    capacitor at a constant resistance load (Volt per Ampère).

    This simulates the demand of very simple loads, like a filament lamp
    or a simple DC motor.
    While the battery is discharging, its voltage drops and the current
    provided also decreases in proportion to the constant resistance.

    The applied current is refreshed at the defined time interval.

    The discharge is finished when the lower target voltage is reached
    (the lower cut-off voltage limit) or after the defined duration.

    Send live I-V versus time at a defined time interval.
    The discharge current is converted to positive values.

    Supported devices:

    - Nexus
    - EmStat4 series (EmStat4S, EmStat4X, MultiEmStat4)
    """

    _name: str = 'Constant Resistance'
    _template: str = 'constant_resistance.mscr'

    id: Literal['dcr'] = 'dcr'
    """Unique method identifier."""

    load: int = -80
    """Constant resistance load in Ohm (make it negative for discharging)."""

    cutoff: int = 2500
    """A cut-off potential in mV to finish the discharge step."""

    duration: int = Field(3600, ge=0)
    """The total duration of the experiment in s (if the cut-off limit currents not met)."""

    interval: int = Field(1, ge=0)
    """The interval time in s of each data point."""

    cell_on_ocp: bool = False
    """Turns cell on with the measured OCP (Nexus only)."""

    mains_frequency: Literal[50, 60] = 50
    """Set the DC mains filter in Hz.

    Adjusts sampling on instrument to account for mains frequency.
    Set to 50 Hz or 60 Hz depending on your region (default: 50)."""


class ConstantPower(BaseMethodScriptTechnique):
    """Discharge at Constant Power.

    Note: This method is experimental and may be subject to change.

    This method implements a single step for discharging a battery or
    capacitor at a constant power rate (Volt x Ampère).

    This simulates the demand of electronic devices when performing a
    specific task, i.e. a smartphone playing a video.
    While the battery is discharging, its voltage drops and the
    demanded current increases in order to maintain the set power.

    The applied current is refreshed at the defined time interval.

    The discharge is finished when the lower target voltage is reached
    (the lower cut-off voltage limit) or after the defined duration.

    Send live I-V versus time at a defined time interval.
    The discharge current is converted to positive values.

    Supported devices:

    - Nexus
    - EmStat4 series (EmStat4S, EmStat4X, MultiEmStat4)
    """

    _name: str = 'Constant Power'
    _template: str = 'constant_power.mscr'

    id: Literal['dcp'] = 'dcp'
    """Unique method identifier."""

    power: int = -200
    """Constant power in Watt (negative for discharging)."""

    cutoff: int = 2500
    """A cut-off potential in mV to finish the discharge step."""

    duration: int = Field(3600, ge=0)
    """The total duration of the experiment in s (if the cut-off limit currents not met)."""

    interval: int = Field(1, ge=0)
    """The interval time in s of each data point."""

    cell_on_ocp: bool = False
    """Turns cell on with the measured OCP (Nexus only)."""

    mains_frequency: Literal[50, 60] = 50
    """Set the DC mains filter in Hz.

    Adjusts sampling on instrument to account for mains frequency.
    Set to 50 Hz or 60 Hz depending on your region (default: 50)."""
