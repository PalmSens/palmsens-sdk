using System.Threading.Tasks;
using PalmSens.Core.Simplified.Data;

namespace PalmSens.Core.Simplified.InternalStorage
{
    /// <summary>
    ///     Internal storage file
    /// </summary>
    public interface IInternalStorageFile : IInternalStorageItem
    {
        /// <summary>
        ///     Get the measurement for this file.
        /// </summary>
        /// <param name="measType">Specify the measurement type</param>
        /// <param name="muxChannel">Specify the mux channel, default is -1</param>
        /// <returns>The measurement.</returns>
        SimpleMeasurement GetMeasurement(MeasType measType = MeasType.Overlay, int muxChannel = -1);

        /// <summary>
        ///     Get the measurement for this file.
        /// </summary>
        /// <param name="measType">Specify the measurement type</param>
        /// <param name="muxChannel">Specify the mux channel, default is -1</param>
        /// <returns>The measurement.</returns>
        Task<SimpleMeasurement> GetMeasurementAsync(MeasType measType = MeasType.Overlay, int muxChannel = -1);
    }
}