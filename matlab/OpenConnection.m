function [comm] = OpenConnection(device)
    % Opens a connection with the specified device and returns its CommManager.
    %
    % If a device's connection has allready been opened it will
    % be closed (for exmpale in PSTrace or Multitrace).
    %
    % Note that connecting multiple devices at once may result in unexpected behaviour.
    %
    % Parameters:
    %   device: The device to open a connection with.
    %
    % Returns:
    %   comm: CommManager object that is used to communicate with the device.
    %       When to the device cannot be openened it will return false.

    comm = PalmSens.Core.Matlab.MatlabInterface();

    try
        device.Open(); % if the connection has allready been opened or it is not a PalmSens device this will result in an error
        comm.NewCommManager(device);
        % comm = PalmSens.Comm.CommManager(device);
    catch
        device.Close();
        comm = false;
    end

end
