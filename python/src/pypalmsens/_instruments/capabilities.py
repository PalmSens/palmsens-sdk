from __future__ import annotations

from typing import Literal

import PalmSens
from pydantic import BaseModel, ConfigDict, computed_field

from .._helpers import single_to_double
from .._methods.types import (
    AllowedCurrentRanges,
    AllowedMethods,
    AllowedPotentialRanges,
    cr_enum_to_string,
    pr_enum_to_string,
)


class AnalogComponent(BaseModel):
    """Dataclass for analog component (DAC / ADC) configuration."""

    model_config = ConfigDict(frozen=True)

    bits: int
    """Number of bits this device uses."""

    gain: float
    """Voltage gain of the device."""

    max_raw_value: int
    """Maximum raw value, based on the amount of bits."""

    max_value: float
    """Maximum analog value this device can handle."""

    min_value: float
    """Minimum analog value this device can handle."""

    offset: float
    """Voltage offset of the device."""

    resolution: float
    """Resolution of this analog device."""

    step_size: float
    """Analog step size for the input or output of this component."""

    v_range: float
    """Gets the reference voltage range of the device."""

    model_config['frozen'] = True

    @classmethod
    def _from_pscomponent(cls, obj: PalmSens.Devices.AnalogComponent) -> AnalogComponent:
        """Convert dotnet object."""
        return cls(
            bits=obj.Bits,
            gain=obj.Gain,
            max_raw_value=int(obj.MaxRawValue),
            max_value=single_to_double(obj.MaxValue),
            min_value=single_to_double(obj.MinValue),
            offset=single_to_double(obj.Offset),
            resolution=single_to_double(obj.Resolution),
            step_size=single_to_double(obj.StepSize),
            v_range=single_to_double(obj.VRange),
        )


class CapabilitiesInterface(BaseModel):
    """Interface to convert from PalmSens.Devices.Capabilities to dataclass."""

    comm: PalmSens.Comm.CommManager

    model_config = {'arbitrary_types_allowed': True}

    @computed_field
    @property
    def acv_max_frequency(self) -> int:
        return int(self.comm.Capabilities.MaxFrequencyACV)

    @computed_field
    @property
    def adc_auxiliary(self) -> AnalogComponent:
        return AnalogComponent._from_pscomponent(self.comm.Capabilities.ADCAuxiliary)

    @computed_field
    @property
    def adc_bipot(self) -> AnalogComponent:
        return AnalogComponent._from_pscomponent(self.comm.Capabilities.ADCBiPot)

    @computed_field
    @property
    def adc_current(self) -> AnalogComponent:
        return AnalogComponent._from_pscomponent(self.comm.Capabilities.ADCCurrent)

    @computed_field
    @property
    def adc_potential(self) -> AnalogComponent:
        return AnalogComponent._from_pscomponent(self.comm.Capabilities.ADCPotential)

    @computed_field
    @property
    def connection(self) -> str:
        return self.comm.Capabilities.ConnDescription

    @computed_field
    @property
    def dac_auxiliary(self) -> AnalogComponent:
        return AnalogComponent._from_pscomponent(self.comm.Capabilities.DACAuxiliary)

    @computed_field
    @property
    def dac_bipot(self) -> AnalogComponent:
        return AnalogComponent._from_pscomponent(self.comm.Capabilities.DACBiPot)

    @computed_field
    @property
    def dac_current(self) -> AnalogComponent:
        return AnalogComponent._from_pscomponent(self.comm.Capabilities.DACCurrent)

    @computed_field
    @property
    def dac_potential(self) -> AnalogComponent:
        return AnalogComponent._from_pscomponent(self.comm.Capabilities.DACPotential)

    @computed_field
    @property
    def default_baudrate(self) -> int:
        return self.comm.Capabilities.DefaultBaudRate

    @computed_field
    @property
    def device_type(self) -> str:
        return str(self.comm.Capabilities.DeviceType)

    @computed_field
    @property
    def max_eis_amplitude_erms(self) -> float:
        return single_to_double(self.comm.Capabilities.MaxEISAmplitudeERMS)

    @computed_field
    @property
    def eis_max_frequency(self) -> float:
        return single_to_double(self.comm.Capabilities.MaxEISFrequency)

    @computed_field
    @property
    def eis_min_frequency(self) -> float:
        return single_to_double(self.comm.Capabilities.MinEISFrequency)

    @computed_field
    @property
    def firmware_build_date(self) -> str:
        return self.comm.Capabilities.FirmwareTimeStamp

    @computed_field
    @property
    def firmware_commit(self) -> str:
        return self.comm.ClientConnection.GetFWCommitHash()

    @computed_field
    @property
    def firmware_release_type(self) -> Literal['Release', 'Beta', 'Debug']:
        return self.comm.Capabilities.FirmwareReleaseType

    @computed_field
    @property
    def firmware_special_description(self) -> str:
        return self.comm.Capabilities.SpecialFirmwareDescription

    @computed_field
    @property
    def firmware_version(self) -> float:
        return single_to_double(self.comm.Capabilities.FirmwareVersion)

    @computed_field
    @property
    def hardware_revision(self) -> int:
        return self.comm.Capabilities.HardwareRevision

    @computed_field
    @property
    def max_v_aux(self) -> float:
        return single_to_double(self.comm.Capabilities.MaxVAux)

    @computed_field
    @property
    def geis_max_frequency(self) -> int:
        return int(self.comm.Capabilities.MaxEISFrequency)

    @computed_field
    @property
    def has_bipot(self) -> bool:
        return self.comm.Capabilities.BiPotPresent

    @computed_field
    @property
    def is_galvanostat(self) -> bool:
        return self.comm.Capabilities.IsGalvanostat

    @computed_field
    @property
    def is_hw_sync_master(self) -> bool:
        return self.comm.Capabilities.IsHardwareSynchronizationMaster

    @computed_field
    @property
    def is_hw_sync_slave(self) -> bool:
        return self.comm.Capabilities.IsSlaveChannel

    @computed_field
    @property
    def max_current(self) -> float:
        return single_to_double(self.comm.Capabilities.MaxCurrent)

    @computed_field
    @property
    def max_n_points(self) -> int:
        return self.comm.Capabilities.MaxNPoints

    @computed_field
    @property
    def max_potential(self) -> float:
        return single_to_double(self.comm.Capabilities.MaxPotential)

    @computed_field
    @property
    def max_potential_bipot(self) -> float:
        return single_to_double(self.comm.Capabilities.MaxPotentialBipot)

    @computed_field
    @property
    def min_current(self) -> float:
        return single_to_double(self.comm.Capabilities.MinCurrent)

    @computed_field
    @property
    def min_potential(self) -> float:
        return single_to_double(self.comm.Capabilities.MinPotential)

    @computed_field
    @property
    def min_potential_step(self) -> float:
        return self.comm.Capabilities.DACPotential.StepSize * 1000.0

    @computed_field
    @property
    def min_potential_bipot(self) -> float:
        return single_to_double(self.comm.Capabilities.MinPotentialBipot)

    @computed_field
    @property
    def model_name(self) -> str:
        return self.comm.DeviceSerial.TypeToModelName()

    @computed_field
    @property
    def model_short_name(self) -> str:
        return self.comm.DeviceSerial.TypeToString()

    @computed_field
    @property
    def serial_number(self) -> str:
        return str(self.comm.DeviceSerial)

    @computed_field
    @property
    def supported_applied_current_ranges(self) -> list[AllowedCurrentRanges]:
        return [
            cr_enum_to_string(item) for item in self.comm.Capabilities.SupportedAppliedRanges
        ]

    @computed_field
    @property
    def supported_bipot_current_ranges(self) -> list[AllowedCurrentRanges]:
        return [cr_enum_to_string(item) for item in self.comm.Capabilities.SupportedBipotRanges]

    @computed_field
    @property
    def supported_current_ranges(self) -> list[AllowedCurrentRanges]:
        return [cr_enum_to_string(item) for item in self.comm.Capabilities.SupportedRanges]

    @computed_field
    @property
    def supported_potential_ranges(self) -> list[AllowedPotentialRanges]:
        return [
            pr_enum_to_string(item) for item in self.comm.Capabilities.SupportedPotentialRanges
        ]

    @computed_field
    @property
    def supported_methods(self) -> list[AllowedMethods]:
        method_ids = []

        for number in self.comm.Capabilities.SupportedMethods:
            try:
                id = PalmSens.Method.FromTechniqueNumber(number).MethodID
            except Exception:
                pass
            else:
                method_ids.append(id)

        return method_ids

    @computed_field
    @property
    def supports_impedance(self) -> bool:
        return self.comm.Capabilities.SupportsImpedance

    @computed_field
    @property
    def supports_ir_drop_compensation(self) -> bool:
        return self.comm.Capabilities.SupportsIRDropComp


class Capabilities(BaseModel):
    """Dataclass for device capabilities and info."""

    model_config = ConfigDict(frozen=True)

    acv_max_frequency: int
    """The maximum frequency for ACV in Hz."""

    adc_auxiliary: AnalogComponent
    """Gets an object with values to calculate the auxiliary voltage from the integer value received from the instrument."""

    adc_bipot: AnalogComponent
    """Gets an object with values to calculate the bipot current from the integer value received from the instrument."""

    adc_current: AnalogComponent
    """Gets an object with values to calculate the current from the integer value received from the instrument."""

    adc_potential: AnalogComponent
    """Gets an object with values to calculate the potential from the integer value received from the instrument."""

    connection: str
    """Connection type for this device."""

    dac_auxiliary: AnalogComponent
    """Gets an object with values to calculate the instrument integer value for setting the auxiliary output voltage."""

    dac_bipot: AnalogComponent
    """Gets an object with values to calculate the instrument integer value for setting the bipot potential."""

    dac_current: AnalogComponent
    """Gets an object with values to calculate the instrument integer value for setting the current."""

    dac_potential: AnalogComponent
    """Gets an object with values to calculate the potential from the integer value received from the instrument."""

    default_baudrate: int
    """Gets the default baud rate."""

    device_type: str
    """The device type for this capabilities."""

    max_eis_amplitude_erms: float
    """Gets the maximum E RMS amplitude for EIS."""

    eis_max_frequency: float
    """Maximum frequency for EIS measurements in Hz."""

    eis_min_frequency: float
    """Minimum frequency for EIS measurements in Hz."""

    firmware_build_date: str
    """Build date of the firmware."""

    firmware_commit: str
    """Commit associated with the build of the firmware."""

    firmware_release_type: Literal['Release', 'Beta', 'Debug']
    """Get a string representation if the build is 'Release', 'Beta' or 'Debug'"""

    firmware_special_description: str
    """Special description for the firmware"""

    firmware_version: float
    """Firmware version of connected device."""

    hardware_revision: int
    """Gets the hardware revision."""

    max_v_aux: float
    """Maximum potential output of the AUX port in V."""

    geis_max_frequency: int
    """Gets the maximum GEIS frequency in Hz."""

    has_bipot: bool
    """True if bipot (WE2) capabilities are present"""

    is_galvanostat: bool
    """True if the potentiastat can act as a galvanostat."""

    is_hw_sync_master: bool
    """Gets or sets a value indicating whether this instance is designated as the hardware synchronization master in MultiTrace."""

    is_hw_sync_slave: bool
    """Gets or sets a value indicating whether this instance is slave channel in a multichannel device."""

    max_current: float
    """Maximum current (* current range) that can be read/applied"""

    max_n_points: int
    """Maximum amount of points within a measurement technique for this device."""

    max_potential: float
    """Maximum potential in V that can be read/applied."""

    max_potential_bipot: float
    """Maximum potential in V that can be read/applied with the bipot."""

    min_current: float
    """Minimum current (* current range) that can be read/applied."""

    min_potential: float
    """Minimum potential in V that can be read/applied"""

    min_potential_step: float
    """Minimum potential step in mV that can be applied."""

    min_potential_bipot: float
    """Minimum potential that can be read/applied with the bipot"""

    model_name: str
    """Name of the device."""

    model_short_name: str
    """Short name of the device."""

    serial_number: str
    """Serial number of the device."""

    supported_applied_current_ranges: list[AllowedCurrentRanges]
    """list of current ranges supported for applying current by this particular device."""

    supported_bipot_current_ranges: list[AllowedCurrentRanges]
    """list of current ranges for the BiPot module supported by this particular device."""

    supported_current_ranges: list[AllowedCurrentRanges]
    """list of current ranges supported by this particular device."""

    supported_potential_ranges: list[AllowedPotentialRanges]
    """list of potential ranges supported by this particular device."""

    supported_methods: list[AllowedMethods]
    """List supported methods."""

    supports_impedance: bool
    """Whether or not the device supports impedance measurements"""

    supports_ir_drop_compensation: bool
    """Whether the device supports IR Drop compensation"""

    @classmethod
    def _from_comm(cls, comm: PalmSens.Comm.CommManager) -> Capabilities:
        """Initialize model from comm manager."""
        interface = CapabilitiesInterface(comm=comm)
        return cls.model_validate(interface.model_dump())


if __name__ == '__main__':
    for k, v in Capabilities.model_computed_fields.items():
        print(f'{k}: {v.return_type}')
        print(f'"""{v.description.__name__}"""')
        print('')
