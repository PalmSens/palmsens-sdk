using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using PalmSens.Comm;
using PalmSens.Devices;
using PalmSens.Plottables;
using PalmSens.Core.Simplified.Data;
using PalmSens.Core.Simplified.InternalStorage;
using PalmSens.Techniques;

namespace PalmSens.Core.Simplified
{
    public class PSCommSimple
    {
        /// <summary>
        /// Initializes a new instance of the <see cref="PSCommSimple" /> class.
        /// This class handles is used to perform measurements and control the device manually.
        /// It requires a reference to the platform specific instance of the class,
        /// i.e. PSCommSimpleWinForms, PSCommSimpleWPF or PSCommSimpleXamarin
        /// </summary>
        /// <param name="platform">The reference to the platform specific PSCommSimple class.</param>
        /// <exception cref="System.ArgumentNullException">Platform cannot be null</exception>
        public PSCommSimple(IPlatform platform)
        {
            if (platform == null)
                throw new ArgumentNullException("Platform cannot be null");
            _platform = platform;
        }

        #region Properties
        /// <summary>
        /// The platform specific interface for WinForms, WPF and Xamarin support
        /// </summary>
        private IPlatform _platform = null;

        /// <summary>
        /// The connected device's CommManager
        /// </summary>
        private CommManager _comm;

        /// <summary>
        /// The task completion source used to obtain the active measurement in the Measure and MeasureAsync functions
        /// </summary>
        private TaskCompletionSource<SimpleMeasurement> _taskCompletionSource = null;

        /// <summary>
        /// Gets or sets the CommManager and (un)subscribes the corresponding events.
        /// </summary>
        /// <value>
        /// The CommManager.
        /// </value>
        public CommManager Comm
        {
            get { return _comm; }
            set
            {
                if (_comm != null) //Unsubscribe events
                {
                    _comm.BeginMeasurement -= Comm_BeginMeasurement;
                    _comm.BeginMeasurementAsync -= Comm_BeginMeasurementAsync;
                    _comm.EndMeasurement -= Comm_EndMeasurement;
                    _comm.EndMeasurementAsync -= Comm_EndMeasurementAsync;
                    _comm.BeginReceiveCurve -= Comm_BeginReceiveCurve;
                    _comm.ReceiveStatus -= Comm_ReceiveStatus;
                    _comm.ReceiveStatusAsync -= Comm_ReceiveStatusAsync;
                    _comm.StateChanged -= Comm_StateChanged;
                    _comm.StateChangedAsync -= Comm_StateChangedAsync;
                    _comm.Disconnected -= Comm_Disconnected;
                    _comm.CommErrorOccurred -= Comm_CommErrorOccurred;
                }
                _comm = value;
                if (_comm != null) //Subscribe events
                {
                    _comm.BeginMeasurement += Comm_BeginMeasurement;
                    _comm.BeginMeasurementAsync += Comm_BeginMeasurementAsync;
                    _comm.EndMeasurement += Comm_EndMeasurement;
                    _comm.EndMeasurementAsync += Comm_EndMeasurementAsync;
                    _comm.BeginReceiveCurve += Comm_BeginReceiveCurve;
                    _comm.ReceiveStatus += Comm_ReceiveStatus;
                    _comm.ReceiveStatusAsync += Comm_ReceiveStatusAsync;
                    _comm.StateChanged += Comm_StateChanged;
                    _comm.StateChangedAsync += Comm_StateChangedAsync;
                    _comm.Disconnected += Comm_Disconnected;
                    _comm.CommErrorOccurred += Comm_CommErrorOccurred;
                }
            }
        }

        /// <summary>
        /// Gets a value indicating whether <see cref="PSCommSimple"/> is connected to a device.
        /// </summary>
        /// <value>
        ///   <c>true</c> if connected; otherwise, <c>false</c>.
        /// </value>
        public bool Connected { get { return Comm != null; } }

        /// <summary>
        /// Gets the connected device type.
        /// </summary>
        /// <value>
        /// The connected device type.
        /// </value>
        /// <exception cref="System.NullReferenceException">Not connected to a device.</exception>
        public enumDeviceType ConnectedDevice
        {
            get
            {
                if (_comm == null)
                    throw new NullReferenceException("Not connected to a device.");
                return _comm.DeviceType;
            }
        }

        /// <summary>
        /// Gets the state of the device.
        /// </summary>
        /// <value>
        /// The state of the device.
        /// </value>
        /// <exception cref="System.NullReferenceException">Not connected to a device.</exception>
        public CommManager.DeviceState DeviceState
        {
            get
            {
                if (_comm == null)
                    throw new NullReferenceException("Not connected to a device.");
                return _comm.State;
            }
        }

        /// <summary>
        /// Gets a value indicating whether the connected device's [cell is on].
        /// </summary>
        /// <value>
        ///   <c>true</c> if [cell is on]; otherwise, <c>false</c>.
        /// </value>
        /// <exception cref="System.NullReferenceException">Not connected to a device.</exception>
        public bool IsCellOn
        {
            get
            {
                if (_comm == null)
                    throw new NullReferenceException("Not connected to a device.");
                return _comm.CellOn;
            }
        }

        /// <summary>
        /// Gets the capabilities of the connected device.
        /// </summary>
        /// <value>
        /// The device capabilities.
        /// </value>
        /// <exception cref="System.NullReferenceException">Not connected to a device.</exception>
        public DeviceCapabilities Capabilities
        {
            get
            {
                if (_comm == null)
                    throw new NullReferenceException("Not connected to a device.");
                return _comm.Capabilities;
            }
        }

        /// <summary>
        /// Determines whether [the specified method] is compatible with the device.
        /// </summary>
        /// <param name="method">The method.</param>
        /// <returns>
        ///   <c>true</c> if the method is valid; otherwise, <c>false</c>.
        /// </returns>
        public bool IsValidMethod(Method method)
        {
            bool valid;
            List<string> errors;
            ValidateMethod(method, out valid, out errors);
            return valid;
        }

        /// <summary>
        /// The active measurement
        /// </summary>
        private Measurement _activeMeasurement;

        /// <summary>
        /// Gets or sets the active measurement manages the subscription to its events,
        /// the active simple measurement and the active curves.
        /// </summary>
        /// <value>
        /// The active measurement.
        /// </value>
        private Measurement ActiveMeasurement
        {
            get { return _activeMeasurement; }
            set
            {
                _activeMeasurement = value;
                if (_activeMeasurement != null)
                    _activeSimpleMeasurement = new SimpleMeasurement(_activeMeasurement);
            }
        }

        /// <summary>
        /// The active SimpleMeasurement
        /// </summary>
        private SimpleMeasurement _activeSimpleMeasurement;
        #endregion

        #region Functions
        /// <summary>
        /// Disconnects from the connected device.
        /// </summary>
        /// <exception cref="System.NullReferenceException">Not connected to a device.</exception>
        public void Disconnect()
        {
            try
            {
                _platform.Disconnect(_comm);
                _activeMeasurement = null;
            }
            catch(Exception e)
            {
                throw new Exception("Failed to disconnect.", e);
            }
        }

        /// <summary>
        /// Disconnects from the connected device.
        /// </summary>
        /// <exception cref="System.NullReferenceException">Not connected to a device.</exception>
        public async Task DisconnectAsync()
        {
            try {
                await Task.Run(async () => { //The disconnect function should not be run using CommManager.ClientConnection.RunAsync()
                    await _platform.DisconnectAsync(_comm);
                    _activeMeasurement = null;
                });
            }
            catch (Exception e)
            {
                throw new Exception("Failed to disconnect.", e);
            }
        }

        /// <summary>
        /// Runs a measurement as specified in the method on the connected device.
        /// </summary>
        /// <param name="method">The method containing the measurement parameters.</param>
        /// <param name="muxChannel">The mux channel to measure on.</param>
        /// <returns>
        /// A SimpleMeasurement instance containing all the data related to the measurement.
        /// </returns>
        /// <exception cref="System.NullReferenceException">Not connected to a device.</exception>
        /// <exception cref="System.ArgumentException">Method is incompatible with the connected device.</exception>
        /// <exception cref="System.Exception">Could not start measurement.</exception>
        public SimpleMeasurement Measure(Method method, int muxChannel)
        {
            _activeMeasurement = null;
            if (_comm == null)
                throw new NullReferenceException("Not connected to a device.");

            //Create a copy of the method and update the method with the device's supported current ranges
            Method copy = null;
            Method.CopyMethod(method, ref copy);

            //Determine optimal pgstat mode for EmStat Pico / Sensit series devices
            if (Capabilities is EmStatPicoCapabilities)
            {
                copy.DeterminePGStatMode(Capabilities);
                Capabilities.ActiveSignalTrainConfiguration = copy.PGStatMode; //Set device capabilities to pgstat mode determined/set in method
            }
            copy.Ranging.SupportedCurrentRanges = Capabilities.SupportedRanges; //Update the autoranging depending on the current ranges supported by the connected device

            //Check whether method is compatible with the connected device
            bool isValidMethod;
            List<string> errors;
            ValidateMethod(copy, out isValidMethod, out errors);
            if (!isValidMethod)
                throw new ArgumentException("Method is incompatible with the connected device.");

            //Init task to wait for the active measurement to be initiated by CommManager.Measure()
            _taskCompletionSource = new TaskCompletionSource<SimpleMeasurement>();
            _comm.BeginMeasurement += GetActiveMeasurement;

            //Start the measurement on the connected device, this triggers an event that updates _activeMeasurement
            string error = Run(() => _comm.Measure(copy, muxChannel));
            if (!(string.IsNullOrEmpty(error)))
                throw new Exception($"Could not start measurement: {error}");

            _taskCompletionSource.Task.Wait();

            return _taskCompletionSource.Task.Result;
        }

        /// <summary>
        /// Runs a measurement as specified in the method on the connected device.
        /// </summary>
        /// <param name="method">The method containing the measurement parameters.</param>
        /// <param name="muxChannel">The mux channel to measure on.</param>
        /// <returns>
        /// A SimpleMeasurement instance containing all the data related to the measurement.
        /// </returns>
        /// <exception cref="System.NullReferenceException">Not connected to a device.</exception>
        /// <exception cref="System.ArgumentException">Method is incompatible with the connected device.</exception>
        /// <exception cref="System.Exception">Could not start measurement.</exception>
        public Task<SimpleMeasurement> MeasureAsync(Method method, int muxChannel, TaskBarrier taskBarrier = null)
        {
            //Start the measurement on the connected channel, this triggers an event that updates _activeMeasurement
            return RunAsync(async (CommManager comm) =>
            {
                //Create a copy of the method and update the method with the device's supported current ranges
                Method copy = null;
                Method.CopyMethod(method, ref copy);

                //Determine optimal pgstat mode for EmStat Pico / Sensit series devices
                if (Capabilities is EmStatPicoCapabilities)
                {
                    copy.DeterminePGStatMode(Capabilities);
                    Capabilities.ActiveSignalTrainConfiguration = copy.PGStatMode; //Set device capabilities to pgstat mode determined/set in method
                }
                copy.Ranging.SupportedCurrentRanges = Capabilities.SupportedRanges; //Update the autoranging depending on the current ranges supported by the connected device

                //Check whether method is compatible with the connected channel
                bool isValidMethod;
                List<string> errors;
                ValidateMethod(copy, out isValidMethod, out errors);
                if (!isValidMethod)
                {
                    throw new ArgumentException("Method is incompatible with the connected device.");
                }

                var tcs = new TaskCompletionSource<SimpleMeasurement>();
                AsyncEventHandler<CommManager.BeginMeasurementEventArgsAsync> asyncEventHandler = new AsyncEventHandler<CommManager.BeginMeasurementEventArgsAsync>((object sender, CommManager.BeginMeasurementEventArgsAsync e) =>
                {
                    CommManager commSender = sender as CommManager;
                    ActiveMeasurement = e.NewMeasurement;

                    if (e.NewMeasurement is ImpedimetricMeasurementBase eis)
                        _activeSimpleMeasurement.NewSimpleCurve(PalmSens.Data.DataArrayType.ZRe, PalmSens.Data.DataArrayType.ZIm, "Nyquist", true); //Create a nyquist curve by default

                    tcs.SetResult(_activeSimpleMeasurement);
                    return Task.CompletedTask;
                });
                comm.BeginMeasurementAsync += asyncEventHandler;

                string errorString = await comm.MeasureAsync(copy, muxChannel, taskBarrier);
                if (!(string.IsNullOrEmpty(errorString)))
                {
                    throw new Exception($"Could not start measurement: {errorString}");
                }

                SimpleMeasurement result = await tcs.Task;
                comm.BeginMeasurementAsync -= asyncEventHandler;

                return result;
            });
        }

        /// <summary>
        /// Gets the active measurement when the BeginMeasurement event is raised.
        /// </summary>
        /// <param name="sender">The sender.</param>
        /// <param name="newMeasurement">The new measurement.</param>
        /// <exception cref="NotImplementedException"></exception>
        private void GetActiveMeasurement(object sender, ActiveMeasurement m)
        {
            _comm.BeginMeasurement -= GetActiveMeasurement;
            ActiveMeasurement = m;
            ImpedimetricMethod eis = ActiveMeasurement.Method as ImpedimetricMethod;
            if (eis != null)
                _activeSimpleMeasurement.NewSimpleCurve(PalmSens.Data.DataArrayType.ZRe, PalmSens.Data.DataArrayType.ZIm, "Nyquist", true); //Create a nyquist curve by default
            _taskCompletionSource.SetResult(_activeSimpleMeasurement);
        }

        /// <summary>
        /// Runs a measurement as specified in the method on the connected device.
        /// </summary>
        /// <param name="method">The method containing the measurement parameters.</param>
        /// <returns>A SimpleMeasurement instance containing all the data related to the measurement.</returns>
        public SimpleMeasurement Measure(Method method)
        {
            if (method.MuxMethod == MuxMethod.Sequentially)
                return Measure(method, method.GetNextSelectedMuxChannel(-1));
            else
                return Measure(method, -1);
        }

        /// <summary>
        /// Runs a measurement as specified in the method on the connected device.
        /// </summary>
        /// <param name="method">The method containing the measurement parameters.</param>
        /// <returns>A SimpleMeasurement instance containing all the data related to the measurement.</returns>
        public async Task<SimpleMeasurement> MeasureAsync(Method method, TaskBarrier taskBarrier = null)
        {
            if (method.MuxMethod == MuxMethod.Sequentially)
                return await MeasureAsync(method, method.GetNextSelectedMuxChannel(-1), taskBarrier);
            else
                return await MeasureAsync(method, -1, taskBarrier);
        }

        /// <summary>
        /// Aborts the active measurement.
        /// </summary>
        /// <exception cref="System.NullReferenceException">Not connected to a device.</exception>
        /// <exception cref="System.Exception">Device is not measuring.</exception>
        public void AbortMeasurement()
        {
            Run(() =>
            {
                if (_comm.ActiveMeasurement == null)
                    throw new Exception("Device is not measuring.");
                _comm.Abort();
            });
        }

        /// <summary>
        /// Aborts the current active measurement.
        /// </summary>
        /// <exception cref="System.NullReferenceException">Not connected to a device.</exception>
        /// <exception cref="System.Exception">The device is not currently performing measurement</exception>
        public Task AbortMeasurementAsync()
        {
            return RunAsync((CommManager comm) => {
                if (comm.ActiveMeasurement == null)
                    throw new Exception("Device is not measuring.");
                return comm.AbortAsync();
            });
        }

        /// <summary>
        /// Turns the cell on.
        /// </summary>
        /// <exception cref="System.NullReferenceException">Not connected to a device</exception>
        /// <exception cref="System.Exception">Device must be in idle mode for manual control</exception>
        public void TurnCellOn()
        {
            Run(() => {
                if (_comm.State != CommManager.DeviceState.Idle)
                    throw new Exception("Device must be in idle mode for manual control");
                if (_comm.CellOn)
                    return;
                _comm.CellOn = true; });
        }

        /// <summary>
        /// Turns the cell on.
        /// </summary>
        /// <exception cref="System.NullReferenceException">Not connected to a device</exception>
        /// <exception cref="System.Exception">Device must be in idle mode for manual control</exception>
        public Task TurnCellOnAsync()
        {
            return RunAsync((CommManager comm) => {
                if (comm.State != CommManager.DeviceState.Idle)
                    throw new Exception("Device must be in idle mode for manual control");
                if (comm.CellOn)
                    return Task.CompletedTask;
                return comm.SetCellOnAsync(true);
            });
        }

        /// <summary>
        /// Turns the cell off.
        /// </summary>
        /// <exception cref="System.NullReferenceException">Not connected to a device</exception>
        /// <exception cref="System.Exception">Device must be in idle mode for manual control</exception>
        public void TurnCellOff()
        {
            Run(() => {
                if (_comm.State != CommManager.DeviceState.Idle)
                    throw new Exception("Device must be in idle mode for manual control");
                if (!_comm.CellOn)
                    return;
                _comm.CellOn = false;
            });
        }

        /// <summary>
        /// Turns the cell off.
        /// </summary>
        /// <exception cref="System.NullReferenceException">Not connected to a device</exception>
        /// <exception cref="System.Exception">Device must be in idle mode for manual control</exception>
        public Task TurnCellOffAsync()
        {
            return RunAsync((CommManager comm) => {
                if (comm.State != CommManager.DeviceState.Idle)
                    throw new Exception("Device must be in idle mode for manual control");
                if (!comm.CellOn)
                    return Task.CompletedTask;
                return comm.SetCellOnAsync(false);
            });
        }

        /// <summary>
        /// Sets the cell potential.
        /// </summary>
        /// <param name="potential">The potential.</param>
        /// <exception cref="System.NullReferenceException">Not connected to a device</exception>
        /// <exception cref="System.Exception">Device must be in idle mode for manual control</exception>
        public void SetCellPotential(float potential)
        {
            Run(() => {
                if (_comm.State != CommManager.DeviceState.Idle)
                    throw new Exception("Device must be in idle mode for manual control");
                _comm.Potential = potential;
            });
        }

        /// <summary>
        /// Sets the cell potential.
        /// </summary>
        /// <param name="potential">The potential.</param>
        /// <exception cref="System.NullReferenceException">Not connected to a device</exception>
        /// <exception cref="System.Exception">Device must be in idle mode for manual control</exception>
        public Task SetCellPotentialAsync(float potential)
        {
            return RunAsync((CommManager comm) => {
                if (comm.State != CommManager.DeviceState.Idle)
                    throw new Exception("Device must be in idle mode for manual control");
                return comm.SetPotentialAsync(potential);
            });
        }

        /// <summary>
        /// Reads the cell potential.
        /// </summary>
        /// <returns></returns>
        /// <exception cref="NullReferenceException">Not connected to a device</exception>
        /// <exception cref="Exception">Device must be in idle mode for manual control</exception>
        public float ReadCellPotential()
        {
            return Run<float>(() => {
                if (_comm.State != CommManager.DeviceState.Idle)
                    throw new Exception("Device must be in idle mode for manual control");
                return _comm.Potential;
            });
        }

        /// <summary>
        /// Reads the cell potential.
        /// </summary>
        /// <returns></returns>
        /// <exception cref="NullReferenceException">Not connected to a device</exception>
        /// <exception cref="Exception">Device must be in idle mode for manual control</exception>
        public Task<float> ReadCellPotentialAsync()
        {
            return RunAsync<float>((CommManager comm) => {
                if (comm.State != CommManager.DeviceState.Idle)
                    throw new Exception("Device must be in idle mode for manual control");
                return comm.GetPotentialAsync();
            });
        }

        /// <summary>
        /// Sets the cell current.
        /// </summary>
        /// <param name="current">The current.</param>
        /// <exception cref="System.NullReferenceException">Not connected to a device</exception>
        /// <exception cref="System.Exception">Device must be in idle mode for manual control</exception>
        public void SetCellCurrent(float current)
        {
            Run(() =>
            {
                if (_comm.State != CommManager.DeviceState.Idle)
                    throw new Exception("Device must be in idle mode for manual control");
                if (!Capabilities.IsGalvanostat)
                    throw new Exception("Device does not support Galvanostat mode");
                _comm.Current = current;
            });
        }

        /// <summary>
        /// Sets the cell current.
        /// </summary>
        /// <param name="current">The current.</param>
        /// <exception cref="System.NullReferenceException">Not connected to a device</exception>
        /// <exception cref="System.Exception">Device must be in idle mode for manual control</exception>
        public Task SetCellCurrentAsync(float current)
        {
            return RunAsync((CommManager comm) => {
                if (comm.State != CommManager.DeviceState.Idle)
                    throw new Exception("Device must be in idle mode for manual control");
                if (!comm.Capabilities.IsGalvanostat)
                    throw new Exception("Device does not support Galvanostat mode");
                return comm.SetCurrentAsync(current);
            });
        }

        /// <summary>
        /// Reads the cell current.
        /// </summary>
        /// <returns></returns>
        /// <exception cref="NullReferenceException">Not connected to a device</exception>
        /// <exception cref="Exception">Device must be in idle mode for manual control</exception>
        public float ReadCellCurrent()
        {
            return Run<float>(() => {
                if (_comm.State != CommManager.DeviceState.Idle)
                    throw new Exception("Device must be in idle mode for manual control");
                return _comm.Current;
            });
        }

        /// <summary>
        /// Reads the cell current.
        /// </summary>
        /// <returns></returns>
        /// <exception cref="NullReferenceException">Not connected to a device</exception>
        /// <exception cref="Exception">Device must be in idle mode for manual control</exception>
        public Task<float> ReadCellCurrentAsync()
        {
            return RunAsync<float>((CommManager comm) => {
                if (comm.State != CommManager.DeviceState.Idle)
                    throw new Exception("Device must be in idle mode for manual control");
                return comm.GetCurrentAsync();
            });
        }

        /// <summary>
        /// Sets the current range.
        /// </summary>
        /// <param name="currentRange">The current range.</param>
        /// <exception cref="System.NullReferenceException">Not connected to a device</exception>
        /// <exception cref="System.Exception">Device must be in idle mode for manual control</exception>
        public void SetCurrentRange(CurrentRange currentRange)
        {
            Run(() => {
                if (_comm.State != CommManager.DeviceState.Idle)
                    throw new Exception("Device must be in idle mode for manual control");
                _comm.CurrentRange = currentRange;
            });
        }

        /// <summary>
        /// Sets the current range.
        /// </summary>
        /// <param name="currentRange">The current range.</param>
        /// <exception cref="System.NullReferenceException">Not connected to a device</exception>
        /// <exception cref="System.Exception">Device must be in idle mode for manual control</exception>
        public Task SetCurrentRangeAsync(CurrentRange currentRange)
        {
            return RunAsync((CommManager comm) => {
                if (comm.State != CommManager.DeviceState.Idle)
                    throw new Exception("Device must be in idle mode for manual control");
                return comm.SetCurrentRangeAsync(currentRange);
            });
        }

        /// <summary>
        /// Runs a MethodSCRIPT on the device, ignoring any output returned by the script.
        /// </summary>
        /// <param name="script">The MethodSCRIPT.</param>
        /// <param name="timeout">The timeout.</param>
        /// <exception cref="NullReferenceException">Not connected to a device</exception>
        /// <exception cref="Exception">Device must be in idle mode to run a MethodSCRIPT</exception>
        public void StartSetterMethodScript(string script, int timeout = 500)
        {
            Run(() =>
            {
                if (_comm.State != CommManager.DeviceState.Idle)
                    throw new Exception("Device must be in idle mode to run a MethodSCRIPT");
                if (Comm.ClientConnection is ClientConnectionMS connMS)
                    connMS.StartSetterMethodScript(script, timeout);
                else
                    throw new Exception("Device does not support MethodSCRIPT");
            });
        }

        /// <summary>
        /// Runs a MethodSCRIPT on the device, ignoring any output returned by the script.
        /// </summary>
        /// <param name="script">The MethodSCRIPT.</param>
        /// <param name="timeout">The timeout.</param>
        /// <exception cref="NullReferenceException">Not connected to a device</exception>
        /// <exception cref="Exception">Device must be in idle mode to run a MethodSCRIPT</exception>
        public Task StartSetterMethodScriptAsync(string script, int timeout = 500)
        {
            return RunAsync((CommManager comm) => {
                if (comm.State != CommManager.DeviceState.Idle)
                    throw new Exception("Device must be in idle mode to run a MethodSCRIPT");
                if (comm.ClientConnection is ClientConnectionMS connMS)
                    return connMS.StartSetterMethodScriptAsync(script, timeout);
                else
                    throw new Exception("Device does not support MethodSCRIPT");
            });
        }

        /// <summary>
        /// Runs a MethodSCRIPT on the device and returns the output.
        /// A timeout exception will be thrown if no new data is received for longer than the timeout.
        /// A timeout exception will be thrown for scripts that do not return anything.
        /// </summary>
        /// <param name="script">The MethodSCRIPT.</param>
        /// <param name="timeout">The timeout.</param>
        /// <returns></returns>
        public string StartGetterMethodScript(string script, int timeout = 2500)
        {
            return Run(() =>
            {
                if (_comm.State != CommManager.DeviceState.Idle)
                    throw new Exception("Device must be in idle mode to run a MethodSCRIPT");
                if (Comm.ClientConnection is ClientConnectionMS connMS)
                    return connMS.StartGetterMethodScript(script, timeout);
                else
                    throw new Exception("Device does not support MethodSCRIPT");
            });
        }

        /// <summary>
        /// Runs a MethodSCRIPT on the device and returns the output.
        /// A timeout exception will be thrown if no new data is received for longer than the timeout.
        /// A timeout exception will be thrown for scripts that do not return anything.
        /// <param name="script">The MethodSCRIPT.</param>
        /// <param name="timeout">The timeout.</param>
        /// <returns></returns>
        public Task<string> StartGetterMethodScriptAsync(string script, int timeout = 2500)
        {
            return RunAsync((CommManager comm) => {
                if (comm.State != CommManager.DeviceState.Idle)
                    throw new Exception("Device must be in idle mode to run a MethodSCRIPT");
                if (comm.ClientConnection is ClientConnectionMS connMS)
                    return connMS.StartGetterMethodScriptAsync(script, timeout);
                else
                    throw new Exception("Device does not support MethodSCRIPT");
            });
        }

        /// <summary>
        /// Reads the specified digital line(s) state(s).
        /// Which lines to read from are specified in a bitmask.
        /// Bit 0 is for GPIO0, bit 1 for GPIO1, etc. Bits that are high correspond with a high output signal
        /// </summary>
        /// <param name="bitMask">A bitmask specifying which digital lines to read (0 = ignore, 1 = read).</param>
        /// <returns>Bitmask that represents the specified lines output signal (0 = low, 1 = high).</returns>
        public uint ReadDigitalLine(byte bitMask)
        {
            return Run(() =>
            {
                if (_comm.State != CommManager.DeviceState.Idle)
                    throw new Exception("Device must be in idle mode for manual control");
                return Comm.ClientConnection.ReadDigitalLine(bitMask);
            });
        }

        /// <summary>
        /// Reads the specified digital line(s) state(s).
        /// Which lines to read from are specified in a bitmask.
        /// Bit 0 is for GPIO0, bit 1 for GPIO1, etc. Bits that are high correspond with a high output signal
        /// </summary>
        /// <param name="bitMask">A bitmask specifying which digital lines to read (0 = ignore, 1 = read).</param>
        /// <returns>Bitmask that represents the specified lines output signal (0 = low, 1 = high).</returns>
        public Task<uint> ReadDigitalLineAsync(byte bitMask)
        {
            return RunAsync((CommManager comm) => {
                if (comm.State != CommManager.DeviceState.Idle)
                    throw new Exception("Device must be in idle mode for manual control");
                return comm.ClientConnection.ReadDigitalLineAsync(bitMask);
            });
        }

        /// <summary>
        /// Sets the digital lines output signal high or low.
        /// The output signal for the digital lines are defined in a bitmask.
        /// Bit 0 is for GPIO0, bit 1 for GPIO1, etc. Bits that are high correspond with a high output signal
        /// </summary>
        /// <param name="bitMask">A bitmask specifying the output of the digital lines (0 = low, 1 = high).</param>
        public void SetDigitalOutput(int bitMask)
        {
            Run(() =>
            {
                if (_comm.State != CommManager.DeviceState.Idle)
                    throw new Exception("Device must be in idle mode for manual control");
                Comm.ClientConnection.SetDigitalOutput(bitMask);
            });
        }

        /// <summary>
        /// Sets the digital lines output signal high or low.
        /// The output signal for the digital lines are defined in a bitmask.
        /// Bit 0 is for GPIO0, bit 1 for GPIO1, etc. Bits that are high correspond with a high output signal
        /// </summary>
        /// <param name="bitMask">A bitmask specifying the output of the digital lines (0 = low, 1 = high).</param>
        public Task SetDigitalOutputAsync(int bitMask)
        {
            return RunAsync((CommManager comm) => {
                if (comm.State != CommManager.DeviceState.Idle)
                    throw new Exception("Device must be in idle mode for manual control");
                return comm.ClientConnection.SetDigitalOutputAsync(bitMask);
            });
        }

        /// <summary>
        /// Sets the specified digital lines to input/output and set the output signal of the lines set to output
        /// The output signal for the digital lines are defined in a bitmask.
        /// Bit 0 is for GPIO0, bit 1 for GPIO1, etc. Bits that are high correspond with a high output signal
        /// </summary>
        /// <param name="bitMask">A bitmask specifying the output signal of the digital lines (0 = low, 1 = high).</param>
        /// <param name="configGPIO">A bitmask specifying the the mode of digital lines (0 = input, 1 = output).</param>
        public void SetDigitalOutput(int bitMask, int configGPIO)
        {
            Run(() =>
            {
                if (_comm.State != CommManager.DeviceState.Idle)
                    throw new Exception("Device must be in idle mode for manual control");
                if (Comm.ClientConnection is ClientConnectionMS connMS)
                    connMS.SetDigitalOutput(bitMask, configGPIO);
                else
                    throw new NotSupportedException("The connection does not support configuring GPIO.");
            });
        }

        /// <summary>
        /// Sets the specified digital lines to input/output and set the output signal of the lines set to output
        /// The output signal for the digital lines are defined in a bitmask.
        /// Bit 0 is for GPIO0, bit 1 for GPIO1, etc. Bits that are high correspond with a high output signal
        /// </summary>
        /// <param name="bitMask">A bitmask specifying the output signal of the digital lines (0 = low, 1 = high).</param>
        /// <param name="configGPIO">A bitmask specifying the the mode of digital lines (0 = input, 1 = output).</param>
        public Task SetDigitalOutputAsync(int bitMask, int configGPIO)
        {
            return RunAsync((CommManager comm) => {
                if (comm.State != CommManager.DeviceState.Idle)
                    throw new Exception("Device must be in idle mode for manual control");
                if (comm.ClientConnection is ClientConnectionMS connMS)
                    return connMS.SetDigitalOutputAsync(bitMask, configGPIO);
                else
                    throw new NotSupportedException("The connection does not support configuring GPIO.");
            });
        }

        /// <summary>
        /// Validates whether the specified method is compatible with the capabilities of the connected device.
        /// </summary>
        /// <param name="method">The method containing the measurement parameters.</param>
        /// <param name="isValidMethod">if set to <c>true</c> [is valid method].</param>
        /// <param name="errors">The errors.</param>
        /// <exception cref="System.NullReferenceException">Not connected to a device.</exception>
        /// <exception cref="System.ArgumentNullException">The specified method cannot be null.</exception>
        public void ValidateMethod(Method method, out bool isValidMethod, out List<string> errors)
        {
            if (_comm == null)
                throw new NullReferenceException("Not connected to a device.");
            if (method == null)
                throw new ArgumentNullException("The specified method cannot be null.");
            errors = new List<string>();

            //Get a list of method compatability warnings and errors for the connected device
            List<MethodError> methodErrors = method.Validate(_comm.Capabilities);

            //Check wheteher the device can perform the measurement described in the method
            isValidMethod = !(methodErrors.Where(c => c.IsFatal == true).Any());

            //Build a list of the warnings and errors
            foreach (MethodError error in methodErrors)
                errors.Add($"{error.Parameter.ToString()}: {error.Message}");
        }

        /// <summary>
        /// Get an internal storage handler that will read the current connected device stored files. This is only for devices that have internal storage.
        /// </summary>
        /// <exception cref="InvalidOperationException">This exception is thrown when the device is not connected or if the device does not support storage.</exception>
        /// <returns>A new instance of the internal storage handler for the current connection.</returns>
        public IInternalStorageBrowser GetInternalStorageBrowser()
        {
            if (!Connected)
                throw new InvalidOperationException("There is no device currently connected. Please connect to a device.");

            if (!Comm.Capabilities.SupportsStorage)
                throw new InvalidOperationException($"The connected device '{Comm.DeviceType}' does not support internal storage.");

            return new InternalStorageBrowser(Comm.ClientConnection);
        }

        /// <summary>
        /// Adds the active curve and its respective to the collection and subscribes to its events.
        /// </summary>
        /// <param name="activeCurve">The active curve.</param>
        private SimpleCurve SetActiveSimpleCurve(Curve activeCurve)
        {
            if (activeCurve == null)
                return null;

            SimpleCurve activeSimpleCurve = _activeSimpleMeasurement.SimpleCurveCollection.FirstOrDefault(sc => sc.Curve == activeCurve);

            if (activeSimpleCurve == null)
            {
                activeSimpleCurve = new SimpleCurve(activeCurve, _activeSimpleMeasurement);
                _activeSimpleMeasurement.AddSimpleCurve(activeSimpleCurve);
            }

            return activeSimpleCurve;
        }

        /// <summary>
        /// Safely run an Action delegate on the clientconnection.
        /// </summary>
        /// <param name="action">The action.</param>
        private void Run(Action action)
        {
            if (_comm == null)
                throw new NullReferenceException("Not connected to a device.");
            if (TaskScheduler.Current == _comm.ClientConnection.TaskScheduler)
                throw new Exception("The device can only execute one command at a time. Dead lock detected");
            _comm.ClientConnection.Semaphore.Wait();
            try { action(); }
            finally { _comm.ClientConnection.Semaphore.Release(); }
        }

        /// <summary>
        /// Safely run a Function delegate on the clientconnection.
        /// </summary>
        /// <typeparam name="T"></typeparam>
        /// <param name="func">The function.</param>
        /// <returns></returns>
        private T Run<T>(Func<T> func)
        {
            if (_comm == null)
                throw new NullReferenceException("Not connected to a device.");
            if (TaskScheduler.Current == _comm.ClientConnection.TaskScheduler)
                throw new Exception("The device can only execute one command at a time. Dead lock detected");
            _comm.ClientConnection.Semaphore.Wait();
            try { return func(); }
            finally { _comm.ClientConnection.Semaphore.Release(); }
        }

        /// <summary>
        /// Runs an async Func delegate asynchronously on the clientconnections taskscheduler.
        /// </summary>
        /// <param name="func">The action.</param>
        /// <param name="comm">The connection to run the delegate on.</param>
        /// <returns></returns>
        private async Task RunAsync(Func<CommManager, Task> func)
        {
            await new SynchronizationContextRemover();

            if (!Connected)
            {
                throw new NullReferenceException("Not connected to a device.");
            }

            await Comm.ClientConnection.RunAsync(() => func(Comm));
        }

        /// <summary>
        /// Runs an async Func delegate asynchronously on the clientconnections taskscheduler.
        /// </summary>
        /// <param name="func">The action.</param>
        /// <param name="comm">The connection to run the delegate on.</param>
        /// <returns></returns>
        private async Task<T> RunAsync<T>(Func<CommManager, Task<T>> func)
        {
            await new SynchronizationContextRemover();

            if (!Connected)
            {
                throw new NullReferenceException("Not connected to a device.");
            }

            return await Comm.ClientConnection.RunAsync(() => func(Comm));
        }

        #endregion

        #region events
        /// <summary>
        /// Occurs when a device status package is received, these packages are not sent during a measurement.
        /// </summary>
        public event StatusEventHandler ReceiveStatus;

        /// <summary>
        /// Casts ReceiveStatus events coming from a different thread to the UI thread when necessary.
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="StatusEventArgs" /> instance containing the device status.</param>
        /// <exception cref="System.NullReferenceException">Platform not set.</exception>
        private void Comm_ReceiveStatus(object sender, StatusEventArgs e)
        {
            if (_platform == null)
                throw new NullReferenceException("Platform not set.");
            if (_platform.InvokeIfRequired(new StatusEventHandler(Comm_ReceiveStatus), sender, e)) //Recast event to UI thread when necessary
                return;
            ReceiveStatus?.Invoke(this, e);
        }

        /// <summary>
        /// Casts ReceiveStatus events coming from a different thread to the UI thread when necessary.
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="StatusEventArgs" /> instance containing the device status.</param>
        /// <exception cref="System.NullReferenceException">Platform not set.</exception>
        private Task Comm_ReceiveStatusAsync(object sender, StatusEventArgs e)
        {
            Comm_ReceiveStatus(sender, e);
            return Task.CompletedTask;
        }

        /// <summary>
        /// Occurs at the start of a new measurement.
        /// </summary>
        public event EventHandler MeasurementStarted;

        /// <summary>
        /// Sets the ActiveMeasurement at the start of a measurement and casts BeginMeasurement events coming from a different thread to the UI thread when necessary.
        /// </summary>
        /// <param name="sender">The sender.</param>
        /// <param name="newMeasurement">The new measurement.</param>
        /// <exception cref="System.NullReferenceException">Platform not set.</exception>
        private void Comm_BeginMeasurement(object sender, ActiveMeasurement newMeasurement)
        {
            if (_platform == null)
                throw new NullReferenceException("Platform not set.");
            if (_platform.InvokeIfRequired(new CommManager.BeginMeasurementEventHandler(Comm_BeginMeasurement), sender, newMeasurement)) //Recast event to UI thread when necessary
                return;
            MeasurementStarted?.Invoke(this, EventArgs.Empty);
        }

        /// <summary>
        /// Sets the ActiveMeasurement at the start of a measurement and casts BeginMeasurement events coming from a different thread to the UI thread when necessary.
        /// </summary>
        /// <param name="sender">The sender.</param>
        /// <param name="e">The new measurement.</param>
        /// <exception cref="System.NullReferenceException">Platform not set.</exception>
        private Task Comm_BeginMeasurementAsync(object sender, CommManager.BeginMeasurementEventArgsAsync e)
        {
            Comm_BeginMeasurement(sender, e.NewMeasurement);
            return Task.CompletedTask;
        }

        /// <summary>
        /// Occurs when a measurement has ended.
        /// </summary>
        public event EventHandler<Exception> MeasurementEnded;

        /// <summary>
        /// Sets the ActiveMeasurement to null at the end of the measurement and casts EndMeasurement events coming from a different thread to the UI thread when necessary.
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="EventArgs" /> instance containing the event data.</param>
        /// <exception cref="System.NullReferenceException">Platform not set.</exception>
        private void Comm_EndMeasurement(object _, EventArgs e)
        {
            if (_platform == null)
                throw new NullReferenceException("Platform not set.");

            ActiveMeasurement = null;

            if (!_platform.InvokeIfRequired(
                (EventHandler<Exception>)((sender, ex) =>
                {
                    MeasurementEnded?.Invoke(sender, ex);
                }), this, _commErrorException)) //Recast event to UI thread when necessary
            {
                MeasurementEnded?.Invoke(this, _commErrorException);
            }
        }

        /// <summary>
        /// Sets the ActiveMeasurement to null at the end of the measurement and casts EndMeasurement events coming from a different thread to the UI thread when necessary.
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="EventArgs" /> instance containing the event data.</param>
        /// <exception cref="System.NullReferenceException">Platform not set.</exception>
        private Task Comm_EndMeasurementAsync(object sender, CommManager.EndMeasurementAsyncEventArgs e)
        {
            Comm_EndMeasurement(sender, e);
            return Task.CompletedTask;
        }

        /// <summary>
        /// Adds the active Curve to the active SimpleMeasurement and casts BeginReceiveCurve events coming from a different thread to the UI thread when necessary.
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="CurveEventArgs"/> instance containing the event data.</param>
        /// <exception cref="System.NullReferenceException">Platform not set.</exception>
        private void Comm_BeginReceiveCurve(object _, CurveEventArgs e)
        {
            if (_platform == null)
                throw new NullReferenceException("Platform not set.");

            var activeSimpleCurve = SetActiveSimpleCurve(e.GetCurve());

            if (!_platform.InvokeIfRequired(
                (SimpleCurveStartReceivingDataHandler) ((sender, simpleCuve) =>
                {
                    if (simpleCuve != null) SimpleCurveStartReceivingData?.Invoke(sender, simpleCuve);
                }), this, activeSimpleCurve)) //Recast event to UI thread when necessary
            {
                if (activeSimpleCurve != null) SimpleCurveStartReceivingData?.Invoke(this, activeSimpleCurve);
            }
        }

        /// <summary>
        /// EventHandler delegate with a reference to a SimpleCurve
        /// </summary>
        /// <param name="sender">The sender.</param>
        /// <param name="activeSimpleCurve">The active simple curve.</param>
        public delegate void SimpleCurveStartReceivingDataHandler(Object sender, SimpleCurve activeSimpleCurve);

        /// <summary>
        /// Occurs when a new [SimpleCurve starts receiving data].
        /// </summary>
        public event SimpleCurveStartReceivingDataHandler SimpleCurveStartReceivingData;

        /// <summary>
        /// Occurs when the devive's [state changed].
        /// </summary>
        public event CommManager.StatusChangedEventHandler StateChanged;

        /// <summary>
        /// Casts StateChanged events coming from a different thread to the UI thread when necessary.
        /// </summary>
        /// <param name="sender">The sender.</param>
        /// <param name="CurrentState">State of the current.</param>
        /// <exception cref="System.NullReferenceException">Platform not set.</exception>
        private void Comm_StateChanged(object sender, CommManager.DeviceState CurrentState)
        {
            if (_platform == null)
                throw new NullReferenceException("Platform not set.");
            if (_platform.InvokeIfRequired(new CommManager.StatusChangedEventHandler(Comm_StateChanged), sender, CurrentState)) //Recast event to UI thread when necessary
                return;
            StateChanged?.Invoke(this, CurrentState);
        }

        /// <summary>
        /// Casts StateChanged events coming from a different thread to the UI thread when necessary.
        /// </summary>
        /// <param name="sender">The sender.</param>
        /// <param name="e">State of the current.</param>
        /// <exception cref="System.NullReferenceException">Platform not set.</exception>
        private Task Comm_StateChangedAsync(object sender, CommManager.StateChangedAsyncEventArgs e)
        {
            Comm_StateChanged(sender, e.State);
            return Task.CompletedTask;
        }

        /// <summary>
        /// Occurs when a device is [disconnected].
        /// </summary>
        public event DisconnectedEventHandler Disconnected;

        /// <summary>
        /// Raises the Disconnected event.
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="EventArgs"/> instance containing the event data.</param>
        /// <exception cref="System.NotImplementedException"></exception>
        private void Comm_Disconnected(object _, EventArgs e)
        {
            if (_platform == null)
                throw new NullReferenceException("Platform not set.");

            _comm?.Dispose();
            Comm = null;
            var ex = _commErrorException;
            _commErrorException = null;

            if (!_platform.InvokeIfRequired(
                (DisconnectedEventHandler) ((sender, exception) =>
                {
                    Disconnected?.Invoke(sender, exception);
                }), this, ex)) //Recast event to UI thread when necessary
            {
                Disconnected?.Invoke(this, ex);
            }
        }

        /// <summary>
        /// The latest comm error exception, this is used for the disconnected event and is set back to null directly after it is raised
        /// </summary>
        private Exception _commErrorException = null;

        /// <summary>
        /// Comms the comm error occorred.
        /// </summary>
        /// <param name="exception">The exception.</param>
        /// <exception cref="System.NotImplementedException"></exception>
        private void Comm_CommErrorOccurred(object sender, Exception exception)
        {
            _commErrorException = exception;

            if (ActiveMeasurement != null)
            {
                Comm_EndMeasurement(sender, EventArgs.Empty);
            }
        }
#endregion

        public void Dispose()
        {
            if(Connected)
                _comm.Dispose();
            _comm = null;
            ActiveMeasurement = null;
            Disconnected = null;
            MeasurementEnded = null;
            MeasurementStarted = null;
            ReceiveStatus = null;
            StateChanged = null;
            SimpleCurveStartReceivingData = null;
        }
    }

    /// <summary>
    /// Delegate for the Disconnected event
    /// </summary>
    /// <param name="sender">The sender.</param>
    /// <param name="CommErrorException">The comm error exception, this is only available when device was disconnected due to a communication error.</param>
    public delegate void DisconnectedEventHandler(Object sender, Exception CommErrorException);
}
