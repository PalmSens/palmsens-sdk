classdef Measurement < handle
    %The measurement class contains the functions for starting, stopping
    %and storing the data from a measurement.
    %
    %This class requires the connected PalmSens or Emstat device's
    %commManager to given in its contstructor (i.e. m = Measurement(CommManager))
    %Setting the properties dispInCommandWindow or dispInPlot to true
    %respectively displays the results of the measurement in the
    %Command Window or a Plot in Figure 1.
    %
    %Recording devices idle status
    %Idle status package can be recorded with the GetIdleData function
    %(i.e. m.GetIdleData()) Recording of idle status can be stopped with
    %the StopIdleData function (i.e. m.StopIdleData())
    %
    %Measuring
    %Use the New function in combination with a method in your workspace
    %to start a new measurement (i.e. m.New(method)). The measurement can
    %be aborted at any time with the Abort function (i.e. m.Abort()). The
    %results of the measurement are stored in the measurement properties
    %and can be retreived after the measurement has been completed
    %(measurement = m.measurement).
    %
    %Measurements
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

    properties

        comm; %Object containing handle for communication with device
        measurement; %The result of the measurement converted for use in matlab
        dispInCommandWindow; %When set to true the latest readings from the device are displayed in the command window.
        dispInPlot; %When set to true the latest readings from the device are displayed in a new Figure.

        %Additional properties (take caution while editting)
        inMeasurement; %Bool indicating whether the device is measuring
        abortMeasurement; %Used by class to indicate when abort function has been used
        x_array; %Array of idle potential readings
        x_unit; %Unit of the data recorded in the x_array.
        y_array; %Array of idle potential readings
        y_unit; %Unit of the data recorded in the y_array.
        previousMeasurement; %The result of the measurement as a .Net object
        curves; %List of .Net curve objects returned by the PalmSens Matlab SDK
        listenerIdleData; %Used to listen to the idle status events invoked by the matlab library
        listenerBeginMeasurement; %Used to listen to the begin measurement event invoked by the matlab library
        listenerCurveReceived; %Used to listen to the curve received events invoked by the matlab library
        listenerEndMeasurement; %Used to listen to the end measurement event invoked by the matlab library
        listenerData; %Used to listen to the new data received events invoked by the matlab library

    end

    methods

        function self = Measurement(commManager)
            self.comm = commManager;
            self.x_array = zeros(0);
            self.y_array = zeros(0);
            self.inMeasurement = false;
            self.dispInCommandWindow = true;
            self.dispInPlot = true;

            %listener objects for the begin and end measurement events.
            self.listenerBeginMeasurement = addlistener(self.comm, 'BeginMeasurement', @self.beginListener);
            self.listenerEndMeasurement = addlistener(self.comm, 'EndMeasurement', @self.endListener);
            self.listenerCurveReceived = addlistener(self.comm, 'ReceiveCurve', @self.curveListener);
            self.listenerIdleData = addlistener(self.comm,'ReceiveStatus',@self.idleListener);
            self.listenerIdleData.Enabled = false;
        end

        function New(self, method)
            %Check if the device is still measuring
            if(isempty(self.comm.Comm.ActiveMeasurement) == 0)
                self.inMeasurement = true;
                disp('Could not start new measurement, device is allready in measurement mode.')
            end
            self.inMeasurement = false;

            %Check if the object passed into this fucntion is a method object
            if(strfind(class(method),'PalmSens.Techniques') == 0)
                disp('Cannot start the measurement. Please check whether you entered a valid method object');
                return;
            end

            self.abortMeasurement = false;

            %Clear previous measurement
            self.measurement = struct('name',{},'type',{},'date',{},'curves',{});
            self.curves = NET.createGeneric('System.Collections.Generic.List',{'PalmSens.Plottables.Curve'},50);

            try
                error = System.String('');
                error = self.comm.Measure(method);
                self.inMeasurement = true;
            catch
                self.inMeasurement = false;
                disp(['An error occured while starting the measurement.' newline char(error)]);
            end
        end

        function Abort(self)
            if(isempty(self.comm.Comm.ActiveMeasurement) == 1)
                self.inMeasurement = false;
                return;
            end
            delete(self.listenerData);
            self.comm.Abort();
            self.abortMeasurement = true;
            if(self.dispInCommandWindow == true)
                disp('Measurement Aborted');
            end
        end

        function GetIdleData(self)
            %Clear previously recorded data
            self.x_array = zeros(0);
            self.x_unit = 'Volt';
            self.y_array = zeros(0);
            self.y_unit = 'Ampere';
            self.listenerIdleData.Enabled = true; %Enable listener
        end

        function StopIdleData(self)
            self.listenerIdleData.Enabled = false; %Disable listener
        end

        function idleListener(self,~,eventArgs)
            status = eventArgs.GetStatus();
            self.y_array(end + 1) = status.CurrentReading.Value;
            self.x_array(end + 1) = status.PotentialReading.Value;

            unitCurrent = char(status.CurrentReading.CurrentRange.ToString());

            if(self.dispInCommandWindow == true)
                disp(['Idle Status: Potential (' num2str(self.x_array(end)) ' V) Current (' num2str(status.CurrentReading.ValueInRange) ' * ' unitCurrent ')']);
            end
        end

        function beginListener(self,~,eventArgs)
            self.previousMeasurement = eventArgs;

            self.listenerData = addlistener(self.comm,'NewDataAdded',@self.dataListener);

            if(self.dispInCommandWindow == true)
                disp([char(eventArgs.Method.Name) ' Measurement Started']);
            end
        end

        function endListener(self,~,~)
            delete(self.listenerData);
            self.processMeasurement(); %Process data when measurement is completed
            self.inMeasurement = false;
            if(self.dispInCommandWindow == true)
                disp('Measurement Ended');
            end
        end

        function dataListener(self,~,eventArgs)
            if(self.dispInCommandWindow == true)
                disp(['data packet(s) ' num2str(eventArgs.StartIndex + 1) ' to ' num2str(eventArgs.Count + eventArgs.StartIndex) '  received']);
            end
            if(self.dispInPlot == true)
                if (strcmp(char(self.previousMeasurement.Method.Name),'Impedance Spectroscopy') || strcmp(char(self.previousMeasurement.Method.Name),'Galvanostatic Impedance Spectroscopy'))
                    self.plotEISDataRealtime();
                else
                    self.plotDataRealtime();
                end
            end
        end

        function curveListener(self,~,eventArgs)
            self.curves.Add(eventArgs.GetCurve());
            if(self.dispInCommandWindow == true)
                disp('Curve Received');
            end
        end

        function plotDataRealtime(self)
            m = self.previousMeasurement;
            c = m.GetCurveArray();
            %             if(strcmp(char(m.Method.Name),'Cyclic Voltammetry')) %in the case of a CV plot the curve of each scan
            xPerPlot = containers.Map;
            yPerPlot = containers.Map;
            xUnitPerPlot = containers.Map;
            yUnitPerPlot = containers.Map;
            for i = 1:c.Length
                key = [char(c(i).XUnit.Abbreviation) char(c(i).YUnit.Abbreviation)];
                xPerPlot(key) = [];
                yPerPlot(key) = [];
                xUnitPerPlot(key) = char(c(i).XUnit.ToString());
                yUnitPerPlot(key) = char(c(i).YUnit.ToString());
            end
            for i = 1:c.Length
                key = [char(c(i).XUnit.Abbreviation) char(c(i).YUnit.Abbreviation)];
                xData = xPerPlot(key);
                xData(length(xData) + 1, 1:length(double(c(i).GetXValues()))) = double(c(i).GetXValues());
                xPerPlot(key) = xData;

                yData = yPerPlot(key);
                yData(length(yData) + 1, 1:length(double(c(i).GetYValues()))) = double(c(i).GetYValues());
                yPerPlot(key) = yData;
            end

            for i = 1:length(keys(xPerPlot))
                xkeys = keys(xPerPlot);
                xkey = xkeys{i};
                x = xPerPlot(xkey)';
                x = x';
                y = yPerPlot(xkey)';
                y= y';

                min_length = min([length(x), length(y)]);
                figure(i);
                plot(x(1:min_length),y(1:min_length)), title(char(m.Title)), xlabel(xUnitPerPlot(xkey)), ylabel(yUnitPerPlot(xkey));
            end
        end

        function plotEISDataRealtime(self)
            m = self.previousMeasurement;

            %Get impedance data arrays (See processEISMeasurement function for extracting data for bode plots)
            dataArrays = m.DataSet.GetDataArrays();
            ZRe = dataArrays(5);
            ZIm = dataArrays(6);

            %Nyquist curve
            x = double(ZRe.GetValues());
            y = double(ZIm.GetValues());

            figure(1);
            plot(x,y), title(char(m.Title)), xlabel(['ZRe(' char(ZRe.Unit.ToString()) ')']), ylabel(['ZIm(' char(ZIm.Unit.ToString()) ')']);
        end

        function measurement = processMeasurement(self)
            m = self.previousMeasurement;
            c = self.curves;
            %Convert .NET measurement to matlab structs
            if(strcmp(char(m.Method.Name),'Impedance Spectroscopy') || strcmp(char(m.Method.Name),'Galvanostatic Impedance Spectroscopy')) %Impedance Spectroscopy data is handled differently
                self.processEISMeasurement();
            else
                measurement = struct('name',{},'type',{},'date',{},'curves',{},'measurement',{});
                measurement(1).name = char(m.Method.ShortName);
                measurement(1).date = datestr(now);
                measurement(1).type = char(m.Method.Name);
                measurement(1).curves = struct('xUnit',{},'xData',{},'yUnit',{},'yData',{});
                for i=1:c.Count %Loop added for CV, in the case of a CV with multiple scans each scan is stored as a seperate curve
                    measurement(1).curves(i).xUnit = char(c.Item(i - 1).XUnit.ToString());
                    measurement(1).curves(i).xData = double(c.Item(i - 1).GetXValues());
                    measurement(1).curves(i).yUnit = char(c.Item(i - 1).YUnit.ToString());
                    measurement(1).curves(i).yData = double(c.Item(i - 1).GetYValues());
                end
                measurement(1).measurement = m;
                self.measurement = measurement;
            end
        end

        function measurement = processEISMeasurement(self)
            m = self.previousMeasurement;

            measurement = struct('name',{},'type',{},'date',{},'curves',{},'measurement',{});
            measurement(1).name = char(m.Method.ShortName);
            measurement(1).date = datestr(now);
            measurement(1).type = char(m.Method.Name);

            %Get impedance data arrays
            dataArrays = m.DataSet.GetDataArrays();
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

            measurement(1).measurement = m;

            self.measurement = measurement;
        end

    end

end
