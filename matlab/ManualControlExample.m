function varargout = ManualControlExample(varargin)
% MANUALCONTROLEXAMPLE MATLAB code for ManualControlExample.fig
%      MANUALCONTROLEXAMPLE, by itself, creates a new MANUALCONTROLEXAMPLE or raises the existing
%      singleton*.
%
%      H = MANUALCONTROLEXAMPLE returns the handle to a new MANUALCONTROLEXAMPLE or the handle to
%      the existing singleton*.
%
%      MANUALCONTROLEXAMPLE('CALLBACK',hObject,eventData,handles,...) calls the local
%      function named CALLBACK in MANUALCONTROLEXAMPLE.M with the given input arguments.
%
%      MANUALCONTROLEXAMPLE('Property','Value',...) creates a new MANUALCONTROLEXAMPLE or raises the
%      existing singleton*.  Starting from the left, property value pairs are
%      applied to the GUI before ManualControlExample_OpeningFcn gets called.  An
%      unrecognized property name or invalid value makes property application
%      stop.  All inputs are passed to ManualControlExample_OpeningFcn via varargin.
%
%      *See GUI Options on GUIDE's Tools menu.  Choose "GUI allows only one
%      instance to run (singleton)".
%
% See also: GUIDE, GUIDATA, GUIHANDLES

% Edit the above text to modify the response to help ManualControlExample

% Last Modified by GUIDE v2.5 06-Apr-2017 13:05:42

% Begin initialization code - DO NOT EDIT
gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
                   'gui_Singleton',  gui_Singleton, ...
                   'gui_OpeningFcn', @ManualControlExample_OpeningFcn, ...
                   'gui_OutputFcn',  @ManualControlExample_OutputFcn, ...
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


% --- Executes just before ManualControlExample is made visible.
function ManualControlExample_OpeningFcn(hObject, ~, handles, varargin)
% This function has no output args, see OutputFcn.
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% varargin   command line arguments to ManualControlExample (see VARARGIN)

% Choose default command line output for ManualControlExample
handles.output = hObject;

set(handles.btnCell,'enable','off');
set(handles.tbPotential,'enable','off');
handles.tbPotential.String = '0';

% Update handles structure
guidata(hObject, handles);

LoadSDK(hObject);
ScanDevices(hObject);

% UIWAIT makes ManualControlExample wait for user response (see UIRESUME)
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
function varargout = ManualControlExample_OutputFcn(~, ~, handles)
% varargout  cell array for returning output args (see VARARGOUT);
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Get default command line output from handles structure
varargout{1} = handles.output;


% --- Executes on selection change in lbLog.
function lbLog_Callback(~, ~, ~)
% hObject    handle to lbLog (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = cellstr(get(hObject,'String')) returns lbLog contents as cell array
%        contents{get(hObject,'Value')} returns selected item from lbLog


% --- Executes during object creation, after setting all properties.
function lbLog_CreateFcn(hObject, ~, ~)
% hObject    handle to lbLog (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: listbox controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in btnCell.
function btnCell_Callback(hObject, ~, handles)
% hObject    handle to btnCell (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
if(strcmp(handles.btnCell.String,'Cell On'))
    %Set the current range
    SetCurrentRange(hObject);
    %Set the potential
    SetPotential(hObject, handles);
    %Turn on the cell
    handles.Settings.Devices.comm.CellOn = 1;
    Log(hObject,'Cell Activated');
    %Turn on the idle packet listener
    handles.Measurement.measurement.GetIdleData;

    handles.btnCell.String = 'Cell Off';
    guidata(hObject, handles);
else
    %Turn off the idle packet listener
    handles.Measurement.measurement.StopIdleData;
    %Turn off the cell
    handles.Settings.Devices.comm.CellOn = 0;
    Log(hObject,'Cell Deactivated');

    handles.btnCell.String = 'Cell On';
    guidata(hObject, handles);
end


% --- Executes on selection change in pmCurrentRange.
function pmCurrentRange_Callback(hObject, ~, handles)
% hObject    handle to pmCurrentRange (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = cellstr(get(hObject,'String')) returns pmCurrentRange contents as cell array
%        contents{get(hObject,'Value')} returns selected item from pmCurrentRange
enabled = get(handles.btnCell,'enable');
if(strcmp(enabled,'on'))
    SetCurrentRange(hObject);
end


function SetCurrentRange(hObject)
handles = guidata(hObject);
currentRange = handles.Settings.Devices.SupportedCurrentRanges.Item(handles.pmCurrentRange.Value - 1);
handles.Settings.Devices.comm.CurrentRange = currentRange;
guidata(hObject,handles);
Log(hObject,['Current range set to: ' char(currentRange.ToString())]);


% --- Executes during object creation, after setting all properties.
function pmCurrentRange_CreateFcn(hObject, ~, ~)
% hObject    handle to pmCurrentRange (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


function tbPotential_Callback(hObject, ~, handles)
% hObject    handle to tbPotential (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of tbPotential as text
%        str2double(get(hObject,'String')) returns contents of tbPotential as a double
SetPotential(hObject, handles);


function SetPotential(hObject, handles)
potential = str2double(handles.tbPotential.String);
min = handles.Settings.Devices.MinPotential;
max = handles.Settings.Devices.MaxPotential;

if(isnan(potential)) %Check if specified potential is supported by the device
    Log(hObject,['Please enter a number between ' num2str(min) 'V and ' num2str(max) 'V.']);
    return;
elseif (potential > max || potential < min)
    Log(hObject,['Please enter a number between ' num2str(min) 'V and ' num2str(max) 'V.']);
    return;
end

handles.Settings.Devices.comm.Potential = potential;
Log(hObject,['Potential set to: ' num2str(potential) 'V.']);


% --- Executes during object creation, after setting all properties.
function tbPotential_CreateFcn(hObject, ~, ~)
% hObject    handle to tbPotential (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on selection change in pmDevices.
function pmDevices_Callback(hObject, eventdata, handles)
% hObject    handle to pmDevices (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = cellstr(get(hObject,'String')) returns pmDevices contents as cell array
%        contents{get(hObject,'Value')} returns selected item from pmDevices


% --- Executes during object creation, after setting all properties.
function pmDevices_CreateFcn(hObject, ~, ~)
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

    %Change Connect and Refresh buttons to Disconnect and Test
    handles.btnRefresh.String = 'Test';
    handles.btnConnect.String = 'Disconnect';
    set(handles.btnCell,'enable','on');
    set(handles.tbPotential,'enable','on');

    %Store the devices communication objecthandle in the GUIs handles
    handles.Settings.Devices.comm = comm;
    guidata(hObject,handles);
    PopulateCurrentRangeMenu(hObject);
else
    handles.Settings.Devices.comm.Disconnect();
    delete(handles.Settings.Devices.comm);
    Log(hObject,'Device disconnected.');

    %Change Disconnect and Test buttons to Connect and Refresh
    set(handles.btnRefresh,'enable','on'); %Reenable if disconnected during testing
    handles.btnRefresh.String = 'Refresh';
    handles.btnConnect.String = 'Connect';
    set(handles.btnCell,'enable','off');
    set(handles.tbPotential,'enable','off');
    guidata(hObject,handles);
    handles.pmCurrentRange.String = {' '};
    handles.pmCurrentRange.Value = 1;
    handles = guidata(hObject);

    %Delete measurement class to remove the even listners and prevent samples from being recorded multiple times
    if(isfield(handles,'Measurement'))
        if(isfield(handles.Measurement,'measurement') ~= 0)
            delete(handles.Measurement.measurement);
        end
    end

    %Update the figures handles
    guidata(hObject,handles);
end


function beginListener(~,~,~)
%Callback not used in this example


function endListener(~,~,~)
%Callback not used in this example


function curveListener(~,~,~)
%Callback not used in this example


function idleListener(~,eventArgs,hObject)
status = eventArgs.GetStatus();
current = status.CurrentReading.ValueInRange;
unitCurrent = char(status.CurrentReading.CurrentRange.ToString());
potential = status.PotentialReading.Value;
Log(hObject,['Idle Status: Potential (' num2str(potential) ' V) Current (' num2str(current) ' ' unitCurrent ')']);


function PopulateCurrentRangeMenu(hObject)
handles = guidata(hObject);
%Get device's supported current ranges
ranges = handles.Settings.Devices.comm.Comm.Capabilities.SupportedRanges;
handles.Settings.Devices.SupportedCurrentRanges = ranges; %Store supported current ranges in figure handle
handles.Settings.Devices.MinPotential = handles.Settings.Devices.comm.Comm.Capabilities.MinPotential;
handles.Settings.Devices.MaxPotential = handles.Settings.Devices.comm.Comm.Capabilities.MaxPotential;
n = ranges.Count;
%Create cell with list of current ranges for menu
list = cell(1,n);
for i = 1:n
    list{i} = char(ranges.Item(i - 1).ToString());
end
handles.pmCurrentRange.String = list;
guidata(hObject, handles);

% --- Executes on button press in btnRefresh.
function btnRefresh_Callback(hObject, ~, handles)
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
