%This example demonstrates how to:
%1. Load the PalmSens SDK library.
%2. Scan for connected devices using the GetConnectedDevices function.
%3. Open a connection to a device and get the comm manager that allows you
%   to communicate with the device using the OpenConnection function.
%4. Getting idle readings from the device.
%5. Close the connection to a device using its comm manager.
%6. Safely remove the connection manager from the workspace.

clear;
%% Get the location of the PalmSens.Core.Windows.dll
%Check if the location of the PalmSens library can be loaded from settings.mat
disp([newline 'Checking presence of settings.mat']);
loadSettings = exist('settings.mat','file');
if loadSettings == 2
    load('settings.mat')
    %Check whether settings contains the required field
    if(isfield(Settings.Default,'dllPath') == 1)
        %Check whether the previously specified folder contains the PalmSens
        %Core dll
        dllPath = Settings.Default.dllPath;
        loadSettings = exist(dllPath,'file');
        if(loadSettings ~= 2)
            loadSettings = 0;
        end
    else
        loadSettings = 0;
    end
end

%Prompt location of SDK library
while(loadSettings == 0)
    disp([newline 'Please specify the location of PalmSens.Core.Matlab.dll']);
    [dllName,dllFolder] = uigetfile('PalmSens.Core.Matlab.dll','Please specify the location of PalmSens.Core.Matlab.dll');

    %Check whether a file was selected
    if isempty(dllFolder) == 1
        disp(['No file selected, example program aborted' newline])
        return;
    end

    %Double check to determine if the selected file exists
    dllPath = fullfile(dllFolder, dllName);
    loadSettings = exist(dllPath,'file');
    if(loadSettings ~= 2)
        loadSettings = 0;
    end

    %Check to determine whether the correct file was specified
    if(dllName ~= "PalmSens.Core.Matlab.dll")
        disp(['Please select the PalmSens SDK library named PalmSens.Core.Matlab.dll' newline])
        return;
    end
end

%Store path of SDK library in settings
Settings.Default.dllPath = dllPath;
if(exist('settings.mat','file') ~= 2)
    save('settings.mat','Settings');
else
    save('settings.mat','Settings','-append');
end

%% 1. Load the PalmSens SDK library
PSSDK = NET.addAssembly(dllPath);
disp('PalmSens SDK dll loaded succesfully')
clear dll* loadSettings %clean up workspace

%% 2. Scan for connected devices
deviceList = GetConnectedDevices(); %see function help for scanning bluetooth and serial devices
nDevices = deviceList.Count; %number of found devices
disp([newline num2str(nDevices) ' device(s) connected:'  newline]);

%Display connected devices
for i=0:nDevices-1
    disp([num2str(i+1) '. ' char(deviceList.Item(i).ToString())]);
end

%Prompt device to open a connection to
selectedDevice = 0;
while(selectedDevice < 1 || selectedDevice > nDevices)
    selectedDevice = input('\nSpecify the index of the device to open a connection to (or press Control+C to cancel): \n \n');
    if(selectedDevice < 1 || selectedDevice > nDevices)
        disp(['Please enter a number between 1 and ' num2str(nDevices)]);
    end
end

%% 3. Open a connection to the selected device
selectedDevice = selectedDevice - 1;
deviceName = char(deviceList.Item(selectedDevice).ToString());
disp('');disp([newline 'Attempting to open a connection with ' deviceName]);
comm = OpenConnection(deviceList.Item(selectedDevice));
if(comm == false) %Check whether the connection was succesfully opened
    disp(['Error while opening a connection to ' deviceName '. Please check whether the specified device' newline ' is a PalmSens or Emstat device, remove the usb and plug it back in, and try to open the connection again' newline]);
    return;
end
disp(['Succesfully connected to ' deviceName]);

%% 4. Get idle readings from the device
%Single manual reading
disp([newline 'Manually reading the devices idle current and potential:']);
potential = comm.Potential;
current = comm.Current;
disp(['Potential = ' num2str(potential) ' V, Current = ' num2str(current) ' A.']);

%Continous readings
disp([newline 'Continuously reading the devices idle current and potential (for 5 seconds):' newline]);
measurement = Measurement(comm); %Instantiate object for measurement.
measurement.GetIdleData; %Start recording idle data.
pause(5)%
measurement.StopIdleData; %Stop recording idle data.
disp([newline 'Stopped recording the current and potential.']);
%retrieve the measured data from the measurement object.
potential = measurement.x_array;
current = measurement.y_array;
delete(measurement); %Delete the measurment object before clearing it
clear measurement %Clean up workspace
disp('Successfully disposed and removed the measurement object and its datalistner.');

%% 5. Close the connection to the device
disp([newline 'Attempting to disconnect from ' deviceName]);
try
    comm.Disconnect();
    disp(['Succesfully closed the connection to ' deviceName]);
catch
    disp(['An error occured while trying to disconnect from ' deviceName]);
end

%% 6. Deleting the CommManager object
delete(comm); %Deleting this object removes its references to the PalmSens library and frees up resources
clear comm
disp([newline 'Comm objects resources released.'])
