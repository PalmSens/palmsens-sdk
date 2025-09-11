function [ PSSDK ] = LoadPSSDK()
%LoadPSSDK loads the PalmSens SDK and adds it to the workspace
%
% Output
%
% PSSDK: the matlab assembly handle of the PalmSens SDK. (if the SDK was
% not loaded successfully this output is set to false)

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


try
    PSSDK = NET.addAssembly(dllPath);
catch ex
    PSSDK = false;
end

end
