function [ measurements ] = LoadSession( sessionPath )
%LoadSession, load a session from the specified path
%
%Input
%
%sessionPath: the path to the pssession file this function will load.
%(The full path is required, i.e. C:\Data\LinearSweep.pssession)
%
%Output
%
%measurements: a struct containing one or more measurements.
%(when the session file cannot be loaded it will return false)
%
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


%Check if the file exists
if(exist(sessionPath,'file') == 0)
    measurements = false;
    return;
end

%Convert the sessionPath to a string
winPath = strrep(sessionPath, '\', '\\');
strPath = System.String(winPath);

%Load the sessionManager object
try
    sessionManager = PalmSens.Data.SessionManager();
    PalmSens.Windows.LoadSaveHelperFunctions.LoadDataAnyFormat(sessionManager, strPath);
catch
    measurements = false;
    return;
end

measurementsPS = sessionManager.GetCollection(); %Get array with measurements from the sessionManager
n = measurementsPS.Length; %Get the number of measurements in the session file

if(n == 0) %No measurements found in session file
    measurements = false;
    return;
end

%Create empty struct to store measurements in
measurements = struct('name',{},'type',{},'date',{},'curves',{},'measurement',{});

for i = 1:n %Convert each measurement in session file to matlab compatible format
    measurements(end + 1) = processMeasurement(measurementsPS(i));
end

end

function measurement = processMeasurement(measurementPS)
%Convert .NET measurement to matlab structs
if(strcmp(char(measurementPS.Method.Name),'Impedance Spectroscopy')) %Impedance Spectroscopy data is handled differently
    measurement = processEISMeasurement(measurementPS);
else
    measurement = struct('name',{},'type',{},'date',{},'curves',{},'measurement',{});
    measurement(1).name = char(measurementPS.Method.ShortName);
    measurement(1).date = char(measurementPS.TimeStamp.ToString());
    measurement(1).type = char(measurementPS.Method.Name);
    measurement(1).curves = struct('xUnit',{},'xData',{},'yUnit',{},'yData',{});
    curves = measurementPS.GetCurveArray();
    for i=1:curves.Length %Loop added for CV, in the case of a CV with multiple scans each scan is stored as a seperate curve
        measurement(1).curves(i).xUnit = char(curves(i).XUnit.ToString());
        measurement(1).curves(i).xData = double(curves(i).GetXValues());
        measurement(1).curves(i).yUnit = char(curves(i).YUnit.ToString());
        measurement(1).curves(i).yData = double(curves(i).GetYValues());
    end
    measurement(1).measurement = measurementPS;
end

end

function measurement = processEISMeasurement(measurementPS)
measurement = struct('name',{},'type',{},'date',{},'curves',{},'measurement',{});
measurement(1).name = char(measurementPS.Method.ShortName);
measurement(1).date = char(measurementPS.TimeStamp.ToString());
measurement(1).type = char(measurementPS.Method.Name);

%Get impedance data arrays
dataArrays = measurementPS.DataSet.GetDataArrays();
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

measurement(1).measurement = measurementPS;
end
