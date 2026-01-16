using System;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using PalmSens.Comm;
using PalmSens.Devices;
using PalmSens.Windows.Comm;

namespace PalmSens.Core.Simplified.WinForms.DeviceFirmware
{
    public interface IFirmwareManager
    {
        /// <summary>
        /// Sets the device in download mode and gets it's firmware uploader from its Communication Manager(CommManager / PSCommSimple.WinForms.Comm).
        /// This will disconnect the instrument and dispose the Communication Manager
        /// before uploading the firmware. A new connection must be established after the update has finished.
        /// </summary>
        /// <param name="commManager">The devices Communication Manager.</param>
        /// <returns></returns>
        Task<IDeviceFirmwareUploader> SetDeviceInDownloadModeAndGetDeviceFirmwareUploader(CommManager commManager);

        /// <summary>
        /// Sets the device in download mode and gets it's firmware uploader. The instrument should not be used in an active CommManager instance.
        /// After the the update has finished the device will be back in the closed state.
        /// </summary>
        /// <param name="device">The device.</param>
        /// <returns></returns>
        Task<IDeviceFirmwareUploader> SetDeviceInDownloadModeAndGetDeviceFirmwareUploader(Device device);

        /// <summary>
        /// Validates whether the selected firmware is compatible with the specified device.
        /// </summary>
        /// <param name="deviceType">The type of the device.</param>
        /// <returns></returns>
        bool Validate(enumDeviceType deviceType);
    }

    public class FirmwareManager : IFirmwareManager
    {
        private readonly Firmware _firmware;

        public FirmwareManager(Firmware firmware)
        {
            _firmware = firmware ?? throw new ArgumentNullException(nameof(firmware));
        }

        public enumDeviceType BootLoaderDeviceType => _firmware.BootloaderDevice;
        public enumDeviceType[] DeviceType => _firmware.Device;
        public double Version => _firmware.Version;

        #region IFirmwareManager Members
        /// <summary>
        /// Sets the device in download mode and gets it's firmware uploader from its Communication Manager(CommManager / PSCommSimple.WinForms.Comm).
        /// This will disconnect the instrument and dispose the Communication Manager
        /// before uploading the firmware. A new connection must be established after the update has finished.
        /// </summary>
        /// <param name="commManager">The devices Communication Manager.</param>
        /// <returns></returns>
        public async Task<IDeviceFirmwareUploader> SetDeviceInDownloadModeAndGetDeviceFirmwareUploader(CommManager commManager)
        {
            if (commManager == null) throw new ArgumentNullException(nameof(commManager));

            await commManager.DisconnectAsync();
            commManager.Dispose();
            var device = commManager.Device;

            return await SetDeviceInDownloadModeAndGetDeviceFirmwareUploader(device);
        }

        /// <summary>
        /// Sets the device in download mode and gets it's firmware uploader. The instrument should not be used in an active CommManager instance.
        /// After the the update has finished the device will be back in the closed state.
        /// </summary>
        /// <param name="device">The device.</param>
        /// <returns></returns>
        public async Task<IDeviceFirmwareUploader> SetDeviceInDownloadModeAndGetDeviceFirmwareUploader(Device device)
        {
            if (device == null) throw new ArgumentNullException(nameof(device));
            if (!device.SupportsDownloading) throw new NotSupportedException("Firmware can only be updated via USB connection!\r\nConnect via USB cable and try again.");

            ClientConnection connection = null;

            try
            {
                await device.OpenAsync();
                connection = await ClientConnection.FromDeviceAsync(device);
            }
            catch
            {
                device.Close();
                throw;
            }

            if (!Validate(connection.DeviceType))
            {
                // Not all devices support device.CloseAsync()
                device.Close();
                throw new InvalidOperationException($"The device {connection.DeviceType} is not supported by the firmware: {this}.");
            }

            try
            {
                //Enter download mode and reset the device before getting the device's firmware uploader
                await connection.EnterDownloadModeAsync();
                switch (connection.DeviceType)
                {
                    case enumDeviceType.PalmSens4:
                    case enumDeviceType.SAMBAProgramPort:
                    case enumDeviceType.EmStat4LR:
                    case enumDeviceType.EmStat4HR:
                    case enumDeviceType.EmStat4Bootloader:
                    case enumDeviceType.EmStatPico:
                    case enumDeviceType.EmStatPicoBootLoader:
                        await device.ReconnectAsync(30000);
                        break;
                }
            }
            catch
            {
                device.Close();
                throw;
            }

            var uploader = device.GetFirmwareUploader();

            if (uploader is SAMBAUploader sambaUploader) return new SambaDeviceFirmwareUploader(_firmware, device, sambaUploader);
            if (uploader is HVGAUploader hvgaUploader) return new HvgaDeviceFirmwareUploader(_firmware, device, hvgaUploader);
            if (uploader is ARMUploader armUploader) return new ArmDeviceFirmwareUploader(_firmware, device, armUploader);
            if (uploader is ADUCUploader aducUploader) return new AducDeviceFirmwareUploader(_firmware, device, aducUploader);

            throw new NotSupportedException("This device is not supported by this factory");
        }

        /// <summary>
        /// Validates whether the selected firmware is compatible with the specified device.
        /// </summary>
        /// <param name="deviceType">The type of the device.</param>
        /// <returns></returns>
        public bool Validate(enumDeviceType deviceType) => _firmware.Device.Contains(deviceType) || _firmware.BootloaderDevice == deviceType;
        #endregion

        public static IFirmwareManager CreateManager(string firmwareFilePath) => CreateManager(new FileInfo(firmwareFilePath));

        public static IFirmwareManager CreateManager(FileInfo firmwareFile)
        {
            if (firmwareFile == null) throw new ArgumentNullException(nameof(firmwareFile));
            if (!firmwareFile.Exists) throw new ArgumentException("The file location does not exists.", nameof(firmwareFile));

            var isBinDevice = firmwareFile.Extension.Equals(".bin", StringComparison.OrdinalIgnoreCase);
            Firmware firmware;
            using (var stream = firmwareFile.OpenRead())
            {
                firmware = isBinDevice ? new FirmwareBin(stream) : new Firmware(stream);
            }

            return new FirmwareManager(firmware);
        }

        public override string ToString()
        {
            var toStringBuilder = new StringBuilder("Firmware Info:").AppendLine();

            if (_firmware is FirmwareBin)
                toStringBuilder.AppendLine($"   Firmware Version: {Version:#0.000}");
            else
                toStringBuilder.AppendLine($"   Firmware Version: {Version:0.0}");

            toStringBuilder.Append("   Supported devices: ").Append(DeviceType[0]);
            for (var i = 1; i < DeviceType.Length; i++) toStringBuilder.Append(',').Append(DeviceType[i]);

            toStringBuilder.AppendLine().Append($"   Boot loader: {BootLoaderDeviceType}");

            return toStringBuilder.ToString();
        }
    }
}
