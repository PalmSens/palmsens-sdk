[![Tests](https://github.com/PalmSens/PalmSens_SDK/actions/workflows/python-tests.yml/badge.svg)](https://github.com/PalmSens/PalmSens_SDK/actions/workflows/python-tests.yml)
![Coverage](https://img.shields.io/badge/coverage-87%25-brightgreen)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pypalmsens)](https://pypi.org/project/pypalmsens/)
[![PyPI](https://img.shields.io/pypi/v/pypalmsens.svg?style=flat)](https://pypi.org/project/pypalmsens/)

<br>

<p align="center">
    <a href="https://dev.palmsens.com/maui/latest" target="_blank">
        <picture>
          <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/PalmSens/PalmSens_SDK/refs/heads/main/python/docs/modules/ROOT/images/banner_dark.svg">
          <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/PalmSens/PalmSens_SDK/refs/heads/main/python/docs/modules/ROOT/images/banner.svg">
          <img alt="PalmSens banner" src="https://raw.githubusercontent.com/PalmSens/PalmSens_SDK/refs/heads/main/python/docs/modules/ROOT/images/banner.svg" width="80%">
        </picture>
    </a>
</p>

<br>

# PyPalmSens: Python SDK for PalmSens devices

PyPalmSens is a Python library for automating electrochemistry experiments with your PalmSens instruments.
It provides an intuitive Python API, making it straightforward to integrate into your Python workflows.

With PyPalmSens, you can:

- Connect to [one](https://dev.palmsens.com/python/latest/_attachments/measuring/#connecting-to-a-device) or [more](https://dev.palmsens.com/python/latest/_attachments/measuring/#multichannel-measurements) instruments/channels
- Automate [electrochemistry measurements](https://dev.palmsens.com/python/latest/_attachments/methods)
- [Read and write method and data files](https://dev.palmsens.com/python/latest/_attachments/files)
- [Access, process, and analyze](https://dev.palmsens.com/python/latest/_attachments/data) measured data
- Perform [peak detection](https://dev.palmsens.com/python/latest/_attachments/reference/data/#pypalmsens.data.Curve.find_peaks)
- Do [Equivalent Circuit Fitting](https://dev.palmsens.com/python/latest/_attachments/circuit_fitting) on impedance data
- Take [manual control](https://dev.palmsens.com/python/latest/_attachments/examples/#manual-control) of the cell

To install:

```python
pip install pypalmsens
```

PyPalmSens is built on top of the included [PalmSens .NET libraries](https://dev.palmsens.com/dotnet/api/core.html), and therefore requires the .NET runtime to be installed.

For specific installation instructions for your platform, see the
[documentation](https://dev.palmsens.com/python/latest/_attachments/index.html).
