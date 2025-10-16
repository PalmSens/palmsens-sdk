using System;
using System.Collections.ObjectModel;
using Android.Content;
using PalmSens.Devices;
using PalmSens.Comm;
using System.Threading.Tasks;
using Android.App;
using PalmSens.PSAndroid.Comm;
using OperationCanceledException = System.OperationCanceledException;

namespace PalmSens.Core.Simplified.Android
{
    public class DeviceHandler : IPlatform, IPlatformInvoker
    {
        internal bool EnableBluetooth = true;
        internal bool EnableUSB = true;
        private DeviceDiscoverer _deviceDiscoverer = null;
        private readonly ObservableCollection<Device> _devices = new ObservableCollection<Device>();
        private readonly ReadOnlyObservableCollection<Device> _devicesReadOnly;
        private readonly IPlatformInvoker _platformInvoker;

        public DeviceHandler(IPlatformInvoker platformInvoker)
        {
            _devicesReadOnly = new ReadOnlyObservableCollection<Device>(_devices);
            _platformInvoker = platformInvoker;
        }

        public bool InvokeIfRequired(Action action) => _platformInvoker.InvokeIfRequired(action);

        public ReadOnlyObservableCollection<Device> DiscoverAvailableDevices() => DiscoverAvailableDevices(TimeSpan.FromSeconds(20));

        public ReadOnlyObservableCollection<Device> DiscoverAvailableDevices(TimeSpan timeOut)
        {
            _devices.Clear();
            _deviceDiscoverer = new DeviceDiscoverer(Application.Context);

            //Start discovery in background
            Task.Run(async () => {
                try
                {
                    await new SynchronizationContextRemover();

                    EventHandler<Device> deviceDiscovered = (sender, device) =>
                    {
                        if (!InvokeIfRequired(() => _devices.Add(device)))
                        {
                            _devices.Add(device);
                        }
                    };

                    EventHandler<Device> deviceRemoved = (sender, device) =>
                    {
                        if (!InvokeIfRequired(() => _devices.Remove(device)))
                        {
                            _devices.Remove(device);
                        }
                    };

                    _deviceDiscoverer.DeviceDiscovered += deviceDiscovered;
                    _deviceDiscoverer.DeviceRemoved += deviceRemoved;

                    await _deviceDiscoverer.Discover(EnableUSB, EnableBluetooth,
                        timeOut: (int)timeOut.TotalMilliseconds);

                    AvailableDeviceDiscoveryCompleted?.Invoke(this, new ScanCompletedEventArgs(null));
                }
                catch (Exception ex) when (ex is not OperationCanceledException)
                {
                    AvailableDeviceDiscoveryCompleted?.Invoke(this, new ScanCompletedEventArgs(new ArgumentException(
                        $"An error occured while attempting to scan for connected devices. {ex.Message}")));
                }
                finally
                {
                    _deviceDiscoverer?.Dispose();
                    _deviceDiscoverer = null;
                }
            });

            return _devicesReadOnly;
        }

        public void CancelAvailableDeviceDiscovery()
        {
            _deviceDiscoverer?.Cancel();
        }

        public event EventHandler<ScanCompletedEventArgs> AvailableDeviceDiscoveryCompleted;

        public Task<CommManager> ConnectAsync(Device device) => Connect(device);

        /// <summary>
        /// Connects to the specified device and returns its CommManager.
        /// </summary>
        /// <param name="device">The device.</param>
        /// <returns>
        /// The CommManager of the device or null
        /// </returns>
        /// <exception cref="System.ArgumentNullException">The specified device cannot be null.</exception>
        /// <exception cref="System.Exception">Could not connect to the specified device.</exception>
        internal async Task<CommManager> Connect(Device device)
        {
            if (device == null)
                throw new ArgumentNullException("The specified device cannot be null.");
            CommManager comm = null;

            await new SynchronizationContextRemover();

            try
            {
                await Task.Run(async () =>
                {
                    await device.OpenAsync(); //Open the device to allow a connection
                    comm = await CommManager.CommManagerAsync(device); //Connect to the selected device
                });
                CheckSupportForFastBLC(device, comm);
            }
            catch (Exception ex)
            {
                device.Close();
                throw new Exception($"Could not connect to the specified device. {ex.Message}");
            }

            return comm;
        }

        /// <summary>
        /// Connects to the specified device and returns its CommManager.
        /// </summary>
        /// <param name="device">The device.</param>
        /// <returns>
        /// The CommManager of the device or null
        /// </returns>
        /// <exception cref="System.ArgumentNullException">The specified device cannot be null.</exception>
        /// <exception cref="System.Exception">Could not connect to the specified device.</exception>
        [Obsolete("Using the synchronous API on Android is discouraged.")]
        CommManager IPlatform.Connect(Device device) => ConnectBC(device);

        /// <summary>
        /// Connects to the specified device and returns its CommManager.
        /// </summary>
        /// <param name="device">The device.</param>
        /// <returns>
        /// The CommManager of the device or null
        /// </returns>
        /// <exception cref="System.ArgumentNullException">The specified device cannot be null.</exception>
        /// <exception cref="System.Exception">Could not connect to the specified device.</exception>
        [Obsolete("Compatible with SDKs 5.4 and earlier. Please use asynchronous functions, as development of synchronous functions will be fased out")]
        internal CommManager ConnectBC(Device device)
        {
            if (device == null)
                throw new ArgumentNullException("The specified device cannot be null.");
            CommManager comm = null;

            try
            {
                //TODO: See GitHub issue #1341 No sync BLE Support
                device.Open(); //Open the device to allow a connection
                comm = new CommManager(device); //Connect to the selected device
                CheckSupportForFastBLC(device, comm);
            }
            catch (Exception ex)
            {
                device.Close();
                throw new Exception($"Could not connect to the specified device. {ex.Message}");
            }

            return comm;
        }

        /// <summary>
        /// Checks and enables support for fast BLC.
        /// This only applies when connecting to a EmStat Pico Devboard,
        /// Sensit BT or EmStat Pico Go with the appropriate firmware.
        /// </summary>
        /// <param name="device">The device.</param>
        /// <param name="comm">The comm.</param>
        private static void CheckSupportForFastBLC(Device device, CommManager comm)
        {
            if (device is BlueToothDevice blcDevice
                && ((comm.DeviceType is enumDeviceType.EmStatPico && comm.ClientConnection.FirmwareVersion > 1.3f)
                    || (comm.DeviceType is enumDeviceType.EmStat4LR && comm.ClientConnection.FirmwareVersion > 1.09f)
                    || (comm.DeviceType is enumDeviceType.EmStat4HR && comm.ClientConnection.FirmwareVersion > 1.09f)))
                blcDevice.EnableReceiveMonitor("\u0016", 2500);
        }

        /// <summary>
        /// Disconnects the device using its CommManager.
        /// </summary>
        /// <param name="comm">The device's CommManager.</param>
        /// <exception cref="System.ArgumentNullException">The specified CommManager cannot be null.</exception>
        [Obsolete("Using the synchronous API on Android is discouraged.")]
        public void Disconnect(CommManager comm)
        {
            if (comm == null)
                throw new ArgumentNullException("The specified CommManager cannot be null.");

            TaskCompletionSource<bool> tcs = new TaskCompletionSource<bool>();
            EventHandler disconnected = (sender, args) => tcs.SetResult(true);
            comm.Disconnected += disconnected;
            comm.DisconnectAsync();
            tcs.Task.Wait();
            comm.Disconnected -= disconnected;
        }

        /// <summary>
        /// The asynchronous version of method 'Disconnect'.
        /// </summary>
        /// <param name="comm">The device's CommManager.</param>
        /// <exception cref="System.ArgumentNullException">The specified CommManager cannot be null.</exception>
        public async Task DisconnectAsync(CommManager comm)
        {
            await new SynchronizationContextRemover();

            if (comm == null) throw new ArgumentNullException("The specified CommManager cannot be null.");
            await Task.Run(() => comm.DisconnectAsync());
        }
    }
}
