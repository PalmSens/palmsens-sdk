# Mixed Mode

This submodule contains the [Mixed Mode][pypalmsens.MixedMode] (`MM`) method.

Note that the mixed mode stages are available under the [pypalmsens.stages][] submodule.

- [`pypalmsens.stages.ConstantE`][pypalmsens.stages.ConstantE]
- [`pypalmsens.stages.ConstantI`][pypalmsens.stages.ConstantI]
- [`pypalmsens.stages.Impedance`][pypalmsens.stages.Impedance]
- [`pypalmsens.stages.OpenCircuit`][pypalmsens.stages.OpenCircuit]
- [`pypalmsens.stages.SweepE`][pypalmsens.stages.SweepE]

See [this link](https://dev.palmsens.com/python/latest/_attachments/examples/#mixed-mode) for an example how to set it up.

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
