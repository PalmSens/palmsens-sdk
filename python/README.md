[![Tests](https://github.com/PalmSens/PalmSens_SDK/actions/workflows/python-tests.yml/badge.svg)](https://github.com/PalmSens/PalmSens_SDK/actions/workflows/python-tests.yml)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pypalmsens)](https://pypi.org/project/pypalmsens/)
[![PyPI](https://img.shields.io/pypi/v/pypalmsens.svg?style=flat)](https://pypi.org/project/pypalmsens/)

<br>

<p align="center">
    <a href="https://sdk.palmsens.com/maui/latest" target="_blank">
        <picture>
          <source media="(prefers-color-scheme: dark)" srcset="./docs/modules/ROOT/images/banner_dark.svg">
          <source media="(prefers-color-scheme: light)" srcset="./docs/modules/ROOT/images/banner.svg">
          <img alt="PalmSens banner" src="./docs/modules/ROOT/images/banner.svg" width="80%">
        </picture>
    </a>
</p>

<br>

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
- Take manual control of the cell
- Read and write method and data files

To install:

```python
pip install pypalmsens
```

PyPalmSens is built on top of the included [PalmSens .NET libraries](https://sdk.palmsens.com/start/core_dll.html), and therefore requires the .NET runtime to be installed.

For specific installation instructions for your platform, see the
[documentation](https://sdk.palmsens.com/python/latest/index.html).
