%List of the supported manual control commands
%To run these commands you must be connected first

%Set device in galvanostatic mode (not all devices support this)
gstat = PalmSens.Comm.EnumMode.Galvanostatic; %define the galvanostatic mode enum
comm.Mode = gstat; %set the connected device in galvanostatic mode

%Set the current range (it is highly recommended to set this manually
%before turning on the cell and setting a current)
% -1 = 100 pA
% 0 = 1 nA
% 1 = 10 nA
% 2 = 100 nA
% 3 = 1 uA
% 4 = 10 uA
% 5 = 100 uA
% 6 = 1 mA
% 7 = 10 mA
% 8 = 100 mA
cr1uA = PalmSens.CurrentRange.FromCRByte(3); %define the 1uA current range
comm.CurrentRange = cr1uA; %set the device in the specified current range

%Set the current
comm.Current = 1; %set the current, note this value is in the current range (i.e. 1 * 1uA)

%another option would be to use comm.Comm.Current = 1;, however, when using
%this the value can be incorrect when switching on a device or after running
%a measurement and NOT setting a current range manually first
%(this is not the case for comm.Comm.ClientConnection.SetCurrent(1), this
%will always return the correct value)

%Turn on the cell
comm.CellOn = true;

%Reading the potential and current
current = comm.Current; %read the current in the specified current range (i.e. current is in 1uA)
potential = comm.Potential; %read the potential in V
