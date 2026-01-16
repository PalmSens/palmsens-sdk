using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Windows.Forms;
using PalmSens.Comm;
using PalmSens.Devices;
using PalmSens.Core.Simplified.Data;
using System.Threading.Tasks;
using PalmSens.Core.Simplified.InternalStorage;

namespace PalmSens.Core.Simplified.WinForms
{
    public partial class PSMultiCommSimpleWinForms : Component, IPlatformMulti, IPlatformInvoker, IDisposable
    {
        /// <summary>
        /// Initializes a new instance of the <see cref="PSMultiCommSimpleWinForms"/> class.
        /// This class handles the communication with a collection of channels and it is used
        /// to perform measurements and control the channels manually.
        /// </summary>
        /// <param name="container">The containing windows form or control.</param>
        public PSMultiCommSimpleWinForms(IContainer container) : this()
        {
            container.Add(this);
        }

        /// <summary>
        /// Initializes a new instance of the <see cref="PSCommSimpleWinForms"/> class.
        /// This class handles the communication with a collection of channels and it is used
        /// to perform measurements and control the channels manually.
        /// </summary>
        public PSMultiCommSimpleWinForms()
        {
            InitializeComponent();
            PalmSens.Windows.CoreDependencies.Init(); //Initiates PSSDK threading dependencies
            InitAsyncFunctionality(Environment.ProcessorCount); //Initiate the asynchronous functions in the SDK
            PalmSens.Devices.Device.InitAsyncQueues(); //Use queue for communication to improve stability
            _psMultiCommSimple = new PSMultiCommSimple(this, this as IPlatformInvoker);
        }

        #region Properties
        /// <summary>
        /// Instance of the platform independent PSCommSimple class that manages measurements and manual control
        /// </summary>
        private PSMultiCommSimple _psMultiCommSimple;

        /// <summary>
        /// The parent control required to invoke events to the UI thread which is done to prevent threading exceptions
        /// </summary>
        private Control _parent = null;

        /// <summary>
        /// Gets or sets the parent form.
        /// </summary>
        /// <value>
        /// The parent form.
        /// </value>
        /// <exception cref="System.NullReferenceException">Parent form/control cannot be null.</exception>
        public Control Parent
        {
            get
            {
                return _parent;
            }
            set
            {
                if (value == null)
                    throw new NullReferenceException("Parent form/control cannot be null.");
                _parent = value as Control;
            }
        }

        /// <summary>
        /// The channel handler class which handles the connection to the channel
        /// </summary>
        private DeviceHandler _deviceHandler = new DeviceHandler();

        private IReadOnlyList<Device> _availableDevices;

        /// <summary>
        /// Gets the CommManager for the current connection.
        /// </summary>
        /// <value>
        /// The CommManager, null when there is no active connection to a channel.
        /// </value>
        public CommManager[] Comms => _psMultiCommSimple.Comms;

        /// <summary>
        /// Gets a dictionary connections by channel index. Do not modify this dictionary.
        /// </summary>
        /// <value>
        /// The index of the comms by channel.
        /// </value>
        public Dictionary<int, CommManager> CommsByChannelIndex => _psMultiCommSimple.CommsByChannelIndex;

        /// <summary>
        /// Gets a value indicating whether <see cref="PSCommSimple"/> is connected to a channel.
        /// </summary>
        /// <value>
        ///   <c>true</c> if connected; otherwise, <c>false</c>.
        /// </value>
        public bool Connected => _psMultiCommSimple.Connected;

        /// <summary>
        /// Gets the number of connected channels.
        /// </summary>
        /// <value>
        /// The n connected channels.
        /// </value>
        public int NConnectedChannels => _psMultiCommSimple.NConnectedChannels;

        /// <summary>
        /// Gets the connected channel type.
        /// </summary>
        /// <value>
        /// The connected channel type.
        /// </value>
        public enumDeviceType[] ConnectedChannels => _psMultiCommSimple.ConnectedChannels;

        /// <summary>
        /// Returns an array of all of the connected devices.
        /// </summary>
        /// <value>
        /// The connected channels.
        /// </value>
        public Device[] ConnectedDevices => _psMultiCommSimple.ConnectedDevices;

        /// <summary>
        /// Gets the state of the connected channel.
        /// </summary>
        /// <value>
        /// The state of the channel.
        /// </value>
        public CommManager.DeviceState[] ChannelStates => _psMultiCommSimple.ChannelStates;

        /// <summary>
        /// Gets a value indicating whether [cell is on].
        /// </summary>
        /// <value>
        ///   <c>true</c> if [cell is on]; otherwise, <c>false</c>.
        /// </value>
        public bool[] CellOn => _psMultiCommSimple.IsCellOn;

        /// <summary>
        /// Gets the capabilities of the connected channel.
        /// </summary>
        /// <value>
        /// The channel capabilities.
        /// </value>
        public DeviceCapabilities[] Capabilities => _psMultiCommSimple.Capabilities;

        /// <summary>
        /// Gets or sets a value indicating whether to enable channels connected via bluetooth.
        /// </summary>
        /// <value>
        ///   <c>true</c> Enable scan for channels over bluetooth; Disable scan for channels over bluetooth <c>false</c>.
        /// </value>
        public bool EnableBluetooth
        {
            get => _deviceHandler.EnableBluetooth;
            set => _deviceHandler.EnableBluetooth = value;
        }

        /// <summary>
        /// Gets or sets a value indicating whether to enable channels in VCP mode.
        /// </summary>
        /// <value>
        ///   <c>true</c> Enable scan for VCP channels on serial port; Disable scan for VCP channels on serial port <c>false</c>.
        /// </value>
        public bool EnableSerialPort
        {
            get => _deviceHandler.EnableSerialPort;
            set => _deviceHandler.EnableSerialPort = value;
        }

        /// <summary>
        /// Determines whether [the specified method] is compatible with all connected channels.
        /// </summary>
        /// <param name="method">The method.</param>
        /// <returns>
        ///   <c>true</c> if the method is valid; otherwise, <c>false</c>.
        /// </returns>
        public bool[] IsValidMethod(Method method) => _psMultiCommSimple.IsValidMethod(method);

        /// <summary>
        /// Determines whether [the specified method] is compatible with the specified channel.
        /// </summary>
        /// <param name="method">The method.</param>
        /// <param name="channel">The specified channel.</param>
        /// <returns>
        ///   <c>true</c> if the method is valid; otherwise, <c>false</c>.
        /// </returns>
        public bool IsValidMethod(Method method, int channel) => _psMultiCommSimple.IsValidMethod(method, channel);

        /// <summary>
        /// Determines whether [the specified method] is compatible with the specified channels.
        /// </summary>
        /// <param name="method">The method.</param>
        /// <param name="channels">The specified channels.</param>
        /// <returns>
        ///   <c>true</c> if the method is valid; otherwise, <c>false</c>.
        /// </returns>
        public bool[] IsValidMethod(Method method, int[] channels) => _psMultiCommSimple.IsValidMethod(method, channels);
        #endregion

        #region Functions
        /// <summary>
        /// Required initialization for using the async functionalities of the PalmSens SDK.
        /// The amount of simultaneous operations will be limited to prevent performance issues.
        /// When possible it will leave one core free for the UI.
        /// </summary>
        /// <param name="nCores">The number of CPU cores.</param>
        private void InitAsyncFunctionality(int nCores)
        {
            SynchronizationContextRemover.Init(nCores > 1 ? nCores - 1 : 1);
        }

        /// <summary>
        /// Returns an array of connected channels.
        /// </summary>
        public Task<IReadOnlyList<Device>> GetConnectedDevicesAsync() => _deviceHandler.GetConnectedDevicesAsync();

        /// <summary>
        /// Connects to the specified channels.
        /// </summary>
        /// <param name="devices">Array devices to connect to.</param>
        /// <param name="channelIndices">Array of unique indices for the specified channel (0, 1, 2, 3... by default)</param>
        public Task ConnectAsync(Device[] devices, int[] channelIndices = null) => _psMultiCommSimple.Connect(devices, channelIndices);

        /// <summary>
        /// Disconnects from the connected channel.
        /// </summary>
        public Task DisconnectAsync() => _psMultiCommSimple.Disconnect();

        /// <summary>
        /// Turns the cell on on specified channel.
        /// </summary>
        /// <param name="channel">The channel.</param>
        /// <returns></returns>
        public Task TurnCellOnAsync(int channel) => _psMultiCommSimple.TurnCellOnAsync(channel);

        /// <summary>
        /// Turns the cell on on specified channels.
        /// </summary>
        /// <param name="channels">The channels.</param>
        /// <returns></returns>
        public Task TurnCellOnAsync(int[] channels) => _psMultiCommSimple.TurnCellOnAsync(channels);

        /// <summary>
        /// Turns the cell on on all channels.
        /// </summary>
        public Task TurnCellOnAsync() => _psMultiCommSimple.TurnCellOnAsync();

        /// <summary>
        /// Turns the cell off on specified channel.
        /// </summary>
        /// <param name="channel">The channel.</param>
        /// <returns></returns>
        public Task TurnCellOffAsync(int channel) => _psMultiCommSimple.TurnCellOffAsync(channel);

        /// <summary>
        /// Turns the cell off on specified channels.
        /// </summary>
        /// <param name="channels">The channels.</param>
        /// <returns></returns>
        public Task TurnCellOffAsync(int[] channels) => _psMultiCommSimple.TurnCellOffAsync(channels);

        /// <summary>
        /// Turns the cell off on all channels.
        /// </summary>
        public Task TurnCellOffAsync() => _psMultiCommSimple.TurnCellOffAsync();

        /// <summary>
        /// Sets the cell potential on the specified channel.
        /// </summary>
        /// <param name="potential">The potential.</param>
        /// <param name="channel">The channel.</param>
        /// <returns></returns>
        public Task SetCellPotentialAsync(float potential, int channel) => _psMultiCommSimple.SetCellPotentialAsync(potential, channel);

        /// <summary>
        /// Sets the cell potential on the specified channels.
        /// </summary>
        /// <param name="potential">The potential.</param>
        /// <param name="channel">The channel.</param>
        /// <returns></returns>
        public Task SetCellPotentialAsync(float potential, int[] channels) => _psMultiCommSimple.SetCellPotentialAsync(potential, channels);

        /// <summary>
        /// Sets the cell potential on all channels.
        /// </summary>
        /// <param name="potential">The potential.</param>
        /// <param name="channel">The channel.</param>
        /// <returns></returns>
        public Task SetCellPotentialAsync(float potential) => _psMultiCommSimple.SetCellPotentialAsync(potential);

        /// <summary>
        /// Reads the cell potential on the specified channel.
        /// </summary>
        /// <param name="channel">The channel.</param>
        /// <returns></returns>
        public Task<float> ReadCellPotentialAsync(int channel) => _psMultiCommSimple.ReadCellPotentialAsync(channel);

        /// <summary>
        /// Reads the cell potential on the specified channels.
        /// </summary>
        /// <param name="channel">The channel.</param>
        /// <returns></returns>
        public Task<IList<(float Potential, int ChannelIndex, Exception Exception)>> ReadCellPotentialAsync(int[] channels) => _psMultiCommSimple.ReadCellPotentialAsync(channels);

        /// <summary>
        /// Reads the cell potential on all channels.
        /// </summary>
        /// <returns></returns>
        public Task<IList<(float Potential, int ChannelIndex, Exception Exception)>> ReadCellPotentialAsync() => _psMultiCommSimple.ReadCellPotentialAsync();

        /// <summary>
        /// Sets the cell current on the specified channel.
        /// </summary>
        /// <param name="current">The current.</param>
        /// <param name="channel">The channel.</param>
        /// <returns></returns>
        public Task SetCellCurrentAsync(float current, int channel) => _psMultiCommSimple.SetCellCurrentAsync(current, channel);

        /// <summary>
        /// Sets the cell current on the specified channels.
        /// </summary>
        /// <param name="current">The current.</param>
        /// <param name="channel">The channel.</param>
        /// <returns></returns>
        public Task SetCellCurrentAsync(float current, int[] channels) => _psMultiCommSimple.SetCellCurrentAsync(current, channels);

        /// <summary>
        /// Sets the cell current on all channels.
        /// </summary>
        /// <param name="current">The current.</param>
        /// <param name="channel">The channel.</param>
        /// <returns></returns>
        public Task SetCellCurrentAsync(float current) => _psMultiCommSimple.SetCellCurrentAsync(current);

        /// <summary>
        /// Reads the cell current on the specified channel.
        /// </summary>
        /// <returns></returns>
        public Task<float> ReadCellCurrentAsync(int channel) => _psMultiCommSimple.ReadCellCurrentAsync(channel);

        /// <summary>
        /// Reads the cell current on the specified channels.
        /// </summary>
        /// <returns></returns>
        public Task<IList<(float Current, int ChannelIndex, Exception Exception)>> ReadCellCurrentAsync(int[] channels) => _psMultiCommSimple.ReadCellCurrentAsync(channels);

        /// <summary>
        /// Reads the cell current on all channels.
        /// </summary>
        /// <returns></returns>
        public Task<IList<(float Current, int ChannelIndex, Exception Exception)>> ReadCellCurrentAsync() => _psMultiCommSimple.ReadCellCurrentAsync();

        /// <summary>
        /// Sets the current range on the specified channel.
        /// </summary>
        /// <param name="currentRange">The current range.</param>
        public Task SetCurrentRangeAsync(CurrentRange currentRange, int channel) => _psMultiCommSimple.SetCurrentRangeAsync(currentRange, channel);

        /// <summary>
        /// Sets the current range on the specified channels.
        /// </summary>
        /// <param name="currentRange">The current range.</param>
        public Task SetCurrentRangeAsync(CurrentRange currentRange, int[] channels) => _psMultiCommSimple.SetCurrentRangeAsync(currentRange, channels);

        /// <summary>
        /// Sets the current range on all channels.
        /// </summary>
        /// <param name="currentRange">The current range.</param>
        public Task SetCurrentRangeAsync(CurrentRange currentRange) => _psMultiCommSimple.SetCurrentRangeAsync(currentRange);

        /// <summary>
        /// Runs a measurement as specified in the method on the specified channel.
        /// </summary>
        /// <param name="method">The method containing the measurement parameters.</param>
        /// <param name="channel">The channel.</param>
        /// <param name="muxChannel">The mux channel to measure on.</param>
        /// <returns>
        /// A SimpleMeasurement instance containing all the data related to the measurement.
        /// </returns>
        public Task<SimpleMeasurement> MeasureAsync(Method method, int channel, int muxChannel, TaskBarrier taskBarrier = null) => _psMultiCommSimple.MeasureAsync(method, channel, muxChannel);

        /// <summary>
        /// Runs a measurement as specified in the method on the specified collection of channels.
        /// </summary>
        /// <param name="method">The method containing the measurement parameters.</param>
        /// <param name="channels">The channels.</param>
        /// <param name="muxChannel">The mux channel to measure on.</param>
        /// <returns>
        /// A SimpleMeasurement instance containing all the data related to the measurement.
        /// </returns>
        public Task<IList<(SimpleMeasurement measurement, int channelIndex, Exception exception)>> MeasureAsync(Method method, int[] channels, int muxChannel) => _psMultiCommSimple.MeasureAsync(method, channels, muxChannel);

        /// <summary>
        /// Runs a measurement as specified in the method on all channels.
        /// </summary>
        /// <param name="method">The method containing the measurement parameters.</param>
        /// <param name="channels">The channels.</param>
        /// <param name="muxChannel">The mux channel to measure on.</param>
        /// <returns>
        /// A SimpleMeasurement instance containing all the data related to the measurement.
        /// </returns>
        public Task<IList<(SimpleMeasurement measurement, int channelIndex, Exception exception)>> MeasureAllChannelsAsync(Method method, int muxChannel) => _psMultiCommSimple.MeasureAllChannelsAsync(method, muxChannel);

        /// <summary>
        /// Runs a measurement as specified in the method on the specified channel.
        /// </summary>
        /// <param name="method">The method containing the measurement parameters.</param>
        /// <returns>A SimpleMeasurement instance containing all the data related to the measurement.</returns>
        public Task<SimpleMeasurement> MeasureAsync(Method method, int channel) => _psMultiCommSimple.MeasureAsync(method, channel);

        /// <summary>
        /// Runs a measurement as specified in the method on the specified channel.
        /// </summary>
        /// <param name="method">The method containing the measurement parameters.</param>
        /// <param name="channels">The channels.</param>
        /// <returns>
        /// A SimpleMeasurement instance containing all the data related to the measurement.
        /// </returns>
        public Task<IList<(SimpleMeasurement measurement, int channelIndex, Exception exception)>> MeasureAsync(Method method, int[] channels) => _psMultiCommSimple.MeasureAsync(method, channels);

        /// <summary>
        /// Runs a measurement as specified in the method on the specified channel.
        /// </summary>
        /// <param name="method">The method containing the measurement parameters.</param>
        /// <param name="channels">The channels.</param>
        /// <returns>
        /// A SimpleMeasurement instance containing all the data related to the measurement.
        /// </returns>
        public Task<IList<(SimpleMeasurement measurement, int channelIndex, Exception exception)>> MeasureAllChannelsAsync(Method method) => _psMultiCommSimple.MeasureAllChannelsAsync(method);

        /// <summary>
        /// Awaits a measurement as specified in the method until completion on the specified channel.
        /// </summary>
        /// <param name="method">The method containing the measurement parameters.</param>
        /// <param name="channel">The channel.</param>
        /// <param name="muxChannel">The mux channel to measure on.</param>
        /// <returns>
        /// A SimpleMeasurement instance containing all the data related to the measurement.
        /// </returns>
        public Task<SimpleMeasurement> AwaitMeasurementCompletionAsync(Method method, int channel, int muxChannel, TaskBarrier taskBarrier = null) => _psMultiCommSimple.AwaitMeasurementCompletionAsync(method, channel, muxChannel);

        /// <summary>
        /// Awaits a measurement as specified in the method until completion on the specified collection of channels.
        /// </summary>
        /// <param name="method">The method containing the measurement parameters.</param>
        /// <param name="channels">The channels.</param>
        /// <param name="muxChannel">The mux channel to measure on.</param>
        /// <returns>
        /// A SimpleMeasurement instance containing all the data related to the measurement.
        /// </returns>
        public Task<IList<(SimpleMeasurement measurement, int channelIndex, Exception exception)>> AwaitMeasurementCompletionAsync(Method method, int[] channels, int muxChannel) => _psMultiCommSimple.AwaitMeasurementCompletionAsync(method, channels, muxChannel);

        /// <summary>
        /// Awaits a measurement as specified in the method until completion on all channels.
        /// </summary>
        /// <param name="method">The method containing the measurement parameters.</param>
        /// <param name="channels">The channels.</param>
        /// <param name="muxChannel">The mux channel to measure on.</param>
        /// <returns>
        /// A SimpleMeasurement instance containing all the data related to the measurement.
        /// </returns>
        public Task<IList<(SimpleMeasurement measurement, int channelIndex, Exception exception)>> AwaitMeasurementCompletionAllChannelsAsync(Method method, int muxChannel) => _psMultiCommSimple.AwaitMeasurementCompletionAllChannelsAsync(method, muxChannel);

        /// <summary>
        /// Awaits a measurement as specified in the method until completion on the specified channel.
        /// </summary>
        /// <param name="method">The method containing the measurement parameters.</param>
        /// <returns>A SimpleMeasurement instance containing all the data related to the measurement.</returns>
        public Task<SimpleMeasurement> AwaitMeasurementCompletionAsync(Method method, int channel) => _psMultiCommSimple.AwaitMeasurementCompletionAsync(method, channel);

        /// <summary>
        /// Awaits a measurement as specified in the method until completion on the specified channel.
        /// </summary>
        /// <param name="method">The method containing the measurement parameters.</param>
        /// <param name="channels">The channels.</param>
        /// <returns>
        /// A SimpleMeasurement instance containing all the data related to the measurement.
        /// </returns>
        public Task<IList<(SimpleMeasurement measurement, int channelIndex, Exception exception)>> AwaitMeasurementCompletionAsync(Method method, int[] channels) => _psMultiCommSimple.AwaitMeasurementCompletionAsync(method, channels);

        /// <summary>
        /// Awaits a measurement as specified in the method until completion on the specified channel.
        /// </summary>
        /// <param name="method">The method containing the measurement parameters.</param>
        /// <param name="channels">The channels.</param>
        /// <returns>
        /// A SimpleMeasurement instance containing all the data related to the measurement.
        /// </returns>
        public Task<IList<(SimpleMeasurement measurement, int channelIndex, Exception exception)>> AwaitMeasurementCompletionAllChannelsAsync(Method method) => _psMultiCommSimple.AwaitMeasurementCompletionAllChannelsAsync(method);

        /// <summary>
        /// Aborts the active measurement on the specified channel.
        /// </summary>
        public Task AbortMeasurementAsync(int channel) => _psMultiCommSimple.AbortMeasurementAsync(channel);

        /// <summary>
        /// Aborts the active measurement on the specified channels.
        /// </summary>
        public Task AbortMeasurementsAsync(int[] channels) => _psMultiCommSimple.AbortMeasurementsAsync(channels);

        /// <summary>
        /// Aborts all active measurements channels.
        /// </summary>
        public Task AbortAllActiveMeasurementsAsync() => _psMultiCommSimple.AbortAllActiveMeasurementsAsync();

        /// <summary>
        /// Validates whether the specified method is compatible with the capabilities of the specified connected channel.
        /// </summary>
        /// <param name="method">The method containing the measurement parameters.</param>
        /// <param name="channel">The specified channel.</param>
        /// <param name="isValidMethod">if set to <c>true</c> [is valid method].</param>
        /// <param name="errors">The errors.</param>
        public void ValidateMethod(Method method, int channel, out bool isValidMethod, out List<string> errors)
        {
            _psMultiCommSimple.ValidateMethod(method, channel, out isValidMethod, out errors);
        }

        /// <summary>
        /// Validates whether the specified method is compatible with the capabilities of the specified connected channels.
        /// </summary>
        /// <param name="method">The method containing the measurement parameters.</param>
        /// <param name="channels">The specified channels.</param>
        /// <param name="isValidMethod">if set to <c>true</c> [is valid method].</param>
        /// <param name="errors">The errors.</param>
        public void ValidateMethod(Method method, int[] channels, out bool[] isValidMethod, out List<string>[] errors)
        {
            _psMultiCommSimple.ValidateMethod(method, channels, out isValidMethod, out errors);
        }

        /// <summary>
        /// Validates whether the specified method is compatible with the capabilities of all connected channels.
        /// </summary>
        /// <param name="method">The method containing the measurement parameters.</param>
        /// <param name="isValidMethod">if set to <c>true</c> [is valid method].</param>
        /// <param name="errors">The errors.</param>
        public void ValidateMethod(Method method, out bool[] isValidMethod, out List<string>[] errors)
        {
            _psMultiCommSimple.ValidateMethod(method, out isValidMethod, out errors);
        }

        /// <summary>
        /// Get an internal storage handler that will read the current connected device stored files. This is only for devices that have internal storage.
        /// </summary>
        /// <exception cref="InvalidOperationException">This is thrown when the device is not connected or if the device does not support storage.</exception>
        /// <exception cref="ArgumentException">This is thrown when the channel passed in does not exist in the current communications mapping.</exception>
        /// <returns>A new instance of the internal storage handler for the current connection.</returns>
        public IInternalStorageBrowser GetInternalStorageHandler(int channel)
        {
            return _psMultiCommSimple.GetInternalStorageHandler(channel);
        }
        #endregion

        #region Platform interface
        /// <summary>
        /// Invokes event to UI thread if required.
        /// </summary>
        /// <param name="method">The method.</param>
        /// <param name="args">The arguments.</param>
        /// <returns></returns>
        /// <exception cref="System.NullReferenceException">Parent control not set.</exception>
        public bool InvokeIfRequired(Delegate method, params object[] args)
        {
            if (Parent == null)
                throw new NullReferenceException("Parent control not set.");
            if (Parent.InvokeRequired) //Check if event needs to be cast to the UI thread
            {
                Parent.BeginInvoke(method, args); //Recast event to UI thread
                return true;
            }
            return false;
        }

        public IReadOnlyList<Device> AvailableDevices => _deviceHandler.ConnectedDevices;

        public Task<IReadOnlyList<Device>> GetAvailableDevices() => _deviceHandler.GetConnectedDevicesAsync();

        /// <summary>
        /// Connects to the specified channels.
        /// Warning use the platform independent method Connect() instead.
        /// Otherwise the generic PSMultiCommSimple does not subscribe to the CommManagers correctly
        /// </summary>
        /// <param name="devices">Array devices to connect to.</param>
        /// <param name="channelIndices">Array of unique indices for the specified channel (0, 1, 2, 3... by default)</param>
        public Task<IList<(CommManager Comm, int ChannelIndex, Exception Exception)>> Connect(IList<Device> devices, IList<int> channelIndices = null) => _deviceHandler.ConnectAsync(devices, channelIndices);

        /// <summary>
        /// Disconnects from channels with the specified CommManagers.
        /// Warning use the platform independent method Disconnect() instead.
        /// Otherwise the generic PSMultiCommSimple does not unsubscribe from the CommManagers correctly
        /// which may result in it not being released from the memory.
        /// </summary>
        /// <param name="comms">The comm.</param>
        public Task<IList<(int ChannelIndex, Exception Exception)>> Disconnect(IList<CommManager> comms) => _deviceHandler.Disconnect(comms, false);

        public Task<Device> MatchDevices(Device deviceInErrorState)
        {
            throw new NotImplementedException();
        }

        #endregion

        #region events
        /// <summary>
        /// Occurs when a channel status package is received, these packages are not sent during a measurement.
        /// </summary>
        public event MultiChannelStatusEventHandler ReceiveStatus
        {
            add { _psMultiCommSimple.ReceiveStatus += value; }
            remove { _psMultiCommSimple.ReceiveStatus -= value; }
        }

        /// <summary>
        /// Occurs at the start of a new measurement.
        /// </summary>
        public event MultiChannelMeasurementEventHandler MeasurementStarted
        {
            add { _psMultiCommSimple.MeasurementStarted += value; }
            remove { _psMultiCommSimple.MeasurementStarted -= value; }
        }

        /// <summary>
        /// Occurs when a measurement has ended.
        /// </summary>
        public event MultiChannelMeasurementEventHandler MeasurementEnded
        {
            add { _psMultiCommSimple.MeasurementEnded += value; }
            remove { _psMultiCommSimple.MeasurementEnded -= value; }
        }

        /// <summary>
        /// Occurs when a new [SimpleCurve starts receiving data].
        /// </summary>
        public event PSCommSimple.SimpleCurveStartReceivingDataHandler SimpleCurveStartReceivingData
        {
            add { _psMultiCommSimple.SimpleCurveStartReceivingData += value; }
            remove { _psMultiCommSimple.SimpleCurveStartReceivingData -= value; }
        }

        /// <summary>
        /// Occurs when the devive's [state changed].
        /// </summary>
        public event MultiChannelStateChangedEventHandler StateChanged
        {
            add { _psMultiCommSimple.StateChanged += value; }
            remove { _psMultiCommSimple.StateChanged -= value; }
        }

        /// <summary>
        /// Occurs when a channel is [disconnected].
        /// </summary>
        public event MultiChannelDisconnectedEventHandler Disconnected
        {
            add { _psMultiCommSimple.Disconnected += value; }
            remove { _psMultiCommSimple.Disconnected -= value; }
        }
        #endregion

        /// <summary>
        /// Releases all resources used by the <see cref="T:System.ComponentModel.Component" />.
        /// </summary>
        public new void Dispose()
        {
            _psMultiCommSimple.Dispose();
            PalmSens.Devices.Device.DisposeAsyncQueues();
            base.Dispose();
        }
    }

}
