from pathlib import Path

import pandas as pd

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

    frames.append(dataset.to_dataframe())
    frame_names.append(measurement.title)

df = pd.concat(frames, keys=frame_names)
print(df)
