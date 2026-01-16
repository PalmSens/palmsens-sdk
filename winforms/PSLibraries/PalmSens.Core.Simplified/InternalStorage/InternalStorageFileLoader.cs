using System;
using System.IO;
using System.Text;
using System.Threading.Tasks;
using PalmSens.Comm;
using PalmSens.Core.Simplified.Data;
using PalmSens.Data;
using PalmSens.DataFiles;
using Buffer = PalmSens.Comm.Buffer;

namespace PalmSens.Core.Simplified.InternalStorage
{
    public interface IInternalStorageFileLoader
    {
        /// <summary>
        /// Get the measurement for this file.
        /// </summary>
        /// <param name="measType">Specify the measurement type</param>
        /// <param name="muxChannel">Specify the mux channel, default is -1</param>
        /// <returns>The measurement.</returns>
        SimpleMeasurement GetMeasurement(MeasType measType, int muxChannel = -1);

        /// <summary>
        /// Get the measurement for this file.
        /// </summary>
        /// <param name="measType">Specify the measurement type</param>
        /// <param name="muxChannel">Specify the mux channel, default is -1</param>
        /// <returns>The measurement.</returns>
        Task<SimpleMeasurement> GetMeasurementAsync(MeasType measType, int muxChannel = -1);
    }

    public abstract class InternalStorageFileLoader : IInternalStorageFileLoader
    {
        private readonly ClientConnection _clientConnection;
        private readonly DeviceFile _rawData;
        private bool _retrievedMeasurementFromStorage;

        protected InternalStorageFileLoader(DeviceFile rawData, ClientConnection clientConnection)
        {
            _rawData = rawData ?? throw new ArgumentNullException(nameof(rawData));
            _clientConnection = clientConnection ?? throw new ArgumentNullException(nameof(clientConnection));
        }

        #region IInternalStorageFileLoader Members

        /// <summary>
        /// Get the measurement for this file.
        /// </summary>
        /// <param name="measType">Specify the measurement type</param>
        /// <param name="muxChannel">Specify the mux channel, default is -1</param>
        /// <returns>The measurement.</returns>
        public SimpleMeasurement GetMeasurement(MeasType measType, int muxChannel = -1)
        {
            //Split the raw data for the method en the measurement
            if (!TryGetEndChar(out var iEndChar) || !TryGetData(iEndChar, out var dataStr) || !TryLoadMethod(iEndChar, out var m))
                return null;

            var clientConnection = _clientConnection;
            var buff = new OfflineBuffer(dataStr);
            buff = CheckVersion(buff, clientConnection);

            var meas = LoadMeasurement(m, _clientConnection, buff, measType, muxChannel);
            ProcessData(meas, buff);

            return new SimpleMeasurement(meas);
        }

        /// <summary>
        /// Get the measurement for this file.
        /// </summary>
        /// <param name="measType">Specify the measurement type</param>
        /// <param name="muxChannel">Specify the mux channel, default is -1</param>
        /// <returns>The measurement.</returns>
        public async Task<SimpleMeasurement> GetMeasurementAsync(MeasType measType, int muxChannel = -1)
        {
            //Split the raw data for the method en the measurement
            if (!TryGetEndChar(out var iEndChar) || !TryGetData(iEndChar, out var dataStr) || !TryLoadMethod(iEndChar, out var m))
                return null;

            var clientConnection = _clientConnection;
            var buff = new OfflineBuffer(dataStr);
            buff = await CheckVersionAsync(buff, clientConnection);

            var meas = await LoadMeasurementAsync(m, _clientConnection, buff, measType, muxChannel);

            await ProcessDataAsync(meas, buff);

            return new SimpleMeasurement(meas);
        }

        #endregion

        protected abstract ActiveMeasurement LoadMeasurement(Method m, ClientConnection connection, Buffer buff, MeasType measType, int muxChannel);
        protected abstract Task<ActiveMeasurement> LoadMeasurementAsync(Method method, ClientConnection connection, Buffer buff, MeasType measType, int muxChannel);

        protected virtual bool TryGetData(int iEndChar, out string dataStr)
        {
            dataStr = _rawData.Content.Substring(iEndChar + 1);
            return dataStr.Length > 0;
        }

        /// <summary>
        ///     Checks the version of the measurement in the Buffer and converts it if necessary.
        /// </summary>
        /// <param name="buff">The buff.</param>
        /// <param name="clientConnection">The comm clientConnection.</param>
        private OfflineBuffer CheckVersion(OfflineBuffer buff, ClientConnection clientConnection)
        {
            double fwVersionMeasurement;
            if ((char) buff.Peek() != 't')
            {
                fwVersionMeasurement = 1.5; //1.5 is the last fw version that did not have (or need) the fw version stored
            }
            else
            {
                var versionString = buff.Pop(buff.IndexOf('*') + 1).Substring(1);
                fwVersionMeasurement = ClientConnection.ParseVersion(versionString);
            }

            if (clientConnection.Capabilities.MinFirmwareVersionRequired - fwVersionMeasurement > 0.001)
                buff = clientConnection.ConvertMeasurementVersion(fwVersionMeasurement, buff);

            return buff;
        }


        /// <summary>
        ///     Checks the version of the measurement in the Buffer and converts it if necessary.
        /// </summary>
        /// <param name="buff">The buff.</param>
        /// <param name="clientConnection">The comm clientConnection.</param>
        private async Task<OfflineBuffer> CheckVersionAsync(OfflineBuffer buff, ClientConnection clientConnection)
        {
            double fwVersionMeasurement;
            if ((char) await buff.PeekAsync() != 't')
            {
                fwVersionMeasurement = 1.5; //1.5 is the last fw version that did not have (or need) the fw version stored
            }
            else
            {
                var versionString = (await buff.PopAsync(buff.IndexOf('*') + 1)).Substring(1);
                fwVersionMeasurement = ClientConnection.ParseVersion(versionString);
            }

            if (clientConnection.Capabilities.MinFirmwareVersionRequired - fwVersionMeasurement > 0.001)
                buff = clientConnection.ConvertMeasurementVersion(fwVersionMeasurement, buff);

            return buff;
        }

        private void Meas_EndMeasurement(object sender, EventArgs e)
        {
            _retrievedMeasurementFromStorage = true;
        }

        private void ProcessData(ActiveMeasurement meas, Buffer buff)
        {
            meas.EndMeasurement += Meas_EndMeasurement;

            try
            {
                _retrievedMeasurementFromStorage = true;
                var charCntSameCnt = 0;

                while (_retrievedMeasurementFromStorage)
                {
                    if (meas.Method.MuxMethod == MuxMethod.Sequentially && buff.Peek() == 't')
                        buff.Pop(buff.IndexOf('*') + 1);

                    var lastCharCnt = buff.CharsInBuffer;

                    meas.ProcessData();

                    if (lastCharCnt == buff.CharsInBuffer)
                    {
                        if (++charCntSameCnt > 5)
                            break; //We did not process any data last iterations, so this file is probably invalid, but still output what we have so far.
                    }
                    else
                    {
                        charCntSameCnt = 0;
                    }
                }
            }
            finally
            {
                meas.EndMeasurement -= Meas_EndMeasurement;
            }
        }

        private async Task ProcessDataAsync(ActiveMeasurement meas, Buffer buff)
        {
            meas.EndMeasurement += Meas_EndMeasurement;

            try
            {
                _retrievedMeasurementFromStorage = true;
                var charCntSameCnt = 0;

                while (_retrievedMeasurementFromStorage)
                {
                    if (meas.Method.MuxMethod == MuxMethod.Sequentially && await buff.PeekAsync() == 't')
                        await buff.PopAsync(buff.IndexOf('*') + 1);
                    var lastCharCnt = buff.CharsInBuffer;
                    await meas.ProcessDataAsync();

                    if (lastCharCnt == buff.CharsInBuffer)
                    {
                        if (charCntSameCnt++ > 5)
                            break; //We did not process any data last iterations, so this file is probably invalid, but still output what we have so far.
                    }
                    else
                    {
                        charCntSameCnt = 0;
                    }
                }
            }
            finally
            {
                meas.EndMeasurement -= Meas_EndMeasurement;
            }
        }

        private bool TryGetEndChar(out int iEndChar)
        {
            iEndChar = _rawData.Content.IndexOf('*');
            return iEndChar >= 0;
        }

        private bool TryLoadMethod(int iEndChar, out Method m)
        {
            m = null;

            var methodStr = _rawData.Content.Substring(0, iEndChar);

            using (var memStream = new MemoryStream(Encoding.UTF8.GetBytes(methodStr)))
            using (var fileStream = new StreamReader(memStream))
            {
                m = MethodFile2.FromStream(fileStream);
            }

            return m.SupportsDeviceStorage(_clientConnection.Capabilities);
        }
    }
}
