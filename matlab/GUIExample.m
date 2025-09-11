function varargout = GUIExample(varargin)
% GUIEXAMPLE MATLAB code for GUIExample.fig
%      GUIEXAMPLE, by itself, creates a new GUIEXAMPLE or raises the existing
%      singleton*.
%
%      H = GUIEXAMPLE returns the handle to a new GUIEXAMPLE or the handle to
%      the existing singleton*.
%
%      GUIEXAMPLE('CALLBACK',hObject,eventData,handles,...) calls the local
%      function named CALLBACK in GUIEXAMPLE.M with the given input arguments.
%
%      GUIEXAMPLE('Property','Value',...) creates a new GUIEXAMPLE or raises the
%      existing singleton*.  Starting from the left, property value pairs are
%      applied to the GUI before GUIExample_OpeningFcn gets called.  An
%      unrecognized property name or invalid value makes property application
%      stop.  All inputs are passed to GUIExample_OpeningFcn via varargin.
%
%      *See GUI Options on GUIDE's Tools menu.  Choose "GUI allows only one
%      instance to run (singleton)".
%
% See also: GUIDE, GUIDATA, GUIHANDLES

% Edit the above text to modify the response to help GUIExample

% Last Modified by GUIDE v2.5 05-Apr-2017 17:30:35

% Begin initialization code - DO NOT EDIT
gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
                   'gui_Singleton',  gui_Singleton, ...
                   'gui_OpeningFcn', @GUIExample_OpeningFcn, ...
                   'gui_OutputFcn',  @GUIExample_OutputFcn, ...
                   'gui_LayoutFcn',  [] , ...
                   'gui_Callback',   []);
if nargin && ischar(varargin{1})
    gui_State.gui_Callback = str2func(varargin{1});
end

if nargout
    [varargout{1:nargout}] = gui_mainfcn(gui_State, varargin{:});
else
    gui_mainfcn(gui_State, varargin{:});
end
% End initialization code - DO NOT EDIT


% --- Executes just before GUIExample is made visible.
function GUIExample_OpeningFcn(hObject, eventdata, handles, varargin)
% This function has no output args, see OutputFcn.
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% varargin   command line arguments to GUIExample (see VARARGIN)

% Choose default command line output for GUIExample
handles.output = hObject;

% Create a struct for storing measurements
handles.Measurement.NET.measurements = struct('curves',{},'measurement',{});
handles.Measurement.measurements = struct('name',{},'type',{},'date',{},'curves',{});
handles.Measurement.abort = false;
guidata(hObject, handles); %Update changes before other functions are called

LoadSDK(hObject);
ScanDevices(hObject);
CreateMethod(hObject,handles.pmTechnique.Value);

%disable the run measurement button by default
set(handles.btnRun,'enable','off');
set(handles.btnSave,'enable','off');

% Refresh & update handles structure
handles = guidata(hObject);
guidata(hObject, handles);

% UIWAIT makes GUIExample wait for user response (see UIRESUME)
% uiwait(handles.figure1);

function LoadSDK(hObject)
handles = guidata(hObject); %Get handles from figure
%Check if the location of the PalmSens library can be loaded from settings.mat
Log(hObject,'Checking presence of settings.mat');
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
    Log(hObject,'Please specify the location of PalmSens.Core.Matlab.dll');
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
        Log(hObject,'Please select the PalmSens SDK library named PalmSens.Core.Matlab.dll')
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

%Load PalmSens SDK library
Settings.PSSDK = NET.addAssembly(dllPath);
Log(hObject,'PalmSens SDK dll loaded succesfully')

%Add Settings and SDK to handles
handles.Settings = Settings;

% Update handles structure
guidata(hObject, handles);

function ScanDevices(hObject)
handles = guidata(hObject); %Get handles from figure

%Get connected devices
deviceList = GetConnectedDevices(); %see function help for scanning bluetooth and serial devices
nDevices = deviceList.Count; %number of found devices
Log(hObject,[num2str(nDevices) ' device(s) connected:']);

devices = cell(nDevices);
%Display connected devices
for i=0:nDevices-1
    Log(hObject,[num2str(i+1) '. ' char(deviceList.Item(i).ToString())]);
    devices{i+1}=char(deviceList.Item(i).ToString());
end

%Disable/enable connect button depending on the presence of devices
if(nDevices == 0)
    set(handles.btnConnect,'enable','off');
    devices = 'No Devices Detected';
else
    set(handles.btnConnect,'enable','on');
end

%Update popup menu and store device information in handles
handles.pmDevices.String = devices;
handles.pmDevices.Value = 1;
handles.Settings.Devices.deviceList = deviceList;
handles.Settings.Devices.nDevices = nDevices;
guidata(hObject,handles);

function CreateMethod(hObject,technique)
method = NewMethod(technique); %Create a new method of the specified type
UpdateMethodFields(hObject,method,technique);


function UpdateMethodFields(hObject,method,technique)
%Update the gui fields with the methods settings
%Set the current range
SetCurrentRange(hObject, method);

%Set the pretreatment settings
SetPreTreatmentSettings(hObject, method);

%This example only includes method specific fields for LSV, CV and EIS
%Other panels can be added using GUIDE and the respective functions to
%update their fields can be added here.
if(technique == 1)
    UpdateLSVMethodFields(hObject,method);
elseif(technique == 2)
    UpdateCVMethodFields(hObject,method);
elseif(technique == 7)
    UpdateCAMethodFields(hObject,method);
elseif(technique == 16)
    UpdateEISMethodFields(hObject,method);
else
    UpdateOtherMethodFields(hObject,method);
end

%Store the method file in the figure
handles = guidata(hObject);
handles.Settings.Method.method = method;
guidata(hObject, handles);


function SetCurrentRange(hObject, method)
handles = guidata(hObject);
fixedCR = isa(method.Ranging,'PalmSens.AutoRanging') == false; %check if current range is fixed or auto
if(fixedCR)
    index = 8 - method.Ranging.MaximumCurrentRange.CRbyte;
    if(index > 8)
        index = 8;
    elseif (index < 1)
        index = 1;
    end
    handles.pmCRMax.Value = index;
    handles.pmCRMin.Value = index;
    handles.pmCRStart.Value = index;
else
    min = 8 - method.Ranging.MinimumCurrentRange.CRbyte;
    if(min > 8)
        min = 8;
    elseif (min < 1)
        min = 1;
    end
    max = 8 - method.Ranging.MaximumCurrentRange.CRbyte;
    if(max > 8)
        max = 8;
    elseif (max < 1)
        max = 1;
    end
    start = 8 - method.Ranging.StartCurrentRange.CRbyte;
    if(start > 8)
        start = 8;
    elseif (start < 1)
        start = 1;
    end
    handles.pmCRMax.Value = max;
    handles.pmCRMin.Value = min;
    handles.pmCRStart.Value = start;
end


function SetPreTreatmentSettings(hObject, method)
handles = guidata(hObject);
handles.tbECondition.String = num2str(method.ConditioningPotential);
handles.tbtCondition.String = num2str(method.ConditioningTime);
handles.tbEDeposition.String = num2str(method.DepositionPotential);
handles.tbtDeposition.String = num2str(method.DepositionTime);
guidata(hObject,handles);


function UpdateLSVMethodFields(hObject,method)
handles = guidata(hObject);

%Hide the other techniques settings panels and show the LSV settings panel
set(handles.pCA, 'visible', 'off');
set(handles.pCV, 'visible', 'off');
set(handles.pEIS, 'visible', 'off');
set(handles.pLSV, 'visible', 'on');
set(handles.pOther, 'visible', 'off');

%Set the LSV specific settings
handles.tbtEquilibrationLSV.String = num2str(method.EquilibrationTime);
handles.tbEBeginLSV.String = num2str(method.BeginPotential);
handles.tbEEndLSV.String = num2str(method.EndPotential);
handles.tbEStepLSV.String = num2str(method.StepPotential);
handles.tbScanRateLSV.String = num2str(method.Scanrate);

%Update the figures text fields
guidata(hObject, handles);


function UpdateCVMethodFields(hObject,method)
handles = guidata(hObject);

%Hide the other techniques settings panels and show the CV settings panel
set(handles.pCA, 'visible', 'off');
set(handles.pCV, 'visible', 'on');
set(handles.pEIS, 'visible', 'off');
set(handles.pLSV, 'visible', 'off');
set(handles.pOther, 'visible', 'off');

%Set the CV specific settings
handles.tbtEquilibrationCV.String = num2str(method.EquilibrationTime);
handles.tbEBeginCV.String = num2str(method.BeginPotential);
handles.tbEVertex1CV.String = num2str(method.Vtx1Potential);
handles.tbEVertex2CV.String = num2str(method.Vtx2Potential);
handles.tbEStepCV.String = num2str(method.StepPotential);
handles.tbScanRateCV.String = num2str(method.Scanrate);
handles.tbNScansCV.String = num2str(method.nScans);

%Update the figures text fields
guidata(hObject, handles);

function UpdateCAMethodFields(hObject,method)
handles = guidata(hObject);

%Hide the other techniques settings panels and show the CV settings panel
set(handles.pCA, 'visible', 'on');
set(handles.pCV, 'visible', 'off');
set(handles.pEIS, 'visible', 'off');
set(handles.pLSV, 'visible', 'off');
set(handles.pOther, 'visible', 'off');

%Set the CV specific settings
handles.tbtEquilibrationCA.String = num2str(method.EquilibrationTime);
handles.tbEDCCA.String = num2str(method.BeginPotential);
handles.tbtIntervalCA.String = num2str(method.IntervalTime);
handles.tbtRunCA.String = num2str(method.RunTime);

%Update the figures text fields
guidata(hObject, handles);


function UpdateEISMethodFields(hObject,method)
handles = guidata(hObject);

%Hide the other techniques settings panels and show the EIS settings panel
set(handles.pCA, 'visible', 'off');
set(handles.pCV, 'visible', 'off');
set(handles.pEIS, 'visible', 'on');
set(handles.pLSV, 'visible', 'off');
set(handles.pOther, 'visible', 'off');

%Set the EIS specific settings
handles.tbtEquilibrationEIS.String = num2str(method.EquilibrationTime);
handles.tbEDCEIS.String = num2str(method.Potential);
handles.tbEACEIS.String = num2str(method.Eac);
handles.tbnFrequenciesEIS.String = num2str(method.nFrequencies);
handles.tbMinFrequencyEIS.String = num2str(method.MinFrequency);
handles.tbMaxFrequencyEIS.String = num2str(method.MaxFrequency);

%Set the methods scantype to fixed potential en frequency scan
method.ScanType = PalmSens.Techniques.enumScanType.FixedPotential;
method.FreqType = PalmSens.Techniques.enumFrequencyType.Fixed;
method.FixedFrequency = 40000;
method.RunTime = 0;

%Update the figures text fields
guidata(hObject, handles);


function UpdateOtherMethodFields(hObject,method)
handles = guidata(hObject);

%Hide the other techniques settings panels and show the CV settings panel
set(handles.pCA, 'visible', 'off');
set(handles.pCV, 'visible', 'off');
set(handles.pEIS, 'visible', 'off');
set(handles.pLSV, 'visible', 'off');
set(handles.pOther, 'visible', 'on');

%Update the figures text fields
guidata(hObject, handles);


function Log(hObject,message)
% Add message to the log listbox
handles = guidata(hObject); %Get handles
log = handles.lbLog.String; %Retreive log contents
if(iscellstr(log) == 0) %Check if log is empty
    log = cell(0); %Convert log to cell array
end
log{end+1} = message; %Add message to log
handles.lbLog.String = log;
handles.lbLog.Value = length(log);
guidata(hObject,handles); %Update figure


% --- Outputs from this function are returned to the command line.
function varargout = GUIExample_OutputFcn(hObject, eventdata, handles)
% varargout  cell array for returning output args (see VARARGOUT);
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Get default command line output from handles structure
varargout{1} = handles.output;


% --- Executes on button press in btnClose.
function btnClose_Callback(hObject, eventdata, handles)
% hObject    handle to btnClose (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
close(handles.figure1)

% --- Executes on selection change in lbLog.
function lbLog_Callback(hObject, eventdata, handles)
% hObject    handle to lbLog (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = cellstr(get(hObject,'String')) returns lbLog contents as cell array
%        contents{get(hObject,'Value')} returns selected item from lbLog


% --- Executes during object creation, after setting all properties.
function lbLog_CreateFcn(hObject, eventdata, handles)
% hObject    handle to lbLog (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: listbox controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in btnSave.
function btnSave_Callback(hObject, eventdata, handles)
% hObject    handle to btnSave (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
%Show save data dialog
[name,folder] = uiputfile('*.mat','Please specify where you would like to save the measurement');

if(isempty(name))
    Log(hObject,'Saving cancelled, no path or file name specified.');
end
fullPath = fullfile(folder,name);

%Get the selected measurement
measurement = handles.Measurement.measurements(handles.pmMeasurement1.Value-1);

save(fullPath,'measurement');

Log(hObject,['Successfully saved the measurement to ' fullPath]);


% --- Executes on button press in btnImport.
function btnImport_Callback(hObject, eventdata, handles)
% hObject    handle to btnImport (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
Settings = handles.Settings;
if(isfield(Settings.Default,'psDataFolder') == 1)
    psDataFolder = Settings.Default.psDataFolder;
    %Check whether psDataFolder is a folder
    if(exist(char(Settings.Default.psDataFolder),'dir') ~= 7)
        clear psDataFolder;
    end
end

%If psDataFolder is unspecified check whether PSTrace method folder exists
%in user data
if(exist('psDataFolder','var') == 0)
    %Get user folder
    userFolder = getenv('USERPROFILE');
    if(exist([userFolder '\My Documents\PSData'],'dir') == 7)
        psDataFolder = [userFolder '\My Documents\PSData\'];
    end
end

%Show load method dialog
if(exist('psDataFolder','var') == 0)
    [name,folder] = uigetfile('*.pssession','Please specify the location of a *.pssession file');
else
    [name,folder] = uigetfile('*.pssession','Please specify the location of a *.pssession file',psDataFolder);
end

%Store folder location of method for future reference
Settings.Default.psDataFolder = folder;
SettingsLocal = Settings;
Settings = cell(0);
Settings.Default = SettingsLocal.Default;
save('settings.mat','Settings','-append');
Log(hObject,[folder ' set as the default data folder in settings.mat']);

%Full method path required for the LoadMethod function
path = fullfile(folder,name);

Log(hObject,['Loading session from ' path '...']);
session = LoadSession(path); %load the method object from the specified path

%Check whether the session was succesfully loaded
if(isstruct(session) == false)
    Log(hObject,'Error loading session, please check if the PalmSens SDK has been loaded, the specified file path is correct and the *.pssession file is valid');
    return;
end
Log(hObject,['Succesfully loaded ' num2str(length(session)) ' measurement(s) from ' name '.']);

%Store measurements in figure handle
for i = 1:length(session)
    handles.Measurement.measurements(end+1) = session(i);
end
guidata(hObject,handles);

%Add measurements to overview
for i = 1:length(session)
    AddToOverview(hObject,session(i));
end


% --- Executes on selection change in pmMeasurement1.
function pmMeasurement1_Callback(hObject, eventdata, handles)
% hObject    handle to pmMeasurement1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = cellstr(get(hObject,'String')) returns pmMeasurement1 contents as cell array
%        contents{get(hObject,'Value')} returns selected item from pmMeasurement1
UpdatePlots(hObject);
if(handles.pmMeasurement1.Value > 1)
    set(handles.btnSave,'enable','on');
else
    set(handles.btnSave,'enable','off');
end


function UpdatePlots(hObject)
handles = guidata(hObject);
if(handles.pmMeasurement1.Value == 1 && handles.pmMeasurement2.Value == 1) %no measurements are selected, thus clear the plot.
    axes(handles.plotArea);
    cla;
elseif (handles.pmMeasurement1.Value > 1 && handles.pmMeasurement2.Value == 1) %plot a single measurement
    plotData(hObject,handles.Measurement.measurements(handles.pmMeasurement1.Value - 1));
elseif (handles.pmMeasurement1.Value == 1 && handles.pmMeasurement2.Value > 1) %plot a single measurement
    plotData(hObject,handles.Measurement.measurements(handles.pmMeasurement2.Value - 1));
elseif (handles.pmMeasurement1.Value > 1 && handles.pmMeasurement2.Value > 1) %plot two measurements
    plotDataOverlay(hObject,handles.Measurement.measurements(handles.pmMeasurement1.Value - 1),handles.Measurement.measurements(handles.pmMeasurement2.Value - 1));
end


% --- Executes during object creation, after setting all properties.
function pmMeasurement1_CreateFcn(hObject, eventdata, handles)
% hObject    handle to pmMeasurement1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on selection change in pmMeasurement2.
function pmMeasurement2_Callback(hObject, eventdata, handles)
% hObject    handle to pmMeasurement2 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = cellstr(get(hObject,'String')) returns pmMeasurement2 contents as cell array
%        contents{get(hObject,'Value')} returns selected item from pmMeasurement2
UpdatePlots(hObject);


% --- Executes during object creation, after setting all properties.
function pmMeasurement2_CreateFcn(hObject, eventdata, handles)
% hObject    handle to pmMeasurement2 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in cbAxisEqual.
function cbAxisEqual_Callback(hObject, eventdata, handles)
% hObject    handle to cbAxisEqual (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of cbAxisEqual
UpdatePlots(hObject);

% --- Executes on button press in btnSaveM.
function btnSaveM_Callback(hObject, eventdata, handles)
% hObject    handle to btnSaveM (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
[valid, method] = UpdateMethod(hObject);
if(valid == false)
    Log(hObject,'Error! Could not save the method. Please make sure the methods settings are correct.');
    return;
end

%Store the method in the figures memory
handles.Settings.Method.method = method;

%Check whether settings contain default data folder
Settings = handles.Settings;
if(isfield(Settings.Default,'psDataFolder') == 1)
    psDataFolder = Settings.Default.psDataFolder;
    %Check whether psDataFolder is a folder
    if(exist(char(Settings.Default.psDataFolder),'dir') ~= 7)
        clear psDataFolder;
    end
end

%If psDataFolder is unspecified check whether PSTrace method folder exists
%in user data
if(exist('psDataFolder','var') == 0)
    %Get user folder
    userFolder = getenv('USERPROFILE');
    if(exist([userFolder '\My Documents\PSData'],'dir') == 7)
        psDataFolder = [userFolder '\My Documents\PSData\'];
    end
end

%Show load method dialog
if(exist('psDataFolder','var') == 0)
    [methodName,methodFolder] = uiputfile('*.psmethod','Please specify where you would like to save the method');
else
    [methodName,methodFolder] = uiputfile('*.psmethod','Please specify where you would like to save the method',psDataFolder);
end

%Saving the method
Log(hObject,'Saving the method...');
fullPath = fullfile(methodFolder,methodName);
saved = SaveMethod(method, fullPath, handles.Settings.PSSDK);
if(saved == true)
    Log(hObject,['Successfully saved the method to ' fullPath]);
else
    Log(hObject,'An error occured while saving the method');
end


function [valid, method] = UpdateMethod(hObject)
valid = true;
handles = guidata(hObject);
method = handles.Settings.Method.method;
technique = GetMethodTechnique(method);

%Attempt to update the methods current range with the specified values
method = UpdateMethodCurrentRange(hObject,method);
if(method == false)
    valid = false;
    return;
end

%Attempt to update the methods pretreatment settings with the specified values
method = UpdateMethodPretreatment(hObject,method);
if(method == false)
    valid = false;
    return;
end

if(technique == 1)
    method = UpdateMethodLSV(hObject,method);
    if(method == false)
        valid = false;
        return;
    end
elseif (technique == 2)
    method = UpdateMethodCV(hObject,method);
    if(method == false)
        valid = false;
        return;
    end
elseif (technique == 7)
    method = UpdateMethodCA(hObject,method);
    if(method == false)
        valid = false;
        return;
    end
elseif (technique == 16)
    method = UpdateMethodEIS(hObject,method);
    if(method == false)
        valid = false;
        return;
    end
end


function method = UpdateMethodCurrentRange(hObject,method)
handles = guidata(hObject);
if (handles.pmCRMin.Value == handles.pmCRMax.Value)
    uA = 10^(5 - handles.pmCRMax.Value);
    fixedCurrentRange = PalmSens.CurrentRange.FromMicroamps(uA); %Convert MicroAmps into current range objects
    newRangingObj = PalmSens.FixedCurrentRange(); %Create a new fixed current range object
    newRangingObj.MaximumCurrentRange = fixedCurrentRange; %Set the fixed current range of the new object
    %Setting the fixed current range object in the method;
    method.Ranging = newRangingObj;
else
    uAMin = 10^(5 - handles.pmCRMin.Value);
    uAMax = 10^(5 - handles.pmCRMax.Value);
    uAStart = 10^(5 - handles.pmCRStart.Value);
    minCurrentRange = PalmSens.CurrentRange.FromMicroamps(uAMin);
    maxCurrentRange = PalmSens.CurrentRange.FromMicroamps(uAMax);
    startCurrentRange = PalmSens.CurrentRange.FromMicroamps(uAStart);
    %Create a new Current AutoRanging object
    newRangingObj = PalmSens.AutoRanging(minCurrentRange, maxCurrentRange, startCurrentRange);
    %Setting the fixed current range object in the method;
    method.Ranging = newRangingObj;
end


function method = UpdateMethodPretreatment(hObject,method)
handles = guidata(hObject);

%Attempt to assign the specified pretreatment settings to the method
fail = false;
try
    method.ConditioningPotential = str2double(handles.tbECondition.String);
    fail = fail || isnan(method.ConditioningPotential);
    method.ConditioningTime = str2double(handles.tbtCondition.String);
    fail = fail || isnan(method.ConditioningTime);
    method.DepositionPotential = str2double(handles.tbEDeposition.String);
    fail = fail || isnan(method.DepositionPotential);
    method.DepositionTime = str2double(handles.tbtDeposition.String);
    fail = fail || isnan(method.DepositionTime);
catch
    method = false; %Return false if error occured when setting the methods pretreatment settings
end

if(fail)
    method = false;
end


function method = UpdateMethodLSV(hObject,method)
handles = guidata(hObject);

%Attempt to assign the specified pretreatment settings to the method
fail = false;
try
    method.EquilibrationTime = str2double(handles.tbtEquilibrationLSV.String);
    fail = fail || isnan(method.EquilibrationTime);
    method.BeginPotential = str2double(handles.tbEBeginLSV.String);
    fail = fail || isnan(method.BeginPotential);
    method.EndPotential = str2double(handles.tbEEndLSV.String);
    fail = fail || isnan(method.EndPotential);
    method.StepPotential = str2double(handles.tbEStepLSV.String);
    fail = fail || isnan(method.StepPotential);
    method.Scanrate = str2double(handles.tbScanRateLSV.String);
    fail = fail || isnan(method.Scanrate);
catch
    method = false; %Return false if error occured when setting the methods pretreatment settings
end

if(fail)
    method = false;
end


function method = UpdateMethodCV(hObject,method)
handles = guidata(hObject);

%Attempt to assign the specified pretreatment settings to the method
fail = false;
try
    method.EquilibrationTime = str2double(handles.tbtEquilibrationCV.String);
    fail = fail || isnan(method.EquilibrationTime);
    method.BeginPotential = str2double(handles.tbEBeginCV.String);
    fail = fail || isnan(method.BeginPotential);
    method.Vtx1Potential = str2double(handles.tbEVertex1CV.String);
    fail = fail || isnan(method.Vtx1Potential);
    method.Vtx2Potential = str2double(handles.tbEVertex2CV.String);
    fail = fail || isnan(method.Vtx2Potential);
    method.StepPotential = str2double(handles.tbEStepCV.String);
    fail = fail || isnan(method.StepPotential);
    method.Scanrate = str2double(handles.tbScanRateCV.String);
    fail = fail || isnan(method.Scanrate);
    method.nScans = str2double(handles.tbNScansCV.String);
    fail = fail || isnan(method.nScans);
catch
    method = false; %Return false if error occured when setting the methods pretreatment settings
end

if(fail)
    method = false;
end

function method = UpdateMethodCA(hObject,method)
handles = guidata(hObject);

%Attempt to assign the specified pretreatment settings to the method
fail = false;
try
    method.EquilibrationTime = str2double(handles.tbtEquilibrationCA.String);
    fail = fail || isnan(method.EquilibrationTime);
    method.BeginPotential = str2double(handles.tbEDCCA.String);
    fail = fail || isnan(method.BeginPotential);
    method.IntervalTime = str2double(handles.tbtIntervalCA.String);
    fail = fail || isnan(method.IntervalTime);
    method.RunTime = str2double(handles.tbtRunCA.String);
    fail = fail || isnan(method.RunTime);
catch
    method = false; %Return false if error occured when setting the methods pretreatment settings
end

if(fail)
    method = false;
end


function method = UpdateMethodEIS(hObject,method)
handles = guidata(hObject);

%Attempt to assign the specified pretreatment settings to the method
fail = false;
try
    method.EquilibrationTime = str2double(handles.tbtEquilibrationEIS.String);
    fail = fail || isnan(method.EquilibrationTime);
    method.Potential = str2double(handles.tbEDCEIS.String);
    fail = fail || isnan(method.Potential);
    method.Eac = str2double(handles.tbEACEIS.String);
    fail = fail || isnan(method.Eac);
    method.nFrequencies = str2double(handles.tbnFrequenciesEIS.String);
    fail = fail || isnan(method.nFrequencies);
    method.MinFrequency = str2double(handles.tbMinFrequencyEIS.String);
    fail = fail || isnan(method.MinFrequency);
    method.MaxFrequency = str2double(handles.tbMaxFrequencyEIS.String);
    fail = fail || isnan(method.MaxFrequency);
catch
    method = false; %Return false if error occured when setting the methods pretreatment settings
end

if(fail)
    method = false;
end


% --- Executes on button press in btnLoadM.
function btnLoadM_Callback(hObject, eventdata, handles)
% hObject    handle to btnLoadM (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
Settings = handles.Settings;
if(isfield(Settings.Default,'psDataFolder') == 1)
    psDataFolder = Settings.Default.psDataFolder;
    %Check whether psDataFolder is a folder
    if(exist(char(Settings.Default.psDataFolder),'dir') ~= 7)
        clear psDataFolder;
    end
end

%If psDataFolder is unspecified check whether PSTrace method folder exists
%in user data
if(exist('psDataFolder','var') == 0)
    %Get user folder
    userFolder = getenv('USERPROFILE');
    if(exist([userFolder '\My Documents\PSData'],'dir') == 7)
        psDataFolder = [userFolder '\My Documents\PSData\'];
    end
end

%Show load method dialog
if(exist('psDataFolder','var') == 0)
    [methodName,methodFolder] = uigetfile('*.psmethod','Please specify the location of a *.psmethod file');
else
    [methodName,methodFolder] = uigetfile('*.psmethod','Please specify the location of a *.psmethod file',psDataFolder);
end

%Store folder location of method for future reference
Settings.Default.psDataFolder = methodFolder;
SettingsLocal = Settings;
Settings = cell(0);
Settings.Default = SettingsLocal.Default;
save('settings.mat','Settings','-append');
Log(hObject,[methodFolder ' set as the default data folder in settings.mat']);

%Full method path required for the LoadMethod function
methodPath = fullfile(methodFolder,methodName);

Log(hObject,['Loading method from ' methodPath '...']);
method = LoadMethod(methodPath); %load the method object from the specified path

%Check whether the method was succesfully loaded
if(method == false)
    Log(hObject,'Error loading method, please check if the PalmSens SDK has been loaded,the specified file path is correct and the *.psmethod file is valid');
    return;
end
Log(hObject,['Succesfully loaded the [ ' char(method.Name) ' ] method ' methodName '.']);

%Update the figure setting fields with the setting from the loaded method
handles = guidata(hObject);
technique = GetMethodTechnique(method);
handles.pmTechnique.Value = technique;
UpdateMethodFields(hObject,method,technique);

%Store method and update figure
handles.Settings.Method.method = method;
guidata(hObject,handles);


function technique = GetMethodTechnique(method)
if (strcmp(char(method.Name),'Linear Sweep Voltammetry'))
    technique = 1;
    return
elseif (strcmp(char(method.Name),'Cyclic Voltammetry'))
    technique = 2;
    return
elseif (strcmp(char(method.Name),'AC Voltammetry'))
    technique = 3;
    return
elseif (strcmp(char(method.Name),'Differential Pulse Voltammetry'))
    technique = 4;
    return
elseif (strcmp(char(method.Name),'Square Wave Voltammetry'))
    technique = 5;
    return
elseif (strcmp(char(method.Name),'Normal Pulse Voltammetry'))
    technique = 6;
    return
elseif (strcmp(char(method.Name),'Chronoamperometry'))
    technique = 7;
    return
elseif (strcmp(char(method.Name),'MultiStep Amperometry'))
    technique = 8;
    return
elseif (strcmp(char(method.Name),'Fast Amperometry'))
    technique = 9;
    return
elseif (strcmp(char(method.Name),'Pulsed Amperometric Detection'))
    technique = 10;
    return
elseif (strcmp(char(method.Name),'Multiple Pulse Amperometry'))
    technique = 11;
    return
elseif (strcmp(char(method.Name),'Open Circuit Potentiometry'))
    technique = 12;
    return
elseif (strcmp(char(method.Name),'Chronopotentiometry'))
    technique = 13;
    return
elseif (strcmp(char(method.Name),'MultiStep Potentiometry'))
    technique = 14;
    return
elseif (strcmp(char(method.Name),'Chronopotentiometric Stripping'))
    technique = 15;
    return
elseif (strcmp(char(method.Name),'Impedance Spectroscopy'))
    technique = 16;
    return
elseif (strcmp(char(method.Name),'Fast Cyclic Voltammetry'))
    technique = 17;
    return
end


% --- Executes on selection change in pmTechnique.
function pmTechnique_Callback(hObject, eventdata, handles)
% hObject    handle to pmTechnique (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = cellstr(get(hObject,'String')) returns pmTechnique contents as cell array
%        contents{get(hObject,'Value')} returns selected item from pmTechnique
%Check if a technique has been loaded in memory
CreateMethod(hObject,handles.pmTechnique.Value);


% --- Executes during object creation, after setting all properties.
function pmTechnique_CreateFcn(hObject, eventdata, handles)
% hObject    handle to pmTechnique (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in btnRun.
function btnRun_Callback(hObject, eventdata, handles)
% hObject    handle to btnRun (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
handles = guidata(hObject);
if(strcmp(handles.btnRun.String,'Run')) %Run or abort measurement
    handles.Measurement.abort = false;
    [valid, method] = UpdateMethod(hObject);
    if(valid == false)
        Log(hObject,'Error! Could not run the method. Please make sure the methods settings are correct.');
        return;
    end
    handles.Measurement.NET.measurements(end+1).curves = NET.createGeneric('System.Collections.Generic.List',{'PalmSens.Plottables.Curve'},50);
    handles.btnRun.String = 'Abort';
    guidata(hObject,handles);
    measurement = handles.Measurement.measurement;
    measurement.New(method);
else
    measurement = handles.Measurement.measurement;
    handles.Measurement.abort = true;
    measurement.Abort();
    Log(hObject,'Aborting Measurement...');
    if(length(handles.Measurement.NET.measurements) == 1)
        handles.Measurement.measurements = struct('name',{},'type',{},'date',{},'curves',{});
    else
        handles.Measurement.NET.measurements = handles.Measurement.NET.measurements(1:end-1);
    end
    handles.btnRun.String = 'Run';
    guidata(hObject,handles);
end


% --- Executes on selection change in pmDevices.
function pmDevices_Callback(hObject, eventdata, handles)
% hObject    handle to pmDevices (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = cellstr(get(hObject,'String')) returns pmDevices contents as cell array
%        contents{get(hObject,'Value')} returns selected item from pmDevices


% --- Executes during object creation, after setting all properties.
function pmDevices_CreateFcn(hObject, eventdata, handles)
% hObject    handle to pmDevices (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in btnConnect.
function btnConnect_Callback(hObject, eventdata, handles)
% hObject    handle to btnConnect (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
if(strcmp(handles.btnConnect.String,'Connect'))
    if(handles.Settings.Devices.nDevices < 1)
        errordlg('No devices connected. Please make sure your device is connected, or remove the usb and plug it back in, and click on the refresh button.','Failed to connect.');
        Log(hObject,'No devices connected. Please make sure your device is connected, or remove the usb and plug it back in, and click on the refresh button.');
        return;
    end

    deviceList = handles.Settings.Devices.deviceList; %Retreive the list of connected devices

    index = handles.pmDevices.Value - 1; %Get index of selected device
    deviceName = char(deviceList.Item(index).ToString());
    Log(hObject,['Attempting to open a connection with ' deviceName]);

    %Attempt to open a connection with the selected device
    comm = OpenConnection(deviceList.Item(index));
    if(comm == false) %Check whether the connection was succesfully opened
        errordlg(['Error while opening a connection to ' deviceName '. Please check whether the specified device is a PalmSens device and try to open the connection again'],'Failed to connect.');
        Log(hObject,['Error while opening a connection to ' deviceName '. Please check whether the specified device is a PalmSens device and try to open the connection again']);
        return;
    end
    Log(hObject,['Succesfully connected to ' deviceName]);

    %Instantiate measurement class with event listners used to record data
    %from the device
    handles.Measurement.measurement = MeasurementGUI(hObject,comm,@beginListener,@endListener,@curveListener,@idleListener);

    %Enable the run measurement button
    set(handles.btnRun,'enable','on');

    %Change Connect and Refresh buttons to Disconnect and Test
    handles.btnRefresh.String = 'Test';
    handles.btnConnect.String = 'Disconnect';

    %Store the devices communication objecthandle in the GUIs handles
    handles.Settings.Devices.comm = comm;
    guidata(hObject,handles);
else
    handles.Settings.Devices.comm.Disconnect();
    delete(handles.Settings.Devices.comm);
    Log(hObject,'Device disconnected.');

    %Change Disconnect and Test buttons to Connect and Refresh
    set(handles.btnRefresh,'enable','on'); %Reenable if disconnected during testing
    handles.btnRefresh.String = 'Refresh';
    handles.btnConnect.String = 'Connect';

    %Delete measurement class to remove the even listners and prevent samples from being recorded multiple times
    if(isfield(handles,'Measurement'))
        if(isfield(handles.Measurement,'measurement') ~= 0)
            delete(handles.Measurement.measurement);
        end
    end

    %Disable the run measurement button
    set(handles.btnRun,'enable','off');

    %Update the figures handles
    guidata(hObject,handles);
end


% --- Executes on button press in btnRefresh.
function btnRefresh_Callback(hObject, eventdata, handles)
% hObject    handle to btnRefresh (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
if(strcmp(handles.btnRefresh.String,'Refresh')) %Refresh or test Connection
    ScanDevices(hObject);
else
    %Testing connection by listning to idle packages for 5 seconds
    set(handles.btnRefresh,'enable','off'); %Disable test button during testing
    Log(hObject,'Checking for idle status packets (for 5 seconds).');
    measurement = handles.Measurement.measurement; %Instantiate object for measurement.
    measurement.GetIdleData; %Start recording idle data.
    pause(5)%
    measurement.StopIdleData; %Stop recording idle data.
    set(handles.btnRefresh,'enable','on'); %Reenable test button after test performed
end


function beginListener(sender,eventArgs,hObject)
handles = guidata(hObject);
measurement = eventArgs;
handles.Measurement.NET.measurements(end).measurement = measurement; %Store curve in figure handle
handles.Measurement.measurement.StartDataListener(hObject,@dataListener)
guidata(hObject,handles);
Log(hObject,'Measurement Started');


function endListener(sender,eventArgs,hObject)
handles = guidata(hObject);
if(handles.Measurement.abort == false)
    Log(hObject,'Measurement Completed');
    handles.btnRun.String = 'Run';
    handles.Measurement.measurement.StopDataListener();
    guidata(hObject,handles);
    m = processMeasurement(hObject,handles.Measurement.NET.measurements(end)); %Process data when measurement is completed
    handles = guidata(hObject); %Update the figure handle to retreive the processed measurement.
    plotData(hObject,m);
    guidata(hObject,handles);
else
    Log(hObject,'Measurement Aborted');
end


function curveListener(sender,eventArgs,hObject)
handles = guidata(hObject);
if(handles.Measurement.abort == false)
    curve = eventArgs.GetCurve();
    handles.Measurement.NET.measurements(end).curves.Add(curve); %Store curve in figure handle
    guidata(hObject,handles);
    Log(hObject,'Curve Received');
end


function idleListener(sender,eventArgs,hObject)
status = eventArgs.GetStatus();
current = status.CurrentReading.ValueInRange;
unitCurrent = char(status.CurrentReading.CurrentRange.ToString());
potential = status.PotentialReading.Value;
Log(hObject,['Idle Status: Potential (' num2str(potential) ' V) Current (' num2str(current) ' * ' unitCurrent ')']);


function dataListener(sender,eventArgs,hObject)
Log(hObject,['data packet(s) ' num2str(eventArgs.StartIndex + 1) ' to ' num2str(eventArgs.Count + eventArgs.StartIndex) '  received']);
handles = guidata(hObject);
if (strcmp(char(handles.Measurement.NET.measurements(end).measurement.Method.Name),'Impedance Spectroscopy'))
    plotEISDataRealtime(hObject)
else
    plotDataRealtime(hObject)
end

function measurement = processMeasurement(hObject,rawData)
handles = guidata(hObject);

%Convert .NET measurement to matlab structs
if(strcmp(char(rawData.measurement.Method.Name),'Impedance Spectroscopy')) %Impedance Spectroscopy data is handled differently
    measurement = processEISMeasurement(hObject, rawData);
else
    measurement = struct('name',{},'type',{},'date',{},'curves',{});
    measurement(1).name = [num2str(length(handles.Measurement.measurements) + 1) '.' char(rawData.measurement.Method.ShortName)];
    measurement(1).date = datestr(now);
    measurement(1).type = char(rawData.measurement.Method.Name);
    measurement(1).curves = struct('xUnit',{},'xData',{},'yUnit',{},'yData',{});
    for i=1:rawData.curves.Count %Loop added for CV, in the case of a CV with multiple scans each scan is stored as a seperate curve
        measurement(1).curves(i).xUnit = char(rawData.curves.Item(i - 1).XUnit.ToString());
        measurement(1).curves(i).xData = double(rawData.curves.Item(i - 1).GetXValues());
        measurement(1).curves(i).yUnit = char(rawData.curves.Item(i - 1).YUnit.ToString());
        measurement(1).curves(i).yData = double(rawData.curves.Item(i - 1).GetYValues());
    end
end

handles.Measurement.measurements(end+1) = measurement;
guidata(hObject,handles);

%Add curves to measurement overview
AddToOverview(hObject,measurement);


function measurement = processEISMeasurement(hObject, rawData)
handles = guidata(hObject);
measurement = struct('name',{},'type',{},'date',{},'curves',{});
measurement(1).name = [num2str(length(handles.Measurement.measurements) + 1) '.' char(rawData.measurement.Method.ShortName)];
measurement(1).date = datestr(now);
measurement(1).type = char(rawData.measurement.Method.Name);

%Get impedance data arrays
dataArrays = rawData.measurement.DataSet.GetDataArrays();
ZRe = dataArrays(5);
ZIm = dataArrays(6);
Zabs = dataArrays(7);
Phase = dataArrays(8);
Frequency = dataArrays(4);

%Nyquist curve
measurement(1).curves(1).xUnit = ['ZRe(' char(ZRe.Unit.ToString()) ')'];
measurement(1).curves(1).xData = double(ZRe.GetValues());
measurement(1).curves(1).yUnit = ['ZIm(' char(ZIm.Unit.ToString()) ')'];
measurement(1).curves(1).yData = double(ZIm.GetValues());

%Bode curves
%Impedance over Frequency
measurement(1).curves(2).xUnit = ['Frequency(' char(Frequency.Unit.ToString()) ')'];
measurement(1).curves(2).xData = double(Frequency.GetValues());
measurement(1).curves(2).yUnit = ['Z(' char(Zabs.Unit.ToString()) ')'];
measurement(1).curves(2).yData = double(Zabs.GetValues());

%-Phase over Frequency
measurement(1).curves(3).xUnit = ['Frequency(' char(Frequency.Unit.ToString()) ')'];
measurement(1).curves(3).xData = double(Frequency.GetValues());
measurement(1).curves(3).yUnit = ['-Phase(' char(Phase.Unit.ToString()) ')'];
measurement(1).curves(3).yData = -1 .* double(Phase.GetValues());

function AddToOverview(hObject,measurement)
handles = guidata(hObject);

%Check whether the menu contains a char array or a cell of strings, if
%necessary create the cell for the list of measurements
if(iscell(handles.pmMeasurement1.String) == 0)
    list = cell(1);
    list{1} = 'none';
else
    list = handles.pmMeasurement1.String;
end

%Update the list of measurements
list{end + 1} = measurement.name;
handles.pmMeasurement1.String = list;
handles.pmMeasurement2.String = list;
handles.pmMeasurement1.Value = length(list);
set(handles.btnSave,'enable','on');
handles.pmMeasurement2.Value = 1;

guidata(hObject,handles); %Update the figure


function plotData(hObject,measurement)
handles = guidata(hObject);
curve = measurement.curves(1);
handles.Settings.Plot.measurement = measurement;
handles.Settings.Plot.axesEqual = handles.cbAxisEqual.Value;

axes(handles.plotArea); %Set the handles of the axes to plot the data in
%Important! Because this function is triggered by an event axes will not work by
%default. So when creating a new GUI in GUIDE with an axes make sure to
%goto the Tools Menu and Select GUI Options, here commandline accessbility
%must be set to on.
if(strcmp(measurement.type,'Cyclic Voltammetry')) %in the case of a CV plot the curve of each scan
    xData = zeros(length(measurement.curves), length(measurement.curves(1).xData));
    yData = zeros(length(measurement.curves), length(measurement.curves(1).yData));
    scans = cell(1,length(measurement.curves));
    for i = 1:length(measurement.curves)
        xData(i,:) = measurement.curves(i).xData;
        yData(i,:) = measurement.curves(i).yData;
        scans{i} = [measurement.name ' scan ' num2str(i)];
    end
    plot(xData',yData'), title(measurement.type), xlabel(curve.xUnit), ylabel(curve.yUnit), legend(scans);
else
    plot(curve.xData,curve.yData), title(measurement.type), xlabel(curve.xUnit), ylabel(curve.yUnit), legend(measurement.name);
end
if(handles.Settings.Plot.axesEqual == 1)
    axis equal
else
    axis auto
end
guidata(hObject,handles);


function plotDataOverlay(hObject,measurement1,measurement2)
handles = guidata(hObject);
curve1 = measurement1.curves(1);
curve2 = measurement2.curves(1);
% names = cell(1, length(measurement1.curves) + length(measurement2.curves));
ni = 1; %set start index for the array of curve names used in the legend
if(strcmp(measurement1.type,'Cyclic Voltammetry')) %in the case of a CV get the curves of all scans
    x1 = zeros(length(measurement1.curves), length(measurement1.curves(1).xData));
    y1 = zeros(length(measurement1.curves), length(measurement1.curves(1).yData));
    for i = 1:length(measurement1.curves)
        x1(i,:) = measurement1.curves(i).xData;
        y1(i,:) = measurement1.curves(i).yData;
        names{ni} = [measurement1.name ' scan ' num2str(i)];
        ni = ni + 1;
    end
    x1=x1';
    y1=y1';
else
    x1 = curve1.xData;
    y1 = curve1.yData;
    names{ni} = measurement1.name;
    ni = ni + 1;
end

if(strcmp(measurement2.type,'Cyclic Voltammetry')) %in the case of a CV get the curves of all scans
    x2 = zeros(length(measurement2.curves), length(measurement2.curves(1).xData));
    y2 = zeros(length(measurement2.curves), length(measurement2.curves(1).yData));
    for i = 1:length(measurement2.curves)
        x2(i,:) = measurement2.curves(i).xData;
        y2(i,:) = measurement2.curves(i).yData;
        names{ni} = [measurement2.name ' scan ' num2str(i)];
        ni = ni + 1;
    end
    x2=x2';
    y2=y2';
else
    x2 = curve2.xData;
    y2 = curve2.yData;
    names{ni} = measurement2.name;
end

if(strcmp(curve1.xUnit,curve2.xUnit) == 0 || strcmp(curve1.yUnit,curve2.yUnit) == 0)
    Log(hObject,'Cannot plot measurements with different units on the axes');
    return;
end

handles.Settings.Plot.measurement = measurement1;
handles.Settings.Plot.axesEqual = handles.cbAxisEqual.Value;

axes(handles.plotArea); %Set the handles of the axes to plot the data in
%Important! Because this function is triggered by an event axes will not work by
%default. So when creating a new GUI in GUIDE with an axes make sure to
%goto the Tools Menu and Select GUI Options, here commandline accessbility
%must be set to on.
plot(x1,y1,x2,y2), title([measurement1.type ' & ' measurement2.type]), xlabel(curve1.xUnit), ylabel(curve1.yUnit), legend(names);
if(handles.Settings.Plot.axesEqual == 1)
    axis equal
else
    axis auto
end
guidata(hObject,handles);


function plotDataRealtime(hObject)
handles = guidata(hObject);
measurement = handles.Measurement.NET.measurements(end).measurement;
handles.Settings.Plot.axesEqual = handles.cbAxisEqual.Value;
curves = measurement.GetCurveArray();
if(strcmp(char(measurement.Method.Name),'Cyclic Voltammetry')) %in the case of a CV plot the curve of each scan
    x = zeros(curves.Length, length(double(curves(1).GetXValues())));
    y = zeros(curves.Length, length(double(curves(1).GetXValues())));
    for i = 1:curves.Length
        x(i,1:length(double(curves(i).GetXValues()))) = double(curves(i).GetXValues());
        y(i,1:length(double(curves(i).GetXValues()))) = double(curves(i).GetYValues());
    end
    x=x';
    y=y';
else
    x = double(curves(1).GetXValues());
    y = double(curves(1).GetYValues());
end

axes(handles.plotArea); %Set the handles of the axes to plot the data in
%Important! Because this function is triggered by an event axes will not work by
%default. So when creating a new GUI in GUIDE with an axes make sure to
%goto the Tools Menu and Select GUI Options, here commandline accessbility
%must be set to on.
plot(x,y), title(char(measurement.Title)), xlabel(char(curves(1).XUnit.ToString())), ylabel(char(curves(1).YUnit.ToString()));
if(handles.Settings.Plot.axesEqual == 1)
    axis equal
else
    axis auto
end
guidata(hObject,handles);


function plotEISDataRealtime(hObject)
handles = guidata(hObject);
measurement = handles.Measurement.NET.measurements(end).measurement;
handles.Settings.Plot.axesEqual = handles.cbAxisEqual.Value;

%Get impedance data arrays (See processEISMeasurement function for extracting data for bode plots)
dataArrays = measurement.DataSet.GetDataArrays();
ZRe = dataArrays(5);
ZIm = dataArrays(6);

%Nyquist curve
x = double(ZRe.GetValues());
y = double(ZIm.GetValues());

axes(handles.plotArea); %Set the handles of the axes to plot the data in
%Important! Because this function is triggered by an event axes will not work by
%default. So when creating a new GUI in GUIDE with an axes make sure to
%goto the Tools Menu and Select GUI Options, here commandline accessbility
%must be set to on.
plot(x,y), title(char(measurement.Title)), xlabel(['ZRe(' char(ZRe.Unit.ToString()) ')']), ylabel(['ZIm(' char(ZIm.Unit.ToString()) ')']);
if(handles.Settings.Plot.axesEqual == 1)
    axis equal
else
    axis auto
end
guidata(hObject,handles);


% --- Executes on selection change in pmCRMin.
function pmCRMin_Callback(hObject, eventdata, handles)
% hObject    handle to pmCRMin (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = cellstr(get(hObject,'String')) returns pmCRMin contents as cell array
%        contents{get(hObject,'Value')} returns selected item from pmCRMin


% --- Executes during object creation, after setting all properties.
function pmCRMin_CreateFcn(hObject, eventdata, handles)
% hObject    handle to pmCRMin (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on selection change in pmCRMax.
function pmCRMax_Callback(hObject, eventdata, handles)
% hObject    handle to pmCRMax (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = cellstr(get(hObject,'String')) returns pmCRMax contents as cell array
%        contents{get(hObject,'Value')} returns selected item from pmCRMax


% --- Executes during object creation, after setting all properties.
function pmCRMax_CreateFcn(hObject, eventdata, handles)
% hObject    handle to pmCRMax (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function tbtEquilibrationEIS_Callback(hObject, eventdata, handles)
% hObject    handle to tbtEquilibrationEIS (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of tbtEquilibrationEIS as text
%        str2double(get(hObject,'String')) returns contents of tbtEquilibrationEIS as a double


% --- Executes during object creation, after setting all properties.
function tbtEquilibrationEIS_CreateFcn(hObject, eventdata, handles)
% hObject    handle to tbtEquilibrationEIS (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function tbEDCEIS_Callback(hObject, eventdata, handles)
% hObject    handle to tbEDCEIS (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of tbEDCEIS as text
%        str2double(get(hObject,'String')) returns contents of tbEDCEIS as a double


% --- Executes during object creation, after setting all properties.
function tbEDCEIS_CreateFcn(hObject, eventdata, handles)
% hObject    handle to tbEDCEIS (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function tbEACEIS_Callback(hObject, eventdata, handles)
% hObject    handle to tbEACEIS (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of tbEACEIS as text
%        str2double(get(hObject,'String')) returns contents of tbEACEIS as a double


% --- Executes during object creation, after setting all properties.
function tbEACEIS_CreateFcn(hObject, eventdata, handles)
% hObject    handle to tbEACEIS (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function tbnFrequenciesEIS_Callback(hObject, eventdata, handles)
% hObject    handle to tbnFrequenciesEIS (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of tbnFrequenciesEIS as text
%        str2double(get(hObject,'String')) returns contents of tbnFrequenciesEIS as a double


% --- Executes during object creation, after setting all properties.
function tbnFrequenciesEIS_CreateFcn(hObject, eventdata, handles)
% hObject    handle to tbnFrequenciesEIS (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function tbMinFrequencyEIS_Callback(hObject, eventdata, handles)
% hObject    handle to tbMinFrequencyEIS (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of tbMinFrequencyEIS as text
%        str2double(get(hObject,'String')) returns contents of tbMinFrequencyEIS as a double


% --- Executes during object creation, after setting all properties.
function tbMinFrequencyEIS_CreateFcn(hObject, eventdata, handles)
% hObject    handle to tbMinFrequencyEIS (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function tbMaxFrequencyEIS_Callback(hObject, eventdata, handles)
% hObject    handle to tbMaxFrequencyEIS (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of tbMaxFrequencyEIS as text
%        str2double(get(hObject,'String')) returns contents of tbMaxFrequencyEIS as a double


% --- Executes during object creation, after setting all properties.
function tbMaxFrequencyEIS_CreateFcn(hObject, eventdata, handles)
% hObject    handle to tbMaxFrequencyEIS (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function tbECondition_Callback(hObject, eventdata, handles)
% hObject    handle to tbECondition (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of tbECondition as text
%        str2double(get(hObject,'String')) returns contents of tbECondition as a double


% --- Executes during object creation, after setting all properties.
function tbECondition_CreateFcn(hObject, eventdata, handles)
% hObject    handle to tbECondition (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function tbtCondition_Callback(hObject, eventdata, handles)
% hObject    handle to tbtCondition (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of tbtCondition as text
%        str2double(get(hObject,'String')) returns contents of tbtCondition as a double


% --- Executes during object creation, after setting all properties.
function tbtCondition_CreateFcn(hObject, eventdata, handles)
% hObject    handle to tbtCondition (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function tbEDeposition_Callback(hObject, eventdata, handles)
% hObject    handle to tbEDeposition (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of tbEDeposition as text
%        str2double(get(hObject,'String')) returns contents of tbEDeposition as a double


% --- Executes during object creation, after setting all properties.
function tbEDeposition_CreateFcn(hObject, eventdata, handles)
% hObject    handle to tbEDeposition (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function tbtDeposition_Callback(hObject, eventdata, handles)
% hObject    handle to tbtDeposition (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of tbtDeposition as text
%        str2double(get(hObject,'String')) returns contents of tbtDeposition as a double


% --- Executes during object creation, after setting all properties.
function tbtDeposition_CreateFcn(hObject, eventdata, handles)
% hObject    handle to tbtDeposition (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function tbtEquilibrationLSV_Callback(hObject, eventdata, handles)
% hObject    handle to tbtEquilibrationLSV (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of tbtEquilibrationLSV as text
%        str2double(get(hObject,'String')) returns contents of tbtEquilibrationLSV as a double


% --- Executes during object creation, after setting all properties.
function tbtEquilibrationLSV_CreateFcn(hObject, eventdata, handles)
% hObject    handle to tbtEquilibrationLSV (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function tbEBeginLSV_Callback(hObject, eventdata, handles)
% hObject    handle to tbEBeginLSV (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of tbEBeginLSV as text
%        str2double(get(hObject,'String')) returns contents of tbEBeginLSV as a double


% --- Executes during object creation, after setting all properties.
function tbEBeginLSV_CreateFcn(hObject, eventdata, handles)
% hObject    handle to tbEBeginLSV (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function tbEEndLSV_Callback(hObject, eventdata, handles)
% hObject    handle to tbEEndLSV (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of tbEEndLSV as text
%        str2double(get(hObject,'String')) returns contents of tbEEndLSV as a double


% --- Executes during object creation, after setting all properties.
function tbEEndLSV_CreateFcn(hObject, eventdata, handles)
% hObject    handle to tbEEndLSV (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function tbEStepLSV_Callback(hObject, eventdata, handles)
% hObject    handle to tbEStepLSV (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of tbEStepLSV as text
%        str2double(get(hObject,'String')) returns contents of tbEStepLSV as a double


% --- Executes during object creation, after setting all properties.
function tbEStepLSV_CreateFcn(hObject, eventdata, handles)
% hObject    handle to tbEStepLSV (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function tbScanRateLSV_Callback(hObject, eventdata, handles)
% hObject    handle to tbScanRateLSV (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of tbScanRateLSV as text
%        str2double(get(hObject,'String')) returns contents of tbScanRateLSV as a double


% --- Executes during object creation, after setting all properties.
function tbScanRateLSV_CreateFcn(hObject, eventdata, handles)
% hObject    handle to tbScanRateLSV (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function tbtEquilibrationCV_Callback(hObject, eventdata, handles)
% hObject    handle to tbtEquilibrationCV (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of tbtEquilibrationCV as text
%        str2double(get(hObject,'String')) returns contents of tbtEquilibrationCV as a double


% --- Executes during object creation, after setting all properties.
function tbtEquilibrationCV_CreateFcn(hObject, eventdata, handles)
% hObject    handle to tbtEquilibrationCV (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function tbEBeginCV_Callback(hObject, eventdata, handles)
% hObject    handle to tbEBeginCV (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of tbEBeginCV as text
%        str2double(get(hObject,'String')) returns contents of tbEBeginCV as a double


% --- Executes during object creation, after setting all properties.
function tbEBeginCV_CreateFcn(hObject, eventdata, handles)
% hObject    handle to tbEBeginCV (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function tbEVertex1CV_Callback(hObject, eventdata, handles)
% hObject    handle to tbEVertex1CV (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of tbEVertex1CV as text
%        str2double(get(hObject,'String')) returns contents of tbEVertex1CV as a double


% --- Executes during object creation, after setting all properties.
function tbEVertex1CV_CreateFcn(hObject, eventdata, handles)
% hObject    handle to tbEVertex1CV (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function tbEVertex2CV_Callback(hObject, eventdata, handles)
% hObject    handle to tbEVertex2CV (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of tbEVertex2CV as text
%        str2double(get(hObject,'String')) returns contents of tbEVertex2CV as a double


% --- Executes during object creation, after setting all properties.
function tbEVertex2CV_CreateFcn(hObject, eventdata, handles)
% hObject    handle to tbEVertex2CV (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function tbEStepCV_Callback(hObject, eventdata, handles)
% hObject    handle to tbEStepCV (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of tbEStepCV as text
%        str2double(get(hObject,'String')) returns contents of tbEStepCV as a double


% --- Executes during object creation, after setting all properties.
function tbEStepCV_CreateFcn(hObject, eventdata, handles)
% hObject    handle to tbEStepCV (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function tbScanRateCV_Callback(hObject, eventdata, handles)
% hObject    handle to tbScanRateCV (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of tbScanRateCV as text
%        str2double(get(hObject,'String')) returns contents of tbScanRateCV as a double


% --- Executes during object creation, after setting all properties.
function tbScanRateCV_CreateFcn(hObject, eventdata, handles)
% hObject    handle to tbScanRateCV (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function tbNScansCV_Callback(hObject, eventdata, handles)
% hObject    handle to tbNScansCV (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of tbNScansCV as text
%        str2double(get(hObject,'String')) returns contents of tbNScansCV as a double


% --- Executes during object creation, after setting all properties.
function tbNScansCV_CreateFcn(hObject, eventdata, handles)
% hObject    handle to tbNScansCV (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on selection change in pmCRStart.
function pmCRStart_Callback(hObject, eventdata, handles)
% hObject    handle to pmCRStart (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = cellstr(get(hObject,'String')) returns pmCRStart contents as cell array
%        contents{get(hObject,'Value')} returns selected item from pmCRStart


% --- Executes during object creation, after setting all properties.
function pmCRStart_CreateFcn(hObject, eventdata, handles)
% hObject    handle to pmCRStart (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function tbtRunCA_Callback(hObject, eventdata, handles)
% hObject    handle to tbtRunCA (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of tbtRunCA as text
%        str2double(get(hObject,'String')) returns contents of tbtRunCA as a double


% --- Executes during object creation, after setting all properties.
function tbtRunCA_CreateFcn(hObject, eventdata, handles)
% hObject    handle to tbtRunCA (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function tbtIntervalCA_Callback(hObject, eventdata, handles)
% hObject    handle to tbtIntervalCA (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of tbtIntervalCA as text
%        str2double(get(hObject,'String')) returns contents of tbtIntervalCA as a double


% --- Executes during object creation, after setting all properties.
function tbtIntervalCA_CreateFcn(hObject, eventdata, handles)
% hObject    handle to tbtIntervalCA (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function tbEDCCA_Callback(hObject, eventdata, handles)
% hObject    handle to tbEDCCA (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of tbEDCCA as text
%        str2double(get(hObject,'String')) returns contents of tbEDCCA as a double


% --- Executes during object creation, after setting all properties.
function tbEDCCA_CreateFcn(hObject, eventdata, handles)
% hObject    handle to tbEDCCA (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function tbtEquilibrationCA_Callback(hObject, eventdata, handles)
% hObject    handle to tbtEquilibrationCA (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of tbtEquilibrationCA as text
%        str2double(get(hObject,'String')) returns contents of tbtEquilibrationCA as a double


% --- Executes during object creation, after setting all properties.
function tbtEquilibrationCA_CreateFcn(hObject, eventdata, handles)
% hObject    handle to tbtEquilibrationCA (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end
