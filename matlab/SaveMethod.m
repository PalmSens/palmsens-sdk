function [ success ] = SaveMethod( method, path, PSSDK )
%SaveMethod save a method object to a specified path
%
% Input
%
% method: a method object
% path: the full path (including filename) where the method file must be
% saved. (A full path is required, i.e. C:\Data\LinearSweep.psmethod)
% PSSDK: the handle to the PalmSens Matlab SDK library.
% (This can be obtained using the LoadPSSDK funtion.)
%
% Output
%
% success: a boolean that returns true if the method was successfully
% saved, otherwise it returns false.

%Check whether the object passed into this fucntion is a method object
if(strfind(class(method),'PalmSens.Techniques') == 0)
    success = false;
    return;
end

%Convert the path to a string
winPath = strrep(path, '\', '\\');
strPath = System.String(winPath);

%SDK version string
%(Please do not change, this is stored for support in case of issues)
try
    strSDK = PSSDK.AssemblyHandle.FullName;
catch
    success = false;
    disp('Save function aborted, this function requires the handle of the PalmSens Matlab SDK from your workspace. Please make sure that the LoadPSSDK function was run first (PSSDK = LoadPSSDK()) and check if the PSSDK in your workspace is not empty (set to false/0).');
    return;
end

%Save the method object
try
    PalmSens.Windows.LoadSaveHelperFunctions.SaveMethod(method, strPath, strSDK);
    success = true;
catch
    success = false;
end

end
