function [ comm ] = OpenConnection( device )
%OpenConnection opens a connection with the specified device and returns
%its CommManager. If a device's connection has allready been opened it will
%be closed (for exmpale in PSTrace or Multitrace).
%
%(Warning! Connecting multiple devices at once may result
%in undesired behaviour)
%
%Input
%
%device: the device to open a connection with.
%
%Output
%
%comm: the CommManager object that is used to communicate with the device.
%(when to the device cannot be openened it will return false)

comm = PalmSens.Core.Matlab.MatlabInterface();

try
    device.Open(); %if the connection has allready been opened or it is not a PalmSens device this will result in an error
    comm.NewCommManager(device);
    %comm = PalmSens.Comm.CommManager(device);
catch
    device.Close();
    comm = false;
end

end
