function [ deviceList ] = GetConnectedDevices( bluetooth, serial )
%GetConnectedDevices returns a list of all the connected comm devices.
%
%Optional Inputs:
%
%bluetooth: a boolean that when set to true enables scanning for bluetooth.
%Setting bluetooth to false is faster. (By default scanning for bluetooth
%is disabled)
%
%serial: a boolean that when set to true enables scanning for serial
%devices. (By default scanning for serial devices is disabled)
%
%Output:
%
%deviceList: List objects<PalmSens.Devices.Device> representing the
%connected devices

%Check input parameters
if(nargin == 1)
    serial = false;
end
if(nargin == 0)
    serial = false;
    bluetooth = false;
end

%Create an empty device list
deviceList = NET.createGeneric('System.Collections.Generic.List',{'PalmSens.Devices.Device'});

%Create an error string, required as an input parameter
errors = System.String('');

%Scan for connected devices
listUSBCDC = PalmSens.Windows.Devices.USBCDCDevice.DiscoverDevicesMatlab(errors);
listFTDI = PalmSens.Windows.Devices.FTDIDevice.DiscoverDevices(errors);

%Add devices to connected device list
deviceList.AddRange(listUSBCDC); %PalmSens 4
deviceList.AddRange(listFTDI); %PalmSens 3 and Emstats

%Scan for and add bluetooth devices to connected device list
if(bluetooth == true)
    listBluetooth = PalmSens.Windows.Devices.BluetoothDevice.DiscoverDevices(errors);
    deviceList.AddRange(listBluetooth);
end

%Scan for and add serial devices to connected device list
if(serial == true)
    listSerial = PalmSens.Windows.Devices.SerialPortDevice.DiscoverDevices(errors);
    deviceList.AddRange(listSerial);
end

%Remove duplicates from the connected device list
n = deviceList.Count - 1;
i = 0;
while(i <= n)
    j = i + 1;
    str = deviceList.Item(i).ToString();
    while(j <= n)
        if(str == deviceList.Item(j).ToString())
            deviceList.RemoveAt(j);
            n = deviceList.Count - 1;
        else
            j = j + 1;
        end
    end
    i = i + 1;
end

end
