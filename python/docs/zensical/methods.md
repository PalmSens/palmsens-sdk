# Methods

## Supported methods

The following methods are supported in PyPalmSens:

**Voltammetric Techniques**

- [Linear Sweep Voltammetry][pypalmsens.LinearSweepVoltammetry]
- [Cyclic Voltammetry][pypalmsens.CyclicVoltammetry]
- [Fast Cyclic Voltammetry][pypalmsens.FastCyclicVoltammetry]
- [AC Voltammetry][pypalmsens.ACVoltammetry]

**Pulsed Techniques**

- [Differential Pulse Voltammetry][pypalmsens.DifferentialPulseVoltammetry]
- [Square Wave Voltammetry][pypalmsens.SquareWaveVoltammetry]
- [Normal Pulse Voltammetry][pypalmsens.NormalPulseVoltammetry]

**Amperometric Techniques**

- [Chronoamperometry][pypalmsens.ChronoAmperometry]
- [Multistep Amperometry][pypalmsens.MultiStepAmperometry]
- [Fast Amperometry][pypalmsens.FastAmperometry]
- [Pulsed Amperometric Detection][pypalmsens.PulsedAmperometricDetection]
- [Multiple Pulse Amperometry][pypalmsens.MultiplePulseAmperometry]

**Potentiometric Techniques**

- [Open Circuit Potentiometry][pypalmsens.OpenCircuitPotentiometry]
- [Chronopotentiometry][pypalmsens.ChronoPotentiometry]
- [Linear Sweep Potentiometry][pypalmsens.LinearSweepPotentiometry]
- [Multistep Potentiometry][pypalmsens.MultiStepPotentiometry]
- [Stripping Chronopotentiometry][pypalmsens.StrippingChronoPotentiometry]

**Coulometric techniques**

- [Chronocoulometry][pypalmsens.ChronoCoulometry]

**Other**

- [Impedance Spectroscopy][pypalmsens.ElectrochemicalImpedanceSpectroscopy]
- [Fast Impedance Spectroscopy][pypalmsens.FastImpedanceSpectroscopy]
- [Galvanostatic Impedance Spectroscopy][pypalmsens.GalvanostaticImpedanceSpectroscopy]
- [Fast Galvanostatic Impedance Spectroscopy][pypalmsens.FastGalvanostaticImpedanceSpectroscopy]
- [Mixed Mode][pypalmsens.MixedMode]
- [Method Script][pypalmsens.MethodScript] | [Stages][pypalmsens.stages]

## Setting up a method

This example creates a method for a [square-wave voltammetry][pypalmsens.SquareWaveVoltammetry] measurement versus the open circuit potential:

```py
import pypalmsens as ps

method = ps.SquareWaveVoltammetry(
    pretreatment={
        'conditioning_potential': 2.0,  # V
        'conditioning_time': 2,  # seconds
    },
    versus_ocp = {'mode': 3,  # versus begin and end potential
        'max_ocp_time': 1,},  # seconds
    begin_potential = -0.5,  # V
    end_potential = 0.5,  # V
    step_potential = 0.01,  # V
    amplitude = 0.08,  # V
    frequency = 10,  # Hz
)
```

Because methods are [pydantic models](https://docs.pydantic.dev/latest/), all attributes can be modified afterwards:

```py
method.begin_potential = -1.0
method.end_potential = 1.0
method.step_potential = 0.02
```

Methods can be serialized to and from a dictionary:

```py
dumped = method.model_dump()
print(dumped)
"""
{
    'general': {
        'save_on_internal_storage': False,
        'use_hardware_sync': False,
        'notes': '',
        'power_frequency': 50,
    },
    'multiplexer': {
        'mode': 'none',
        'channels': [],
        'connect_sense_to_working_electrode': False,
        'combine_reference_and_counter_electrodes': False,
        'use_channel_1_reference_and_counter_electrodes': False,
        'set_unselected_channel_working_electrode': 0,
    },
    'data_processing': {'smooth_level': 0, 'min_height': 0.0, 'min_width': 0.1},
    'measurement_triggers': {'d0': False, 'd1': False, 'd2': False, 'd3': False},
    'equilibrion_triggers': {'d0': False, 'd1': False, 'd2': False, 'd3': False},
    'ir_drop_compensation': {'resistance': None},
    'post_measurement': {
        'cell_on_after_measurement': False,
        'standby_potential': 0.0,
        'standby_time': 0.0,
    },
    'bipot': {'mode': 'constant', 'potential': 0.0, 'current_range': '1uA'},
    'versus_ocp': {'mode': 3, 'max_ocp_time': 1.0, 'stability_criterion': 0.0},
    'pretreatment': {
        'deposition_potential': 0.0,
        'deposition_time': 0.0,
        'conditioning_potential': 2.0,
        'conditioning_time': 2.0,
    },
    'current_range': {'max': '10mA', 'min': '1uA', 'start': '100uA'},
    'id': 'swv',
    'equilibration_time': 0.0,
    'begin_potential': -1.0,
    'end_potential': 1.0,
    'step_potential': 0.02,
    'frequency': 10.0,
    'amplitude': 0.08,
    'enable_bipot_current': False,
    'record_auxiliary_input': False,
    'record_cell_potential': False,
    'record_we_potential': False,
    'record_forward_and_reverse_currents': False,
}
"""
method2 = ps.SquareWaveVoltammetry(**dumped)
assert method == method2
```

Methods can be copied and updated:

```py
method3 = method.model_copy(update={'equilibration_time' : 10.0})
assert method != method3
```

!!! TIP

    The VSCode Debug Console or another Python REPL environment like [IPython](https://ipython.readthedocs.io) will auto complete on the properties and functions.

    ![Debug console in VSCode](assets/ipython_autocomplete.png){ width="80%" }


### Common settings

Many settings are shared between methods.
For a full listing, see [`pypalmsens.settings`](reference/methods/settings.md).

If you don’t specify any arguments, the default values are loaded.
These are accessible via attributes on the methods.

For example:

```py
cv = ps.CyclicVoltammetry()
print(cv.current_range)
#> max='10mA' min='1uA' start='100uA'
```

There are two ways to modify the current ranges, for example, if you want so set the start current at 10 μA.

1. By passing current ranges as an argument during initialization

    ```py
    cv = ps.CyclicVoltammetry(current_range={'start':'10uA'})
    cv.current_range
    #> CurrentRange(max='10mA', min='1uA', start='10uA') # (1)!
    ```

    1. Only the start value was set, so the min/max are populated with the defaults.

2. By updating the attributes (after initialization)

    ```py
    cv = ps.CyclicVoltammetry()
    cv.current_range.start = '10uA'
    ```

!!! TIP "Fixed ranges"

    If you want to use a fixed current (or potential) range,
    you can save yourself some typing by passing the current range string directly.
    This automatically expands into the `CurrentRange` object with `min`, `max`, and `start` equal.

    ```py
    cv = ps.CyclicVoltammetry(current_range='10uA')
    cv.current_range
    #> CurrentRange(max = '10uA',min = '10uA',start = '10uA')
    ```

### Validation

Methods are defined as [Pydantic Models](https://docs.pydantic.dev/latest/concepts/models/).
Pydantic is a library for defining a schema via models.
They are very similar to [Python dataclasses](https://docs.python.org/3/library/dataclasses.html#module-dataclasses) in the way that they work.

The important difference is that Pydantic offers more options for [validation, serialization, and conversion](https://docs.pydantic.dev/latest/concepts/dataclasses/).

This means is automatically converts dictionaries to the correct type (if the fields can be matched), for example:

```py
import pypalmsens as ps

cv = ps.CyclicVoltammetry(
    current_range = {'min':'10mA', 'max':'1uA', 'start':'100uA'}
)
print(cv.current_range)
#> max='1uA' min='10mA' start='100uA'
```

And gives an errorr when trying to overwrite types by invalid dictionaries or instances:

```py test="skip"
cv.current_range='foo'
#> ValidationError: 1 validation error for CyclicVoltammetry
#> current_range
#>   Input should be a valid dictionary or instance of CurrentRange [type=model_type, input_value='foo', input_type=str]
#>     For further information visit https://errors.pydantic.dev/2.12/v/model_type
```

It is also helps prevents setting non-existant variables and guard against typos:

```py test="skip"
cv = ps.CyclicVoltammetry(foo=123, scanreat=2.0)
#> ValidationError: 2 validation errors for CyclicVoltammetry
#> foo
#>   Extra inputs are not permitted [type=extra_forbidden, input_value=123, input_type=int]
#>     For further information visit https://errors.pydantic.dev/2.12/v/extra_forbidden
#>     scanreat
#>   Extra inputs are not permitted [type=extra_forbidden, input_value=1.0, input_type=float]
#>     For further information visit https://errors.pydantic.dev/2.12/v/extra_forbidden
```

['Strict' mode](https://docs.pydantic.dev/latest/concepts/strict_mode/) helps catching variable errors, for example when you set a string when a number (float) is expected:

```py test="skip"
cv = ps.CyclicVoltammetry(scanrate='1.0')
#> ValidationError: 1 validation error for CyclicVoltammetry
#> scanrate
#>   Input should be a valid number [type=float_type, input_value='1.0', input_type=str]
#>     For further information visit https://errors.pydantic.dev/2.12/v/float_type
```

It also prevents setting non-existant attributes:

```py test="skip"
cv.scanreat=1.0
#> ValueError: "CyclicVoltammetry" object has no field "scanreat"
```

Or unexpected values:

```py test="skip"
cp = ps.ChronoPotentiometry(applied_current_range='1GA')
#> ValidationError: 1 validation error for ChronoPotentiometry
#> applied_current_range
#>   Input should be '100pA', '1nA', ... or '1A' [type=literal_error, input_value='1GA', input_type=str]
#>     For further information visit https://errors.pydantic.dev/2.12/v/literal_error
```

## Starting a measurement

For further information on how to run a measurement:

* [Measuring](measuring.md)
* [Examples](examples.md)
