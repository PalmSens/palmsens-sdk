%This example demonstrates how to:
%1. Connect to a PalmSens, Emstat or Sensit device
%2. Load a method specifying the measurement technique and settings
%3. Performing a measurement using the method
%4. Plotting the measurement

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

%Open a connection to the specified device
selectedDevice = selectedDevice - 1;
deviceName = char(deviceList.Item(selectedDevice).ToString());
disp('');disp([newline 'Attempting to open a connection with ' deviceName]);
comm = OpenConnection(deviceList.Item(selectedDevice));
if(comm == false) %Check whether the connection was succesfully opened
    disp(['Error while opening a connection to ' deviceName '. Please check whether the specified device' newline ' is a PalmSens or Emstat device, remove the usb and plug it back in, and try to open the connection again' newline]);
    return;
end
disp(['Succesfully connected to ' deviceName]);
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
disp([newline 'Specify the location a *.psmethod file']);
if (exist('psDataFolder','var') == 0 | isnumeric(psDataFolder) | isempty(psDataFolder))
    [methodName,methodFolder] = uigetfile('*.psmethod','Load PalmSens method file');
else
    [methodName,methodFolder] = uigetfile('*.psmethod','Load PalmSens method file',psDataFolder);
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
m = Measurement(comm);
disp([newline 'Measurement class initialized.']);

%The measurement class has two additional data logging options that can be
%set
m.dispInCommandWindow = true; %Displays status information in the command window
m.dispInPlot = true; %Plots measurement data in realtime

%A new measurement is performed with the New function of the Measurement
%class which requires a method specifying the technique and its settings
m.New(method);

while(m.inMeasurement)
    pause(0.01);
end

%Get the measurement
measurement = m.measurement;

%% 4. Plotting measurement data
%Measurements are converted to structs to improve their compatability with
%Matlab. Each measurement is stored in its own struct and contains a
%character array with its name (.name), measurement technique (.type) and
%date (.date). The measurement itself is stored in one or more curves.
%Generally a measurement has one curve struct, however, Cyclic Voltammetry
%and Impedance Spectroscopy are exceptions. Cyclic Voltammetry measurements
%have one curve per each scan and Impedance Spectroscopy measurements have
%three curves (Nyquist plot (Zre vs Zim), Bode plot (freq vs Z) and Bode
%plot (freq vs -phase)). Each curve struct contains an array of x and y
%data (xData & yData) and their respective units (xUnit & yUnit).

disp([newline 'Plotting the measurent']);
if (strcmp(measurement.type,'Cyclic Voltammetry'))%Check if Cyclic Voltammetry measurement
    %preallocate the x & y axis and the legend
    x = zeros(length(measurement.curves), length(measurement.curves(1).xData));
    y = zeros(length(measurement.curves), length(measurement.curves(1).yData));
    scans = cell(1,length(measurement.curves));
    %Get the data from all the scans in the Cyclic Voltammetry measurement
    for i = 1:length(measurement.curves)
        x(i,:) = measurement.curves(i).xData;
        y(i,:) = measurement.curves(i).yData;
        scans{i} = [measurement.name ' scan ' num2str(i)];
    end
    %Plot the data
    figure(1);
    plot(x',y'), title(measurement.type), xlabel(measurement.curves(1).xUnit), ylabel(measurement.curves(1).yUnit), legend(scans);
elseif (strcmp(measurement.type,'Impedance Spectroscopy') || strcmp(measurement.type,'Galvanostatic Impedance Spectroscopy'))%Check if Impedance Spectroscopy
    %Plot the Nyquist plot
    figure(1);
    subplot 311; plot(measurement.curves(1).xData,measurement.curves(1).yData), title('Nyquist'), xlabel(measurement.curves(1).xUnit), ylabel(measurement.curves(1).yUnit), legend(measurement.name);
    %Plot the Bode plot impedance over frequency
    figure(1);
    subplot 312; plot(measurement.curves(2).xData,measurement.curves(2).yData), title('Bode (Z over frequency)'), xlabel(measurement.curves(2).xUnit), ylabel(measurement.curves(2).yUnit), legend(measurement.name);
    %Plot the Bode plot -phase over frequency
    figure(1);
    subplot 313; plot(measurement.curves(3).xData,measurement.curves(3).yData), title('Bode (-phase over frequency)'), xlabel(measurement.curves(3).xUnit), ylabel(measurement.curves(3).yUnit), legend(measurement.name);
else %In case of other measurement
    figure(1);
    plot(measurement.curves(1).xData,measurement.curves(1).yData), title(measurement.type), xlabel(measurement.curves(1).xUnit), ylabel(measurement.curves(1).yUnit), legend(measurement.name);
end

%% Safely close the connection to the device
%Disposing the measurement class
delete(m);
clear m;

%Close the connection to the device
disp([newline 'Attempting to disconnect from ' deviceName]);
try
    comm.Disconnect();
    disp(['Succesfully closed the connection to ' deviceName]);
catch
    disp(['An error occured while trying to disconnect from ' deviceName]);
end

%Deleting the CommManager object
delete(comm); %Deleting this object removes its references to the PalmSens library and frees up resources
clear comm
disp([newline 'Comm objects resources released.'])
