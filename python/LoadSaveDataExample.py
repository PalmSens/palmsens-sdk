import os

import numpy as np
import pandas

from pspython import pspyfiles, pspymethods

scriptDir = os.path.dirname(os.path.realpath(__file__))

# load a method file
method = pspyfiles.load_method_file(os.path.join(scriptDir, 'PSDummyCell_LSV.psmethod'))
print(
    f'loaded method, estimated duration: {pspymethods.get_method_estimated_duration(method)} seconds'
)

# save the method file
pspyfiles.save_method_file(os.path.join(scriptDir, 'PSDummyCell_LSV_copy.psmethod'), method)

# load a session file
measurements = pspyfiles.load_session_file(
    os.path.join(scriptDir, 'Demo CV DPV EIS IS-C electrode.pssession'),
    load_peak_data=True,
    load_eis_fits=True,
    return_dotnet_object=True,
)

for measurement in measurements:
    print(f'loaded measurement: {measurement.title}, {measurement.timestamp}')
    print(f'number of curves: {len(measurement.curves)}')
    for curve in measurement.curves:
        print(f'curve title: {curve.title}')
        print(f'number of points: {len(curve.x_array)}')
        print(f'number of peaks: {len(curve.peaks)}')
    print(f'Has EIS fit results: {"yes" if len(measurement.eis_fit) > 0 else "no"}')

# save the session file
pspyfiles.save_session_file(
    os.path.join(scriptDir, 'Demo CV DPV EIS IS-C electrode_copy.pssession'), [measurements[0]]
)

# convert measurments to pandas dataframes
frames = []
frame_names = []

for m in measurements:
    data = []
    columns = []

    for i, a in enumerate(m.time_arrays):
        columns.append(f'time {i + 1}')
        data.append(a)

    for i, a in enumerate(m.freq_arrays):
        columns.append(f'frequency {i + 1}')
        data.append(a)

    for i, a in enumerate(m.potential_arrays):
        columns.append(f'potential {i + 1}')
        data.append(a)

    for i, a in enumerate(m.current_arrays):
        columns.append(f'current {i + 1}')
        data.append(a)

    for i, a in enumerate(m.zre_arrays):
        columns.append(f'zre {i + 1}')
        data.append(a)

    for i, a in enumerate(m.zim_arrays):
        columns.append(f'zim {i + 1}')
        data.append(a)

    length = max(map(len, data))
    arrays = np.array([xi + [None] * (length - len(xi)) for xi in data], dtype=float)
    df_m = pandas.DataFrame(arrays.transpose(), index=range(length), columns=columns)
    frames.append(df_m)
    frame_names.append(m.title)

df = pandas.concat(frames, keys=frame_names)
print(df.head(10))
