using System;
using System.Globalization;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Forms;
using PalmSens.Comm;
using PalmSens.Devices;
using PalmSens.Windows.Comm;

namespace PalmSens.Core.Simplified.WinForms.DeviceFirmware
{
    public class HvgaDeviceFirmwareUploader : DeviceFirmwareUploader<HVGAUploader>
    {
        private readonly bool _isEmStat4;

        public HvgaDeviceFirmwareUploader(Firmware firmware, Device device, HVGAUploader uploader) : base(firmware, device, uploader)
        {
            // Get an indicator if the current firmware is an EmStat4 firmware.
            _isEmStat4 = firmware.Device.Contains(enumDeviceType.EmStat4HR) || firmware.Device.Contains(enumDeviceType.EmStat4LR);
        }

        protected override void OnUpload(Firmware firmware)
        {
            if (string.IsNullOrEmpty(Uploader.VersionString)) return;

            try
            {
                //EmStat4 encrypt time per file length, assuming this scales linearly
                if (_isEmStat4) Uploader.EncryptRate = 0.117f;

                OnMessage(FirmwareUploadStatus.Uploading, "Uploading firmware v" + firmware.Version.ToString("0.000", CultureInfo.InvariantCulture));
                Uploader.Upload(firmware);
            }
            catch (Exception exception)
            {
                OnMessage(FirmwareUploadStatus.Failure, $"Failure uploading firmware: {exception.Message}");
                throw;
            }
        }

        protected override async Task OnDownloadComplete()
        {
            if (_isEmStat4)
            {
                //Wait for ES4 to decrypt firmware (reconnecting while it is still decrypting will give the wrong com port)
                await Task.Delay(3000);
                OnMessage(FirmwareUploadStatus.UploadCompleted, "Resetting device");
                // Reconnect to the device after device has been decrypted.
                await Device.ReconnectAsync(3000);
                // Validate the firmware uploaded correctly.
                await ValidateFirmwareUpload();
            }
        }

        private async Task ValidateFirmwareUpload()
        {
            // Validate that the firmware upload went completed successfully.
            var versionString = await Device.GetVersionStringAsync();
            var version = ((int)(Firmware.Version * 1000)).ToString();
            if (!versionString[0].EndsWith(version))
                OnMessage(FirmwareUploadStatus.Failure, "Firmware update failed, reverted device to previous version.");
        }
    }
}
