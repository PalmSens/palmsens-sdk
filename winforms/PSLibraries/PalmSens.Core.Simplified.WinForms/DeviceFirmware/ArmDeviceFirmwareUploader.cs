using System;
using System.Globalization;
using System.Reflection;
using PalmSens.Comm;
using PalmSens.Devices;
using PalmSens.Windows.Comm;

namespace PalmSens.Core.Simplified.WinForms.DeviceFirmware
{
    public class ArmDeviceFirmwareUploader : DeviceFirmwareUploader<ARMUploader>
    {
        public ArmDeviceFirmwareUploader(Firmware firmware, Device device, ARMUploader uploader) : base(firmware, device, uploader)
        {
        }

        protected override void OnUpload(Firmware firmware)
        {
            OnMessage(FirmwareUploadStatus.Uploading, "Resetting device");
            Uploader.Reset();
            UploadBootloaderFirmware();
            UploadFirmware(firmware);
            OnMessage(FirmwareUploadStatus.UploadCompleted, "Resetting device");
            Uploader.Reset(); // uses the ftdi DTR signal to reset the micro.
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
                var resourceName =
                    Assembly.GetExecutingAssembly()
                        .GetManifestResourceStream(
                            "PalmSens.Core.Simplified.WinForms.BootloaderFirmware.palmBootloader-sam3s4.hex");
                var bootloaderImage = new Firmware(resourceName);

                Uploader.Upload(bootloaderImage);
            }
            catch (Exception exception)
            {
                OnMessage(FirmwareUploadStatus.Failure, $"Failure flash programmer: {exception.Message}");
                throw;
            }
        }
    }
}
