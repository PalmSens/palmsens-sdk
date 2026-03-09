# Installation

To install:

```bash
pip install pypalmsens
```

## Requirements (Windows)

* [Python version 3.10, 3.11, 3.12 or 3.13.](https://python.org)
* .NET Framework 4.7.2
* Drivers included with PSTrace 5, MultiTrace 4, PSTrace Xpress or the [driver installer](https://github.com/PalmSens/PalmSens_SDK/releases/download/drivers-5.12/PalmSens.Drivers.exe).

!!! NOTE "Python 3.14"

    Support for Python 3.14 or newer is anticipated, pending one of PyPalmSens's dependencies.

    See [this issue](https://github.com/PalmSens/PalmSens_SDK/issues/113) for more information.

## Requirements (Linux and MacOS)  {#req-linux}

* [Python version 3.10, 3.11, 3.12 or 3.13.](https://python.org). Use your system’s package manager to install Python.
* .NET Runtime 9.0 or newer. This is called something like `dotnet-runtime-9.0` in your [package manager](https://learn.microsoft.com/en-us/dotnet/core/install/linux).
    * [Ubuntu](https://learn.microsoft.com/en-us/dotnet/core/install/linux-ubuntu-install)
    * [Debian](https://learn.microsoft.com/en-us/dotnet/core/install/linux-debian)
    * [Fedora](https://learn.microsoft.com/en-us/dotnet/core/install/linux-fedora)
    * [Redhat](https://learn.microsoft.com/en-us/dotnet/core/install/linux-rhel)
    * [Raspberry Pi and other single-board ARM computers](https://learn.microsoft.com/en-us/dotnet/iot/deployment)
    * [MacOS](https://learn.microsoft.com/en-us/dotnet/core/install/macos)
* Optional: [FTDI d2xx drivers](https://ftdichip.com/drivers/d2xx-drivers/).
    * For a list of devices with an FTDI chip, see the [Compatibility table](#compatibility).
    * For Raspberry Pi 4 or 5 you need the ARMv8 driver.
    * See [below](#ftdisetup) for how to set up your system for FTDI devices.

In addition, make sure your user is added to the 'dialout' group:

```bash
$ groups
pi adm dialout ...
```

If your username is not among the list, add it using:


```bash
sudo usermod -a -G dialout $USER
```

And log out and in again to make sure the changes have take effect.
This avoids errors like `can’t open device "/dev/ttyACM0": Permission denied` when trying to connect to a device.

!!! NOTE "Known issues"

    Linux / MacOS support is a work in progress.
    Although many features work, there are some limitations compared to the Windows version.

    See [this issue](https://github.com/PalmSens/PalmSens_SDK/issues/60) for an actual list of known issues.

### FTDI devices {#ftdisetup}

To set up your system to work with devices using the [FTDI chip](https://ftdichip.com/), you need to follow a few additional steps.
To see if your device needs the FTDI drivers, see the [Compatibility table](#compatibility).

First, install the [D2XX drivers](https://ftdichip.com/drivers/d2xx-drivers/).

Set up [udev rules](https://wiki.archlinux.org/title/Udev).
`udev` manages permissions of the device to be accessible to non-root users and groups.
Add the following lines to `/etc/udev/rules.d/50-ftdi.rules`:

```ascii
ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6015", RUN+="/bin/sh -c 'rmmod ftdi_sio && rmmod usbserial'", MODE="0666"
ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6011", RUN+="/bin/sh -c 'rmmod ftdi_sio && rmmod usbserial'", MODE="0666"
ATTRS{idVendor}=="0403", ATTRS{idProduct}=="d180", RUN+="/bin/sh -c 'rmmod ftdi_sio && rmmod usbserial'", MODE="0666"
ATTRS{idVendor}=="0403", ATTRS{idProduct}=="d181", RUN+="/bin/sh -c 'rmmod ftdi_sio && rmmod usbserial'", MODE="0666"
```

And restart `udevadm`:

```bash
sudo udevadm control --reload
sudo udevadm trigger
```

### RuntimeError: Failed to create a .NET runtime (coreclr)

This error is raised if you did not install the dotnet runtime correctly. See [installation instructions above](#req-linux).

The error will say somethin along the likes of:

```bash
RuntimeError: Can not determine dotnet root
...
RuntimeError: Failed to create a .NET runtime (coreclr) using the
                parameters {'runtime_config': '/home/pi/palmsenssdk/python/src/pypalmsens/_pssdk/mono/runtimeconfig.json'}.
```

??? NOTE "Click to see example error message"

    ```bash
    (.venv) pi@raspberrypi:~/palmsenssdk/python $ python
    Python 3.13.5 (main, Jun 25 2025, 18:55:22) [GCC 14.2.0] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import pypalmsens as ps
    Traceback (most recent call last):
      File "/home/pi/palmsenssdk/python/.venv/lib/python3.13/site-packages/pythonnet/__init__.py", line 77, in _create_runtime_from_spec
        return clr_loader.get_coreclr(**params)
              ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^
      File "/home/pi/palmsenssdk/python/.venv/lib/python3.13/site-packages/clr_loader/__init__.py", line 121, in get_coreclr
        dotnet_root = find_dotnet_root()
      File "/home/pi/palmsenssdk/python/.venv/lib/python3.13/site-packages/clr_loader/util/find.py", line 57, in find_dotnet_root
        raise RuntimeError("Can not determine dotnet root")
    RuntimeError: Can not determine dotnet root

    The above exception was the direct cause of the following exception:

    Traceback (most recent call last):
      File "<&lt;>python-input-0>", line 1, in <&lt;>module>
        import pypalmsens as ps
      File "/home/pi/palmsenssdk/python/src/pypalmsens/__init__.py", line 9, in <&lt;>module>
        from ._lib.mono import sdk_version
      File "/home/pi/palmsenssdk/python/src/pypalmsens/_lib/mono.py", line 13, in <&lt;>module>
        load('coreclr', runtime_config=str(PSSDK_DIR / 'runtimeconfig.json'))
        ~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/home/pi/palmsenssdk/python/.venv/lib/python3.13/site-packages/pythonnet/__init__.py", line 135, in load
        set_runtime(runtime, **params)
        ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^
      File "/home/pi/palmsenssdk/python/.venv/lib/python3.13/site-packages/pythonnet/__init__.py", line 29, in set_runtime
        runtime = _create_runtime_from_spec(runtime, params)
      File "/home/pi/palmsenssdk/python/.venv/lib/python3.13/site-packages/pythonnet/__init__.py", line 90, in _create_runtime_from_spec
        raise RuntimeError(
        ...<&lt;>2 lines>...
        ) from exc
    RuntimeError: Failed to create a .NET runtime (coreclr) using the
                    parameters {'runtime_config': '/home/pi/palmsenssdk/python/src/pypalmsens/_pssdk/mono/runtimeconfig.json'}.
    ```

## Virtual environments

Virtual enviroments are used to create isolated Python installations.
Tools like [venv](https://docs.python.org/3/library/venv.html) or [conda](https://docs.conda.io/projects/conda/) help you create and update environment that have different versions of Python and/or packages installed in them. This makes them useful for software development.

This section shows how to set up and activate an environment.

Setting up a virtual environment using [Python, pip and venv](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/):


```powershell
python -m venv .venv
.venv/Scripts/activate.ps1
python -m pip install -e .[develop]
```

Alternatively, setting up a [virtual environment using Conda](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html):

```powershell
conda create -n pypalmsens python=3.13
conda activate pypalmsens
pip install pypalmsens
```

### Visual Studio Code

[VS Code](https://code.visualstudio.com/) supports virtual environments. In combination with the Python, Python Debugger and Pylance extensions, VS code makes it easy to create virtual environments and load the python dependencies.

See the [VSCode documentation](https://code.visualstudio.com/docs/python/environments#_creating-environments) for how to set this up.


## Compatible devices and firmware {#compatibility}

The PalmSens SDK is based on PalmSens core version 5.12.

The table below lists the minimum supported firmwares versions and required drivers.

You can update the firmware using a recent version of PSTrace on a Windows PC
See the chapter 'Updating firmware' in the [PSTrace user manual](https://www.palmsens.com/knowledgebase-article/pstrace-user-manual/) for more information.

| Instrument | Firmware version | Windows drivers | Linux/MacOS drivers |
|-|-|-|-|
| Nexus | 1.100 | palmsens_cdc.inf (optional) [^1] | n/a [^3] |
| Palmsens1 | 4.4 | PalmSens FTDI [^1] | Generic FTDI [^4] |
| Palmsens2 | 4.4 | PalmSens FTDI [^1] | Generic FTDI [^4] |
| Palmsens3 | 2.8 | PalmSens FTDI [^1] | Generic FTDI [^4] |
| Palmsens4 | 1.7 | palmsens_cdc.inf (optional) [^1] | n/a [^3] |
| MultiPalmsens4 | 1.7 | Generic FTDI [^2] | Generic FTDI [^4] |
| EmStat1 | 3.7 | PalmSens FTDI [^1] | Generic FTDI [^4] |
| EmStat2 | 7.7 | PalmSens FTDI [^1] | Generic FTDI [^4] |
| EmStat3 | 7.7 | PalmSens FTDI [^1] | Generic FTDI [^4] |
| EmStat3+ | 7.7 | PalmSens FTDI [^1] | Generic FTDI [^4] |
| MultiEmStat3 | 7.7 | PalmSens FTDI [^1] | Generic FTDI [^4] |
| EmStat3 Blue | 7.7 | PalmSens FTDI [^1] | Generic FTDI [^4] |
| EmStat3+ Blue | 7.7 | PalmSens FTDI [^1] | Generic FTDI [^4] |
| EmStat3 Go | 7.7 | PalmSens FTDI [^1] | Generic FTDI [^4] |
| EmStat3+ Go | 7.7 | PalmSens FTDI [^1] | Generic FTDI [^4] |
| EmStat4S | 1.307 | palmsens_cdc.inf (optional) [^1] | n/a [^3] |
| MultiEmStat4 | 1.307 | palmsens_cdc.inf (optional) [^1] | n/a [^3] |
| EmStat4X | 1.307 | palmsens_winusb.inf (optional) [^1] | n/a [^3] |
| EmStat4R | 1.307 | Generic FTDI [^2] | Generic FTDI [^4] |
| EmStat4M | 1.307 | palmsens_cdc.inf (optional) [^1] | n/a [^3] |
| EmStat4T | 1.406 | palmsens_cdc.inf (optional) [^1] | n/a [^3] |
| EmStat4 Go | 1.307 | Generic FTDI [^2] | Generic FTDI [^4] |
| EmStat Pico DevBoard | 1.601 | Generic FTDI (optional) [^2] | n/a [^3] |
| EmStat Pico Module | 1.601 | Generic FTDI (optional) [^2] | n/a [^3] |
| EmStat Pico Go | 1.601 | Generic FTDI (optional) [^2] | n/a [^3] |
| Sensit Smart | 1.601 | Generic FTDI (optional) [^2] | n/a [^3] |
| Sensit BT | 1.601 | Generic FTDI (optional) [^2] | n/a [^3] |
| Sensit Wearable | 1.600 | Generic FTDI (optional) [^2] | n/a [^3] |

[^1]: Drivers are installed with alongside the PSTrace desktop software or using [the driver installer](https://github.com/PalmSens/PalmSens_SDK/releases/download/drivers-5.12/PalmSens.Drivers.exe).
[^2]: Available from https://ftdichip.com/drivers/d2xx-drivers/
[^3]: The SDK communicates directly via the serial port. No drivers are necessary.
[^4]: See [the installation instructions](#req-linux) for more info.
