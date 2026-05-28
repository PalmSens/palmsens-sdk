# Energy techniques

This section contains a listing of all available energy techniques in PyPalmSens.

!!! Note

    These methods are based on MethodSCRIPT and therefore behave differently than the other [electrochemistry](../methods/) or [corrosion](./corrosion/) techniques.

!!! Warning "Experimental"

    Methods with the `experimental_` prefix are things that we're still working on or trying to understand. In the energy submodule you will find new, experimental methods only available in PyPalmSens.

    These methods are subject to change or removal. We welcome any [feedback and suggestions](https://github.com/palmsens/palmsens_sdk/issues) before making them a permanent part of PyPalmSens.

- [experimental_BatteryCycling][pypalmsens.energy.experimental_BatteryCycling] (CC-CV-CC)

For example to set up a battery cyclings experiment:

```python
>>> import pypalmsens as ps

>>> method = ps.experimental_BatteryCycling(
...     cycles = 10,
... )
```


## Classes

- [`pypalmsens.energy.experimental_BatteryCycling`][pypalmsens.energy.experimental_BatteryCycling]
