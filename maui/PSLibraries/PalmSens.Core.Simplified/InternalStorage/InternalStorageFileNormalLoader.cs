using System.Threading.Tasks;
using PalmSens.Comm;
using PalmSens.Data;

namespace PalmSens.Core.Simplified.InternalStorage
{
    /// <summary>
    ///     A normal file loader, this is for older devices that have internal storage,
    /// </summary>
    public class InternalStorageFileNormalLoader : InternalStorageFileLoader
    {
        public InternalStorageFileNormalLoader(DeviceFile rawData, ClientConnection clientConnection) : base(rawData, clientConnection)
        {
        }
        
        /// <summary>
        ///     Load a method script measurement
        /// </summary>
        /// <returns></returns>
        protected override ActiveMeasurement LoadMeasurement(Method m, ClientConnection connection, Buffer buff, MeasType measType, int muxChannel)
        {
            return m.ReceiveMeasurement(connection, muxChannel, measType, buff);
        }
        
        /// <summary>
        ///     Load a method script measurement
        /// </summary>
        /// <returns></returns>
        protected override Task<ActiveMeasurement> LoadMeasurementAsync(Method method, ClientConnection connection, Buffer buff, MeasType measType, int muxChannel)
        {
            return method.ReceiveMeasurementAsync(connection, muxChannel, measType, buff);
        }
    }
}