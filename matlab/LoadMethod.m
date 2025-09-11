function [ method ] = LoadMethod( methodPath )
%LoadMethod load a method object from the specified path
%
%Input
%
%methodPath: the path to the psmethod file this function will load.
%(The full path is required, i.e. C:\Data\LinearSweep.psmethod)
%
%Output
%
%method: the method object containing its parameters. (when the method file
%cannot be loaded it will return false)

%Check if the file exists
if(exist(methodPath,'file') == 0)
    method = false;
    return;
end

%Convert the methodPath to a string
winPath = strrep(methodPath, '\', '\\');
strPath = System.String(winPath);

%Load the method object
try
    method = PalmSens.Windows.LoadSaveHelperFunctions.LoadMethod(strPath);
catch ex
    method = false;
end

end
