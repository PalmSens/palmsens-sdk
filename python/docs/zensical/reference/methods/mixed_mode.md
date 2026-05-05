# Mixed Mode

This submodule contains the Mixed Mode (`MM`) method and Stage classes.

See [this link](https://dev.palmsens.com/python/latest/_attachments/examples/#mixed-mode) for an example how to set it up.

Note that the mixed mode stages are available under the [pypalmsens.stages][] submodule.

For example:

```python
import pypalmsens as ps

method = ps.MixedMode(
    stages=[
        ps.stages.ConstantI(run_time=5, current=1.0)
        ps.stages.ConstantE(run_time=5, potential=0.5),
        ps.stages.OpenCircuit(run_time=30),
    ]
)
```

::: pypalmsens.MixedMode
    options:
      members_order: source

::: pypalmsens.stages
    options:
      members_order: source
      members:
        - ConstantE
        - ConstantI
        - SweepE
        - OpenCircuit
        - Impedance
