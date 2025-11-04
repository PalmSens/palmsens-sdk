using PalmSens.Comm;
using PalmSens.Core.Simplified.Data;
using PalmSens.Core.Simplified.InternalStorage;
using PalmSens.Devices;
using PalmSens.Plottables;
using PalmSens.Techniques;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Channels;
using System.Threading.Tasks;
using static PalmSens.Comm.CommManager;

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
        public PSCommSimple(IPlatform platform, IPlatformInvoker platformInvoker)
        {
            if (platform == null)
                throw new ArgumentNullException("Platform cannot be null");
            _platform = platform;
            _platformInvoker = platformInvoker;
        }

        #region Properties
        /// <summary>
        /// The platform specific interface implementing the layers to communicate with the instrument
        /// </summary>
        private IPlatform _platform = null;

        /// <summary>
        /// The platform specific interface implementing the dispatch of events to the UI thread
        /// </summary>
        private IPlatformInvoker _platformInvoker = null;

        /// <summary>
        /// Returns an array of connected devices.
        /// </summary>
        /// <value>
        /// The connected devices.
        /// </value>
        public Task<IReadOnlyList<Device>> GetAvailableDevices() => _platform.GetAvailableDevices();

        /// <summary>
        /// The connected device's CommManager
        /// </summary>
        private CommManager _comm;

        /// <summary>
        /// The task completion source used to obtain the active measurement in the Measure and StartMeasurementAsync functions
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
                    _comm.BeginMeasurementAsync -= Comm_BeginMeasurement;
                    _comm.EndMeasurementAsync -= Comm_EndMeasurement;
                    _comm.BeginReceiveCurve -= Comm_BeginReceiveCurve;
                    _comm.ReceiveStatusAsync -= Comm_ReceiveStatus;
                    _comm.StateChangedAsync -= Comm_StateChanged;
                    _comm.Disconnected -= Comm_Disconnected;
                    _comm.CommErrorOccurred -= Comm_CommErrorOccurred;
                }
                _comm = value;
                if (_comm != null) //Subscribe events
                {
                    _comm.BeginMeasurementAsync += Comm_BeginMeasurement;
                    _comm.EndMeasurementAsync += Comm_EndMeasurement;
                    _comm.BeginReceiveCurve += Comm_BeginReceiveCurve;
                    _comm.ReceiveStatusAsync += Comm_ReceiveStatus;
                    _comm.StateChangedAsync += Comm_StateChanged;
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
        /// Connects to the device with the highest priority.
        /// </summary>
        public async Task Connect()
        {
            await Connect((await GetAvailableDevices())[0]);
        }

        /// <summary>
        /// Connects to the specified device.
        /// </summary>
        /// <param name="device">The device.</param>
        public async Task Connect(Device device)
        {
            Comm = await _platform.Connect(device);
        }

        /// <summary>
        /// Disconnects from the connected device.
        /// </summary>
        /// <exception cref="System.NullReferenceException">Not connected to a device.</exception>
        public async Task Disconnect()
        {
            try
            {
                await _platform.Disconnect(_comm);
                _activeMeasurement = null;
            }
            catch (Exception e)
            {
                throw new Exception("Failed to disconnect.", e);
            }
        }

        /// <summary>
        /// Starts a measurement as specified in the method on the connected device.
        /// </summary>
        /// <param name="method">The method containing the measurement parameters.</param>
        /// <param name="muxChannel">The mux channel to measure on.</param>
        /// <returns>
        /// A SimpleMeasurement instance containing all the data related to the measurement.
        /// </returns>
        /// <exception cref="System.NullReferenceException">Not connected to a device.</exception>
        /// <exception cref="System.ArgumentException">Method is incompatible with the connected device.</exception>
        /// <exception cref="System.Exception">Could not start measurement.</exception>
        public async Task<SimpleMeasurement> StartMeasurement(Method method, int muxChannel, TaskBarrier taskBarrier = null)
        {
            var tcs = new TaskCompletionSource<SimpleMeasurement>();
            AsyncEventHandler<CommManager.BeginMeasurementEventArgsAsync> asyncEventHandler = async (sender, e) =>
            {
                CommManager commSender = sender as CommManager;
                ActiveMeasurement = e.NewMeasurement;

                if (e.NewMeasurement is ImpedimetricMeasurementBase || e.NewMeasurement is ImpedimetricMeasBaseMS)
                    _activeSimpleMeasurement.NewSimpleCurve(PalmSens.Data.DataArrayType.ZRe, PalmSens.Data.DataArrayType.ZIm, "Nyquist", true); //Create a nyquist curve by default

                tcs.SetResult(_activeSimpleMeasurement);
            };

            CommManager.EventHandlerCommErrorOccurred asyncEventHandlerCommError = (sender, exception) =>
            {
                tcs.SetException(exception);
            };

            try
            {
                try
                {
                    //Start the measurement on the connected channel, this triggers an event that updates _activeMeasurement
                    await Run(async (CommManager comm) =>
                    {
                        //Create a copy of the method and update the method with the device's supported current ranges
                        Method copy = null;
                        Method.CopyMethod(method, ref copy);

                        //Determine optimal pgstat mode for EmStat Pico / Sensit series devices
                        if (Capabilities is EmStatPicoCapabilities)
                        {
                            copy.DeterminePGStatMode(Capabilities);
                            Capabilities.ActiveSignalTrainConfiguration =
                                copy.PGStatMode; //Set device capabilities to pgstat mode determined/set in method
                        }

                        copy.Ranging.SupportedCurrentRanges =
                            Capabilities
                                .SupportedRanges; //Update the autoranging depending on the current ranges supported by the connected device

                        //Check whether method is compatible with the connected channel
                        bool isValidMethod;
                        List<string> errors;
                        ValidateMethod(copy, out isValidMethod, out errors);
                        if (!isValidMethod)
                        {
                            throw new ArgumentException("Method is incompatible with the connected device.");
                        }

                        comm.BeginMeasurementAsync += asyncEventHandler;
                        comm.CommErrorOccurred += asyncEventHandlerCommError;

                        string errorString = await comm.MeasureAsync(copy, muxChannel, taskBarrier);
                        if (!(string.IsNullOrEmpty(errorString)))
                        {
                            throw new Exception($"Could not start measurement: {errorString}");
                        }
                    });
                }
                catch (Exception exception)
                {
                    tcs.SetException(exception);
                }
                
                return await tcs.Task;
            }
            finally
            {
                Comm.BeginMeasurementAsync -= asyncEventHandler;
                Comm.CommErrorOccurred -= asyncEventHandlerCommError;
            }
        }

        /// <summary>
        /// Runs a measurement as specified in the method on the connected device until completion.
        /// </summary>
        /// <param name="method">The method.</param>
        /// <param name="channel">The channel.</param>
        /// <param name="muxChannel">The mux channel.</param>
        /// <param name="taskBarrier">The task barrier.</param>
        /// <returns></returns>
        public async Task<SimpleMeasurement> Measure(Method method, int muxChannel, TaskBarrier taskBarrier = null)
        {
            var tcsMeasurementStarted = new TaskCompletionSource<SimpleMeasurement>();
            var tcsMeasurementFinished = new TaskCompletionSource();

            AsyncEventHandler<CommManager.BeginMeasurementEventArgsAsync> asyncEventHandlerMeasurementStarted =
                (sender, e) =>
                {
                    CommManager commSender = sender as CommManager;

                    ActiveMeasurement = e.NewMeasurement;
                    if (ActiveMeasurement is ImpedimetricMeasurementBase || ActiveMeasurement is ImpedimetricMeasBaseMS)
                        _activeSimpleMeasurement
                            .NewSimpleCurve(PalmSens.Data.DataArrayType.ZRe,
                                PalmSens.Data.DataArrayType.ZIm, "Nyquist",
                                true); //Create a nyquist curve by default

                    tcsMeasurementStarted.SetResult(_activeSimpleMeasurement);
                    return Task.CompletedTask;
                };

            AsyncEventHandler<CommManager.EndMeasurementAsyncEventArgs> asyncEventHandlerMeasurementFinished = async (sender, args) =>
            {
                tcsMeasurementFinished.SetResult();
            };

            CommManager.EventHandlerCommErrorOccurred asyncEventHandlerCommError = (sender, exception) =>
            {
                tcsMeasurementFinished.SetException(exception);
            };

            try
            {
                try
                {
                    //Start the measurement on the connected channel, this triggers an event that updates _activeMeasurement
                    await Run(async (CommManager comm) =>
                    {
                        //Create a copy of the method and update the method with the device's supported current ranges
                        Method copy = null;
                        Method.CopyMethod(method, ref copy);

                        var capabilities = comm.Capabilities;

                        //Determine optimal pgstat mode for EmStat Pico / Sensit series devices
                        if (capabilities is EmStatPicoCapabilities)
                        {
                            copy.DeterminePGStatMode(capabilities);
                            capabilities.ActiveSignalTrainConfiguration =
                                copy.PGStatMode; //Set device capabilities to pgstat mode determined/set in method
                        }

                        copy.Ranging.SupportedCurrentRanges =
                            capabilities
                                .SupportedRanges; //Update the autoranging depending on the current ranges supported by the connected device

                        //Check whether method is compatible with the connected channel
                        bool isValidMethod;
                        List<string> errors;
                        ValidateMethod(copy, out isValidMethod, out errors);
                        if (!isValidMethod)
                        {
                            throw new ArgumentException(
                                $"Method is incompatible with the connected instrument: {string.Join("\n", errors)}");
                        }

                        comm.BeginMeasurementAsync += asyncEventHandlerMeasurementStarted;
                        comm.EndMeasurementAsync += asyncEventHandlerMeasurementFinished;
                        comm.CommErrorOccurred += asyncEventHandlerCommError;

                        string errorString = await comm.MeasureAsync(copy, muxChannel, taskBarrier);
                        if (!(string.IsNullOrEmpty(errorString)))
                        {
                            throw new Exception($"Could not start measurement.");
                        }
                    });
                }
                catch (Exception exception)
                {
                    tcsMeasurementStarted.SetException(exception);
                    tcsMeasurementFinished.SetException(exception);
                }

                try
                {
                    SimpleMeasurement measurement = await tcsMeasurementStarted.Task;
                    await tcsMeasurementFinished.Task;
                    return measurement;
                }
                catch
                {
                    tcsMeasurementFinished.SetCanceled();
                    throw;
                }
            }
            finally
            {
                Comm.BeginMeasurementAsync -= asyncEventHandlerMeasurementStarted;
                Comm.EndMeasurementAsync -= asyncEventHandlerMeasurementFinished;
                Comm.CommErrorOccurred -= asyncEventHandlerCommError;
            }
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
        /// Starts a measurement as specified in the method on the connected device.
        /// </summary>
        /// <param name="method">The method containing the measurement parameters.</param>
        /// <returns>A SimpleMeasurement instance containing all the data related to the measurement.</returns>
        public async Task<SimpleMeasurement> StartMeasurement(Method method, TaskBarrier taskBarrier = null)
        {
            if (method.MuxMethod == MuxMethod.Sequentially)
                return await StartMeasurement(method, method.GetNextSelectedMuxChannel(-1), taskBarrier);
            else
                return await StartMeasurement(method, -1, taskBarrier);
        }

        /// <summary>
        /// Runs a measurement as specified in the method on the connected device until completion.
        /// </summary>
        /// <param name="method">The method containing the measurement parameters.</param>
        /// <returns>A SimpleMeasurement instance containing all the data related to the measurement.</returns>
        public async Task<SimpleMeasurement> Measure(Method method, TaskBarrier taskBarrier = null)
        {
            if (method.MuxMethod == MuxMethod.Sequentially)
                return await Measure(method, method.GetNextSelectedMuxChannel(-1), taskBarrier);
            else
                return await Measure(method, -1, taskBarrier);
        }

        /// <summary>
        /// Aborts the current active measurement.
        /// </summary>
        /// <exception cref="System.NullReferenceException">Not connected to a device.</exception>
        /// <exception cref="System.Exception">The device is not currently performing measurement</exception>
        public async Task AbortMeasurement()
        {
            await Run(async (CommManager comm) => {
                if (comm.ActiveMeasurement == null)
                    throw new Exception("Device is not measuring.");
                await comm.AbortAsync();
            });
        }

        /// <summary>
        /// Turns the cell on.
        /// </summary>
        /// <exception cref="System.NullReferenceException">Not connected to a device</exception>
        /// <exception cref="System.Exception">Device must be in idle mode for manual control</exception>
        public async Task TurnCellOn()
        {
            await Run(async (CommManager comm) => {
                if (comm.State != CommManager.DeviceState.Idle)
                    throw new Exception("Device must be in idle mode for manual control");
                if (comm.CellOn)
                    return;
                await comm.SetCellOnAsync(true);
            });            
        }

        /// <summary>
        /// Turns the cell off.
        /// </summary>
        /// <exception cref="System.NullReferenceException">Not connected to a device</exception>
        /// <exception cref="System.Exception">Device must be in idle mode for manual control</exception>
        public async Task TurnCellOff()
        {
            await Run(async (CommManager comm) => {
                if (comm.State != CommManager.DeviceState.Idle)
                    throw new Exception("Device must be in idle mode for manual control");
                if (!comm.CellOn)
                    return;
                await comm.SetCellOnAsync(false);
            });
        }

        /// <summary>
        /// Sets the cell potential.
        /// </summary>
        /// <param name="potential">The potential.</param>
        /// <exception cref="System.NullReferenceException">Not connected to a device</exception>
        /// <exception cref="System.Exception">Device must be in idle mode for manual control</exception>
        public async Task SetCellPotential(float potential)
        {
            await Run(async (CommManager comm) => {
                if (comm.State != CommManager.DeviceState.Idle)
                    throw new Exception("Device must be in idle mode for manual control");
                await comm.SetPotentialAsync(potential);
            });
        }

        /// <summary>
        /// Reads the cell potential.
        /// </summary>
        /// <returns></returns>
        /// <exception cref="NullReferenceException">Not connected to a device</exception>
        /// <exception cref="Exception">Device must be in idle mode for manual control</exception>
        public async Task<float> ReadCellPotential()
        {
            return await Run(async (CommManager comm) => {
                if (comm.State != CommManager.DeviceState.Idle) 
                    throw new Exception("Device must be in idle mode for manual control");
                return await comm.GetPotentialAsync();
            });
        }

        /// <summary>
        /// Sets the cell current.
        /// </summary>
        /// <param name="current">The current.</param>
        /// <exception cref="System.NullReferenceException">Not connected to a device</exception>
        /// <exception cref="System.Exception">Device must be in idle mode for manual control</exception>
        public async Task SetCellCurrent(float current)
        {
            await Run(async (CommManager comm) => {
                if (comm.State != CommManager.DeviceState.Idle)
                    throw new Exception("Device must be in idle mode for manual control");
                if (!comm.Capabilities.IsGalvanostat)
                    throw new Exception("Device does not support Galvanostat mode");
                await comm.SetCurrentAsync(current);
            });
        }

        /// <summary>
        /// Reads the cell current.
        /// </summary>
        /// <returns></returns>
        /// <exception cref="NullReferenceException">Not connected to a device</exception>
        /// <exception cref="Exception">Device must be in idle mode for manual control</exception>
        public async Task<float> ReadCellCurrent()
        {
            return await Run(async (CommManager comm) => {
                if (comm.State != CommManager.DeviceState.Idle)
                    throw new Exception("Device must be in idle mode for manual control");
                return await comm.GetCurrentAsync();
            });
        }

        /// <summary>
        /// Sets the current range.
        /// </summary>
        /// <param name="currentRange">The current range.</param>
        /// <exception cref="System.NullReferenceException">Not connected to a device</exception>
        /// <exception cref="System.Exception">Device must be in idle mode for manual control</exception>
        public async Task SetCurrentRange(CurrentRange currentRange)
        {
            await Run(async (CommManager comm) => {
                if (comm.State != CommManager.DeviceState.Idle)
                    throw new Exception("Device must be in idle mode for manual control");
                await comm.SetCurrentRangeAsync(currentRange);
            });
        }

        /// <summary>
        /// Runs a MethodSCRIPT on the device, ignoring any output returned by the script.
        /// </summary>
        /// <param name="script">The MethodSCRIPT.</param>
        /// <param name="timeout">The timeout.</param>
        /// <exception cref="NullReferenceException">Not connected to a device</exception>
        /// <exception cref="Exception">Device must be in idle mode to run a MethodSCRIPT</exception>
        public async Task StartSetterMethodScriptAsync(string script, int timeout = 500)
        {
            await Run(async (CommManager comm) => {
                if (comm.State != CommManager.DeviceState.Idle)
                    throw new Exception("Device must be in idle mode to run a MethodSCRIPT");
                if (comm.ClientConnection is ClientConnectionMS connMS)
                    await connMS.StartSetterMethodScriptAsync(script, timeout);
                    
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
        public async Task<string> StartGetterMethodScript(string script, int timeout = 2500)
        {
            return await Run(async (CommManager comm) => {
                if (comm.State != CommManager.DeviceState.Idle)
                    throw new Exception("Device must be in idle mode to run a MethodSCRIPT");
                if (comm.ClientConnection is ClientConnectionMS connMS)
                    return await connMS.StartGetterMethodScriptAsync(script, timeout);
                
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
        public async Task<uint> ReadDigitalLine(byte bitMask)
        {
            return await Run(async (CommManager comm) => {
                if (comm.State != CommManager.DeviceState.Idle)
                    throw new Exception("Device must be in idle mode for manual control");
                return await comm.ClientConnection.ReadDigitalLineAsync(bitMask);
            });
        }

        /// <summary>
        /// Sets the digital lines output signal high or low.
        /// The output signal for the digital lines are defined in a bitmask.
        /// Bit 0 is for GPIO0, bit 1 for GPIO1, etc. Bits that are high correspond with a high output signal
        /// </summary>
        /// <param name="bitMask">A bitmask specifying the output of the digital lines (0 = low, 1 = high).</param>
        public async Task SetDigitalOutput(int bitMask)
        {
            await Run(async (CommManager comm) => {
                if (comm.State != CommManager.DeviceState.Idle)
                    throw new Exception("Device must be in idle mode for manual control");
                await comm.ClientConnection.SetDigitalOutputAsync(bitMask);
            });
        }

        /// <summary>
        /// Sets the specified digital lines to input/output and set the output signal of the lines set to output
        /// The output signal for the digital lines are defined in a bitmask.
        /// Bit 0 is for GPIO0, bit 1 for GPIO1, etc. Bits that are high correspond with a high output signal
        /// </summary>
        /// <param name="bitMask">A bitmask specifying the output signal of the digital lines (0 = low, 1 = high).</param>
        /// <param name="configGPIO">A bitmask specifying the the mode of digital lines (0 = input, 1 = output).</param>
        public Task SetDigitalOutput(int bitMask, int configGPIO)
        {
            return Run((CommManager comm) => {
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
        /// Runs an async Func delegate asynchronously on the clientconnections taskscheduler.
        /// </summary>
        /// <param name="func">The action.</param>
        /// <param name="comm">The connection to run the delegate on.</param>
        /// <returns></returns>
        private async Task Run(Func<CommManager, Task> func)
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
        private async Task<T> Run<T>(Func<CommManager, Task<T>> func)
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
        /// <exception cref="System.NullReferenceException">PlatformInvoker not set.</exception>
        private async Task Comm_ReceiveStatus(object sender, StatusEventArgs e)
        {
            if (_platformInvoker == null)
                throw new NullReferenceException("PlatformInvoker not set.");
            if (_platformInvoker.InvokeIfRequired(new AsyncEventHandler<StatusEventArgsAsync>(Comm_ReceiveStatus), sender, e)) //Recast event to UI thread when necessary
                return;
            ReceiveStatus?.Invoke(this, e);
        }

        /// <summary>
        /// Occurs at the start of a new measurement.
        /// </summary>
        public event EventHandler MeasurementStarted;

        /// <summary>
        /// Sets the ActiveMeasurement at the start of a measurement and casts BeginMeasurement events coming from a different thread to the UI thread when necessary.
        /// </summary>
        /// <param name="sender">The sender.</param>
        /// <param name="e">The new measurement.</param>
        /// <exception cref="System.NullReferenceException">PlatformInvoker not set.</exception>
        private async Task Comm_BeginMeasurement(object sender, BeginMeasurementEventArgsAsync e)
        {
            if (_platformInvoker == null)
                throw new NullReferenceException("PlatformInvoker not set.");
            if (_platformInvoker.InvokeIfRequired(new AsyncEventHandler<BeginMeasurementEventArgsAsync>(Comm_BeginMeasurement), sender, e)) //Recast event to UI thread when necessary
                return;
            MeasurementStarted?.Invoke(this, EventArgs.Empty);
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
        /// <exception cref="System.NullReferenceException">PlatformInvoker not set.</exception>
        private async Task Comm_EndMeasurement(object sender, EndMeasurementAsyncEventArgs e)
        {
            if (_platformInvoker == null)
                throw new NullReferenceException("PlatformInvoker not set.");

            ActiveMeasurement = null;

            if (!_platformInvoker.InvokeIfRequired(
                    (EventHandler<Exception>)((sender, ex) =>
                    {
                        MeasurementEnded?.Invoke(sender, ex);
                    }), this, _commErrorException)) //Recast event to UI thread when necessary
            {
                MeasurementEnded?.Invoke(this, _commErrorException);
            }
        }

        /// <summary>
        /// Adds the active Curve to the active SimpleMeasurement and casts BeginReceiveCurve events coming from a different thread to the UI thread when necessary.
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="CurveEventArgs"/> instance containing the event data.</param>
        /// <exception cref="System.NullReferenceException">PlatformInvoker not set.</exception>
        private void Comm_BeginReceiveCurve(object _, CurveEventArgs e)
        {
            if (_platformInvoker == null)
                throw new NullReferenceException("PlatformInvoker not set.");

            var activeSimpleCurve = SetActiveSimpleCurve(e.GetCurve());

            if (!_platformInvoker.InvokeIfRequired(
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
        public event StatusChangedEventHandler StateChanged;

        /// <summary>
        /// Casts StateChanged events coming from a different thread to the UI thread when necessary.
        /// </summary>
        /// <param name="sender">The sender.</param>
        /// <param name="e">State of the current.</param>
        /// <exception cref="System.NullReferenceException">PlatformInvoker not set.</exception>
        private async Task Comm_StateChanged(object sender, StateChangedAsyncEventArgs e)
        {
            if (_platformInvoker == null)
                throw new NullReferenceException("PlatformInvoker not set.");
            if (_platformInvoker.InvokeIfRequired(new AsyncEventHandler<StateChangedAsyncEventArgs>(Comm_StateChanged), sender, e)) //Recast event to UI thread when necessary
                return;
            StateChanged?.Invoke(this, e.State);
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
            if (_platformInvoker == null)
                throw new NullReferenceException("PlatformInvoker not set.");

            _comm?.Dispose();
            Comm = null;
            var ex = _commErrorException;
            _commErrorException = null;

            if (!_platformInvoker.InvokeIfRequired(
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
                Comm_EndMeasurement(sender, null).Wait();
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
