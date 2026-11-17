from __future__ import annotations

from typing import Literal, TypeVar

import System
from PalmSens import Comm as PSComm
from PalmSens import Devices as PSDevices
from PalmSens import Method as PSMethod
from PalmSens.Comm import enumDeviceType
from pydantic import BaseModel, ConfigDict, computed_field

from ._converters import (
    cr_enum_to_string,
    pr_enum_to_string,
    single_to_double,
)
from ._types import (
    AllowedCurrentRanges,
    AllowedMethods,
    AllowedPotentialRanges,
)

T = TypeVar('T')


class AnalogComponent(BaseModel):
    """Dataclass for analog component (DAC / ADC) configuration."""

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

    model_config = ConfigDict(frozen=True)

    @classmethod
    def _from_pscomponent(cls, obj: PSDevices.AnalogComponent) -> AnalogComponent:
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

    capabilities: PSDevices.DeviceCapabilities

    model_config = ConfigDict(
        frozen=True,
        arbitrary_types_allowed=True,
    )

    @computed_field
    @property
    def acv_max_frequency(self) -> int | None:
        try:
            return int(self.capabilities.MaxFrequencyACV)
        except System.InvalidOperationException:
            return None

    @computed_field
    @property
    def adc_auxiliary(self) -> AnalogComponent | None:
        try:
            return AnalogComponent._from_pscomponent(self.capabilities.ADCAuxiliary)
        except System.InvalidOperationException:
            return None

    @computed_field
    @property
    def adc_bipot(self) -> AnalogComponent | None:
        try:
            return AnalogComponent._from_pscomponent(self.capabilities.ADCBiPot)
        except System.InvalidOperationException:
            return None

    @computed_field
    @property
    def adc_current(self) -> AnalogComponent | None:
        try:
            return AnalogComponent._from_pscomponent(self.capabilities.ADCCurrent)
        except System.InvalidOperationException:
            return None

    @computed_field
    @property
    def adc_potential(self) -> AnalogComponent | None:
        try:
            return AnalogComponent._from_pscomponent(self.capabilities.ADCPotential)
        except System.InvalidOperationException:
            return None

    @computed_field
    @property
    def connection(self) -> str:
        try:
            return self.capabilities.ConnDescription or ''
        except AttributeError:
            return ''

    @computed_field
    @property
    def dac_auxiliary(self) -> AnalogComponent | None:
        try:
            return AnalogComponent._from_pscomponent(self.capabilities.DACAuxiliary)
        except System.InvalidOperationException:
            return None

    @computed_field
    @property
    def dac_bipot(self) -> AnalogComponent | None:
        try:
            return AnalogComponent._from_pscomponent(self.capabilities.DACBiPot)
        except System.InvalidOperationException:
            return None

    @computed_field
    @property
    def dac_current(self) -> AnalogComponent | None:
        try:
            return AnalogComponent._from_pscomponent(self.capabilities.DACCurrent)
        except System.InvalidOperationException:
            return None

    @computed_field
    @property
    def dac_potential(self) -> AnalogComponent | None:
        try:
            return AnalogComponent._from_pscomponent(self.capabilities.DACPotential)
        except System.InvalidOperationException:
            return None

    @computed_field
    @property
    def default_baudrate(self) -> int:
        return self.capabilities.DefaultBaudRate

    @computed_field
    @property
    def device_type(self) -> str:
        return str(self.capabilities.DeviceType)

    @computed_field
    @property
    def max_eis_amplitude_erms(self) -> float:
        return single_to_double(self.capabilities.MaxEISAmplitudeERMS)

    @computed_field
    @property
    def eis_max_frequency(self) -> float:
        return single_to_double(self.capabilities.MaxEISFrequency)

    @computed_field
    @property
    def eis_min_frequency(self) -> float:
        return single_to_double(self.capabilities.MinEISFrequency)

    @computed_field
    @property
    def firmware_build_date(self) -> str:
        return self.capabilities.FirmwareTimeStamp or ''

    @computed_field
    @property
    def firmware_commit(self) -> str:
        try:
            return self.capabilities.ClientConnection.GetFWCommitHash()
        except AttributeError:
            return ''

    @computed_field
    @property
    def firmware_release_type(self) -> Literal['Release', 'Beta', 'Debug']:
        return self.capabilities.FirmwareReleaseType

    @computed_field
    @property
    def firmware_special_description(self) -> str:
        return self.capabilities.SpecialFirmwareDescription or ''

    @computed_field
    @property
    def firmware_version(self) -> float:
        return single_to_double(self.capabilities.FirmwareVersion)

    @computed_field
    @property
    def hardware_revision(self) -> int:
        return self.capabilities.HardwareRevision

    @computed_field
    @property
    def max_v_aux(self) -> float:
        return single_to_double(self.capabilities.MaxVAux)

    @computed_field
    @property
    def geis_max_frequency(self) -> int:
        return int(self.capabilities.MaxEISFrequency)

    @computed_field
    @property
    def has_bipot(self) -> bool:
        return self.capabilities.BiPotPresent

    @computed_field
    @property
    def is_galvanostat(self) -> bool:
        return self.capabilities.IsGalvanostat

    @computed_field
    @property
    def is_hw_sync_main(self) -> bool:
        return self.capabilities.IsHardwareSynchronizationMaster

    @computed_field
    @property
    def is_hw_sync_follower(self) -> bool:
        return self.capabilities.IsSlaveChannel

    @computed_field
    @property
    def max_current(self) -> float:
        return single_to_double(self.capabilities.MaxCurrent)

    @computed_field
    @property
    def max_n_points(self) -> int:
        return self.capabilities.MaxNPoints

    @computed_field
    @property
    def max_potential(self) -> float:
        return single_to_double(self.capabilities.MaxPotential)

    @computed_field
    @property
    def max_potential_bipot(self) -> float:
        return single_to_double(self.capabilities.MaxPotentialBipot)

    @computed_field
    @property
    def min_current(self) -> float:
        return single_to_double(self.capabilities.MinCurrent)

    @computed_field
    @property
    def min_potential(self) -> float:
        return single_to_double(self.capabilities.MinPotential)

    @computed_field
    @property
    def min_potential_step(self) -> float:
        return self.capabilities.DACPotential.StepSize * 1000.0

    @computed_field
    @property
    def min_potential_bipot(self) -> float:
        return single_to_double(self.capabilities.MinPotentialBipot)

    @computed_field
    @property
    def model_name(self) -> str:
        try:
            return self.capabilities.DeviceSerial.TypeToModelName()
        except AttributeError:
            return ''

    @computed_field
    @property
    def model_short_name(self) -> str:
        try:
            return self.capabilities.DeviceSerial.TypeToString()
        except AttributeError:
            return ''

    @computed_field
    @property
    def serial_number(self) -> str:
        try:
            return str(self.capabilities.DeviceSerial)
        except AttributeError:
            return ''

    @computed_field
    @property
    def supported_applied_current_ranges(self) -> list[AllowedCurrentRanges]:
        if not self.capabilities.SupportedAppliedRanges:
            return []

        return [cr_enum_to_string(item) for item in self.capabilities.SupportedAppliedRanges]

    @computed_field
    @property
    def supported_bipot_current_ranges(self) -> list[AllowedCurrentRanges]:
        return [cr_enum_to_string(item) for item in self.capabilities.SupportedBipotRanges]

    @computed_field
    @property
    def supported_current_ranges(self) -> list[AllowedCurrentRanges]:
        return [cr_enum_to_string(item) for item in self.capabilities.SupportedRanges]

    @computed_field
    @property
    def supported_potential_ranges(self) -> list[AllowedPotentialRanges]:
        return [pr_enum_to_string(item) for item in self.capabilities.SupportedPotentialRanges]

    @computed_field
    @property
    def supported_methods(self) -> list[AllowedMethods]:
        method_ids = []

        for number in self.capabilities.SupportedMethods:
            try:
                id = PSMethod.FromTechniqueNumber(number).MethodID
            except System.Exception:
                pass
            else:
                method_ids.append(id)

        return method_ids

    @computed_field
    @property
    def supports_impedance(self) -> bool:
        return self.capabilities.SupportsImpedance

    @computed_field
    @property
    def supports_ir_drop_compensation(self) -> bool:
        return self.capabilities.SupportsIRDropComp

    @computed_field
    @property
    def supports_storage(self) -> bool:
        return self.capabilities.SupportsStorage


class Capabilities(BaseModel):
    """Dataclass for device capabilities and info."""

    model_config = ConfigDict(frozen=True)

    acv_max_frequency: int
    """The maximum frequency for ACV in Hz."""

    adc_auxiliary: AnalogComponent | None
    """Gets an object with values to calculate the auxiliary voltage from the integer value received from the instrument."""

    adc_bipot: AnalogComponent | None
    """Gets an object with values to calculate the bipot current from the integer value received from the instrument."""

    adc_current: AnalogComponent | None
    """Gets an object with values to calculate the current from the integer value received from the instrument."""

    adc_potential: AnalogComponent | None
    """Gets an object with values to calculate the potential from the integer value received from the instrument."""

    connection: str
    """Connection type for this device."""

    dac_auxiliary: AnalogComponent | None
    """Gets an object with values to calculate the instrument integer value for setting the auxiliary output voltage."""

    dac_bipot: AnalogComponent | None
    """Gets an object with values to calculate the instrument integer value for setting the bipot potential."""

    dac_current: AnalogComponent | None
    """Gets an object with values to calculate the instrument integer value for setting the current."""

    dac_potential: AnalogComponent | None
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

    is_hw_sync_main: bool
    """Gets or sets a value indicating whether this instance is designated as the main hardware synchronization channel in MultiTrace."""

    is_hw_sync_follower: bool
    """Gets or sets a value indicating whether this instance is a follower channel in a multichannel device."""

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
    """List of potential ranges supported by this particular device."""

    supported_methods: list[AllowedMethods]
    """List supported methods."""

    supports_impedance: bool
    """Whether or not the device supports impedance measurements"""

    supports_ir_drop_compensation: bool
    """Whether the device supports IR Drop compensation"""

    supports_storage: bool
    """Whether the device contains and supports insternal storage"""

    @classmethod
    def _from_comm(cls, comm: PSComm.CommManager) -> Capabilities:
        """Initialize model from comm manager."""
        interface = CapabilitiesInterface(capabilities=comm.Capabilities)
        return cls.model_validate(interface.model_dump())


CAPABILITIES_BY_DEVICE_TYPE: dict[enumDeviceType, type[PSDevices.DeviceCapabilities]] = {
    enumDeviceType.PalmSens: PSDevices.PalmSensCapabilities,
    enumDeviceType.PalmSens3: PSDevices.PalmSens3Capabilities,
    enumDeviceType.PalmSens4: PSDevices.PalmSens4Capabilities,
    enumDeviceType.EmStat1: PSDevices.EmstatCapabilities,
    enumDeviceType.EmStat2: PSDevices.Emstat2Capabilities,
    enumDeviceType.EmStat3: PSDevices.Emstat3Capabilities,
    enumDeviceType.EmStat3P: PSDevices.Emstat3PCapabilities,
    enumDeviceType.EmStat3BP: PSDevices.Emstat3BPCapabilities,
    enumDeviceType.EmStat4Bootloader: PSDevices.EmStat4BLCapabilities,
    enumDeviceType.EmStat4LR: PSDevices.EmStat4LRCapabilities,
    enumDeviceType.EmStat4HR: PSDevices.EmStat4HRCapabilities,
    enumDeviceType.Nexus: PSDevices.NexusCapabilities,
    enumDeviceType.NexusBootloader: PSDevices.NexusCapabilities,
    enumDeviceType.EmStatPico: PSDevices.EmStatPicoCapabilities,
    enumDeviceType.EmStatPicoBootLoader: PSDevices.EmStatPicoCapabilities,
    enumDeviceType.EmStatPicoSim: PSDevices.EmStatPicoCapabilitiesSim,
    enumDeviceType.SensitWearable: PSDevices.SensitWearableCapabilities,
    enumDeviceType.SensitWearableBootloader: PSDevices.SensitWearableCapabilities,
    enumDeviceType.EmStatPicoExtended: PSDevices.EmStatPicoExtendedCapabilities,
    enumDeviceType.SAMBAProgramPort: PSDevices.SambaProgramPortCabalities,  # sic, original spelling
}


class UnknownCapabilitiesException(BaseException): ...


def parse_enum(enum_type: type[T], name: str, ignore_case: bool = True) -> T:
    """Parse dotnet enum from string."""
    try:
        return System.Enum.Parse(enum_type, name, ignore_case)
    except System.ArgumentException as exc:
        raise ValueError(f'{name!r} is not a member of {enum_type}') from exc


def _get_capabilities(model: str) -> PSDevices.DeviceCapabilities:
    device_type = parse_enum(enumDeviceType, name=model, ignore_case=True)
    if device_type == enumDeviceType.Unknown:
        raise UnknownCapabilitiesException(f'No capabilities found for {device_type}')
    if device_type == enumDeviceType.EmStat2BP:
        raise NotImplementedError(f'Capabilities not implemented for {device_type}')

    cls = CAPABILITIES_BY_DEVICE_TYPE[device_type]
    return cls()


def get_capabilities(model: str) -> CapabilitiesInterface:
    """Get capabilitities for device model."""
    capabilities = _get_capabilities(model=model)
    return CapabilitiesInterface(capabilities=capabilities)


if __name__ == '__main__':
    for k, v in Capabilities.model_computed_fields.items():
        print(f'{k}: {v.return_type}')
        print(f'"""{v.description}"""')
        print()
