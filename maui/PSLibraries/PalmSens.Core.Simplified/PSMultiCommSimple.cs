using System;
using System.Collections.Concurrent;
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
using System.Runtime.InteropServices;
using System.Threading;

namespace PalmSens.Core.Simplified
{
    public partial class PSMultiCommSimple
    {
        /// <summary>
        /// Initializes a new instance of the <see cref="PSMultiCommSimple" /> class.
        /// This class handles is used to perform measurements and control a collection of channels manually.
        /// It requires a reference to the platform specific instance of the class,
        /// i.e. PSMultiCommSimpleWinForms, PSMultiCommSimpleWPF or PSMultiCommSimpleXamarin
        /// </summary>
        /// <param name="platform">The reference to the platform specific PSMultiCommSimple class.</param>
        /// <exception cref="System.ArgumentNullException">Platform cannot be null</exception>
        public PSMultiCommSimple(IPlatformMulti platform, IPlatformInvoker platformInvoker)
        {
            if (platform == null)
                throw new ArgumentNullException("Platform cannot be null");
            _platform = platform;
            _platformInvoker = platformInvoker;
            PalmSens.Devices.Device.InitAsyncQueues();
        }

        #region Properties
        /// <summary>
        /// The platform specific interface implementing the layers to communicate with the instrument
        /// </summary>
        private IPlatformMulti _platform = null;

        /// <summary>
        /// The platform specific interface implementing the dispatch of events to the UI thread
        /// </summary>
        private IPlatformInvoker _platformInvoker = null;

        /// <summary>
        /// The connected channels' CommManagers by their unique channel index
        /// </summary>
        private Dictionary<int, CommManager> _commsByChannelIndex = new Dictionary<int, CommManager>();

        /// <summary>
        /// Gets or sets the connected channels' CommManagers and (un)subscribes the corresponding events.
        /// </summary>
        /// <value>
        /// The CommManager.
        /// </value>
        public CommManager[] Comms
        {
            get { return _commsByChannelIndex.Values.ToArray(); }
        }

        /// <summary>
        /// The connected channels' CommManagers by their unique channel index
        /// </summary>
        private Dictionary<int, CommManager> _commsByChannelIndexCopy = new Dictionary<int, CommManager>();

        /// <summary>
        /// Gets a dictionary connections by channel index. Do not modify this dictionary.
        /// </summary>
        /// <value>
        /// The index of the comms by channel.
        /// </value>
        public Dictionary<int, CommManager> CommsByChannelIndex => _commsByChannelIndexCopy;

        private bool _connected = false;

        /// <summary>
        /// Gets a value indicating whether <see cref="PSCommSimple"/> is connected to any channels.
        /// </summary>
        /// <value>
        ///   <c>true</c> if connected; otherwise, <c>false</c>.
        /// </value>
        public bool Connected => _connected;

        private int _nConnectedChannels = 0;

        /// <summary>
        /// Gets the number of connected channels.
        /// </summary>
        /// <value>
        /// The n connected channels.
        /// </value>
        public int NConnectedChannels => _nConnectedChannels;

        /// <summary>
        /// Gets the connected devices.
        /// </summary>
        /// <value>
        /// The connected devices.
        /// </value>
        /// <exception cref="System.NullReferenceException">Not connected to any channels.</exception>
        public Device[] ConnectedDevices
        {
            get
            {
                if (!Connected)
                    throw new NullReferenceException("Not connected to any channels.");
                return Comms.Select(c => c.Device).ToArray();
            }
        }

        /// <summary>
        /// Gets the connected channel types.
        /// </summary>
        /// <value>
        /// The connected channel types.
        /// </value>
        /// <exception cref="System.NullReferenceException">Not connected to any channels.</exception>
        public enumDeviceType[] ConnectedChannels
        {
            get
            {
                if (!Connected)
                    throw new NullReferenceException("Not connected to any channels.");
                return Comms.Select(c => c.DeviceType).ToArray();
            }
        }

        /// <summary>
        /// Gets the states of the connected channels.
        /// </summary>
        /// <value>
        /// The states of the connected channels.
        /// </value>
        /// <exception cref="System.NullReferenceException">Not connected to any channels.</exception>
        public CommManager.DeviceState[] ChannelStates
        {
            get
            {
                if (!Connected)
                    throw new NullReferenceException("Not connected to any channels.");
                return Comms.Select(c => c.State).ToArray();
            }
        }

        /// <summary>
        /// Gets values indicating whether the connected channels' [cell is on].
        /// </summary>
        /// <value>
        ///   <c>true</c> if [cell is on]; otherwise, <c>false</c>.
        /// </value>
        /// <exception cref="System.NullReferenceException">Not connected to any channels.</exception>
        public bool[] IsCellOn
        {
            get
            {
                if (!Connected)
                    throw new NullReferenceException("Not connected to any channels.");
                return Comms.Select(c => c.CellOn).ToArray();
            }
        }

        /// <summary>
        /// Gets the capabilities of the connected channels.
        /// </summary>
        /// <value>
        /// The channel capabilities.
        /// </value>
        /// <exception cref="System.NullReferenceException">Not connected to any channels.</exception>
        public DeviceCapabilities[] Capabilities
        {
            get
            {
                if (!Connected)
                    throw new NullReferenceException("Not connected to any channels.");
                return Comms.Select(c => c.Capabilities).ToArray();
            }
        }

        /// <summary>
        /// Determines whether [the specified method] is compatible with all connected channels.
        /// </summary>
        /// <param name="method">The method.</param>
        /// <returns>
        ///   <c>true</c> if the method is valid; otherwise, <c>false</c>.
        /// </returns>
        public bool[] IsValidMethod(Method method)
        {
            bool[] valid;
            List<string>[] errors;
            ValidateMethod(method, out valid, out errors);
            return valid;
        }

        /// <summary>
        /// Determines whether [the specified method] is compatible with the specified channel.
        /// </summary>
        /// <param name="method">The method.</param>
        /// <param name="channel">The specified channel.</param>
        /// <returns>
        ///   <c>true</c> if the method is valid; otherwise, <c>false</c>.
        /// </returns>
        public bool IsValidMethod(Method method, int channel)
        {
            bool valid;
            List<string> errors;
            ValidateMethod(method, channel, out valid, out errors);
            return valid;
        }

        /// <summary>
        /// Determines whether [the specified method] is compatible with the specified channels.
        /// </summary>
        /// <param name="method">The method.</param>
        /// <param name="channels">The specified channels.</param>
        /// <returns>
        ///   <c>true</c> if the method is valid; otherwise, <c>false</c>.
        /// </returns>
        public bool[] IsValidMethod(Method method, int[] channels)
        {
            bool[] valid;
            List<string>[] errors;
            ValidateMethod(method, channels, out valid, out errors);
            return valid;
        }

        /// <summary>
        /// The active SimpleMeasurements
        /// </summary>
        private ConcurrentDictionary<int, SimpleMeasurement> _activeSimpleMeasurements = new ConcurrentDictionary<int, SimpleMeasurement>();

        /// <summary>
        /// Gets array with indices of all channels.
        /// </summary>
        /// <value>
        /// All channels.
        /// </value>
        /// <exception cref="System.NullReferenceException">Not connected to any channels.</exception>
        private int[] AllChannels
        {
            get
            {
                if (!Connected)
                    throw new NullReferenceException("Not connected to any channels.");
                return _commsByChannelIndex.Keys.ToArray();
            }
        }
        #endregion

        #region Functions
        /// <summary>
        /// Returns an array of available instruments/channels.
        /// </summary>
        public Task<IReadOnlyList<Device>> GetAvailableDevicesAsync() => _platform.GetAvailableDevices();

        /// <summary>
        /// Connects the specified devices.
        /// </summary>
        /// <param name="devices">The devices.</param>
        /// <param name="channelIndices">The channel indices.</param>
        public async Task Connect(IReadOnlyList<Device> devices, IList<int> channelIndices = null)
        {
            AddComms(await _platform.Connect(devices, channelIndices));
        }

        /// <summary>
        /// Disconnects from the connected channels.
        /// </summary>
        /// <exception cref="System.NullReferenceException">Not connected to any channels.</exception>
        public async Task Disconnect()
        {
            RemoveComms(await _platform.Disconnect(Comms));
        }

        public async Task CheckConnections(IList<Device> devices, CancellationToken cancellationToken)
        {
            for (int index = 0; index < devices.Count; index++)
            {
                var device = devices[index];
                int retries = 0;
                List<Exception> exceptions = new List<Exception>();

                do
                {
                    cancellationToken.ThrowIfCancellationRequested();

                    var connectionCheckResult = await CheckConnection(device);
                    if (connectionCheckResult.IsConnected)
                    {
                        break;
                    }

                    exceptions.Add(connectionCheckResult.Exception);

                    if (retries == 3)
                    {
                        throw new AggregateException("Failed to reconnect", exceptions);
                    }

                    try
                    {
                        await device.CloseAsync();
                        await Task.Delay(25 + (retries * retries * retries * 300), cancellationToken);

                        try
                        {
                            if (CommsByChannelIndex.ContainsKey(index))
                            {
                                RemoveComms(await _platform.Disconnect(new List<CommManager>()
                                    { CommsByChannelIndex[index] }));
                            }
                        }
                        catch { }

                        await Connect(new List<Device>() { device }, new List<int>() { index });
                    }
                    catch (Exception exception)
                    {
                        exceptions.Add(exception);
                        devices[index] = await _platform.MatchDevices(device);
                    }

                    retries++;
                } while (true);
            }
        }

        private async Task<(bool IsConnected, Exception Exception)> CheckConnection(Device device)
        {
            try
            {
                var commManager = Comms.First(comm => comm.Device == device);

                await commManager.ClientConnection.Semaphore.WaitAsync();

                try
                {
                    var versionString = await device.GetVersionStringAsync();

                    var model = ClientConnection.FindDeviceType(versionString[0]);
                    if (model == enumDeviceType.Unknown)
                    {
                        return (false, new Exception("Failed to identify instrument"));
                    }
                }
                finally
                {
                    commManager.ClientConnection.Semaphore.Release();
                }

                return (true, null);
            }
            catch (Exception exception)
            {
                return (false, exception);
            }
        }

        /// <summary>
        /// Adds newly connected channels to the collection of connected channels.
        /// </summary>
        /// <param name="connectedChannels">The connected channels.</param>
        internal void AddComms(IReadOnlyList<(CommManager Comm, int ChannelIndex, Exception Exception)> connectedChannels)
        {
            List<Exception> exceptions = new List<Exception>();

            foreach (var channel in connectedChannels)
            {
                int channelIndex = _commsByChannelIndex.ContainsKey(channel.ChannelIndex)
                    ? _commsByChannelIndex.Count
                    : channel.ChannelIndex;

                if (channel.Exception != null || channel.Comm == null)
                {
                    exceptions.Add(new Exception(
                        $"Error occured while connecting to channel {channelIndex}.",
                        channel.Exception));
                    continue;
                }

                _commsByChannelIndex[channelIndex] = channel.Comm;
                SubscribeCommEvents(channel.Comm);
            }

            _nConnectedChannels = _commsByChannelIndex.Count;
            _connected = _nConnectedChannels > 0;
            _commsByChannelIndexCopy.Clear();
            foreach (var valuePair in _commsByChannelIndex)
                _commsByChannelIndexCopy.Add(valuePair.Key, valuePair.Value);

            if (exceptions.Count > 0)
                throw new AggregateException(exceptions);
        }

        /// <summary>
        /// Remove disconnected channels from collection of connected channels.
        /// </summary>
        /// <param name="disconnectedChannels">The disconnected channels.</param>
        internal void RemoveComms(IReadOnlyList<(int channelIndex, Exception exception)> disconnectedChannels)
        {
            List<Exception> exceptions = new List<Exception>();

            foreach (var disconnectedChannel in disconnectedChannels)
            {
                if (_commsByChannelIndex.ContainsKey(disconnectedChannel.channelIndex))
                {
                    CommManager comm = _commsByChannelIndex[disconnectedChannel.channelIndex];
                    if(comm!=null)
                        UnSubscribeCommEvents(comm);
                    _commsByChannelIndex.Remove(disconnectedChannel.channelIndex);
                }
                else
                {
                    continue;
                }

                if (_activeSimpleMeasurements.ContainsKey(disconnectedChannel.channelIndex))
                    _activeSimpleMeasurements.TryRemove(disconnectedChannel.channelIndex, out _);

                if (disconnectedChannel.exception != null)
                    exceptions.Add(new Exception($"Error occured while disconnecting from channel {disconnectedChannel.channelIndex}.",disconnectedChannel.exception));
            }

            _nConnectedChannels = _commsByChannelIndex.Count;
            _connected = _nConnectedChannels > 0;
            _commsByChannelIndexCopy.Clear();
            foreach (var valuePair in _commsByChannelIndex)
                _commsByChannelIndexCopy.Add(valuePair.Key, valuePair.Value);

            if (exceptions.Count > 0)
                throw new AggregateException(exceptions);
        }

        /// <summary>
        /// Subscribes to the CommManager's events.
        /// </summary>
        /// <param name="comm">The comm.</param>
        private void SubscribeCommEvents(CommManager comm)
        {
            comm.BeginMeasurementAsync += Comm_BeginMeasurementAsync;
            comm.EndMeasurementAsync += Comm_EndMeasurementAsync;
            comm.BeginReceiveCurve += Comm_BeginReceiveCurve;
            comm.ReceiveStatusAsync += Comm_ReceiveStatusAsync;
            comm.StateChangedAsync += Comm_StateChangedAsync;
            comm.Disconnected += Comm_Disconnected;
            comm.CommErrorOccurred += Comm_CommErrorOccurred;
        }

        /// <summary>
        /// Unsubscribes the CommManager's events.
        /// </summary>
        /// <param name="comm">The comm.</param>
        private void UnSubscribeCommEvents(CommManager comm)
        {
            comm.BeginMeasurementAsync -= Comm_BeginMeasurementAsync;
            comm.EndMeasurementAsync -= Comm_EndMeasurementAsync;
            comm.BeginReceiveCurve -= Comm_BeginReceiveCurve;
            comm.ReceiveStatusAsync -= Comm_ReceiveStatusAsync;
            comm.StateChangedAsync -= Comm_StateChangedAsync;
            comm.Disconnected -= Comm_Disconnected;
            comm.CommErrorOccurred -= Comm_CommErrorOccurred;
        }

        /// <summary>
        /// Starts a measurement as specified in the method on the specified channel.
        /// </summary>
        /// <param name="method">The method containing the measurement parameters.</param>
        /// <param name="channel">The channel.</param>
        /// <param name="muxChannel">The mux channel to measure on.</param>
        /// <returns>
        /// A SimpleMeasurement instance containing all the data related to the measurement.
        /// </returns>
        /// <exception cref="System.NullReferenceException">
        /// Not connected to any channels.
        /// or
        /// Not connected to specified channel.
        /// </exception>
        /// <exception cref="System.ArgumentException">Method is incompatible with the connected channel.</exception>
        /// <exception cref="System.Exception">Could not start measurement.</exception>
        public async Task<SimpleMeasurement> StartMeasureAsync(Method method, int channel, int muxChannel, TaskBarrier taskBarrier = null)
        {
            return (await StartMeasurementTask(method, channel, muxChannel, taskBarrier, true, false)).Measurement;
        }

        /// <summary>
        /// Starts a measurement as specified in the method on the specified channel.
        /// </summary>
        /// <param name="method">The method.</param>
        /// <param name="channel">The channel.</param>
        /// <param name="muxChannel">The mux channel.</param>
        /// <param name="throwExceptions">if set to <c>true</c> [throw exceptions].</param>
        /// <param name="taskBarrier">The task barrier.</param>
        /// <param name="useHWSync">Used for enabling hardware synchronization on supported multi-channel instruments.</param>
        /// <returns></returns>
        private async Task<(SimpleMeasurement Measurement, int ChannelIndex, Exception Exception)> StartMeasurementTask(Method method, int channel, int muxChannel, TaskBarrier taskBarrier, bool throwExceptions, bool useHWSync)
        {
            var tcs = new TaskCompletionSource<SimpleMeasurement>();

            AsyncEventHandler<CommManager.BeginMeasurementEventArgsAsync> asyncEventHandler = async (sender, e) =>
            {
                CommManager commSender = sender as CommManager;

                SimpleMeasurement simpleMeasurement = new SimpleMeasurement(e.NewMeasurement);
                simpleMeasurement.Title += $" Channel {commSender.ChannelIndex + 1}";
                simpleMeasurement.Channel = commSender.ChannelIndex + 1;
                _activeSimpleMeasurements.TryAdd(commSender.ChannelIndex, simpleMeasurement);
                if (e.NewMeasurement is ImpedimetricMeasurementBase || e.NewMeasurement is ImpedimetricMeasBaseMS)
                    _activeSimpleMeasurements[commSender.ChannelIndex].NewSimpleCurve(PalmSens.Data.DataArrayType.ZRe, PalmSens.Data.DataArrayType.ZIm, "Nyquist", true); //Create a nyquist curve by default

                tcs.SetResult(simpleMeasurement);
            };

            CommManager.EventHandlerCommErrorOccurred asyncEventHandlerCommError = (sender, exception) =>
            {
                tcs.SetException(exception);
            };

            try
            {
                //Start the measurement on the connected channel, this triggers an event that updates _activeMeasurement
                var result = await RunAsync(async (int ch, CommManager comm) =>
                {
                    if (comm.State != CommManager.DeviceState.Idle)
                    {
                        throw new ArgumentException($"Channel {channel} is not idle");
                    }

                    //Create a copy of the method and update the method with the device's supported current ranges
                    Method copy = null;
                    Method.CopyMethod(method, ref copy);

                    //Check whether method is compatible with the connected channel
                    bool isValidMethod;
                    List<string> errors;
                    ValidateMethod(copy, channel, out isValidMethod, out errors);
                    if (!isValidMethod)
                    {
                        throw new ArgumentException(
                            $"Method is incompatible with the connected channel: {channel}. {string.Join("\n", errors)}");
                    }

                    if (useHWSync)
                    {
                        comm.Capabilities.IsSlaveChannel = true;
                    }

                    comm.BeginMeasurementAsync += asyncEventHandler;
                    comm.CommErrorOccurred += asyncEventHandlerCommError;

                    string errorString = await comm.MeasureAsync(copy, muxChannel, taskBarrier);

                    if (useHWSync)
                    {
                        comm.Capabilities.IsSlaveChannel = false;
                    }

                    if (!(string.IsNullOrEmpty(errorString)))
                    {
                        throw new Exception($"Could not start measurement on channel {channel}.\n{errorString}");
                    }
                }, channel, throwExceptions);

                if (result.Item2 != null)
                {
                    tcs.SetCanceled();

                    return (null, result.Item1, result.Item2);
                }

                try
                {
                    SimpleMeasurement measurement = await tcs.Task;
                    return (measurement, result.Item1, result.Item2);
                }
                catch (Exception exception)
                {
                    return (null, channel, exception);
                }
            }
            finally
            {
                if (_commsByChannelIndex.TryGetValue(channel, out var commManager))
                {
                    commManager.BeginMeasurementAsync -= asyncEventHandler;
                    commManager.CommErrorOccurred -= asyncEventHandlerCommError;
                }
            }
        }

        /// <summary>
        /// Starts a measurement as specified in the method on the specified collection of channels.
        /// No results will be returned if other measurements were started correctly.
        /// </summary>
        /// <param name="method">The method containing the measurement parameters.</param>
        /// <param name="channels">The channels.</param>
        /// <param name="muxChannel">The mux channel to measure on.</param>
        /// <returns>
        /// An array of ValueTuples containing:
        /// - An instance of the SimpleMeasurement instance containing all the data related to the measurement, null in the case of an exception
        /// - The channel index
        /// - Null unless an exception was caught
        /// </returns>
        /// <exception cref="System.NullReferenceException">Not connected to any channels.
        /// or
        /// Not connected to specified channel.</exception>
        /// <exception cref="System.ArgumentException">Method is incompatible with the connected channel.</exception>
        /// <exception cref="System.Exception">Could not start measurement.</exception>
        public Task<IReadOnlyList<(SimpleMeasurement Measurement, int ChannelIndex, Exception Exception)>> StartMeasurementAsync(Method method, int[] channels, int muxChannel, bool useHWSync = false)
        {
            int n = channels.Length;

            if (useHWSync)
            {
                return StartMeasurementWithHWSyncAsync(method, channels, muxChannel, n);
            }

            //Barrier used to synchronize measurements (measurements initiate first and desynchronize slightly
            //before the measurement is triggered on the channels, this barrier synchornizes the triggering on the channels)
            TaskBarrier taskBarrier = new TaskBarrier(n);
            return GetTaskResultsAndOrExceptions<SimpleMeasurement>(
                (int channel) => StartMeasurementTask(method, channel, muxChannel, taskBarrier, false, false)
                , channels);
        }

        /// <summary>
        /// Starts a measurement with hardware synchronization on supported multi-channel instruments
        /// </summary>
        /// <param name="method"></param>
        /// <param name="channels"></param>
        /// <param name="muxChannel"></param>
        /// <param name="n"></param>
        /// <returns></returns>
        /// <exception cref="IndexOutOfRangeException"></exception>
        /// <exception cref="ArgumentException"></exception>
        /// <exception cref="Exception"></exception>
        private async Task<IReadOnlyList<(SimpleMeasurement Measurement, int ChannelIndex, Exception Exception)>> StartMeasurementWithHWSyncAsync(Method method, int[] channels, int muxChannel, int n)
        {
            if (!channels.All(i => CommsByChannelIndex.TryGetValue(i, out var comm) && comm != null))
            {
                throw new IndexOutOfRangeException("Not all specified channels are currently connected");
            }

            ((int Channel, string Serial) ChannelInfo, enumDeviceType DeviceType)[] deviceInfo = channels.Select(i =>
                (Helpers.DeviceDescriptionHelper.GetMultiChannelInfoFromDeviceDescription(CommsByChannelIndex[i]
                    .Device.ToString()), CommsByChannelIndex[i].DeviceType)).ToArray();

            var firstSerial = deviceInfo.First().ChannelInfo.Serial;
            if (deviceInfo.Any(s => string.IsNullOrEmpty(s.ChannelInfo.Serial)
                                    || s.ChannelInfo.Serial != firstSerial
                                    || s.ChannelInfo.Channel < 0))
            {
                throw new ArgumentException(
                    "Hardware synchronization is only supported when a single multi-channel instrument is selected");
            }

            if (deviceInfo.All(s => s.ChannelInfo.Channel != 1))
            {
                throw new ArgumentException(
                    "Hardware synchronization requires the first channel of the multi-channel instrument to be selected");
            }

            if (n < 2)
            {
                throw new ArgumentException(
                    "Hardware synchronization requires at least two channels to be selected");
            }

            switch (deviceInfo.First().DeviceType)
            {
                case enumDeviceType.PalmSens4:
                case enumDeviceType.EmStat4LR:
                case enumDeviceType.EmStat4HR:
                {
                    var channelsOrdered = channels.OrderBy(i => i).ToArray();
                    method.UseHWSync = true;

                    var secondaryChannels =
                        (await GetTaskResultsAndOrExceptions<SimpleMeasurement>(
                            (int channel) => StartMeasurementTask(
                                method,
                                channel,
                                muxChannel,
                                null,
                                false,
                                true)
                            , channelsOrdered.Skip(1).ToArray())).ToList(); //Before starting the measurement on the primary channels
                                                                     //it needs to be started on the secondary channels
                    var primaryChannel =
                        await StartMeasurementTask(method,
                            channelsOrdered.First(),
                            muxChannel,
                            null,
                            true,
                            true); //If the measurement is not started on the primary channel
                                    //it will not start on the secondary channels therefore the exception is thrown in this case

                    method.UseHWSync = false;
                    secondaryChannels.Insert(0, primaryChannel);
                    return secondaryChannels;
                }
                    break;
                default:
                    throw new Exception("The selected multi-channel instrument does not support hardware synchronization");
            }
        }

        /// <summary>
        /// Starts a measurement as specified in the method on all channels.
        /// </summary>
        /// <param name="method">The method containing the measurement parameters.</param>
        /// <param name="channels">The channels.</param>
        /// <param name="muxChannel">The mux channel to measure on.</param>
        /// <returns>
        /// A SimpleMeasurement instance containing all the data related to the measurement.
        /// </returns>
        /// <exception cref="System.NullReferenceException">Not connected to any channels.
        /// or
        /// Not connected to specified channel.</exception>
        /// <exception cref="System.ArgumentException">Method is incompatible with the connected channel.</exception>
        /// <exception cref="System.Exception">Could not start measurement.</exception>
        public Task<IReadOnlyList<(SimpleMeasurement Measurement, int ChannelIndex, Exception Exception)>> StartMeasureAllChannelsAsync(Method method, int muxChannel, bool useHWsync = false)
        {
            return StartMeasurementAsync(method, AllChannels, muxChannel, useHWsync);
        }

        /// <summary>
        /// Starts a measurement as specified in the method on the specified channel.
        /// </summary>
        /// <param name="method">The method containing the measurement parameters.</param>
        /// <returns>A SimpleMeasurement instance containing all the data related to the measurement.</returns>
        public Task<SimpleMeasurement> StartMeasureAsync(Method method, int channel)
        {
            return StartMeasureAsync(method, channel, -1);
        }

        /// <summary>
        /// Starts a measurement as specified in the method on the specified channel.
        /// </summary>
        /// <param name="method">The method containing the measurement parameters.</param>
        /// <param name="channels">The channels.</param>
        /// <returns>
        /// A SimpleMeasurement instance containing all the data related to the measurement.
        /// </returns>
        public Task<IReadOnlyList<(SimpleMeasurement Measurement, int ChannelIndex, Exception Exception)>> StartMeasureAsync(Method method, int[] channels, bool useHWSync = false)
        {
            return StartMeasurementAsync(method, channels, -1, useHWSync);
        }

        /// <summary>
        /// Starts a measurement as specified in the method on the specified channel.
        /// </summary>
        /// <param name="method">The method containing the measurement parameters.</param>
        /// <param name="channels">The channels.</param>
        /// <returns>
        /// A SimpleMeasurement instance containing all the data related to the measurement.
        /// </returns>
        public Task<IReadOnlyList<(SimpleMeasurement Measurement, int ChannelIndex, Exception Exception)>> StartMeasurementAllChannelsAsync(Method method, bool useHWSync = false)
        {
            return StartMeasurementAsync(method, AllChannels, -1, useHWSync);
        }

        /// <summary>
        /// Awaits a measurement as specified in the method on the specified channel until completion.
        /// </summary>
        /// <param name="method">The method containing the measurement parameters.</param>
        /// <param name="channel">The channel.</param>
        /// <param name="muxChannel">The mux channel to measure on.</param>
        /// <returns>
        /// A SimpleMeasurement instance containing all the data related to the measurement.
        /// </returns>
        /// <exception cref="System.NullReferenceException">
        /// Not connected to any channels.
        /// or
        /// Not connected to specified channel.
        /// </exception>
        /// <exception cref="System.ArgumentException">Method is incompatible with the connected channel.</exception>
        /// <exception cref="System.Exception">Could not start measurement.</exception>
        public async Task<SimpleMeasurement> MeasureAsync(Method method, int channel, int muxChannel, TaskBarrier taskBarrier = null)
        {
            return (await MeasureTask(method, channel, muxChannel, taskBarrier, true)).Measurement;
        }

        /// <summary>
        /// Awaits a measurement as specified in the method on the specified channel until completion.
        /// </summary>
        /// <param name="method">The method.</param>
        /// <param name="channel">The channel.</param>
        /// <param name="muxChannel">The mux channel.</param>
        /// <param name="taskBarrier">The task barrier.</param>
        /// <returns></returns>
        private async Task<(SimpleMeasurement Measurement, int ChannelIndex, Exception)> MeasureTask(Method method, int channel, int muxChannel, TaskBarrier taskBarrier, bool throwExceptions)
        {
            var tcsMeasurementStarted = new TaskCompletionSource<SimpleMeasurement>();
            var tcsMeasurementFinished = new TaskCompletionSource();

            AsyncEventHandler<CommManager.BeginMeasurementEventArgsAsync> asyncEventHandlerMeasurementStarted =
                async (sender, e) =>
                {
                    CommManager commSender = sender as CommManager;

                    SimpleMeasurement simpleMeasurement = new SimpleMeasurement(e.NewMeasurement);
                    simpleMeasurement.Title += $" Channel {commSender.ChannelIndex + 1}";
                    simpleMeasurement.Channel = commSender.ChannelIndex + 1;
                    _activeSimpleMeasurements.TryAdd(commSender.ChannelIndex, simpleMeasurement);
                    if (e.NewMeasurement is ImpedimetricMeasurementBase || e.NewMeasurement is ImpedimetricMeasBaseMS)
                        _activeSimpleMeasurements[commSender.ChannelIndex]
                            .NewSimpleCurve(PalmSens.Data.DataArrayType.ZRe,
                                PalmSens.Data.DataArrayType.ZIm, "Nyquist",
                                true); //Create a nyquist curve by default

                    tcsMeasurementStarted.SetResult(simpleMeasurement);
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
                //Start the measurement on the connected channel, this triggers an event that updates _activeMeasurement
                var result = await RunAsync(async (int ch, CommManager comm) =>
                    {
                        if (comm.State != CommManager.DeviceState.Idle)
                        {
                            throw new ArgumentException($"Channel {channel} is not idle");
                        }

                        //Create a copy of the method and update the method with the device's supported current ranges
                        Method copy = null;
                        Method.CopyMethod(method, ref copy);

                        var capabilities = _commsByChannelIndex[channel].Capabilities;

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
                        ValidateMethod(copy, channel, out isValidMethod, out errors);
                        if (!isValidMethod)
                        {
                            throw new ArgumentException(
                                $"Method is incompatible with the connected channel: {channel}. {string.Join("\n", errors)}");
                        }

                        comm.BeginMeasurementAsync += asyncEventHandlerMeasurementStarted;
                        comm.EndMeasurementAsync += asyncEventHandlerMeasurementFinished;
                        comm.CommErrorOccurred += asyncEventHandlerCommError;

                        string errorString = await comm.MeasureAsync(copy, muxChannel, taskBarrier);
                        if (!(string.IsNullOrEmpty(errorString)))
                        {
                            throw new Exception($"Could not start measurement on channel {channel}.");
                        }
                    },
                    channel,
                    throwExceptions);

                if (result.Item2 != null)
                {
                    tcsMeasurementStarted.SetCanceled();
                    tcsMeasurementFinished.SetCanceled();

                    return (null, result.Item1, result.Item2);
                }

                try
                {
                    SimpleMeasurement measurement = await tcsMeasurementStarted.Task;

                    try
                    {
                        await tcsMeasurementFinished.Task;
                        return (measurement, result.Item1, result.Item2);
                    }
                    catch (Exception exception)
                    {
                        return (measurement, channel, exception);
                    }
                }
                catch (Exception exception)
                {
                    tcsMeasurementFinished.SetCanceled();
                    return (null, channel, exception);
                }
            }
            finally
            {
                if (_commsByChannelIndex.TryGetValue(channel, out var commManager))
                {
                    commManager.BeginMeasurementAsync -= asyncEventHandlerMeasurementStarted;
                    commManager.EndMeasurementAsync -= asyncEventHandlerMeasurementFinished;
                    commManager.CommErrorOccurred -= asyncEventHandlerCommError;
                }
            }
        }

        /// <summary>
        /// Awaits a measurement as specified in the method until completion on the specified collection of channels.
        /// No results will be returned if other measurements were started correctly.
        /// </summary>
        /// <param name="method">The method containing the measurement parameters.</param>
        /// <param name="channels">The channels.</param>
        /// <param name="muxChannel">The mux channel to measure on.</param>
        /// <returns>
        /// An array of ValueTuples containing:
        /// - An instance of the SimpleMeasurement instance containing all the data related to the measurement, null in the case of an exception
        /// - The channel index
        /// - Null unless an exception was caught
        /// </returns>
        /// <exception cref="System.NullReferenceException">Not connected to any channels.
        /// or
        /// Not connected to specified channel.</exception>
        /// <exception cref="System.ArgumentException">Method is incompatible with the connected channel.</exception>
        /// <exception cref="System.Exception">Could not start measurement.</exception>
        public Task<IReadOnlyList<(SimpleMeasurement Measurement, int ChannelIndex, Exception Exception)>> MeasureAsync(Method method, int[] channels, int muxChannel)
        {
            int n = channels.Length;
            //Barrier used to synchronize measurements (measurements initiate first and desynchronize slightly
            //before the measurement is triggered on the channels, this barrier synchornizes the triggering on the channels)
            TaskBarrier taskBarrier = new TaskBarrier(n);
            return GetTaskResultsAndOrExceptions<SimpleMeasurement>(
                (int channel) => MeasureTask(method, channel, muxChannel, taskBarrier, false)
                , channels);
        }

        /// <summary>
        /// Awaits a measurement as specified in the method until completion on all channels.
        /// </summary>
        /// <param name="method">The method containing the measurement parameters.</param>
        /// <param name="channels">The channels.</param>
        /// <param name="muxChannel">The mux channel to measure on.</param>
        /// <returns>
        /// A SimpleMeasurement instance containing all the data related to the measurement.
        /// </returns>
        /// <exception cref="System.NullReferenceException">Not connected to any channels.
        /// or
        /// Not connected to specified channel.</exception>
        /// <exception cref="System.ArgumentException">Method is incompatible with the connected channel.</exception>
        /// <exception cref="System.Exception">Could not start measurement.</exception>
        public Task<IReadOnlyList<(SimpleMeasurement Measurement, int ChannelIndex, Exception Exception)>> MeasureAllChannelsAsync(Method method, int muxChannel)
        {
            return MeasureAsync(method, AllChannels, muxChannel);
        }

        /// <summary>
        /// Runs a measurement as specified in the method on the specified channel.
        /// </summary>
        /// <param name="method">The method containing the measurement parameters.</param>
        /// <returns>A SimpleMeasurement instance containing all the data related to the measurement.</returns>
        public Task<SimpleMeasurement> MeasureAsync(Method method, int channel)
        {
            return MeasureAsync(method, channel, -1);
        }

        /// <summary>
        /// Awaits a measurement as specified in the method until completion on the specified collection of channels.
        /// </summary>
        /// <param name="method">The method containing the measurement parameters.</param>
        /// <param name="channels">The channels.</param>
        /// <returns>
        /// A SimpleMeasurement instance containing all the data related to the measurement.
        /// </returns>
        public Task<IReadOnlyList<(SimpleMeasurement Measurement, int ChannelIndex, Exception Exception)>> MeasureAsync(Method method, int[] channels)
        {
            return MeasureAsync(method, channels, -1);
        }

        /// <summary>
        /// Awaits a measurement as specified in the method until completion on all channels.
        /// </summary>
        /// <param name="method">The method containing the measurement parameters.</param>
        /// <param name="channels">The channels.</param>
        /// <returns>
        /// A SimpleMeasurement instance containing all the data related to the measurement.
        /// </returns>
        public Task<IReadOnlyList<(SimpleMeasurement Measurement, int ChannelIndex, Exception Exception)>> MeasureAllChannelsAsync(Method method)
        {
            return MeasureAsync(method, AllChannels, -1);
        }


        /// <summary>Aborts the measurement on the specified channel.</summary>
        /// <param name="channel">The channel.</param>
        /// <param name="throwExceptions">if set to <c>true</c> [throw on exceptions], otherwise return them.</param>
        /// <returns>A ValueTuple containing the channel index and any exceptions that were thrown</returns>
        private async Task<(int ChannelIndex, Exception Exception)> AbortMeasurementTask(int channel, bool throwExceptions)
        {
            return await RunAsync((int channelIndex, CommManager comm) =>
            {
                if (comm.ActiveMeasurement == null)
                    throw new Exception($"Channel {channelIndex} is not measuring.");
                try
                {
                    return comm.AbortAsync();
                }
                catch (Exception ex)
                {
                    throw new Exception($"Failed to abort measurement on channel {channel}.", ex);
                }
            }, channel, throwExceptions);
        }

        /// <summary>
        /// Aborts the active measurement on the specified channel.
        /// </summary>
        /// <exception cref="System.NullReferenceException">Not connected to a channel.</exception>
        /// <exception cref="System.Exception">The channel is not currently performing measurement</exception>
        public async Task AbortMeasurementAsync(int channel)
        {
            await AbortMeasurementTask(channel, true);
        }

        /// <summary>
        /// Aborts the active measurement on the specified channels.
        /// </summary>
        /// <exception cref="System.NullReferenceException">Not connected to a channel.</exception>
        /// <exception cref="System.Exception">The channel is not currently performing measurement</exception>
        public Task AbortMeasurementsAsync(int[] channels)
        {
            return RunAsyncAggregateExceptions((int channel) => AbortMeasurementTask(channel, false), channels);
        }

        /// <summary>
        /// Aborts all active measurements channels.
        /// </summary>
        /// <exception cref="System.NullReferenceException">Not connected to a channel.</exception>
        /// <exception cref="System.Exception">The channel is not currently performing measurement</exception>
        public Task AbortAllActiveMeasurementsAsync()
        {
            var activeChannels = _activeSimpleMeasurements.Keys.ToArray(); //TODO: possible improvement is to use concurrent dictionary
            return AbortMeasurementsAsync(activeChannels);
        }

        /// <summary>
        /// Turns the cell on on specified channel.
        /// </summary>
        /// <param name="channel">The channel.</param>
        /// <returns></returns>
        /// <exception cref="System.NullReferenceException">Not connected to a channel</exception>
        /// <exception cref="System.Exception">Channel must be in idle mode for manual control</exception>
        public Task TurnCellOnAsync(int channel)
        {
            return TurnCellOnTask(channel, true);
        }

        /// <summary>Turns the cell on task.</summary>
        /// <param name="channel">The index of the channel.</param>
        /// <param name="throwExceptions">if set to <c>true</c> [throw on exceptions], otherwise return them.</param>
        /// <returns>A ValueTuple containing the channel index and any exceptions that were thrown</returns>
        private Task<(int ChannelIndex, Exception Exception)> TurnCellOnTask(int channel, bool throwExceptions)
        {
            return RunAsync((int channelIndex, CommManager comm) => {
                if (comm.State != CommManager.DeviceState.Idle)
                    throw new Exception($"Channel {channelIndex} must be in idle mode for manual control");
                if (comm.CellOn)
                    return Task.CompletedTask;
                try
                {
                    return comm.SetCellOnAsync(true);
                }
                catch (Exception e)
                {
                    throw new Exception($"Failed to turn on cell on channel {channelIndex}.", e);
                }
            }, channel, throwExceptions);
        }

        /// <summary>
        /// Turns the cell on on specified channels.
        /// </summary>
        /// <param name="channels">The channels.</param>
        /// <returns></returns>
        /// <exception cref="System.NullReferenceException">Not connected to a channel</exception>
        /// <exception cref="System.Exception">Channel must be in idle mode for manual control</exception>
        public Task TurnCellOnAsync(int[] channels)
        {
            return RunAsyncAggregateExceptions((int channel) => TurnCellOnTask(channel, false), channels);
        }

        /// <summary>
        /// Turns the cell on on all channels.
        /// </summary>
        /// <exception cref="System.NullReferenceException">Not connected to a channel</exception>
        /// <exception cref="System.Exception">Channel must be in idle mode for manual control</exception>
        public Task TurnCellOnAsync()
        {
            return TurnCellOnAsync(AllChannels);
        }

        /// <summary>
        /// Turns the cell off on specified channel.
        /// </summary>
        /// <param name="channel">The channel.</param>
        /// <returns></returns>
        /// <exception cref="System.NullReferenceException">Not connected to a channel</exception>
        /// <exception cref="System.Exception">Channel must be in idle mode for manual control</exception>
        public Task TurnCellOffAsync(int channel)
        {
            return TurnCellOffTask(channel, true);
        }

        /// <summary>Turns the cell off on the specified channel.</summary>
        /// <param name="channel">The channel.</param>
        /// <param name="throwExceptions">if set to <c>true</c> [throw on exceptions], otherwise return them.</param>
        /// <returns>A ValueTuple containing the channel index and any exceptions that were thrown</returns>
        public Task<(int ChannelIndex, Exception Exception)> TurnCellOffTask(int channel, bool throwExceptions)
        {
            return RunAsync((int channelIndex, CommManager comm) => {
                if (comm.State != CommManager.DeviceState.Idle)
                    throw new Exception($"Channel {channelIndex} must be in idle mode for manual control");
                if (!comm.CellOn)
                    return Task.CompletedTask;
                try
                {
                    return comm.SetCellOnAsync(false);
                }
                catch (Exception e)
                {
                    throw new Exception($"Failed to turn off cell on channel {channelIndex}.", e);
                }
            }, channel, throwExceptions);
        }

        /// <summary>
        /// Turns the cell off on specified channels.
        /// </summary>
        /// <param name="channels">The channels.</param>
        /// <returns></returns>
        /// <exception cref="System.NullReferenceException">Not connected to a channel</exception>
        /// <exception cref="System.Exception">Channel must be in idle mode for manual control</exception>
        public Task TurnCellOffAsync(int[] channels)
        {
            return RunAsyncAggregateExceptions((int channel) => TurnCellOffTask(channel, false), channels);
        }

        /// <summary>
        /// Turns the cell off on all channels.
        /// </summary>
        /// <exception cref="System.NullReferenceException">Not connected to a channel</exception>
        /// <exception cref="System.Exception">Channel must be in idle mode for manual control</exception>
        public Task TurnCellOffAsync()
        {
            return TurnCellOffAsync(AllChannels);
        }

        /// <summary>
        /// Sets the cell potential on the specified channel.
        /// </summary>
        /// <param name="potential">The potential.</param>
        /// <param name="channel">The channel.</param>
        /// <returns></returns>
        /// <exception cref="System.NullReferenceException">Not connected to a channel</exception>
        /// <exception cref="System.Exception">Channel must be in idle mode for manual control</exception>
        public Task SetCellPotentialAsync(float potential, int channel)
        {
            return SetCellPotentialTask(potential, channel, true);
        }

        /// <summary>
        /// Sets the cell potential on the specified channel.
        /// </summary>
        /// <param name="potential">The potential.</param>
        /// <param name="channel">The channel.</param>
        /// <param name="throwExceptions">if set to <c>true</c> [throw on exceptions], otherwise return them.</param>
        /// <returns>A ValueTuple containing the channel index and any exceptions that were thrown</returns>
        private Task<(int ChannelIndex, Exception Exception)> SetCellPotentialTask(float potential, int channel, bool throwExceptions)
        {
            return RunAsync((int channelIndex, CommManager comm) => {
                if (comm.State != CommManager.DeviceState.Idle)
                    throw new Exception($"Channel {channelIndex} must be in idle mode for manual control");
                try
                {
                    return comm.SetPotentialAsync(potential);
                }
                catch (Exception e)
                {
                    throw new Exception($"Failed to set cell potential on channel {channelIndex}.", e);
                }
            }, channel, throwExceptions);
        }

        /// <summary>
        /// Sets the cell potential on the specified channels.
        /// </summary>
        /// <param name="potential">The potential.</param>
        /// <param name="channel">The channel.</param>
        /// <returns></returns>
        /// <exception cref="System.NullReferenceException">Not connected to a channel</exception>
        /// <exception cref="System.Exception">Channel must be in idle mode for manual control</exception>
        public Task SetCellPotentialAsync(float potential, int[] channels)
        {
            return RunAsyncAggregateExceptions((int channel) => SetCellPotentialTask(potential, channel, false), channels);
        }

        /// <summary>
        /// Sets the cell potential on all channels.
        /// </summary>
        /// <param name="potential">The potential.</param>
        /// <param name="channel">The channel.</param>
        /// <returns></returns>
        /// <exception cref="System.NullReferenceException">Not connected to a channel</exception>
        /// <exception cref="System.Exception">Channel must be in idle mode for manual control</exception>
        public Task SetCellPotentialAsync(float potential)
        {
            return SetCellPotentialAsync(potential, AllChannels);
        }

        /// <summary>
        /// Reads the cell potential on the specified channel.
        /// </summary>
        /// <param name="channel">The channel.</param>
        /// <returns></returns>
        /// <exception cref="System.NullReferenceException">Not connected to any channels.
        /// or
        /// Not connected to a channel</exception>
        /// <exception cref="System.Exception">Channel must be in idle mode for manual control</exception>
        /// <exception cref="NullReferenceException">Not connected to a channel</exception>
        /// <exception cref="Exception">Channel must be in idle mode for manual control</exception>
        public async Task<float> ReadCellPotentialAsync(int channel)
        {
            return (await ReadCellPotentialTask(channel, true)).Potential;
        }

        /// <summary>
        /// Reads the cell potential on the specified channel.
        /// </summary>
        /// <param name="channel">The channel.</param>
        /// <param name="throwExceptions">if set to <c>true</c> [throw on exceptions], otherwise return them.</param>
        /// <returns>A ValueTuple containing the potential, the channel index and any exceptions that were thrown</returns>
        private Task<(float Potential, int ChannelIndex, Exception Exception)> ReadCellPotentialTask(int channel, bool throwExceptions)
        {
            return RunAsync<float>((int chan, CommManager comm) => {
                if (comm == null)
                    throw new NullReferenceException("Not connected to a channel");
                if (comm.State != CommManager.DeviceState.Idle)
                    throw new Exception("Channel must be in idle mode for manual control");
                try
                {
                    return comm.GetPotentialAsync();
                }
                catch (Exception e)
                {
                    throw new Exception($"Failed to read cell potential on channel {chan}", e);
                }
            }, channel, throwExceptions);
        }

        /// <summary>
        /// Reads the cell potential on the specified channels.
        /// </summary>
        /// <param name="channel">The channel.</param>
        /// <returns></returns>
        /// <exception cref="System.NullReferenceException">Not connected to any channels.
        /// or
        /// Not connected to a channel</exception>
        /// <exception cref="System.Exception">Channel must be in idle mode for manual control</exception>
        /// <exception cref="NullReferenceException">Not connected to a channel</exception>
        /// <exception cref="Exception">Channel must be in idle mode for manual control</exception>
        public Task<IReadOnlyList<(float Potential, int ChannelIndex, Exception Exception)>> ReadCellPotentialAsync(int[] channels)
        {
            return GetTaskResultsAndOrExceptions((int channel) => ReadCellPotentialTask(channel, false), channels);
        }

        /// <summary>
        /// Reads the cell potential on all channels.
        /// </summary>
        /// <returns></returns>
        /// <exception cref="System.NullReferenceException">Not connected to any channels.
        /// or
        /// Not connected to a channel</exception>
        /// <exception cref="System.Exception">Channel must be in idle mode for manual control</exception>
        /// <exception cref="NullReferenceException">Not connected to a channel</exception>
        /// <exception cref="Exception">Channel must be in idle mode for manual control</exception>
        public Task<IReadOnlyList<(float Potential, int ChannelIndex, Exception Exception)>> ReadCellPotentialAsync()
        {
            return ReadCellPotentialAsync(AllChannels);
        }

        /// <summary>
        /// Sets the cell current on the specified channel.
        /// </summary>
        /// <param name="current">The current.</param>
        /// <param name="channel">The channel.</param>
        /// <returns></returns>
        /// <exception cref="System.NullReferenceException">Not connected to a channel</exception>
        /// <exception cref="System.Exception">Channel must be in idle mode for manual control</exception>
        public Task SetCellCurrentAsync(float current, int channel)
        {
            return SetCellCurrentTask(current, channel, true);
        }

        /// <summary>
        /// Sets the cell current on the specified channel.
        /// </summary>
        /// <param name="current">The current.</param>
        /// <param name="channel">The channel.</param>
        /// <param name="throwExceptions">if set to <c>true</c> [throw on exceptions], otherwise return them.</param>
        /// <returns>A ValueTuple containing the channel index and any exceptions that were thrown</returns>
        private Task<(int ChannelIndex, Exception Exception)> SetCellCurrentTask(float current, int channel, bool throwExceptions)
        {
            return RunAsync((int channelIndex, CommManager comm) => {
                if (comm.State != CommManager.DeviceState.Idle)
                    throw new Exception($"Channel {channelIndex} must be in idle mode for manual control");
                if (!comm.Capabilities.IsGalvanostat)
                    throw new Exception("Channel does not support Galvanostat mode");
                try
                {
                    return comm.SetCurrentAsync(current);
                }
                catch (Exception e)
                {
                    throw new Exception($"Failed to set cell current on channel {channelIndex}.", e);
                }
            }, channel, throwExceptions);
        }

        /// <summary>
        /// Sets the cell current on the specified channels.
        /// </summary>
        /// <param name="current">The current.</param>
        /// <param name="channel">The channel.</param>
        /// <returns></returns>
        /// <exception cref="System.NullReferenceException">Not connected to a channel</exception>
        /// <exception cref="System.Exception">Channel must be in idle mode for manual control</exception>
        public Task SetCellCurrentAsync(float current, int[] channels)
        {
            return RunAsyncAggregateExceptions((int channel) => SetCellCurrentTask(current, channel, false), channels);
        }

        /// <summary>
        /// Sets the cell current on all channels.
        /// </summary>
        /// <param name="current">The current.</param>
        /// <param name="channel">The channel.</param>
        /// <returns></returns>
        /// <exception cref="System.NullReferenceException">Not connected to a channel</exception>
        /// <exception cref="System.Exception">Channel must be in idle mode for manual control</exception>
        public Task SetCellCurrentAsync(float current)
        {
            return SetCellCurrentAsync(current, AllChannels);
        }

        /// <summary>
        /// Reads the cell current on the specified channel.
        /// </summary>
        /// <returns></returns>
        /// <exception cref="NullReferenceException">Not connected to a channel</exception>
        /// <exception cref="Exception">Channel must be in idle mode for manual control</exception>
        public async Task<float> ReadCellCurrentAsync(int channel)
        {
            return (await ReadCellCurrentTask(channel, true)).Current;
        }

        /// <summary>
        /// Reads the cell current on the specified channel.
        /// </summary>
        /// <param name="channel">The channel.</param>
        /// <param name="throwExceptions">if set to <c>true</c> [throw on exceptions], otherwise return them.</param>
        /// <returns>A ValueTuple containing the current, the channel index and any exceptions that were thrown</returns>
        private Task<(float Current, int ChannelIndex, Exception Exception)> ReadCellCurrentTask(int channel, bool throwExceptions)
        {
            return RunAsync<float>((int chan, CommManager comm) => {
                if (comm == null)
                    throw new NullReferenceException("Not connected to a channel");
                if (comm.State != CommManager.DeviceState.Idle)
                    throw new Exception("Channel must be in idle mode for manual control");
                try
                {
                    return comm.GetCurrentAsync();
                }
                catch (Exception e)
                {
                    throw new Exception($"Failed to read cell current on channel {chan}", e);
                }
            }, channel, throwExceptions);
        }

        /// <summary>
        /// Reads the cell current on the specified channels.
        /// </summary>
        /// <returns></returns>
        /// <exception cref="NullReferenceException">Not connected to a channel</exception>
        /// <exception cref="Exception">Channel must be in idle mode for manual control</exception>
        public Task<IReadOnlyList<(float Current, int ChannelIndex, Exception Exception)>> ReadCellCurrentAsync(int[] channels)
        {
            return GetTaskResultsAndOrExceptions((int channel) => ReadCellCurrentTask(channel, false), channels);
        }

        /// <summary>
        /// Reads the cell current on all channels.
        /// </summary>
        /// <returns></returns>
        /// <exception cref="NullReferenceException">Not connected to a channel</exception>
        /// <exception cref="Exception">Channel must be in idle mode for manual control</exception>
        public Task<IReadOnlyList<(float Current, int ChannelIndex, Exception Exception)>> ReadCellCurrentAsync()
        {
            return ReadCellCurrentAsync(AllChannels);
        }

        /// <summary>
        /// Sets the current range on the specified channel.
        /// </summary>
        /// <param name="currentRange">The current range.</param>
        /// <exception cref="System.NullReferenceException">Not connected to a channel</exception>
        /// <exception cref="System.Exception">Channel must be in idle mode for manual control</exception>
        public Task SetCurrentRangeAsync(CurrentRange currentRange, int channel)
        {
            return SetCurrentRangeTask(currentRange, channel, true);
        }

        /// <summary>
        /// Sets the current range on the specified channel.
        /// </summary>
        /// <param name="currentRange">The current range.</param>
        /// <param name="channel">The channel.</param>
        /// <param name="throwExceptions">if set to <c>true</c> [throw exceptions].</param>
        /// <returns></returns>
        private Task<(int ChannelIndex, Exception Exception)> SetCurrentRangeTask(CurrentRange currentRange, int channel, bool throwExceptions)
        {
            return RunAsync((int channelIndex, CommManager comm) => {
                if (comm.State != CommManager.DeviceState.Idle)
                    throw new Exception($"Channel {channelIndex} must be in idle mode for manual control");

                try
                {
                    return comm.SetCurrentRangeAsync(currentRange);
                }
                catch (Exception e)
                {
                    throw new Exception($"Failed to set cell current on channel {channelIndex}.", e);
                }
            }, channel, throwExceptions);
        }

        /// <summary>
        /// Sets the current range on the specified channels.
        /// </summary>
        /// <param name="currentRange">The current range.</param>
        /// <exception cref="System.NullReferenceException">Not connected to a channel</exception>
        /// <exception cref="System.Exception">Channel must be in idle mode for manual control</exception>
        public Task SetCurrentRangeAsync(CurrentRange currentRange, int[] channels)
        {
            return RunAsyncAggregateExceptions((int channel) => SetCurrentRangeTask(currentRange, channel, false), channels);
        }

        /// <summary>
        /// Sets the current range on all channels.
        /// </summary>
        /// <param name="currentRange">The current range.</param>
        /// <exception cref="System.NullReferenceException">Not connected to a channel</exception>
        /// <exception cref="System.Exception">Channel must be in idle mode for manual control</exception>
        public Task SetCurrentRangeAsync(CurrentRange currentRange)
        {
            return SetCurrentRangeAsync(currentRange, AllChannels);
        }

        /// <summary>
        /// Validates whether the specified method is compatible with the capabilities of the specified connected channel.
        /// </summary>
        /// <param name="method">The method containing the measurement parameters.</param>
        /// <param name="channel">The specified channel.</param>
        /// <param name="isValidMethod">if set to <c>true</c> [is valid method].</param>
        /// <param name="errors">The errors.</param>
        /// <exception cref="System.NullReferenceException">Not connected to a channel.</exception>
        /// <exception cref="System.ArgumentNullException">The specified method cannot be null.</exception>
        public void ValidateMethod(Method method, int channel, out bool isValidMethod, out List<string> errors)
        {
            if (!Connected)
                throw new NullReferenceException("Not connected to any channel.");
            if (method == null)
                throw new ArgumentNullException("The specified method cannot be null.");
            errors = new List<string>();

            //Get a list of method compatability warnings and errors for the connected channel
            List<MethodError> methodErrors = method.Validate(_commsByChannelIndex[channel].Capabilities);

            //Check wheteher the channel can perform the measurement described in the method
            isValidMethod = !(methodErrors.Where(c => c.IsFatal == true).Any());

            //Build a list of the warnings and errors
            foreach (MethodError error in methodErrors)
                errors.Add($"{error.Parameter.ToString()}: {error.Message}");
        }

        /// <summary>
        /// Validates whether the specified method is compatible with the capabilities of the specified connected channels.
        /// </summary>
        /// <param name="method">The method containing the measurement parameters.</param>
        /// <param name="channels">The specified channels.</param>
        /// <param name="isValidMethod">if set to <c>true</c> [is valid method].</param>
        /// <param name="errors">The errors.</param>
        /// <exception cref="System.NullReferenceException">Not connected to a channel.</exception>
        /// <exception cref="System.ArgumentNullException">The specified method cannot be null.</exception>
        public void ValidateMethod(Method method, int[] channels, out bool[] isValidMethod, out List<string>[] errors)
        {
            int n = channels.Length;
            isValidMethod = new bool[n];
            errors = new List<string>[n];

            for (int i = 0; i < n; i++)
            {
                bool valid;
                List<string> error;
                ValidateMethod(method, channels[i], out valid, out error);
                isValidMethod[i] = valid;
                errors[i] = error;
            }
        }

        /// <summary>
        /// Validates whether the specified method is compatible with the capabilities of all connected channels.
        /// </summary>
        /// <param name="method">The method containing the measurement parameters.</param>
        /// <param name="isValidMethod">if set to <c>true</c> [is valid method].</param>
        /// <param name="errors">The errors.</param>
        /// <exception cref="System.NullReferenceException">Not connected to a channel.</exception>
        /// <exception cref="System.ArgumentNullException">The specified method cannot be null.</exception>
        public void ValidateMethod(Method method, out bool[] isValidMethod, out List<string>[] errors)
        {
            ValidateMethod(method, AllChannels, out isValidMethod, out errors);
        }

        /// <summary>
        /// Adds the active curve and its respective to the collection and subscribes to its events.
        /// </summary>
        /// <param name="activeCurve">The active curve.</param>
        private SimpleCurve SetActiveSimpleCurve(Curve activeCurve, CommManager comm)
        {
            if (activeCurve == null || comm == null)
                return null;

            SimpleMeasurement activeSimpleMeasurement = _activeSimpleMeasurements[comm.ChannelIndex];
            SimpleCurve activeSimpleCurve = activeSimpleMeasurement.SimpleCurveCollection.Where(sc => sc.Curve == activeCurve).FirstOrDefault();

            if (activeSimpleCurve == null)
            {
                activeSimpleCurve = new SimpleCurve(activeCurve, activeSimpleMeasurement);
                activeSimpleMeasurement.AddSimpleCurve(activeSimpleCurve);
            }

            return activeSimpleCurve;
        }

        /// <summary>
        /// Runs an async Func delegate asynchronously on the clientconnections taskscheduler.
        /// </summary>
        /// <param name="func">The action.</param>
        /// <param name="comm">The connection to run the delegate on.</param>
        /// <returns></returns>
        private async Task<(int, Exception)> RunAsync(Func<int, CommManager, Task> func, int channel, bool throwExceptions = true)
        {
            Exception ex = null;

            try
            {
                await new SynchronizationContextRemover();

                if (!Connected)
                {
                    throw new NullReferenceException("Not connected to any channels.");
                }

                if (!_commsByChannelIndex.ContainsKey(channel))
                {
                    throw new ArgumentException($"Not connected to specified channel: {channel}.");
                }

                CommManager comm = _commsByChannelIndex[channel];

                if (comm == null)
                {
                    throw new NullReferenceException($"Not connected to specified channel: {channel}.");
                }

                await comm.ClientConnection.RunAsync(() => func(channel, comm));
            }
            catch (Exception e)
            {
                ex = e;
                if(throwExceptions) throw ex;
            }

            return (channel, ex);
        }

        /// <summary>
        /// Runs an async Func delegate asynchronously on the clientconnections taskscheduler.
        /// </summary>
        /// <typeparam name="T"></typeparam>
        /// <param name="func">The action.</param>
        /// <param name="comm">The connection to run the delegate on.</param>
        /// <returns></returns>
        private async Task<(T, int, Exception)> RunAsync<T>(Func<int, CommManager, Task<T>> func, int channel, bool throwExceptions = true)
        {
            Exception ex = null;
            T result = default(T);

            try
            {
                await new SynchronizationContextRemover();

                if (!Connected)
                {
                    throw new NullReferenceException("Not connected to any channels.");
                }

                if (!_commsByChannelIndex.ContainsKey(channel))
                {
                    throw new ArgumentException($"Not connected to specified channel: {channel}.");
                }

                CommManager comm = _commsByChannelIndex[channel];

                if (comm == null)
                {
                    throw new NullReferenceException($"Not connected to specified channel: {channel}.");
                }

                result = await comm.ClientConnection.RunAsync(() => func(channel, comm));
            }
            catch (Exception e)
            {
                ex = e;
                if (throwExceptions) throw ex;
            }

            return (result, channel, ex);
        }

        /// <summary>
        /// Runs a Func delegate asynchronously on the specified channels and aggregates any exceptions
        /// </summary>
        /// <param name="func"></param>
        /// <param name="channels"></param>
        /// <returns></returns>
        public static async Task RunAsyncAggregateExceptions(Func<int, Task<(int ChannelIndex, Exception Exception)>> func, int[] channels)
        {
            int n = channels.Length;

            Task<(int ChannelIndex, Exception Exception)>[] tasks = new Task<(int channelIndex, Exception exception)>[n];

            for (int i = 0; i < n; i++)
                tasks[i] = func(channels[i]);

            var result = await Task.WhenAll(tasks);

            List<Exception> exceptions = new List<Exception>();
            foreach (var channel in result)
            {
                if (channel.Exception != null)
                    exceptions.Add(new MultiChannelInstrumentException(channel.ChannelIndex, channel.Exception));
            }

            if (exceptions.Count > 0) throw new AggregateException(exceptions);
        }

        /// <summary>
        /// Runs an Func delegate asynchronously on the specified channels and handles any exceptions preventing successful results from being returned
        /// unless throwExceptions is specifically set to true
        /// </summary>
        /// <typeparam name="T"></typeparam>
        /// <param name="func"></param>
        /// <param name="channels"></param>
        /// <param name="throwExceptions">Set to false by default to prevent an exception on one channel interfering with the results of other channels</param>
        /// <returns></returns>
        public static async Task<IReadOnlyList<(T Result, int ChannelIndex, Exception Exception)>> GetTaskResultsAndOrExceptions<T>(Func<int, Task<(T Result, int ChannelIndex, Exception Exception)>> func, IList<int> channels)
        {
            int n = channels.Count;

            Task<(T Result, int ChannelIndex, Exception Exception)>[] tasks = new Task<(T Result, int ChannelIndex, Exception Exception)>[n];
            var results = new (T Result, int ChannelIndex, Exception Exception)[n];

            for (int i = 0; i < n; i++)
            {
                int channel = channels[i];
                int index = i;
                Func<Task<(T Result, int ChannelIndex, Exception Exception)>> wrappedFunc = async () =>
                {
                    try
                    {
                        var result = await func(channel);
                        return result;
                    }
                    catch (Exception exception)
                    {
                        var ex = new MultiChannelInstrumentException(channel, exception);
                        return (default(T), channel, ex);
                    }
                };
                tasks[index] = wrappedFunc();
            }

            results = await Task.WhenAll(tasks);

            return results;
        }

        /// <summary>
        /// Get an internal storage handler that will read the current connected device stored files. This is only for devices that have internal storage.
        /// </summary>
        /// <exception cref="InvalidOperationException">This is thrown when the device is not connected or if the device does not support storage.</exception>
        /// <exception cref="ArgumentException">This is thrown when the channel passed in does not exist in the current communications mapping.</exception>
        /// <returns>A new instance of the internal storage handler for the current connection.</returns>
        public IInternalStorageBrowser GetInternalStorageHandler(int channel)
        {
            if (!Connected)
                throw new InvalidOperationException("There is no device currently connected. Please connect to a device.");


            if (!_commsByChannelIndex.TryGetValue(channel, out var comm))
            {
                throw new ArgumentException($"Not connected to specified channel: {channel}.");
            }

            if (!comm.Capabilities.SupportsStorage)
                throw new InvalidOperationException($"The connected device '{comm.DeviceType}' does not support internal storage.");

            return new InternalStorageBrowser(comm.ClientConnection);
        }
        #endregion

        #region events
        /// <summary>
        /// Occurs when a channel status package is received, these packages are not sent during a measurement.
        /// </summary>
        public event MultiChannelStatusEventHandler ReceiveStatus;

        /// <summary>
        /// Casts ReceiveStatus events coming from a different thread to the UI thread when necessary.
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="StatusEventArgs" /> instance containing the channel status.</param>
        /// <exception cref="System.NullReferenceException">Platform not set.</exception>
        private Task Comm_ReceiveStatusAsync(object sender, StatusEventArgs e)
        {
            if (_platformInvoker == null)
                throw new NullReferenceException("PlatformInvoker not set.");

            CommManager comm = Comms.FirstOrDefault(c => c.ClientConnection == sender);
            if (comm == null)
                throw new NullReferenceException("Sender no longer in connected Comms list");

            if (!_platformInvoker.InvokeIfRequired(
                (MultiChannelStatusEventHandler)((multiComm, status, channel) =>
                {
                    ReceiveStatus?.Invoke(multiComm, status, channel);
                }), this, e, comm.ChannelIndex)) //Recast event to UI thread when necessary
            {
                ReceiveStatus?.Invoke(this, e, comm.ChannelIndex);
            }

            return Task.CompletedTask;
        }

        /// <summary>
        /// Occurs at the start of a new measurement.
        /// </summary>
        public event MultiChannelMeasurementEventHandler MeasurementStarted;

        /// <summary>
        /// Sets the ActiveMeasurement at the start of a measurement and casts BeginMeasurement events coming from a different thread to the UI thread when necessary.
        /// </summary>
        /// <param name="sender">The sender.</param>
        /// <param name="e">The new measurement.</param>
        /// <exception cref="System.NullReferenceException">PlatformInvoker not set.</exception>
        private Task Comm_BeginMeasurementAsync(object sender, CommManager.BeginMeasurementEventArgsAsync e)
        {
            if (_platformInvoker == null)
                throw new NullReferenceException("PlatformInvoker not set.");

            CommManager comm = sender as CommManager;

            if (!_platformInvoker.InvokeIfRequired(
                (MultiChannelMeasurementEventHandler) ((multiComm, channel, args) =>
                {
                    MeasurementStarted?.Invoke(multiComm, channel, args);
                }), this, comm.ChannelIndex, null)) //Recast event to UI thread when necessary
            {
                MeasurementStarted?.Invoke(this, comm.ChannelIndex, null);
            }

            return Task.CompletedTask;
        }

        /// <summary>
        /// Occurs when a measurement has ended.
        /// </summary>
        public event MultiChannelMeasurementEventHandler MeasurementEnded;

        /// <summary>
        /// Sets the ActiveMeasurement to null at the end of the measurement and casts EndMeasurement events coming from a different thread to the UI thread when necessary.
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="EventArgs" /> instance containing the event data.</param>
        /// <exception cref="System.NullReferenceException">PlatformInvoker not set.</exception>
        private Task Comm_EndMeasurementAsync(object sender, EventArgs e)
        {
            if (_platformInvoker == null)
                throw new NullReferenceException("PlatformInvoker not set.");

            CommManager comm = sender as CommManager;
            Exception exception = null;
            if (_commErrorExceptions.ContainsKey(comm))
                exception = _commErrorExceptions[comm];
            _activeSimpleMeasurements.TryRemove(comm.ChannelIndex, out _);

            if (!_platformInvoker.InvokeIfRequired(
                (MultiChannelMeasurementEventHandler) ((multiComm, channel, ex) =>
                {
                    MeasurementEnded?.Invoke(multiComm, channel, ex);
                }), this, comm.ChannelIndex, exception)) //Recast event to UI thread when necessary
            {
                MeasurementEnded?.Invoke(this, comm.ChannelIndex, exception);
            }

            return Task.CompletedTask;
        }

        /// <summary>
        /// Adds the active Curve to the active SimpleMeasurement and casts BeginReceiveCurve events coming from a different thread to the UI thread when necessary.
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="CurveEventArgs"/> instance containing the event data.</param>
        /// <exception cref="System.NullReferenceException">PlatformInvoker not set.</exception>
        private void Comm_BeginReceiveCurve(object sender, CurveEventArgs e)
        {
            if (_platformInvoker == null)
                throw new NullReferenceException("PlatformInvoker not set.");

            var activeSimpleCurve = SetActiveSimpleCurve(e.GetCurve(), sender as CommManager);

            if (!_platformInvoker.InvokeIfRequired((PSCommSimple.SimpleCurveStartReceivingDataHandler)(
                    (multiComm, simpleCurve) =>
                    {
                        if (simpleCurve != null) SimpleCurveStartReceivingData?.Invoke(multiComm, simpleCurve);
                    }), this, activeSimpleCurve)) //Recast event to UI thread when necessary
            {
                if (activeSimpleCurve != null) SimpleCurveStartReceivingData?.Invoke(this, activeSimpleCurve);
            }
        }

        /// <summary>
        /// Occurs when a new [SimpleCurve starts receiving data].
        /// </summary>
        public event PSCommSimple.SimpleCurveStartReceivingDataHandler SimpleCurveStartReceivingData;

        /// <summary>
        /// Occurs when the devive's [state changed].
        /// </summary>
        public event MultiChannelStateChangedEventHandler StateChanged;

        /// <summary>
        /// Casts StateChanged events coming from a different thread to the UI thread when necessary.
        /// </summary>
        /// <param name="sender">The sender.</param>
        /// <param name="e">State of the current.</param>
        /// <exception cref="System.NullReferenceException">PlatformInvoker not set.</exception>
        private Task Comm_StateChangedAsync(object sender, CommManager.StateChangedAsyncEventArgs e)
        {
            if (_platformInvoker == null)
                throw new NullReferenceException("PlatformInvoker not set.");

            CommManager comm = sender as CommManager;

            if (!_platformInvoker.InvokeIfRequired(
                (MultiChannelStateChangedEventHandler) ((multiComm, state, channel) =>
                {
                    StateChanged?.Invoke(multiComm, state, channel);
                }), this, e.State, comm.ChannelIndex)) //Recast event to UI thread when necessary
            {
                StateChanged?.Invoke(this, e.State, comm.ChannelIndex);
            }

            return Task.CompletedTask;
        }

        /// <summary>
        /// Occurs when a channel is [disconnected].
        /// </summary>
        public event MultiChannelDisconnectedEventHandler Disconnected;

        /// <summary>
        /// Raises the Disconnected event.
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="EventArgs"/> instance containing the event data.</param>
        /// <exception cref="System.NotImplementedException"></exception>
        private void Comm_Disconnected(object sender, EventArgs e)
        {
            if (_platformInvoker == null)
                throw new NullReferenceException("PlatformInvoker not set.");

            CommManager comm = sender as CommManager;
            Exception exception = _commErrorExceptions.ContainsKey(comm) ? _commErrorExceptions[comm] : null;

            if (exception != null) //Remove the channel from the managed connections when disconnected due to comm error
                RemoveComms(new (int channelIndex, Exception exception)[] { (comm.ChannelIndex, null) });

            if (_commErrorExceptions.ContainsKey(comm))
                _commErrorExceptions.TryRemove(comm, out _);

            if (!_platformInvoker.InvokeIfRequired(
                (MultiChannelDisconnectedEventHandler) ((multiComm, ex, channel, device) =>
                {
                    Disconnected?.Invoke(multiComm, ex, channel, device);
                }), this, exception, comm.ChannelIndex, comm.Device)) //Recast event to UI thread when necessary
            {
                Disconnected?.Invoke(this, exception, comm.ChannelIndex, comm.Device);
            }
        }

        /// <summary>
        /// The latest comm error exception, this is used for the disconnected event and is set back to null directly after it is raised
        /// </summary>
        private ConcurrentDictionary<CommManager, Exception> _commErrorExceptions = new ConcurrentDictionary<CommManager, Exception>();

        /// <summary>
        /// Comms the comm error occorred.
        /// </summary>
        /// <param name="exception">The exception.</param>
        /// <exception cref="System.NotImplementedException"></exception>
        private void Comm_CommErrorOccurred(object sender, Exception exception)
        {
            if (_platform == null)
                throw new NullReferenceException("Platform not set.");

            CommManager comm = sender as CommManager;
            _commErrorExceptions.TryAdd(comm, exception);

            if (_activeSimpleMeasurements.ContainsKey(comm.ChannelIndex))
            {
                Comm_EndMeasurementAsync(sender, EventArgs.Empty);
            }
        }
        #endregion

        public void Dispose()
        {
            if (Connected)
                foreach (CommManager comm in Comms)
                    comm.Dispose();
            PalmSens.Devices.Device.DisposeAsyncQueues();
            _commsByChannelIndex.Clear();
            _commsByChannelIndex = null;
            _activeSimpleMeasurements.Clear();
            _activeSimpleMeasurements = null;
            _commErrorExceptions.Clear();
            _commErrorExceptions = null;
        }
    }

    public class MultiChannelInstrumentException : Exception
    {
        public int ChannelIndex { get; }

        public MultiChannelInstrumentException(int channel) : base($"Exception occurred on channel {channel}")
        {
            ChannelIndex = channel;
        }

        public MultiChannelInstrumentException(int channel, string message) : base(message)
        {
            ChannelIndex = channel;
        }

        public MultiChannelInstrumentException(int channel, Exception innerException) : base($"Exception occurred on channel {channel}", innerException)
        {
            ChannelIndex = channel;
        }

        public MultiChannelInstrumentException(int channel, string message, Exception innerException) : base(message, innerException)
        {
            ChannelIndex = channel;
        }
    }

    #region MultiChannelEventHandlers
    /// <summary>
    /// MultiChannelEventHandler that includes which channel the event was raised by
    /// </summary>
    /// <param name="sender">The sender.</param>
    /// <param name="channel">The channel.</param>
    public delegate void MultiChannelMeasurementEventHandler(object sender, int channel, Exception exception);

    /// <summary>
    /// EventHandler that reports changes in the DeviceState of a channel
    /// </summary>
    /// <param name="sender">The sender.</param>
    /// <param name="ChannelState">State of the channel.</param>
    /// <param name="channel">The channel.</param>
    public delegate void MultiChannelStateChangedEventHandler(object sender, CommManager.DeviceState ChannelState, int channel);

    /// <summary>
    /// EventHandler that reports idle status readings of a channel
    /// </summary>
    /// <param name="sender">The sender.</param>
    /// <param name="status">The <see cref="StatusEventArgs"/> instance containing the event data.</param>
    /// <param name="channel">The channel.</param>
    public delegate void MultiChannelStatusEventHandler(object sender, StatusEventArgs status, int channel);

    /// <summary>
    /// EventHandler that reports when a channel is disconnected if this was due to an exception this is also included
    /// </summary>
    /// <param name="sender">The sender.</param>
    /// <param name="exception">The exception.</param>
    /// <param name="channel">The channel.</param>
    public delegate void MultiChannelDisconnectedEventHandler(object sender, Exception exception, int channel, Device device);
    #endregion
}
