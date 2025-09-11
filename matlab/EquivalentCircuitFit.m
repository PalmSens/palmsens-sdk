classdef EquivalentCircuitFit
    %EquivalentCircuitFit Summary of this class goes here
    %   Fits the equivalent circuit specified with the
    %   CDC descriptor code. Optional settings are fixing
    %   the value of a parameter, setting the min/max bounds
    %   for a parameter, specifying the frequency range to fit,
    %   limitting the number of iterations, delta error term or
    %   delta parameter term

    properties
        Parameters
    end

    properties ( SetAccess = private, Hidden = true )
        Model
        FitOptions
        EISData
        CDC
    end

    methods
        function self = EquivalentCircuitFit(measurement,cdc)
            %EquivalentCircuitFit Construct an instance of this class
            %   a reference to the .NET measurement selfect and
            %   the circuit design in the CDC format are required
            self.CDC = cdc;
            self.Model = PalmSens.Fitting.Models.CircuitModel();
            self.EISData = self.GetEISDataFromMeasurement(measurement);
            self.Model.SetEISdata(self.EISData);
            self.Model.SetCircuit(System.String(cdc));
            self.FitOptions = PalmSens.Fitting.FitOptionsCircuit();
            self.FitOptions.Model = self.Model;
            self.FitOptions.RawData = self.EISData;
            self.Parameters = self.Model.InitialParameters;
        end

        function SetFitOptions(self, MaxIterations, MinDeltaError, MinParameterStepSize)
            %SetFitOptions returns a list of the circuit's parameters
            %   Defaults
            %   MaxIterations = 500
            %   MinDeltaError = 1e-9
            %   MinParameterStepSize = 1e-12
            self.FitOptions.MaxIterations = MaxIterations;
            self.FitOptions.MinimumDeltaErrorTerm = MinDeltaError;
            self.FitOptions.MinimumDeltaParameters = MinParameterStepSize;
        end

        function SetFitRange(self, MinHz, MaxHz)
            %SetFitRange Sets the frequency range to fit the circuit over
            data = double(self.EISData.EISDataSet.GetLastOfType(PalmSens.Data.DataArrayType.Frequency).GetValues());
            n = length(data);
            array = NET.createArray('System.Boolean',n);
            for i=1:n
                array(i) = data(i)>= MinHz && data(i) <= MaxHz;
            end
            self.FitOptions.SelectedDataPoints = array;
        end

        function result = FitCircuit(self)
            %FitCircuit Fits the equivalent circuit and returns the fit
            %   results
            fitter = PalmSens.Fitting.FitAlgorithm.FromAlgorithm(self.FitOptions);
            fitter.ApplyFitCircuit();
            result = struct();
            result.ParameterValues = double(fitter.FitResult.FinalParameters);
            result.ParameterErrors = double(fitter.FitResult.ParameterSDs);
            result.ChiSq = fitter.FitResult.ChiSq;
            result.NIterations = fitter.FitResult.NIterations - 1;
            result.ExitCode = char(fitter.FitResult.ExitCode.ToString());
            result.FitCurves = self.GetFittedCurves(fitter.FitResult.FinalParameters);
        end
    end

    methods ( Access = private )
        function eisData = GetEISDataFromMeasurement(self, measurement)
            measurement = self.IsValidMeasurement(measurement);
            eisData = self.IsValidEISMeasurement(measurement);
        end

        function validMeasurement = IsValidMeasurement(self,measurement)
            type = whos('measurement');
            if(strcmp(type.class,'struct'))
                if(isfield(measurement,'measurement'))
                    validMeasurement = self.IsValidMeasurement(measurement.measurement);
                else
                    error("Invalid argument for measurement")
                end
            elseif (strcmp(type.class,'PalmSens.Measurement') || strcmp(type.class,'PalmSens.Techniques.ImpedimetricMeasurement'))
                validMeasurement = measurement;
            else
                error("Invalid argument for measurement")
            end
        end

        function eisData = IsValidEISMeasurement(self,measurement)
            method = measurement.Method;
            mtype = whos('method');
            if(strcmp(mtype.class, 'PalmSens.Techniques.ImpedimetricMethod'))
                if(strcmp(char(method.FreqType.ToString()),'Scan') &&  strcmp(char(method.ScanType.ToString()),'Fixed'))
                    eisData = measurement.EISdata.Item(0);
                else
                    error("Fit only supports EIS scans at a fixed potential")
                end
            else
                error("Fit only EIS measurements supported")
            end
        end

        function curves = GetFittedCurves(self, fitParamters)
            modelFit = PalmSens.Fitting.Models.CircuitModel();
            modelFit.SetEISdata(self.EISData);
            modelFit.SetCircuit(System.String(self.CDC));
            modelFit.SetInitialParameters(fitParamters);

            %Nyquist curve
            nyquist = modelFit.GetNyquist();
            nyquist = nyquist(1);
            ZRe = nyquist.XAxisDataArray;
            ZIm = nyquist.YAxisDataArray;
            curves(1).xUnit = ['ZRe(' char(ZRe.Unit.ToString()) ')'];
            curves(1).xData = double(ZRe.GetValues());
            curves(1).yUnit = ['ZIm(' char(ZIm.Unit.ToString()) ')'];
            curves(1).yData = double(ZIm.GetValues());

            %Bode curves
            %Impedance over Frequency
            zvsFreq = modelFit.GetCurveZabsOverFrequency(false);
            zvsFreq = zvsFreq(1);
            Frequency = zvsFreq.XAxisDataArray;
            Zabs = zvsFreq.YAxisDataArray;
            curves(2).xUnit = ['Frequency(' char(Frequency.Unit.ToString()) ')'];
            curves(2).xData = double(Frequency.GetValues());
            curves(2).yUnit = ['Z(' char(Zabs.Unit.ToString()) ')'];
            curves(2).yData = double(Zabs.GetValues());

            %-Phase over Frequency
            phasevsFreq = modelFit.GetCurvePhaseOverFrequency(false);
            phasevsFreq = phasevsFreq(1);
            Phase = phasevsFreq.YAxisDataArray;
            curves(3).xUnit = ['Frequency(' char(Frequency.Unit.ToString()) ')'];
            curves(3).xData = double(Frequency.GetValues());
            curves(3).yUnit = ['-Phase(' char(Phase.Unit.ToString()) ')'];
            curves(3).yData = -1 .* double(Phase.GetValues());
        end
    end
end
