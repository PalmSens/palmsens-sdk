# Installation

Getting started is easy! Follow the installation steps below based on your operating system.

To install the package globally using pip, run this command in your terminal:

```bash
pip install pypalmsens
```

!!! NOTE "Python 3.15"

    Python 3.15 is currently not supported, pending support of the libraries we use. Please refer to [this issue](https://github.com/palmsens/palmsens-sdk/issues/433) for the latest information.

## Windows

*   Install [Python](https://python.org) version 3.10 or newer
*   Install [.NET Runtime 10.0](https://dotnet.microsoft.com/en-us/download/dotnet/10.0) or newer
*   Install device drivers (see the [Compatibility table](#compatibility)):
    * If you installed PSTrace or Multitrace, drivers are already installed
    * For standalone installations, use the [driver installer](https://github.com/palmsens/palmsens-sdk/releases/download/drivers-5.12/PalmSens.Drivers.exe).

## Linux and macOS {#req-linux}

*   Install [Python](https://python.org) version 3.10 or newer
*   Install [.NET Runtime 10.0](https://dotnet.microsoft.com/en-us/download/dotnet/10.0) or newer. You can typically find the required runtime (e.g., `dotnet-runtime-10.0`) in your [package manager](https://learn.microsoft.com/en-us/dotnet/core/install/linux).
    *   [Installation guides for Ubuntu](https://learn.microsoft.com/en-us/dotnet/core/install/linux-ubuntu-install)
    *   [Installation guides for Debian](https://learn.microsoft.com/en-us/dotnet/core/install/linux-debian)
    *   [Installation guides for Fedora](https://learn.microsoft.com/en-us/dotnet/core/install/linux-fedora)
    *   [Installation guides for Red Hat](https://learn.microsoft.com/en-us/dotnet/core/install/linux-rhel)
    *   [Installation guides for Raspberry Pi and other ARM computers](https://learn.microsoft.com/en-us/dotnet/iot/deployment)
    *   [Installation guides for macOS](https://learn.microsoft.com/en-us/dotnet/core/install/macos)

*   Optional: Install FTDI d2xx drivers
    *   For a list of compatible devices, see the [Compatibility table](#compatibility).
    *   If you are using a Raspberry Pi 4 or 5, you will need the ARMv8 driver.
    *   See the [FTDI setup guide](#ftdisetup) for detailed system setup instructions.


### System Permissions

To avoid permission errors (like `"can’t open device "/dev/ttyACM0": Permission denied"`), ensure your user is part of the `dialout` group:

```bash
groups
# pi adm dialout ...
```

If your username is missing from the list, add it using this command:

```bash
sudo usermod -a -G dialout $USER
```
**You must log out and log back in** for these changes to take effect.

### FTDI Device Setup {#ftdisetup}

Some devices have an [FTDI chip](https://ftdichip.com) that needs additional drivers. To see if your device needs the FTDI drivers, see the [Compatibility table](#compatibility).

#### 1. Install the drivers

Download and install the [D2XX drivers](https://ftdichip.com/drivers/d2xx-drivers/).
See the link for full instructions. You can use this command sequence for a typical Linux system:

```bash
tar xfvz libftd2xx-$PLATFORM-$VERSION.tgz
cd $PLATFORM
sudo cp libftd2xx.* /usr/local/lib
sudo chmod 0755 /usr/local/lib/libftd2xx.so.$VERSION
sudo ln -sf /usr/local/lib/libftd2xx.so.$VERSION /usr/local/lib/libftd2xx.so
```

And update the linker cache:

```bash
sudo ldconfig -v
```

#### 2. Configure udev rules


Second, set up [udev rules](https://wiki.archlinux.org/title/Udev).
`udev` manages permissions of the device to be accessible to non-root users and groups.

Set up [`udev` rules](https://wiki.archlinux.org/title/Udev) to grant access permissions to your device to non-root users and groups.

Add the following lines to `/etc/udev/rules.d/50-ftdi.rules`:

```ascii
ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6015", RUN+="/bin/sh -c 'rmmod ftdi_sio && rmmod usbserial'", MODE="0666"
ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6011", RUN+="/bin/sh -c 'rmmod ftdi_sio && rmmod usbserial'", MODE="0666"
ATTRS{idVendor}=="0403", ATTRS{idProduct}=="d180", RUN+="/bin/sh -c 'rmmod ftdi_sio && rmmod usbserial'", MODE="0666"
ATTRS{idVendor}=="0403", ATTRS{idProduct}=="d181", RUN+="/bin/sh -c 'rmmod ftdi_sio && rmmod usbserial'", MODE="0666"
```

Restart `udevadm` to load the new rules:

```bash
sudo udevadm control --reload
sudo udevadm trigger
```

### RuntimeError: Failed to create a .NET runtime (coreclr)

This error usually means the .NET runtime was not installed correctly. If you encounter this error, please review the [installation instructions above](#req-linux).

The error message might look something like this:

```
RuntimeError: Can not determine dotnet root
...
RuntimeError: Failed to create a .NET runtime (coreclr) using the
                parameters {'runtime_config': '/home/pi/palmsenssdk/python/src/pypalmsens/_pssdk/mono/runtimeconfig.json'}.
```

## Virtual Environments

We recommend using virtual environments to isolate your project dependencies. Use tools like [venv](https://docs.python.org/3/library/venv.html) or [Conda](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html) to manage different Python versions and packages.

### venv

The venv module is part of the standard library and therefore a common way to set up an environment.

For Windows:

```powershell
python -m venv .venv
.venv/Scripts/activate.ps1
python -m pip install -e .[develop]
```

For Bash:

```powershell
python -m venv .venv
. .venv/bin/activate
python -m pip install -e .[develop]
```

### Conda

If you prefer Conda, use these commands:

```powershell
conda create -n pypalmsens python=3.14
conda activate pypalmsens
pip install pypalmsens
```

### Visual Studio Code

[VS Code](https://code.visualstudio.com/) also supports virtual environments. In combination with the Python, Python Debugger and Pylance extensions, VS code makes it easy to create virtual environments and load your python dependencies.

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

[^1]: Drivers are installed with alongside the PSTrace desktop software or using [the driver installer](https://github.com/palmsens/palmsens-sdk/releases/download/drivers-5.12/PalmSens.Drivers.exe).
[^2]: Available from <https://ftdichip.com/drivers/d2xx-drivers/>
[^3]: The SDK communicates directly via the serial port. No drivers are necessary.
[^4]: See [the installation instructions](#req-linux) for more info.
