using System;
using System.Threading.Tasks;
using PalmSens.Core.Simplified.Data;
using PalmSens.Data;

namespace PalmSens.Core.Simplified.InternalStorage
{
    internal class InternalStorageFile : InternalStorageItem, IInternalStorageFile
    {
        private readonly IInternalStorageBrowser _browser;

        public InternalStorageFile(IInternalStorageItem parent, string name, IInternalStorageBrowser browser) : base(parent, name, DeviceFileType.Measurement)
        {
            _browser = browser ?? throw new ArgumentNullException(nameof(browser));
        }

        #region IInternalStorageFile Members

        /// <summary>
        ///     Get the measurement for this file.
        /// </summary>
        /// <param name="measType">Specify the measurement type</param>
        /// <param name="muxChannel">Specify the mux channel, default is -1</param>
        /// <returns>The measurement.</returns>
        public SimpleMeasurement GetMeasurement(MeasType measType = MeasType.Overlay, int muxChannel = -1)
        {
            //Load the actual raw data of the measurement into a DeviceFile
            var rawData = _browser.Run(connection => connection.GetDeviceFile(FullPath));
            var loader = _browser.GetLoader(rawData);

            return loader.GetMeasurement(measType, muxChannel);
        }

        /// <summary>
        ///     Get the measurement for this file.
        /// </summary>
        /// <param name="measType">Specify the measurement type</param>
        /// <param name="muxChannel">Specify the mux channel, default is -1</param>
        /// <returns>The measurement.</returns>
        public async Task<SimpleMeasurement> GetMeasurementAsync(MeasType measType = MeasType.Overlay, int muxChannel = -1)
        {
            //Load the actual raw data of the measurement into a DeviceFile
            var rawData = await _browser.RunAsync(connection => connection.GetDeviceFileAsync(FullPath));
            var loader = _browser.GetLoader(rawData);

            return await loader.GetMeasurementAsync(measType, muxChannel);
        }

        #endregion
    }
}