using System;
using System.Globalization;
using PalmSens.Comm;
using PalmSens.Devices;
using PalmSens.Windows.Comm;

namespace PalmSens.Core.Simplified.WinForms.DeviceFirmware
{
    /// <summary>
    /// The ADUC device firmware uploader.
    /// </summary>
    public class AducDeviceFirmwareUploader : DeviceFirmwareUploader<ADUCUploader>
    {
        public AducDeviceFirmwareUploader(Firmware firmware, Device device, ADUCUploader uploader) : base(firmware, device, uploader)
        {
        }

        protected override void OnUpload(Firmware firmware)
        {
            try
            {
                EnterDownloadMode(); //Set to download mode again to assure the version response is not missed
                WaitVersionIfNeeded();
                OnMessage(FirmwareUploadStatus.Uploading, "Resetting device");
                Uploader.Reset();
                OnMessage(FirmwareUploadStatus.Uploading, "Clearing code memory");
                Uploader.ClearCodeMemory();
                OnMessage(FirmwareUploadStatus.Uploading, "Uploading firmware v" + firmware.Version.ToString("0.0", CultureInfo.InvariantCulture));
                Uploader.Upload(firmware);
                OnMessage(FirmwareUploadStatus.UploadCompleted, "Running new firmware");
                OnMessage(FirmwareUploadStatus.Completed, "Running new firmware");
            }
            catch (Exception ex)
            {
                OnMessage(FirmwareUploadStatus.Failure, $"Failure uploading firmware: {ex.Message}");
                throw;
            }
            // Regardless of error, run the firmware.
            Uploader.RunFirmware();
        }

        private void EnterDownloadMode()
        {
            OnMessage(FirmwareUploadStatus.EnterDownloadMode, "Device is entering download mode.");

            try
            {
                OnMessage(FirmwareUploadStatus.EnterDownloadMode, "Device reconnected.");
                Device.EnterDownloadMode();
            }
            catch (Exception exception)
            {
                OnMessage(FirmwareUploadStatus.Failure, $"An error has occurred trying to enter download mode on device: {exception.Message}");
                throw;
            }
        }

        /// <summary>
        /// Wait for the version if needed.
        /// </summary>
        private void WaitVersionIfNeeded()
        {
            OnMessage(FirmwareUploadStatus.UploadStarted, "Waiting for version to be retrieved from device.");
            var timeout = DateTime.Now.AddSeconds(5);
            while (!Uploader.WaitVersion())
            {
                // If it takes longer than 5 seconds to get the version, then throw an exception
                if (timeout > DateTime.Now)
                {
                    const string TimeOutMessage = "Timeout while waiting for the device version.";

                    OnMessage(FirmwareUploadStatus.Failure, "Timeout while waiting for the device version.");
                    throw new TimeoutException(TimeOutMessage);
                }
            }
        }
    }
}
