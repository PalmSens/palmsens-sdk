using PalmSens.Devices;
using PalmSens.Comm;
using PalmSens.Core.Android.Comm;
using PalmSens.Core.Android.Comm.BlueTooth;

namespace PalmSens.Core.Simplified.Android
{
    public class DeviceHandler : IPlatform
    {
        internal DeviceDiscoverer _deviceDiscoverer;

        internal bool EnableBluetooth = true;
        internal bool EnableUSB = true;

        /// <summary>
        /// Scans for connected devices.
        /// </summary>
        /// <param name="timeOut">Discovery time out in milliseconds.</param>
        /// <returns>
        /// Returns an array of connected devices
        /// </returns>
        /// <exception cref="System.ArgumentException">An error occured while attempting to scan for connected devices.</exception>
        internal async Task<IReadOnlyList<Device>> ScanDevicesAsync(int timeOut = 20000)
        {
            Device[] devices = new Device[0];

            await new SynchronizationContextRemover();

            try //Attempt to find connected palmsens/emstat devices
            {
                _deviceDiscoverer = new DeviceDiscoverer();
                devices = await Task.Run(async () => (await _deviceDiscoverer.Discover(EnableUSB, EnableBluetooth, timeOut: timeOut)).ToArray());
                _deviceDiscoverer.Dispose();
            }
            catch (Exception ex)
            {
                throw new ArgumentException($"An error occured while attempting to scan for connected devices. {ex.Message}");
            }
            return devices;
        }

        public Task<IReadOnlyList<Device>> GetAvailableDevices() => ScanDevicesAsync();

        /// <summary>
        /// Connects to the specified device and returns its CommManager.
        /// </summary>
        /// <param name="device">The device.</param>
        /// <returns>
        /// The CommManager of the device or null
        /// </returns>
        /// <exception cref="System.ArgumentNullException">The specified device cannot be null.</exception>
        /// <exception cref="System.Exception">Could not connect to the specified device.</exception>
        public async Task<CommManager> Connect(Device device)
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
        /// The asynchronous version of method 'Disconnect'.
        /// </summary>
        /// <param name="comm">The device's CommManager.</param>
        /// <exception cref="System.ArgumentNullException">The specified CommManager cannot be null.</exception>
        public async Task Disconnect(CommManager comm)
        {
            await new SynchronizationContextRemover();

            if (comm == null) throw new ArgumentNullException("The specified CommManager cannot be null.");
            await Task.Run(() => comm.DisconnectAsync());
        }
    }
}