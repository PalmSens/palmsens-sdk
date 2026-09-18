from typing import Any

import numpy as np
import xarray as xr
from pydantic import TypeAdapter

import pypalmsens as ps

dpv = ps.load_session_file('examples/Demo CV DPV EIS IS-C electrode.pssession')[0]
data = dpv.dataset

attrs: dict[str, Any] = TypeAdapter(ps._data.measurement.MeasurementMetadata).dump_python(
    dpv.metadata()
)

ds = xr.Dataset(
    data_vars={
        # signal data, always with `point` (or `time`) as the dimension
        'current': (
            'point',
            data['Current'],
            {'units': data['Current'].unit, 'long_name': data['Current'].name},
        ),
        # "charge":   ("point", data['Charge'],     {"units": data['Charge'].unit, "long_name": data['Charge'].name}),
        # ancillary per-point data
        'current_range': (
            'point',
            data['Current'].current_range(),
            {'flag_values': [0, 1, 2, 3], 'flag_meanings': '100pA 1uA 10uA 100uA'},
        ),
        'current_in_range': (
            'point',
            data['Current'].current_in_range(),
            {
                'units': '?',
            },
        ),
        'current_reading_status': (
            'point',
            data['Current'].reading_status(),
            {
                'flag_values': [0, 1, 2, 4],
                'flag_meanings': 'OK Overload Underload OverloadWarning',
            },
        ),
        'current_timing_status': (
            'point',
            data['Current'].timing_status(),
            {'flag_values': [0, 1, 2], 'flag_meanings': 'Unknown OK OverStep'},
        ),
    },
    coords={
        'time': (
            'point',
            data['Time'],
            {'units': data['Time'].unit, 'long_name': data['Time'].name},
        ),
        'potential': ('point', data['Potential'], {'units': data['Potential'].unit}),
        'point': np.arange(data.n_points),
    },
    attrs=attrs,
)

print(ds)

eis = ps.load_session_file('examples/Demo CV DPV EIS IS-C electrode.pssession')[2]
data = eis.dataset

attrs: dict[str, Any] = TypeAdapter(ps._data.measurement.MeasurementMetadata).dump_python(
    eis.metadata()
)


ds = xr.Dataset(
    data_vars={
        'impedance': (
            'frequency',
            data['Z'],
            {'units': 'ohm', 'long_name': 'complex impedance'},
        ),
        # derived — store or recompute, but as variables not columns
        'Z_re': ('frequency', data['ZRe'], {'units': 'ohm'}),
        'Z_im': ('frequency', data['ZIm'], {'units': 'ohm'}),
        'admittance': ('frequency', data['Y'], {'units': 'S'}),
        'Y_re': ('frequency', data['YRe'], {'units': 'S'}),
        'Y_im': ('frequency', data['YIm'], {'units': 'S'}),
        'capacitance': ('frequency', data['Cs'], {'units': 'F'}),
        'Cs_re': ('frequency', data['CsRe'], {'units': 'F'}),
        'Cs_im': ('frequency', data['CsIm'], {'units': 'F'}),
        'phase': ('frequency', data['Phase'], {'units': 'degrees'}),
        'Time': ('frequency', data['Time']),
        'ac_current': ('frequency', data['Iac'], {'units': 'A'}),
        'current': ('frequency', data['Current'], {'units': 'A'}),
        'potential': ('frequency', data['Potential'], {'units': 'V'}),
        'n_ac_points': ('frequency', data['nPointsAC']),
        'ac_integration_time': ('frequency', data['realtintac'], {'units': 's'}),
    },
    coords={
        'frequency': ('frequency', data['Frequency'], {'units': 'Hz'}),
        'sweep_step': [0],
    },
    attrs=attrs,
)

print(ds)

breakpoint()
