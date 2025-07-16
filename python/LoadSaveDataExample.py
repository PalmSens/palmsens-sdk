from pathlib import Path

import numpy as np
import pandas

from pspython import pspyfiles, pspymethods

script_dir = Path(__file__).parent

# load a method file
method = pspyfiles.load_method_file(script_dir / 'PSDummyCell_LSV.psmethod')
print(
    f'loaded method, estimated duration: {pspymethods.get_method_estimated_duration(method)} seconds'
)

# save the method file
pspyfiles.save_method_file(script_dir / 'PSDummyCell_LSV_copy.psmethod', method)

# load a session file
measurements = pspyfiles.load_session_file(
    script_dir / 'Demo CV DPV EIS IS-C electrode.pssession'
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
    script_dir / 'Demo CV DPV EIS IS-C electrode_copy.pssession', [measurements[0]]
)

# convert measurments to pandas dataframes
frames = []
frame_names = []

for measurement in measurements:
    dataset = measurement.dataset

    data = []
    columns = []

    for i, a in enumerate(dataset.time_arrays):
        columns.append(f'time {i + 1}')
        data.append(a)

    for i, a in enumerate(dataset.freq_arrays):
        columns.append(f'frequency {i + 1}')
        data.append(a)

    for i, a in enumerate(dataset.potential_arrays):
        columns.append(f'potential {i + 1}')
        data.append(a)

    for i, a in enumerate(dataset.current_arrays):
        columns.append(f'current {i + 1}')
        data.append(a)

    for i, a in enumerate(dataset.zre_arrays):
        columns.append(f'zre {i + 1}')
        data.append(a)

    for i, a in enumerate(dataset.zim_arrays):
        columns.append(f'zim {i + 1}')
        data.append(a)

    length = max(map(len, data))
    arrays = np.array(
        [np.pad(xi, (0, length - len(xi)), constant_values=np.nan) for xi in data]
    )
    df_m = pandas.DataFrame(arrays.transpose(), index=range(length), columns=columns)
    frames.append(df_m)
    frame_names.append(measurement.title)

df = pandas.concat(frames, keys=frame_names)
print(df.head(10))
