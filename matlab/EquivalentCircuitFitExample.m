%This example demonstrates how to:
%1. Import a Session file
%2. Fit an equivalent circuit
%3. Plot the data.

% clear;
%% Add PalmSens Matlab SDK to workspace
PSSDK = LoadPSSDK();
if(PSSDK == false)
    disp('Error while adding the PalmSens SDK to the workspace. Please resolve before continuing.');
    return;
end

%% 1. Import a Session file
sessionPath = [pwd,'\BatteryCurve.pssession'];
disp([newline 'Importing measurements from session, ' sessionPath '...']);
measurements = LoadSession(sessionPath); %load the method object from the specified path

%Check whether the method was succesfully loaded
if(isstruct(measurements) == false)
    disp('Error importing session, please check if the PalmSens SDK has been loaded,the specified file path is correct and the *.pssession file is valid');
    return;
end
%Display list of loaded measurments
disp(['Succesfully loaded BatteryCurve.pssession. Containing ' num2str(length(measurements)) ' measurement(s):' newline]);
for i = 1:length(measurements)
    disp([num2str(i) '. ' measurements(i).name ' (' measurements(i).type ') measured on ' measurements(i).date]);
end

%% 2. Fit an equivalent circuit
%Fitting of an equivalent circuit can be done using the Matlab
%EquivalentCircuitFit class. This class makes it easier to communicate with
%the PalmSens Matlab SDK library. This class has two input arguments (1) a
%measurement, loaded using the LoadSession function or measured using the
%Measurement function and (2) the circuit specified in the Circuit
%Description Code (https://www.utwente.nl/en/tnw/ims/publications/downloads/CDC_Explained.pdf)
%Optionally you can change the initial values of the parameters, their
%min/max bounds or fix their value. The EquivalentCircuitFit class also
%supports fitting over a specified frequency range and adjustment of exit
%conditions (i.e. max # iterations, min delta error, min parameter step
%size).

measurement = measurements(1); %Get the first measurement;

%Create an instance of the EquivalentCircuitFit class, please note that the
%CDC code must be in CAPS!
fit = EquivalentCircuitFit(measurement,'R(RC)');

%Adjusting the initial parameters, setting bounds and fixating values
parameters = fit.Parameters;

%Get the first parameter in the model (first item is 0 because this is a .NET object)
seriesR = parameters.Item(0);
disp([newline 'Parameter ' char(seriesR.Symbol) ' is a parameter of the type ' char(seriesR.Type) ' and an initial value of '  num2str(seriesR.Value)]);
seriesR.Value = 5; %Change the initial value of the series resistance
seriesR.Fixed = true; %Fix the initial vlaue of the series resistance

%Change the min/max bounds of the capacitance in paralles
parallelC = parameters.Item(2);
parallelC.Value = 1e-3;
parallelC.MinValue = 1e-9;
parallelC.MaxValue = 5e-2;

%Set the frequency range to fit the circuit over (default is all frequencies)
fit.SetFitRange(2,100);

%Set the fit parameters
maxIter = 100; %Set the max # iterations (default is 500)
minDeltaError = 1e-8; %Set the minimum delta error (default is 1e-9)
minStepSize = 1e-10; %Set the minimum parameter step size (default is 1e-12)
fit.SetFitOptions(maxIter, minDeltaError, minStepSize);

%Perform the equivalent circuit fit
result = fit.FitCircuit();

disp([newline 'Fit Results:'])
for i = 1:3
    disp([char(parameters.Item(i-1).Symbol) '. Value = ' num2str(result.ParameterValues(i)) ', Error = ' num2str(result.ParameterErrors(i))])
end
disp([newline 'Chi Squared = ' num2str(result.ChiSq) ', n Iteration = ' num2str(result.NIterations)])
disp(['Exit code = ' result.ExitCode])
%% 3. Plot the data
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

disp([newline 'Plotting the raw data and fit result']);

%Plot the Nyquist plot
figure(2);
subplot 311; plot(measurement.curves(1).xData,measurement.curves(1).yData,'*r',result.FitCurves(1).xData, result.FitCurves(1).yData), title('Nyquist'), xlabel(measurement.curves(1).xUnit), ylabel(measurement.curves(1).yUnit), legend(measurement.name, 'fit');
%Plot the Bode plot impedance over frequency
figure(2);
subplot 312; plot(log10(measurement.curves(2).xData),log10(measurement.curves(2).yData),'*r',log10(result.FitCurves(2).xData),log10(result.FitCurves(2).yData)), title('Bode (Z over frequency)'), xlabel(['Log ' measurement.curves(2).xUnit]), ylabel(['Log ' measurement.curves(2).yUnit]), legend(measurement.name, 'fit');
%Plot the Bode plot -phase over frequency
figure(2);
subplot 313; plot(log10(measurement.curves(3).xData),measurement.curves(3).yData,'*r',log10(result.FitCurves(3).xData),result.FitCurves(3).yData), title('Bode (-phase over frequency)'), xlabel(['Log ' measurement.curves(3).xUnit]), ylabel(measurement.curves(3).yUnit), legend(measurement.name, 'fit');
