using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using PalmSens.Comm;
using PalmSens.Devices;

namespace PalmSens.Core.Simplified
{
    public interface IPlatform
    {
        Task<IReadOnlyList<Device>> GetAvailableDevices();

        Task<CommManager> Connect(Device device);

        Task Disconnect(CommManager comm);
    }

    public interface IPlatformMulti
    {
        Task<IReadOnlyList<Device>> GetAvailableDevices();

        /// <summary>
        /// Connects to the specified channels.
        /// Warning use the platform independent method Connect() instead.
        /// Otherwise the generic PSMultiCommSimple does not subscribe to the CommManagers correctly
        /// </summary>
        /// <param name="devices">Array devices to connect to.</param>
        /// <param name="channelIndices">Array of unique indices for the specified channel (0, 1, 2, 3... by default)</param>
        Task<IReadOnlyList<(CommManager Comm, int ChannelIndex, Exception Exception)>> Connect(IReadOnlyList<Device> devices,
            IList<int> channelIndices = null);

        /// <summary>
        /// Disconnects from channel with the specified CommManagers. 
        /// Warning use the platform independent method Disconnect() instead.
        /// Otherwise the generic PSMultiCommSimple does not unsubscribe from the CommManagers correctly
        /// which may result in it not being released from the memory.
        /// </summary>
        /// <param name="comms">The comm.</param>
        Task<IReadOnlyList<(int ChannelIndex, Exception Exception)>> Disconnect(IReadOnlyList<CommManager> comms);

        /// <summary>
        /// Replaces the instance of a device with a new one if possible.
        /// This is used to recover a dropped connection.
        /// </summary>
        /// <param name="deviceInErrorState"></param>
        /// <returns></returns>
        Task<Device> MatchDevices(Device deviceInErrorState);
    }

    public interface IPlatformInvoker
    {
        /// <summary>
        /// Invokes if required.
        /// </summary>
        /// <param name="method">The method.</param>
        /// <param name="args">The arguments.</param>
        /// <returns></returns>
        bool InvokeIfRequired(Delegate method, params object[] args);

        /// <summary>
        /// Invokes if required.
        /// </summary>
        /// <param name="action">The action.</param>
        /// <returns></returns>
        bool InvokeIfRequired(Action action);
    }
}
