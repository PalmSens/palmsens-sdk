classdef MeasurementGUI < handle
    %The measurement class contains the functions for starting, stopping
    %and storing the data from a measurement.
    %   Detailed explanation goes here

    properties

        comm; %Object containing handle for communication with device
        inMeasurement; %Bool indicating whether the device is measuring

        %Additional properties
        activeMeasurement;
        curve;
        listenerIdleData;
        listenerBeginMeasurement;
        listenerCurveReceived;
        listenerEndMeasurement;
        listenerData;

    end

    methods

        function self = MeasurementGUI(hObject, commManager, beginMeasurmentCallback, endMeasurementCallback, receiveCurveCallback, receiveStatusCallback)
            self.comm = commManager;
            self.inMeasurement = false;

            %listener objects for the begin and end measurement events.
            self.listenerBeginMeasurement = addlistener(self.comm, 'BeginMeasurement', @(sender,eventArgs) beginMeasurmentCallback(sender,eventArgs,hObject));
            self.listenerEndMeasurement = addlistener(self.comm, 'EndMeasurement', @(sender,eventArgs) endMeasurementCallback(sender,eventArgs,hObject));
            self.listenerCurveReceived = addlistener(self.comm, 'ReceiveCurve', @(sender,eventArgs) receiveCurveCallback(sender,eventArgs,hObject));
            self.listenerIdleData = addlistener(self.comm,'ReceiveStatus',@(sender,eventArgs) receiveStatusCallback(sender,eventArgs,hObject));
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
            if(isempty(self.comm.Comm.ActiveMeasurement) == 1)
                self.inMeasurement = false;
                return;
            end
            delete(self.listenerData);
            self.comm.Abort();
            self.inMeasurement = false;
        end

        function GetIdleData(self)
            self.listenerIdleData.Enabled = true; %Enable listener
        end

        function StopIdleData(self)
            self.listenerIdleData.Enabled = false; %Disable listener
        end

        function StartDataListener(self,hObject,dataCallback)
            self.listenerData = addlistener(self.comm,'NewDataAdded',@(sender,eventArgs) dataCallback(sender,eventArgs,hObject));
        end

        function StopDataListener(self)
            delete(self.listenerData)
        end

    end

end
