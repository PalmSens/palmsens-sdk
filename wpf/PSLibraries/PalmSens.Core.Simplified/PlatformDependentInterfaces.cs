using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using PalmSens.Comm;
using PalmSens.Devices;

namespace PalmSens.Core.Simplified
{
    public interface IPlatform : IPlatformInvoker
    {
        void Disconnect(CommManager comm);

        Task DisconnectAsync(CommManager comm);
    }

    public interface IPlatformMulti : IPlatformInvoker
    {
        /// <summary>
        /// Connects to the specified channels.
        /// Warning use the platform independent method Connect() instead.
        /// Otherwise the generic PSMultiCommSimple does not subscribe to the CommManagers correctly
        /// </summary>
        /// <param name="devices">Array devices to connect to.</param>
        /// <param name="channelIndices">Array of unique indices for the specified channel (0, 1, 2, 3... by default)</param>
        Task<(CommManager Comm, int ChannelIndex, Exception Exception)[]> Connect(Device[] devices,
            int[] channelIndices = null);

        /// <summary>
        /// Disconnects from channel with the specified CommManagers.
        /// Warning use the platform independent method Disconnect() instead.
        /// Otherwise the generic PSMultiCommSimple does not unsubscribe from the CommManagers correctly
        /// which may result in it not being released from the memory.
        /// </summary>
        /// <param name="comms">The comm.</param>
        Task<IEnumerable<(int channelIndex, Exception exception)>> Disconnect(IEnumerable<CommManager> comm);
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
    }
}
