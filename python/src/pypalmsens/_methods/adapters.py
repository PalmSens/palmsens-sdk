from __future__ import annotations

from typing import Annotated

from pydantic import Field, TypeAdapter

from . import corrosion, energy, mixed_mode, techniques

TechniqueType = Annotated[
    corrosion.CyclicPolarization
    | corrosion.CorrosionPotential
    | corrosion.Galvanostatic
    | corrosion.LinearPolarization
    | corrosion.Potentiostatic
    | mixed_mode.MixedMode
    | techniques.ACVoltammetry
    | techniques.ChronoAmperometry
    | techniques.ChronoCoulometry
    | techniques.ChronoPotentiometry
    | techniques.CyclicVoltammetry
    | techniques.DifferentialPulseVoltammetry
    | techniques.ElectrochemicalImpedanceSpectroscopy
    | techniques.FastAmperometry
    | techniques.FastCyclicVoltammetry
    | techniques.FastGalvanostaticImpedanceSpectroscopy
    | techniques.FastImpedanceSpectroscopy
    | techniques.GalvanostaticImpedanceSpectroscopy
    | techniques.LinearSweepPotentiometry
    | techniques.LinearSweepVoltammetry
    | techniques.MethodScript
    | techniques.MultiStepAmperometry
    | techniques.MultiStepPotentiometry
    | techniques.MultiplePulseAmperometry
    | techniques.NormalPulseVoltammetry
    | techniques.OpenCircuitPotentiometry
    | techniques.PulsedAmperometricDetection
    | techniques.SquareWaveVoltammetry
    | techniques.StrippingChronoPotentiometry,
    Field(discriminator='id'),
]

EnergyTechniqueType = energy.experimental_BatteryCycling

technique_adapter = TypeAdapter(TechniqueType)
energy_technique_adapter = TypeAdapter(EnergyTechniqueType)
