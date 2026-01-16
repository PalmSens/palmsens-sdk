using System;
using System.Globalization;
using System.Reflection;
using System.Threading.Tasks;
using PalmSens.Comm;
using PalmSens.Devices;
using PalmSens.Windows.Comm;

namespace PalmSens.Core.Simplified.WinForms.DeviceFirmware
{
    public class SambaDeviceFirmwareUploader : DeviceFirmwareUploader<SAMBAUploader>
    {
        public SambaDeviceFirmwareUploader(Firmware firmware, Device device, SAMBAUploader uploader) : base(firmware, device, uploader)
        {
        }

        protected override void OnUpload(Firmware firmware)
        {
            UploadBootloaderFirmware();
            UploadFirmware(firmware);
            OnMessage(FirmwareUploadStatus.UploadCompleted, "Resetting device");
            Uploader.Reset();
        }

        protected override async Task OnDownloadComplete()
        {
            // Delay the device after download completed.
            await Task.Delay(6000);
            OnMessage(FirmwareUploadStatus.Completed, "Reconnecting device.");
            await Device.ReconnectAsync(30000);
        }

        private void UploadFirmware(Firmware firmware)
        {
            OnMessage(FirmwareUploadStatus.Uploading, "Uploading firmware v" + firmware.Version.ToString("0.0", CultureInfo.InvariantCulture));
            try
            {
                Uploader.Upload(firmware);
            }
            catch (Exception ex)
            {
                OnMessage(FirmwareUploadStatus.Failure, $"Failure uploading firmware:{ex.Message}");
            }
        }

        private void UploadBootloaderFirmware()
        {
            OnMessage(FirmwareUploadStatus.Uploading, "Uploading flash programmer");
            try
            {
                var resourceStream =
                    Assembly.GetExecutingAssembly()
                        .GetManifestResourceStream(
                            "PalmSens.Core.Simplified.WinForms.BootloaderFirmware.applet-flash-sam3s4.hex");
                var flashApplet = new Firmware(resourceStream);

                Uploader.UploadApplet(flashApplet);
            }
            catch (Exception exception)
            {
                OnMessage(FirmwareUploadStatus.Failure, $"Failure flash programmer: {exception.Message}");
                throw;
            }
        }
    }
}
