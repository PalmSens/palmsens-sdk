from __future__ import annotations

from typing import Protocol

import PalmSens
from PalmSens.Comm import CommManager

from .._types import (
    AllowedCurrentRanges,
    AllowedMethods,
    AllowedPotentialRanges,
    MethodTypeCompatible,
)
from .capabilities import Capabilities, CapabilitiesInterface
from .shared import MethodIncompatibleError


class HasCommProtocol(Protocol):
    _comm: CommManager

    def ensure_connection(self) -> None: ...


class HasCapabilities(Protocol):
    capabilities: Capabilities


class CapabilitiesMixin:
    @property
    def capabilities(self: HasCommProtocol) -> Capabilities:
        """Retrieve device capabilities and device info as a dataclass.

        Returns
        -------
        capabilities: Capabilities
            Device capabilities and device info.
        """
        self.ensure_connection()
        return Capabilities._from_comm(self._comm)

    def supported_methods(self: HasCommProtocol) -> list[AllowedMethods]:
        """List methods supported by this device.

        Returns
        -------
        methods: list[AllowedMethods]
            List of supported methods.
        """
        self.ensure_connection()
        return CapabilitiesInterface(comm=self._comm).supported_methods

    def supported_current_ranges(self: HasCommProtocol) -> list[AllowedCurrentRanges]:
        """List current ranges supported by this device.

        Returns
        -------
        current_ranges: list[AllowedCurrentRanges]
            List of supported current ranges.
        """
        self.ensure_connection()
        return CapabilitiesInterface(comm=self._comm).supported_current_ranges

    def supported_applied_current_ranges(self: HasCommProtocol) -> list[AllowedCurrentRanges]:
        """List applied current ranges supported by this device.

        Returns
        -------
        current_ranges: list[AllowedCurrentRanges]
            List of supported current ranges.
        """
        self.ensure_connection()
        return CapabilitiesInterface(comm=self._comm).supported_applied_current_ranges

    def supported_bipot_current_ranges(self: HasCommProtocol) -> list[AllowedCurrentRanges]:
        """List bipot current ranges supported by this device.

        Returns
        -------
        current_ranges: list[AllowedCurrentRanges]
            List of supported current ranges.
        """
        self.ensure_connection()
        return CapabilitiesInterface(comm=self._comm).supported_bipot_current_ranges

    def supported_potential_ranges(self: HasCommProtocol) -> list[AllowedPotentialRanges]:
        """List applied potential ranges supported by this device.

        Returns
        -------
        potential_ranges: list[AllowedPotentialRanges]
            List of supported potential ranges.
        """
        self.ensure_connection()
        return CapabilitiesInterface(comm=self._comm).supported_potential_ranges

    def get_estimated_duration(
        self: HasCommProtocol,
        method: PalmSens.Method | MethodTypeCompatible,
    ) -> float:
        """Get the estimated duration for this method.

        Parameters
        -----------
        method : MethodType
            The method to get the estimated duration for.

        Returns
        -------
        float
            Estimated duration in seconds.
        """
        self.ensure_connection()

        if not isinstance(method, PalmSens.Method):
            method = method._to_psmethod()

        capabilities = self._comm.Capabilities

        return method.GetMinimumEstimatedMeasurementDuration(capabilities)

    def validate_method(
        self: HasCommProtocol,
        method: MethodTypeCompatible,
    ):
        """Validate method.

        Raise ValueError if the method cannot be validated.

        Parameters
        -----------
        method: MethodType
            The method to validate.
        """
        self.ensure_connection()

        capabilities = self._comm.Capabilities

        psmethod = method._to_psmethod()
        errors = psmethod.Validate(capabilities)

        if any(error.IsFatal for error in errors):
            message = '\n'.join([error.Message for error in errors])
            raise MethodIncompatibleError(f'Method not compatible:\n{message}')
