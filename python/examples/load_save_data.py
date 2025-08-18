from pathlib import Path

import pandas as pd

import pypalmsens

script_dir = Path(__file__).parent

# load a method file
method = pypalmsens.load_method_file(script_dir / 'PSDummyCell_LSV.psmethod', as_method=True)

# save the method file
pypalmsens.save_method_file(script_dir / 'PSDummyCell_LSV_copy.psmethod', method)

# load a session file
measurements = pypalmsens.load_session_file(
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
pypalmsens.save_session_file(
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
