# Equivalent Circuit Fitting

[pypalmsens.fitting.CircuitModel][] fits the equivalent circuit specified with the CDC descriptor code.
Optional settings are fixing the value of a parameter, setting the min/max bounds for a parameter,
specifying the frequency range to fit, limitting the number of iterations, delta error term or delta parameter term.

Example usage for fitting an equivalent circuit:

```python
import pypalmsens as ps

measurements = ps.load_session_file('examples/Demo CV DPV EIS IS-C electrode.pssession')
eis_data = measurements[2].eis_data[0]

cdc = 'R(RC)'
model = ps.fitting.CircuitModel(cdc=cdc)
result = model.fit(eis_data)
result
#> FitResult(cdc='R(RC)', parameters=[564.65, 10077.11, 3.327e-08], chisq=0.00040, exit_code='MinimumDeltaErrorTerm', n_iter=9, error=[1.47, 1.54, 1.92])
```

`CircuitModel` takes a single parameter, the circuit description code
(CDC). Note that the code must be in all caps. For more information, see
[this link](https://www.utwente.nl/en/tnw/ims/publications/downloads/cdc-explained.pdf).

`result` is an instance of [pypalmsens.fitting.FitResult][], a dataclass with fit values,
errors, and other fitting data.
You can pass `result.parameters` back to [pypalmsens.fitting.CircuitModel.fit][]) to redo the fit:

```python
result = model.fit(eis_data, parameters=result.parameters)
print(result)
"""
FitResult(
    cdc='R(RC)',
    parameters=[134.2601650977178, 11839.398754903794, 4.7630699773802777e-07],
    error=[2.3519772479721124, 2.4664309823158033, 2.7610160451589962],
    chisq=0.01449396640068309,
    n_iter=2,
    exit_code='MinimumDeltaErrorTerm',
)
"""
```

## Parameters

If you want to tune the parameters, like fixing values or setting
bounds, you can use set them using the [pypalmsens.fitting.Parameters][] class.
`model.default_parameters` grabs the default parameters for the CDC.
These can be modified, for example:

```python
parameters = model.default_parameters()

parameters[0].value = 123  # set starting value to 123
parameters[0].fixed = True  # fix this value
parameters[1].min = 12  # set lower bound
parameters[1].max = 34  # set upper bound

result = model.fit(eis_data, parameters=parameters)
print(result)
"""
FitResult(
    cdc='R(RC)',
    parameters=[123.0, 34.0, 4.7534793266759166e-07],
    error=[nan, 160.54174486975174, 243.91299971145614],
    chisq=0.639761596501756,
    n_iter=282,
    exit_code='MinimumDeltaErrorTerm',
)
"""
```

## Re-fit EIS data

If you already fitted your data in PSTrace, you can redo the fit or use the values as a starting parameters:

```python
model = ps.fitting.CircuitModel(cdc=eis_data.cdc)
result = model.fit(eis_data, parameters=eis_data.cdc_values)
print(result)
"""
FitResult(
    cdc='R([RT]Q)',
    parameters=[
        132.14597573482914,
        11009.960398871117,
        3710.5012402266098,
        3.780788780211564,
        0.9714238919891629,
        6.237895257571337e-07,
        0.9616123965729131,
    ],
    error=[
        1.5100310284471883,
        4.600055852184849,
        37.556727628788636,
        165.04785164182704,
        25.814541664143285,
        7.221623047995394,
        0.9499742351252066,
    ],
    chisq=0.005418877355555921,
    n_iter=5,
    exit_code='MinimumDeltaErrorTerm',
)
"""
```

## Plotting

If you have [matplotlib](https://matplotlib.org) installed, you can
generate the plots from the result:

```python
fig = result.plot_nyquist(eis_data)
fig.show()

fig = result.plot_bode(eis_data)
fig.show()
```
