%This example demonstrates how to:
%1. Connect to a PalmSens, Emstat or Sensit device
%2. Load a method specifying the measurement technique and settings
%3. Performing a measurement using the method
%Warning this will not work when only a single channel/instrument is connected

clear
%% Add PalmSens Matlab SDK to workspace
PSSDK = LoadPSSDK();
if(PSSDK == false)
    disp('Error while adding the PalmSens SDK to the workspace. Please resolve before continuing.');
    return;
end
%% 1. Connect to a PalmSens, Emstat or Sensit device
%Scan for connected devices
deviceList = GetConnectedDevices(); %see function help for scanning bluetooth and serial devices
nDevices = deviceList.Count; %number of found devices
disp([newline num2str(nDevices) ' device(s) connected:'  newline]);

%Display connected devices
for i=0:nDevices-1
    deviceName = char(deviceList.Item(i).ToString());
    disp(['Attempting to open a connection with ' deviceName]);
    %Open a connection to the specified device
    comms(i + 1).comm = OpenConnection(deviceList.Item(i));
    if(comms(i + 1).comm == false) %Check whether the connection was succesfully opened
        disp(['Error while opening a connection to ' deviceName '. Please check whether the specified device' newline ' is a PalmSens or Emstat device, remove the usb and plug it back in, and try to open the connection again' newline]);
        return;
    end
end

for i=0:nDevices-1
    deviceName = char(deviceList.Item(i).ToString());
    disp(['Succesfully connected to ' deviceName]);
end
%% 2. Load a method specifying the measurement technique and settings
%Get the folder to load/save methods from and to
%Check whether a folder containing Method files has been specified in
%settings.mat
disp([newline 'Checking presence of settings.mat']);
if (exist('settings.mat','file') == 2)
    load('settings.mat')
    %Check whether settings contains the required field
    if(isfield(Settings.Default,'psDataFolder') == 1)
        psDataFolder = Settings.Default.psDataFolder;
    end
end

%If psDataFolder is unspecified check whether PSTrace method folder exists
%in user data
if(exist('psDataFolder','var') == 0 || isnumeric(psDataFolder) || isempty(psDataFolder))
    %Get user folder
    userFolder = getenv('USERPROFILE');
    if(exist([userFolder '\My Documents\PSData'],'dir') == 7)
        psDataFolder = [userFolder '\My Documents\PSData\'];
    end
end

%Show load method dialog
disp([newline 'Please specify the location a *.psmethod file']);
if(exist('psDataFolder','var') == 0 || isnumeric(psDataFolder) || isempty(psDataFolder))
    [methodName,methodFolder] = uigetfile('*.psmethod','Please specify the location of a *.psmethod file');
else
    [methodName,methodFolder] = uigetfile('*.psmethod','Please specify the location of a *.psmethod file',psDataFolder);
end

%Store folder location of method for future reference
Settings.Default.psDataFolder = methodFolder;
save('settings.mat','Settings','-append');
disp([methodFolder ' set as default folder in settings.mat']);

%Full method path required for the LoadMethod function
methodPath = fullfile(methodFolder,methodName);
clear methodFolder psDataFolder userFolder %clean up workspace

%Load the specified method file
disp([newline 'Loading method from ' methodPath '...']);
method = LoadMethod(methodPath); %load the method object from the specified path

%Check whether the method was succesfully loaded
if(method == false)
    disp('Error loading method, please check if the PalmSens SDK has been loaded,the specified file path is correct and the *.psmethod file is valid');
end
disp(['Succesfully loaded the [ ' char(method.Name) ' ] method ' methodName '.' newline]);
%% 3. Performing a measurement using the method
%Measurements can be performed the Measurement.m class, this class gets the
%measured data from you and converts it to matlab compatible structs.
%Optionally it can display additional information on the measurement in the
%Command Window and show a plot of the data that is updated in realtime.

%Initiate an instance of the Measurement.m class using the device's
%commManager
for i=1:nDevices
    fig = figure(double(i));
    comms(i).m = MultiChannelMeasurement(comms(i).comm, fig);
    for j = 1:3 %queue methods for each channel (can be different methods)
        comms(i).queue(j).method = method;
    end
    comms(i).queueIndex = 1;

    %The measurement class has two additional data logging options that can be
    %set
    comms(i).m.dispInCommandWindow = true; %Displays status information in the command window
    comms(i).m.dispInPlot = true; %Plots measurement data in realtime (Not working properly would need to add option to pass figure to plot in as argument)
end

busy = true;
while(busy) %use helper function to process measurement queue
    [busy, comms] = MultiChannelMeasurementLoopHelper(comms);
    pause(0.01);
end
%% Safely close the connection to the device
%Disposing the measurement class
for i=1:nDevices
    delete(comms(i).m);

    %Close the connection to the device
    deviceName = char(deviceList.Item(i - 1).ToString());
    disp([newline 'Attempting to disconnect from ' deviceName]);
    try
        comms(i).comm.Disconnect();
        comms(i).comm.Dispose();
        disp(['Succesfully closed the connection to ' deviceName]);
    catch
        disp(['An error occured while trying to disconnect from ' deviceName]);
    end

    %Deleting the CommManager object
    delete(comms(i).comm); %Deleting this object removes its references to the PalmSens library and frees up resources
    disp([newline 'Comm objects resources released.'])
end

clear comms
