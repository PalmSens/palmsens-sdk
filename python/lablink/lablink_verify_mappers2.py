"""Compare `to_payload()` against the built .NET SDK, case by case.

Per case the output is one of `ok`, `missing` / `extra` / `differs` lines,
`port not implemented` (port-able, not ported yet), or `blocked in C#` (no golden
output exists; see PLAN.md §6). The exit status is nonzero when any checked case
fails to match or raises.

Usage:

    LABLINK_SDK="C:\\Users\\stef\\code\\palmsenssdkdotnet\\PalmSens.Sdk.Lablink\\PalmSens.Sdk.Lablink\\bin\\Debug\\net10.0"
    python lablink_verify_mappers.py

    export LABLINK_SDK=/home/stef/code/palmsens-sdk-dotnet/PalmSens.Sdk.Lablink/PalmSens.Sdk.Lablink/bin/Debug/net10.0/
    python lablink_verify_mappers.py

Run it with the editable pypalmsens environment; a non-editable copy in
site-packages verifies stale code instead of the working tree.
"""

from __future__ import annotations

import os
import sys
from typing import cast

if not os.getenv('LABLINK_SDK'):
    raise SystemExit(
        'Set LABLINK_SDK to the directory holding PalmSens.Sdk.Data.dll and '
        'PalmSens.Sdk.Lablink.Example.dll, e.g. '
        'PalmSens.Sdk.Lablink/PalmSens.Sdk.Lablink/bin/Debug/net10.0/'
    )

import pypalmsens as ps
from pypalmsens.lablink.models._method_mapper import to_payload
from pypalmsens.types import MethodTypeCompatible

if True:
    # Loaded by pypalmsens' .NET loader, which reads LABLINK_SDK at import time.
    from PalmSens.Core.Domain.Models import CurveTemplate
    from PalmSens.Sdk.Data.Extensions.Method import MethodExtensions
    from System import Array, DateTimeOffset, String

CV = ps.CyclicVoltammetry(
    begin_potential=0.25,
    vertex1_potential=0.6,
    vertex2_potential=-0.6,
    step_potential=0.25,
    scanrate=5,
    n_scans=2,
    current_range={'max': '1mA', 'min': '100nA', 'start': '100uA'},
)


FCV = ps.FastCyclicVoltammetry(
    begin_potential=-1,
    vertex1_potential=-1,
    vertex2_potential=1,
    step_potential=0.25,
    scanrate=500,
    n_scans=3,
    n_avg_scans=2,
    n_equil_scans=2,
    current_range='10uA',
)


LSV = ps.LinearSweepVoltammetry(
    begin_potential=-1.0,
    end_potential=1.0,
    step_potential=0.1,
    scanrate=2.0,
    current_range={'max': '1mA', 'min': '100nA', 'start': '100uA'},
)


LSV_aux = ps.LinearSweepVoltammetry(
    begin_potential=0.0,
    end_potential=1.0,
    step_potential=0.2,
    scanrate=8.0,
    record_auxiliary_input=True,
)


ACV = ps.ACVoltammetry(
    begin_potential=-0.15,
    end_potential=0.15,
    step_potential=0.15,
    ac_potential=0.25,
    frequency=200.0,
    scanrate=0.2,
    current_range={'max': '1mA', 'min': '100nA', 'start': '100uA'},
)


SWV = ps.SquareWaveVoltammetry(
    equilibration_time=0.0,
    begin_potential=-0.5,
    end_potential=0.5,
    step_potential=0.1,
    frequency=10.0,
    amplitude=0.05,
    record_forward_and_reverse_currents=True,
    current_range={'max': '1mA', 'min': '100nA', 'start': '100uA'},
)


CP = ps.ChronoPotentiometry(
    current=0.0,
    applied_current_range='100uA',
    interval_time=0.1,
    run_time=1.0,
    potential_range={'max': '1V', 'min': '100mV', 'start': '1V'},
)


SCP = ps.StrippingChronoPotentiometry(
    current=0.1,
    applied_current_range='100uA',
    measurement_time=1.0,
    # No `potential_range`: the C# stripping mapper ignores it (measured against the DLL),
    # so the port rejects a non-default one instead of silently dropping it.
    pretreatment={'deposition_time': 1, 'deposition_potential': 0.1},
)


LSP = ps.LinearSweepPotentiometry(
    applied_current_range='100uA',
    current_step=0.1,
    scan_rate=8.0,
    potential_range={'max': '1V', 'min': '100mV', 'start': '1V'},
)


OCP = ps.OpenCircuitPotentiometry(
    interval_time=0.1,
    run_time=1.0,
    potential_range={'max': '1V', 'min': '100mV', 'start': '1V'},
)


CA = ps.ChronoAmperometry(interval_time=0.1, run_time=1.0)


FAM = ps.FastAmperometry(interval_time=0.1, run_time=1.0)


DPV = ps.DifferentialPulseVoltammetry(
    begin_potential=-0.25,
    end_potential=0.25,
    step_potential=0.25,
    pulse_potential=0.10,
    pulse_time=0.1,
    scan_rate=0.5,
)


PAD = ps.PulsedAmperometricDetection(
    potential=0.5,
    pulse_potential=1.0,
    pulse_time=0.1,
    mode='pulse',
    run_time=1.0,
    interval_time=0.2,
)


MPAD = ps.MultiplePulseAmperometry(
    run_time=2.5,
    potential_1=0.1,
    potential_2=0.1,
    potential_3=0.1,
    duration_1=0.15,
    duration_2=0.15,
    duration_3=0.15,
)


NPV = ps.NormalPulseVoltammetry(
    begin_potential=-0.25,
    end_potential=0.25,
    step_potential=0.25,
    pulse_time=0.1,
    scan_rate=0.5,
)


MA = ps.MultiStepAmperometry(
    equilibration_time=0.0,
    interval_time=0.01,
    n_cycles=2,
    levels=[
        {'level': 0.5, 'duration': 0.1},
        {'level': 0.3, 'duration': 0.2},
    ],
)


MP = ps.MultiStepPotentiometry(
    interval_time=0.01,
    n_cycles=2,
    levels=[
        {'level': 0.5, 'duration': 0.1},
        {'level': 0.3, 'duration': 0.2},
    ],
)


CC = ps.ChronoCoulometry(
    equilibration_time=0.0, interval_time=0.01, step1_run_time=0.1, step2_run_time=0.2
)


EIS = ps.ElectrochemicalImpedanceSpectroscopy(
    n_frequencies=5,
    max_frequency=1e5,
    min_frequency=1e3,
    scan_type='fixed',
    frequency_type='scan',
    min_sampling_time=0.01,
    max_equilibration_time=0.01,
)


EIS_pot_fixed = ps.ElectrochemicalImpedanceSpectroscopy(
    n_frequencies=5,
    max_frequency=1e5,
    min_frequency=1e3,
    scan_type='potential',
    frequency_type='fixed',
    begin_potential=0.0,
    end_potential=-0.1,
    step_potential=0.1,
)


EIS_pot_scan = ps.ElectrochemicalImpedanceSpectroscopy(
    n_frequencies=5,
    max_frequency=1e5,
    min_frequency=1e3,
    scan_type='potential',
    frequency_type='scan',
    begin_potential=0.0,
    end_potential=-0.1,
    step_potential=0.1,
)


EIS_time_fixed = ps.ElectrochemicalImpedanceSpectroscopy(
    n_frequencies=5,
    max_frequency=1e5,
    min_frequency=1e3,
    scan_type='time',
    frequency_type='fixed',
    run_time=1.3,
)


EIS_time_scan = ps.ElectrochemicalImpedanceSpectroscopy(
    n_frequencies=5,
    max_frequency=1e5,
    min_frequency=1e3,
    scan_type='time',
    frequency_type='scan',
    run_time=0.4,
)


EIS_single_point = ps.ElectrochemicalImpedanceSpectroscopy(
    n_frequencies=5,
    max_frequency=1e5,
    min_frequency=1e3,
    scan_type='fixed',
    frequency_type='fixed',
)


FIS = ps.FastImpedanceSpectroscopy(frequency=40000, run_time=0.5)


GIS = ps.GalvanostaticImpedanceSpectroscopy(
    applied_current_range='10uA',
    equilibration_time=0.0,
    n_frequencies=5,
    max_frequency=1e5,
    min_frequency=1e3,
    min_sampling_time=0.01,
    max_equilibration_time=0.01,
)


GIS_cur_fixed = ps.GalvanostaticImpedanceSpectroscopy(
    n_frequencies=3,
    max_frequency=1e5,
    min_frequency=1e3,
    scan_type='current',
    frequency_type='fixed',
    begin_current=0.0,
    end_current=-0.1,
    step_current=0.1,
)


GIS_cur_scan = ps.GalvanostaticImpedanceSpectroscopy(
    n_frequencies=3,
    max_frequency=1e5,
    min_frequency=1e3,
    scan_type='current',
    frequency_type='scan',
    begin_current=0.0,
    end_current=-0.1,
    step_current=0.1,
)

GIS_time_fixed = ps.GalvanostaticImpedanceSpectroscopy(
    n_frequencies=3,
    max_frequency=1e5,
    min_frequency=1e3,
    scan_type='time',
    frequency_type='fixed',
    run_time=0.5,
)


GIS_time_scan = ps.GalvanostaticImpedanceSpectroscopy(
    n_frequencies=3,
    max_frequency=1e5,
    min_frequency=1e3,
    scan_type='time',
    frequency_type='scan',
    run_time=0.3,
)


GIS_single_point = ps.GalvanostaticImpedanceSpectroscopy(
    n_frequencies=5,
    max_frequency=1e5,
    min_frequency=1e3,
    scan_type='fixed',
    frequency_type='fixed',
)


FGIS = ps.FastGalvanostaticImpedanceSpectroscopy(applied_current_range='10uA', run_time=0.3)


MS = ps.MethodScript(
    script=(
        'var p\n'
        'var c\n'
        'set_pgstat_chan 0\n'
        'set_pgstat_mode 2\n'
        'cell_on\n'
        'meas_loop_ca p c 100m 200m 1000m\n'
        '    pck_start\n'
        '    pck_add p\n'
        '    pck_add c\n'
        '    pck_end\n'
        'endloop\n'
    )
)


MM = ps.MixedMode(
    cycles=3,
    interval_time=0.02,
    stages=[
        {
            'stage_type': 'ConstantE',
            'current_limits': {'max': 10.0, 'min': 1},
            'potential': 0.5,
            'run_time': 0.1,
            'measurement_triggers': {'d0': True, 'd2': True},
        },
        {
            'stage_type': 'ConstantI',
            'potential_limits': {'max': 1, 'min': -1},
            'current': 1.0,
            'applied_current_range': '100nA',
            'run_time': 0.1,
        },
        {
            'stage_type': 'SweepE',
            'begin_potential': -0.5,
            'end_potential': 0.5,
            'step_potential': 0.25,
            'scanrate': 20.0,
            'measurement_triggers': {'d1': True},
        },
        {'stage_type': 'OpenCircuit', 'run_time': 0.1},
        {
            'stage_type': 'Impedance',
            'run_time': 0.2,
            'dc_potential': 0.0,
            'ac_potential': 0.01,
            'min_sampling_time': 0.01,
            'max_equilibration_time': 5.0,
        },
    ],
)

CASES = {
    'cv': CV,
    'fcv': FCV,
    'lsv': LSV,
    'lsv_aux': LSV_aux,
    'acv': ACV,
    'swv': SWV,
    'cp': CP,
    'scp': SCP,
    'lsp': LSP,
    'ocp': OCP,
    'ca': CA,
    'fam': FAM,
    'dpv': DPV,
    'pad': PAD,
    'mpad': MPAD,
    'npv': NPV,
    'ma': MA,
    'mp': MP,
    'cc': CC,
    'eis': EIS,
    'eis_pot_fixed': EIS_pot_fixed,
    'eis_pot_scan': EIS_pot_scan,
    'eis_time_fixed': EIS_time_fixed,
    'eis_time_scan': EIS_time_scan,
    'eis_single_point': EIS_single_point,
    'fis': FIS,
    'gis': GIS,
    'gis_cur_fixed': GIS_cur_fixed,
    'gis_cur_scan': GIS_cur_scan,
    'gis_time_fixed': GIS_time_fixed,
    'gis_time_scan': GIS_time_scan,
    'gis_single_point': GIS_single_point,
    'fgis': FGIS,
    'ms': MS,
    'mm': MM,
}

# Blocked in C# itself, so no reference output can be produced (PLAN.md §6). These stay
# separate from the port-able techniques, which report `port not implemented`.
DEFERRED = [
    'fcv',
    'eis_pot_fixed',
    'eis_pot_scan',
    'eis_time_fixed',
    'eis_time_scan',
    'eis_single_point',
    'gis_cur_fixed',
    'gis_cur_scan',
    'gis_time_fixed',
    'gis_time_scan',
    'gis_single_point',
    'fis',
    'fgis',
    'mm',
]


def dll_payload(method: MethodTypeCompatible) -> tuple[str, dict[str, str]]:
    """Reference side: the technique name and parameters straight from the built DLL.

    `MethodMappers.ToDto` is only a composition of public APIs, so it is bypassed here;
    empty labels and curve templates mean no `Curves` keys are emitted at all.
    """
    ps_method = method._to_psmethod()
    technique = MethodExtensions.FromLegacyMethodId(ps_method.GetMethodID())
    entity = MethodExtensions.ToEntity(
        MethodExtensions.ToMethodParameters(ps_method),
        str(technique),
        '',
        Array[String](0),
        Array[CurveTemplate](0),
        DateTimeOffset.UtcNow,
    )
    return str(entity.Technique), {p.Key: p.Value for p in entity.Parameters}


def port_payload(method: MethodTypeCompatible) -> tuple[str, dict[str, str]]:
    payload = to_payload(method)
    return (
        cast('str', payload['Technique']),
        cast('dict[str, str]', payload['MethodParameters']),
    )


def mismatches(dll: tuple[str, dict[str, str]], ours: tuple[str, dict[str, str]]) -> list[str]:
    dll_technique, dll_parameters = dll
    ours_technique, ours_parameters = ours
    problems = (
        [
            f'missing {key}={value}'
            for key, value in dll_parameters.items()
            if key not in ours_parameters
        ]
        + [
            f'extra {key}={value}'
            for key, value in ours_parameters.items()
            if key not in dll_parameters
        ]
        + [
            f'differs {key}: dll={value} py={ours_parameters[key]}'
            for key, value in dll_parameters.items()
            if key in ours_parameters and ours_parameters[key] != value
        ]
    )
    if dll_technique != ours_technique:
        problems.insert(0, f'technique: dll={dll_technique} py={ours_technique}')
    return problems


def main() -> int:
    checked = 0
    failing = 0

    for name, method in CASES.items():
        print(name, method.id, type(method).__name__)

        if name in DEFERRED:
            print('  not implemented in C#')
            continue

        checked += 1

        try:
            dll = dll_payload(method)
        except Exception as exc:  # noqa: BLE001
            print(f'  dll error: {type(exc).__name__}: {exc}')
            failing += 1
            continue

        try:
            ours = port_payload(method)
        except NotImplementedError as exc:
            print(f'  port not implemented: {exc}')
            continue
        except Exception as exc:  # noqa: BLE001
            print(f'  port error: {type(exc).__name__}: {exc}')
            failing += 1
            continue

        problems = mismatches(dll, ours)
        for problem in problems:
            print(f'  {problem}')
        if problems:
            failing += 1
        else:
            print('  ok')

    blocked = len(DEFERRED)
    print(f'{checked - failing} of {checked} checked cases match, {blocked} blocked in C#')
    return 1 if failing else 0


if __name__ == '__main__':
    sys.exit(main())
