[![Tests](https://github.com/PalmSens/PalmSens_SDK/actions/workflows/python-tests.yml/badge.svg)](https://github.com/PalmSens/PalmSens_SDK/actions/workflows/python-tests.yml)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pypalmsens)](https://pypi.org/project/pypalmsens/)
[![PyPI](https://img.shields.io/pypi/v/pypalmsens.svg?style=flat)](https://pypi.org/project/pypalmsens/)

# PyPalmSens: Python SDK for PalmSens devices

PyPalmSens is a Python library for automating electrochemistry experiments with your PalmSens instruments.
It provides an intuitive Python API, making it straightforward to integrate into your Python workflows.

With PyPalmSens, you can:

- Connect to one or more instruments/channels
- Automate electrochemistry measurements
- Access and process measured data
- Analyze and manipulate data
- Perform peak detection
- Do Equivalent Circuit Fitting on impedance data
- Manually control of the cell
- Read and write method and data files

To install:

```python
pip install pypalmsens
```

PyPalmSens is built on top of the included [PalmSens .NET libraries](https://palmsens.github.io/PalmSens_SDK/palmsens-sdk/core_dll.html), and therefore requires the .NET runtime to be installed.

For specific installation instructions for your platform, see the
[documentation](https://palmsens.github.io/PalmSens_SDK/palmsens-sdk/python/index.html).
