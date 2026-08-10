# Equivalent Circuit Fitting

[pypalmsens.fitting.CircuitModel][] fits the equivalent circuit specified with the CDC descriptor code.
Optional settings are fixing the value of a parameter, setting the min/max bounds for a parameter,
specifying the frequency range to fit, limiting the number of iterations, delta error term or delta parameter term.

Example usage for fitting an equivalent circuit:

```pycon
>>> import pypalmsens as ps

>>> measurements = ps.load_session_file('examples/Demo CV DPV EIS IS-C electrode.pssession')
>>> eis_data = measurements[2].eis_data[0]

>>> cdc = 'R(RC)'
>>> model = ps.fitting.CircuitModel(cdc=cdc)
>>> result = model.fit(eis_data)
>>> result
FitResult(cdc='R(RC)', parameters=[134.2601648341703, 11839.397430811792, 4.763069310462662e-07], error=[...], ...)

```

`result` is an instance of [pypalmsens.fitting.FitResult][], a dataclass with fit values, errors, and other fitting data:

```pycon
>>> result.cdc
'R(RC)'

>>> result.parameters
[134.2601648341703, 11839.397430811792, 4.763069310462662e-07]

>>> result.error
[2.3519772735560074, 2.466430045381699, 2.7610107312609493]

>>> result.n_iter
19

>>> result.chisq
0.014493966401698677

>>> result.exit_code
'MinimumDeltaErrorTerm'

```

`CircuitModel` takes a single parameter, the circuit description code (CDC).
Note that the code must be in all caps. For more information, see the [CDC documentation](https://www.utwente.nl/en/tnw/ims/publications/downloads/cdc-explained.pdf).

You can pass `result.parameters` back to [pypalmsens.fitting.CircuitModel.fit][]) to redo the fit from different starting parameters:

```pycon
>>> model.fit(eis_data, parameters=result.parameters)
FitResult(cdc='R(RC)', parameters=[...], ...)

```

## Parameters

If you want to tune the parameters, like fixing values or setting bounds, you can set them using the [pypalmsens.fitting.Parameters][] class.
`model.default_parameters` grabs the default parameters for the CDC.

These can be modified, for example:

```pycon
>>> parameters = model.default_parameters()

>>> parameters[0].value = 123  # set starting value to 123
>>> parameters[0].fixed = True # fix this value
>>> parameters[1].min = 12  # set lower bound
>>> parameters[1].max = 34  # set upper bound

>>> model.fit(eis_data, parameters=parameters)
FitResult(cdc='R(RC)', parameters=[...], error=[...], ...)

```

## Re-fit EIS data

If you have already fitted your data in PSTrace, you can redo the fit or use the values as starting parameters:

```pycon
>>> model = ps.fitting.CircuitModel(cdc=eis_data.cdc)
>>> model.fit(eis_data, parameters=eis_data.cdc_values)
FitResult(cdc='R([RT]Q)', parameters=[...], error=[...], ...)

```

## Plotting

If you have [matplotlib](https://matplotlib.org) installed, you can
generate the plots from the result:

```pycon
>>> result.plot_nyquist(eis_data)
<Figure size 640x480 with 1 Axes>

>>> result.plot_bode(eis_data)
<Figure size 640x480 with 2 Axes>

```
