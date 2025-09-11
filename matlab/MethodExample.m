%This example demonstrates how to:
%1. Load an existing Method file.
%2. Edit the parameters of a Method file.
%3. Save a method file.
%4. Create a new method.
%5. Safely remove a method from the workspace.

clear
%% Add PalmSens Matlab SDK to workspace
PSSDK = LoadPSSDK();
if(PSSDK == false)
    disp('Error while adding the PalmSens SDK to the workspace. Please resolve before continuing.');
    return;
end

%% Get the folder to load/save methods from and to
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
if(exist('psDataFolder','var') == 0)
    %Get user folder
    userFolder = getenv('USERPROFILE');
    if(exist([userFolder '\My Documents\PSData'],'dir') == 7)
        psDataFolder = [userFolder '\My Documents\PSData\'];
    end
end

%Show load method dialog
disp([newline 'Please specify the location a *.psmethod file']);
if(exist('psDataFolder','var') == 0)
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

%% 1. Load an existing method file
disp([newline 'Loading method from ' methodPath '...']);
method = LoadMethod(methodPath); %load the method object from the specified path

%Check whether the method was succesfully loaded
if(method == false)
    disp('Error loading method, please check if the PalmSens SDK has been loaded,the specified file path is correct and the *.psmethod file is valid');
end
disp(['Succesfully loaded the [ ' char(method.Name) ' ] method ' methodName '.' newline]);

%% 2. Edit method parameters (For the purpose of this example please load a linear sweep method)

%Caution! Editing certain method parameters can result in an incompatible
%method (Not all PalmSense devices are compatible with all settings,
%please refer to the manual for your devices capabilities). If parameters
%in a method are incorrectly specified the device will not run the
%measurement.
%
%(A simpler alternative would be to load a method you edited in
%PSTrace or the PalmSens Matlab SDK gUIde Example.)

%Check if the loaded method object is a Linear Sweep Method
if(method.TechniqueNumber == 0)

    %Example 1. Editting the begin, end and step potential of a linear sweep
    %method

    %Begin end and step potential are properties of the method object and
    %can be accessed directly

    %Get the methods begin, end and step potential
    bPot = method.BeginPotential;
    ePot = method.EndPotential;
    sPot = method.StepPotential;
    disp(['This methods begin, end and step potential are:' newline]);
    disp(['Begin potential = ' num2str(bPot)]);
    disp(['End potential = ' num2str(ePot)]);
    disp(['Step potential = ' num2str(sPot) newline]);

    %Prompting for the new begin, end and step potential
    disp('Please check your devices capabilities first to assure that the method does not become incompatible.')
    bPotNew = input('Please enter a new begin potential for the linear sweep measurement: ');
    ePotNew = input('Please enter a new end potential for the linear sweep measurement: ');
    sPotNew = input('Please enter a new step potential for the linear sweep measurement: ');

    %Setting the new begin, end and step potential in the method object.
    method.BeginPotential = bPotNew;
    method.EndPotential = ePotNew;
    method.StepPotential = sPotNew;

    %Display results
    bPot = method.BeginPotential;
    ePot = method.EndPotential;
    sPot = method.StepPotential;
    disp([newline 'This methods new begin, end and step potential are:' newline]);
    disp(['Begin potential = ' num2str(bPot)]);
    disp(['End potential = ' num2str(ePot)]);
    disp(['Step potential = ' num2str(sPot) newline]);

    %Example 2. Editting the current range

    %Current range is specified in a Ranging object that is located in the
    %method. Current range can be editted by replacing this object with a
    %new instance of either a PalmSens.FixedRanging (fixed to a single
    %current range) or a PalmSens.AutoRanging (auto ranging between a
    %minimum and maximum current range) object.

    %Get the methods current range
    rangingObj = class(method.Ranging);
    rangingType = strsplit(rangingObj,'.');
    if(strcmp(rangingType{end},'AutoRanging') == 1)
        minRange = char(method.Ranging.MinimumCurrentRange.Description);
        maxRange = char(method.Ranging.MaximumCurrentRange.Description);
        startRange = char(method.Ranging.StartCurrentRange.Description);
        disp(['This method currently uses ' rangingType{end} ' between ' minRange ' and ' maxRange ' starting at ' startRange '.']);
    else
        fixedRange = char(method.Ranging.StartCurrentRange.Description);
        disp(['This method currently uses ' rangingType{end} ' set to ' startRange '.']);
    end

    %Prompt new current range
    disp([newline 'Select whether you wish to fix the current range or set it to auto ranging.' newline]);
    disp('1. Fix to single current range');
    disp(['2. Select auto ranging between a minimun and maximum range' newline]);
    type = 0;
    while(type ~= 1 && type ~= 2)
        type = input(':');
        disp('please select enter either 1 or 2, or press control + c to abort.')
    end
    disp([newline '1. 100 pA']);
    disp('2. 1 nA');
    disp('3. 10 nA');
    disp('4. 100 nA');
    disp('5. 1 uA');
    disp('6. 10 uA');
    disp('7. 100 uA');
    disp('8. 1 mA');
    disp('9. 10 mA');
    disp(['10. 100mA' newline]);
    if(type == 1)
        maxRangeNew = input('Enter a number from 1 to 10 to specify the current range: ');
    else
        minRangeNew = input('Enter a number from 1 to 10 to specify the minimum current range: ');
        maxRangeNew = input('Enter a number from 1 to 10 to specify the maximum current range: ');
        startRangeNew = input('Enter a number from 1 to 10 to specify the current range to start the measurement at: ');
    end

    %Setting the current range
    if(type == 1) %Setting a fixed current range
        %Creating a new fixed current range object
        uA=10^(maxRangeNew - 5); %Convert input value into MicroAmps
        fixedCurrentRange = PalmSens.CurrentRange.FromMicroamps(uA); %Convert MicroAmps into current range objects
        newRangingObj = PalmSens.FixedCurrentRange(); %Create a new fixed current range object
        newRangingObj.MaximumCurrentRange = fixedCurrentRange; %Set the fixed current range of the new object
        %Setting the fixed current range object in the method;
        method.Ranging = newRangingObj;
    else %Setting an autoranging current range
        %Creating a new autoranging object
        %Converting input values into MicroAmps
        uAmin = 10^(minRangeNew - 5);
        uAmax = 10^(maxRangeNew - 5);
        uAstart = 10^(startRangeNew - 5);
        %Converting MicroAmps into current range objects
        minCurrentRange = PalmSens.CurrentRange.FromMicroamps(uAmin);
        maxCurrentRange = PalmSens.CurrentRange.FromMicroamps(uAmax);
        startCurrentRange = PalmSens.CurrentRange.FromMicroamps(uAstart);
        %Create a new Current AutoRanging object
        newRangingObj = PalmSens.AutoRanging(minCurrentRange, maxCurrentRange, startCurrentRange);
        %Setting the fixed current range object in the method;
        method.Ranging = newRangingObj;
    end

    %Display results
    rangingObj = class(method.Ranging);
    rangingType = strsplit(rangingObj,'.');
    if(strcmp(rangingType{end},'AutoRanging') == 1)
        minRange = char(method.Ranging.MinimumCurrentRange.Description);
        maxRange = char(method.Ranging.MaximumCurrentRange.Description);
        startRange = char(method.Ranging.StartCurrentRange.Description);
        disp([newline 'This method now uses ' rangingType{end} ' between ' minRange ' and ' maxRange ' starting at ' startRange '.']);
    else
        fixedRange = char(method.Ranging.StartCurrentRange.Description);
        disp([newline 'This method now uses ' rangingType{end} ' set to ' startRange '.']);
    end
end

%% 3. Saving a method file
%Show save method dialog
disp([newline 'Please specify where the method must be saved']);
[methodName,methodFolder] = uiputfile('*.psmethod','Please specify where you would like to save the method',Settings.Default.psDataFolder);

%Saving the method
disp('Saving the method...')
fullPath = fullfile(methodFolder,methodName);
saved = SaveMethod(method, fullPath, PSSDK);
if(saved == true)
    disp(['Successfully saved the method to ' fullPath]);
else
    disp('An error occured while saving the method');
end

%% 4. Creating a new method
%Instead of loading and editing a method it is also possible to instantiate
%a new method using the NewMethod function. Refer to the NewMethod's help
%function to see the available types of methods (for example a linear
%sweep, Pulse or Cyclic Voltammetry method).

%Instantiate a new linear sweep voltammetry method object.
newLSV = NewMethod(1);
if(newLSV == false)
    disp([newline 'An error occured while instantiating a new method'])
else
    methodType = strsplit(class(newLSV),'.');
    disp([newline 'Succesfully instantiated a new ' methodType{end} ' method.'])
end

%Instantiate a new cyclic voltammetry method object.
newCV = NewMethod(2);
if(newCV == false)
    disp('An error occured while instantiating a new method')
else
    methodType = strsplit(class(newCV),'.');
    disp(['Succesfully instantiated a new ' methodType{end} ' method.'])
end

%% 5. Safely remove a method from the workspace.
delete(newLSV); %Deleting this object removes its references to the PalmSens library and frees up resources
clear newLSV
disp([newline 'Methods resources released.'])
