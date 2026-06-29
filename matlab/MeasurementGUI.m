classdef MeasurementGUI < handle
    % The measurement class contains the functions for starting, stopping
    % and storing the data from a measurements
    % This is a version of the `Measurement` class that can be used with a MATLAB GUIDE user interface.

    properties

        comm  % Object containing handle for communication with device
        inMeasurement  % Bool indicating whether the device is measuring

    end

    properties (SetAccess = private, Hidden = true)

        listenerIdleData
        listenerBeginMeasurement
        listenerCurveReceived
        listenerEndMeasurement
        listenerData

    end

    methods

        function self = MeasurementGUI(hObject, commManager, beginMeasurmentCallback, endMeasurementCallback, receiveCurveCallback, receiveStatusCallback)
            % Initialize measurement class.
            %
            % Parameters:
            %   hObject (Handle):
            %       Handle to btnConnect
            %   commManager (PalmSens.Comm.CommManager):
            %       The comm manager manages the connection with the device.
            %   beginMeasurmentCallback (Callable):
            %       Callback for begin measurement event.
            %   endMeasurementCallback (Callable):
            %       Callback for end measurement event.
            %   receiveCurveCallback (Callable):
            %       Callback for curve event.
            %   receiveStatusCallback (Callable):
            %       Callback for status update event.
            self.comm = commManager;
            self.inMeasurement = false;

            % listener objects for the begin and end measurement events.
            self.listenerBeginMeasurement = addlistener(self.comm, 'BeginMeasurement', @(sender, eventArgs) beginMeasurmentCallback(sender, eventArgs, hObject));
            self.listenerEndMeasurement = addlistener(self.comm, 'EndMeasurement', @(sender, eventArgs) endMeasurementCallback(sender, eventArgs, hObject));
            self.listenerCurveReceived = addlistener(self.comm, 'ReceiveCurve', @(sender, eventArgs) receiveCurveCallback(sender, eventArgs, hObject));
            self.listenerIdleData = addlistener(self.comm, 'ReceiveStatus', @(sender, eventArgs) receiveStatusCallback(sender, eventArgs, hObject));
            self.listenerIdleData.Enabled = false;
        end

        function New(self, method)
            % Start a new measurement.
            %
            % Parameters:
            %     method (PalmSens.Method):
            %         Method class with technique parameters.

            % Check if the device is still measuring
            if isempty(self.comm.Comm.ActiveMeasurement) == 0
                self.inMeasurement = true;
                disp('Could not start new measurement, device is allready in measurement mode.');
            end
            self.inMeasurement = false;

            % Check if the object passed into this fucntion is a method object
            if strfind(class(method), 'PalmSens.Techniques') == 0
                disp('Cannot start the measurement. Please check whether you entered a valid method object');
                return
            end

            try
                error = System.String('');
                error = self.comm.Measure(method);
                self.inMeasurement = true;
            catch
                self.inMeasurement = false;
                disp(['An error occured while starting the measurement. ' char(error)]);
            end

        end

        function Abort(self)
            % Abort a running measurement.
            if isempty(self.comm.Comm.ActiveMeasurement) == 1
                self.inMeasurement = false;
                return
            end
            delete(self.listenerData);
            self.comm.Abort();
            self.inMeasurement = false;
        end

        function GetIdleData(self)
            % Record idle data.
            %
            % This will be stopped once a measurement starts.
            % Recording idle data will clear any previously recorded data.
            self.listenerIdleData.Enabled = true; % Enable listener
        end

        function StopIdleData(self)
            % Stop recording idle data.
            self.listenerIdleData.Enabled = false; % Disable listener
        end

        function StartDataListener(self, hObject, dataCallback)
            % Start listener for measurement data.
            self.listenerData = addlistener(self.comm, 'NewDataAdded', @(sender, eventArgs) dataCallback(sender, eventArgs, hObject));
        end

        function StopDataListener(self)
            % Stop listener for measurement data.
            delete(self.listenerData);
        end

    end

end
