%This example demonstrates how to:
%1. Import measurements from a PSTrace Session file.
%2. Plotting the data.

clear;
%% Add PalmSens Matlab SDK to workspace
PSSDK = LoadPSSDK();
if(PSSDK == false)
    disp('Error while adding the PalmSens SDK to the workspace. Please resolve before continuing.');
    return;
end

%% Get the folder to load/save session files from and to
%Check whether a folder containing Session and Method files has been specified in
%settings.mat
disp([newline 'Checking presence of settings.mat']);
if (exist('settings.mat','file') == 2)
    load('settings.mat')
    %Check whether settings contains the required field
    if(isfield(Settings.Default,'psDataFolder') == 1)
        psDataFolder = Settings.Default.psDataFolder;
    end
end

%If psDataFolder is unspecified check whether PSTrace data folder exists
%in user data
if(exist('psDataFolder','var') == 0 || (~isnumeric(psDataFolder) && isempty(psDataFolder)))
    %Get user folder
    userFolder = getenv('USERPROFILE');
    if(exist([userFolder '\My Documents\PSData'],'dir') == 7)
        psDataFolder = [userFolder '\My Documents\PSData\'];
    end
end

%Show load method dialog
disp([newline 'Please specify the location a *.pssession file']);
if(exist('psDataFolder','var') == 0)
    [sessionName,sessionFolder,filterIndex] = uigetfile('*','Please specify the location of a palmsens data file');
else
    [sessionName,sessionFolder,filterIndex] = uigetfile('*','Please specify the location of a palmsens datafile',psDataFolder);
end

%Store folder location for future reference
Settings.Default.psDataFolder = sessionFolder;
save('settings.mat','Settings','-append');
disp([sessionFolder ' set as default folder in settings.mat']);

%Full method path required for the LoadMethod function
sessionPath = fullfile(sessionFolder,sessionName);
clear methodFolder psDataFolder userFolder %clean up workspace

%% 1. Import a Session file
disp([newline 'Importing measurements from session, ' sessionPath '...']);
measurements = LoadSession(sessionPath); %load the method object from the specified path

%Check whether the method was succesfully loaded
if(isstruct(measurements) == false)
    disp('Error importing session, please check if the PalmSens SDK has been loaded,the specified file path is correct and the *.pssession file is valid');
    return;
end
%Display list of loaded measurments
disp(['Succesfully loaded ' sessionName '. Containing ' num2str(length(measurements)) ' measurement(s):' newline]);
for i = 1:length(measurements)
    disp([num2str(i) '. ' measurements(i).name ' (' measurements(i).type ') measured on ' measurements(i).date]);
end
%% 2. Plotting measurement data
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

disp([newline 'Plotting the first measurent']);
measurement = measurements(1); %Get the first measurement;
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
    subplot 312; plot(log10(measurement.curves(2).xData),log10(measurement.curves(2).yData)), title('Bode (Z over frequency)'), xlabel(['Log ' measurement.curves(2).xUnit]), ylabel(['Log ' measurement.curves(2).yUnit]), legend(measurement.name);
    %Plot the Bode plot -phase over frequency
    figure(1);
    subplot 313; plot(log10(measurement.curves(3).xData),measurement.curves(3).yData), title('Bode (-phase over frequency)'), xlabel(['Log ' measurement.curves(3).xUnit]), ylabel(measurement.curves(3).yUnit), legend(measurement.name);
else %In case of other measurement
    figure(1);
    plot(measurement.curves(1).xData,measurement.curves(1).yData), title(measurement.type), xlabel(measurement.curves(1).xUnit), ylabel(measurement.curves(1).yUnit), legend(measurement.name);
end
