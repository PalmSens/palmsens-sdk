# Energy techniques

This section contains a listing of all available energy techniques in PyPalmSens.

In the energy submodule you will find new methods only available in PyPalmSens.

!!! Note

    These methods are based on MethodSCRIPT and therefore behave differently than the other [electrochemistry](../methods/) or [corrosion](./corrosion/) techniques.

!!! Warning "Experimental"

    Classes with the `experimental_` prefix are things that we're still working on or trying to understand. That means these classes are subject to change.

    We welcome any [feedback and suggestions](https://github.com/palmsens/palmsens_sdk/issues) before making them a permanent part of PyPalmSens.

- [experimental_BatteryCycling][pypalmsens.energy.experimental_BatteryCycling] (CC-CV-CC)
- [experimental_ConstantPower][pypalmsens.energy.experimental_ConstantPower] (Discharge at constant power)
- [experimental_ConstantResistance][pypalmsens.energy.experimental_ConstantResistance] (Discharge at constant resistance)

For example to set up a battery cycling experiment:

```python
>>> import pypalmsens as ps

>>> method = ps.experimental_BatteryCycling(
...     cycles = 10,
... )
```


## Classes

- [`pypalmsens.energy.experimental_BatteryCycling`][pypalmsens.energy.experimental_BatteryCycling]
- [`pypalmsens.energy.experimental_ConstantPower`][pypalmsens.energy.experimental_ConstantPower]
- [`pypalmsens.energy.experimental_ConstantResistance`][pypalmsens.energy.experimental_ConstantResistance]
