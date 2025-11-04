using System;
using System.Collections.Generic;
using System.Data;
using System.Diagnostics.Contracts;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using PalmSens.Annotations;
using PalmSens.Comm;
using PalmSens.Devices;
using PalmSens.Windows.Devices;

namespace PalmSens.Core.Simplified.WinUi
{
    public class DeviceHandler : IPlatform, IPlatformMulti
    {
        public bool EnableBluetooth = false;

        public bool EnableSerialPort = false;

        /// <summary>
        /// Scans for connected devices.
        /// </summary>
        /// <returns>
        /// Returns an array of connected devices
        /// </returns>
        /// <exception cref="System.ArgumentException">An error occured while attempting to scan for connected devices.</exception>
        public async Task<IReadOnlyList<Device>> GetAvailableDevices()
        {
            List<Device> devices = new List<Device>();
            string errors = "";

            await new SynchronizationContextRemover();

            try //Attempt to find connected palmsens/emstat devices
            {
                var discResults = await Task.Run(async () =>
                {
                    List<Task<List<Device>>> discFuncs = new List<Task<List<Device>>>();
                    //Add delegates to list for finding devices on specific communication protocols
                    discFuncs.Add(USBCDCDevice.DiscoverDevicesAsync()); //Default for PS4
                    discFuncs.Add(FTDIDevice.DiscoverDevicesAsync()); //Default for Emstat + PS3
                    discFuncs.Add(WinUSBDevice.DiscoverDevicesAsync()); //Default for ES4X
                    if (EnableSerialPort)
                        discFuncs.Add(SerialPortDevice.DiscoverDevicesAsync()); //Devices connected via serial port
                    if (EnableBluetooth)
                    {
                        discFuncs.Add(BluetoothDevice
                            .DiscoverDevicesAsync()); //Bluetooth devices (PS4, PS3, Emstat Blue)
                        discFuncs.Add(BLEDevice.DiscoverDevicesAsync()); //BLEDevices requires adding a reference to the PalmSens.Core.Windows.BLE.dll
                    }

                    //Return a new array of connected devices found with the included delegate functions 
                    return await Task.WhenAll(discFuncs);
                });
                foreach (List<Device> discDevices in discResults)
                    devices.AddRange(discDevices);
            }
            catch (Exception)
            {
                throw new ArgumentException($"An error occured while attempting to scan for connected devices. {Environment.NewLine} {errors}");
            }
            return devices.ToArray();
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
        public async Task<CommManager> Connect(Device device)
        {
            return (await ConnectAsync(device, channel: -1, throwExceptions: true)).Comm;
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
        internal async Task<(CommManager Comm, int ChannelIndex, Exception Exception)> ConnectAsync(Device device, int channel = -1, bool throwExceptions = true)
        {
            if (device == null)
                throw new ArgumentNullException("The specified device cannot be null.");
            CommManager comm = null;
            Exception ex = null;

            await new SynchronizationContextRemover();

            try
            {
                await Task.Run(async () =>
                {
                    await device.OpenAsync(); //Open the device to allow a connection
                    comm = await CommManager.CommManagerAsync(device); //Connect to the selected device
                });

                if (channel > -1)
                {
                    comm.ChannelIndex = channel;
                }
            }
            catch (Exception exception)
            {
                device.Close();
                ex = new Exception(channel > -1 ? $"Could not connect to channel {channel}" : "Could not connect to the specified device.", exception);
                if (throwExceptions) throw ex;
            }

            return (comm, channel, ex);
        }

        /// <summary>
        /// Connects to the specified devices and returns their CommManagers.
        /// </summary>
        /// <param name="devices">The devices.</param>
        /// <returns>
        /// The CommManagers
        /// </returns>
        /// <exception cref="ArgumentNullException">The specified devices cannot be null.</exception>
        public Task<IReadOnlyList<(CommManager Comm, int ChannelIndex, Exception Exception)>> Connect(IReadOnlyList<Device> devices, IList<int> channelIndices = null)
        {
            if (devices == null)
                throw new ArgumentNullException("The specified devices cannot be null.");

            if (channelIndices == null)
            {
                channelIndices = new int[devices.Count];
                for (int i = 0; i < devices.Count; i++)
                    channelIndices[i] = i;
            }

            return PalmSens.Core.Simplified.PSMultiCommSimple.GetTaskResultsAndOrExceptions(
                (int channel) => ConnectAsync(devices[channel], channel, false), channelIndices);
        }

        /// <summary>
        /// Disconnects the device using its CommManager.
        /// </summary>
        /// <param name="comm"></param>
        /// <returns></returns>
        public async Task Disconnect(CommManager comm)
        {
            await DisconnectAsync(comm, throwException: true);
        }

        /// <summary>
        /// Disconnects the device using its CommManager.
        /// </summary>
        /// <param name="comm">The device's CommManager.</param>
        /// <exception cref="System.ArgumentNullException">The specified CommManager cannot be null.</exception>
        internal async Task<(int channelIndex, Exception ex)> DisconnectAsync(CommManager comm, bool throwException = true)
        {
            Exception ex = null;
            int index = -1;
            if (comm == null)
                ex = new ArgumentNullException("The specified CommManager cannot be null.");
            else
            {
                index = comm.ChannelIndex;

                await new SynchronizationContextRemover();

                try
                {
                    await Task.Run(() => comm.DisconnectAsync());
                }
                catch (Exception exception)
                {
                    ex = new Exception(string.Format("Failed to connect{0}.", index == -1 ? "" : "to channel " + index.ToString()), exception);
                    if (throwException) throw ex;
                }
            }

            return (index, ex);
        }

        /// <summary>
        /// Disconnects the devices using their CommManagers.
        /// </summary>
        /// <param name="comms">The comms.</param>
        /// <exception cref="System.ArgumentNullException">The specified CommManager array cannot be null.</exception>
        public async Task<IReadOnlyList<(int ChannelIndex, Exception Exception)>> Disconnect(IReadOnlyList<CommManager> comms)
        {
            if (comms == null)
                throw new ArgumentNullException("The specified CommManager array cannot be null.");
            List<Task<(int, Exception)>> disconnectTasks = new List<Task<(int, Exception)>>();
            foreach (CommManager comm in comms)
                disconnectTasks.Add(DisconnectAsync(comm, false));
            IReadOnlyList<(int channelIndex, Exception exception)> result = await Task.WhenAll(disconnectTasks);

            List<Exception> exceptions = new List<Exception>();
            foreach (var channel in result)
            {
                if (channel.exception != null)
                    exceptions.Add(new Exception(string.Format("Failed to disconnect{0}.", channel.channelIndex == -1 ? "" : "to channel " + channel.channelIndex.ToString()), channel.exception));
            }

            return result;
        }

        public Task<Device> MatchDevices(Device deviceInErrorState)
        {
            throw new NotImplementedException();
        }
    }
}
