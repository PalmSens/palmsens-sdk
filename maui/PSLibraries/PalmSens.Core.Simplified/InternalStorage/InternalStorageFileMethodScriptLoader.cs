using System.Threading.Tasks;
using PalmSens.Comm;
using PalmSens.Data;

namespace PalmSens.Core.Simplified.InternalStorage
{
    /// <summary>
    ///     Method script file loader. This will load method script files correctly.
    /// </summary>
    public class InternalStorageFileMethodScriptLoader : InternalStorageFileLoader
    {
        public InternalStorageFileMethodScriptLoader(DeviceFile rawData, ClientConnection clientConnection) : base(rawData, clientConnection)
        {
        }

        /// <summary>
        ///     Load a method script measurement
        /// </summary>
        /// <returns></returns>
        protected override ActiveMeasurement LoadMeasurement(Method m, ClientConnection connection, Buffer buff, MeasType measType, int muxChannel)
        {
            var meas = m.ReceiveMeasurementMS(connection, -1, MeasType.Overlay, buff);

            if (meas is ImpedimetricMeasMS) meas.AddEISdataForGraphView();

            return meas;
        }

        /// <summary>
        ///     Load a method script measurement
        /// </summary>
        /// <returns></returns>
        protected override async Task<ActiveMeasurement> LoadMeasurementAsync(Method method, ClientConnection connection, Buffer buff, MeasType measType, int muxChannel)
        {
            var measurement = await method.ReceiveMeasurementMSAsync(connection, -1, MeasType.Overlay, buff);

            if (measurement is ImpedimetricMeasMS) measurement.AddEISdataForGraphView();

            return measurement;
        }

        /// <summary>
        ///     Override the try get data for additional parsing of the data string.
        /// </summary>
        /// <param name="iEndChar"></param>
        /// <param name="dataStr"></param>
        /// <returns></returns>
        protected override bool TryGetData(int iEndChar, out string dataStr)
        {
            if (!base.TryGetData(iEndChar, out dataStr)) return false;

            if (dataStr.StartsWith("v"))
            {
                var split = dataStr.Split(new[] {'\n'}, 2);
                dataStr = split[1];
            }

            return true;
        }
    }
}