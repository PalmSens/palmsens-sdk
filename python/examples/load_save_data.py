from pathlib import Path


import pypalmsens as ps

examples_dir = Path(__file__).parent

# load a method file
method = ps.load_method_file(examples_dir / 'PSDummyCell_LSV.psmethod', as_method=True)

# save the method file
ps.save_method_file(examples_dir / 'PSDummyCell_LSV_copy.psmethod', method)

# load a session file
measurements = ps.load_session_file(examples_dir / 'Demo CV DPV EIS IS-C electrode.pssession')

for measurement in measurements:
    print(f'\n# Measurement: {measurement.title} @ {measurement.timestamp}')
    print(f'\n- number of curves: {len(measurement.curves)}')
    for curve in measurement.curves:
        print(f'  - curve title: {curve.title} ({curve.x_label} vs. {curve.y_label})')
        print(f'    number of points: {len(curve)}')
        print(f'    number of peaks: {len(curve.peaks)}')
    print(f'- Has EIS fit results: {"yes" if len(measurement.eis_fit) > 0 else "no"}')

    # convert measurments to pandas dataframes
    frame = measurement.dataset.to_dataframe()

    print()
    print(frame)

# save a copy of the session file
ps.save_session_file(
    examples_dir / 'Demo CV DPV EIS IS-C electrode_copy.pssession', measurements
)
