using System;
using System.Threading;
using System.Threading.Tasks;
using PalmSens.Comm;
using PalmSens.Devices;

namespace PalmSens.Core.Simplified.WinForms.DeviceFirmware
{
    public interface IDeviceFirmwareUploader : IDisposable
    {
        /// <summary>
        ///     Uploader progress event that will be invoked during the upload process.
        /// </summary>
        event EventHandler<DeviceFirmwareUploaderProgressEventArgs> Progress;

        /// <summary>
        ///     Uploader message event that will invoke for all messages.
        /// </summary>
        event EventHandler<DeviceFirmwareUploaderMessageEventArgs> Message;

        /// <summary>
        /// Upload the firmware to the device asynchronously.
        /// The task returns when the upload is complete.
        /// The device has to be set into download mode first
        /// </summary>
        Task UploadAsync();
    }

    public abstract class DeviceFirmwareUploader<TUploader> : IDeviceFirmwareUploader where TUploader : FirmwareUploader
    {
        private readonly CancellationTokenSource _cancellation;
        private readonly TaskScheduler _taskScheduler;
        private bool _isDisposed;

        protected DeviceFirmwareUploader(Firmware firmware, Device device, TUploader uploader)
        {
            Firmware = firmware ?? throw new ArgumentNullException(nameof(firmware));
            Device = device ?? throw new ArgumentNullException(nameof(device));
            Uploader = uploader ?? throw new InvalidOperationException("The device does not have an uploader.");

            // Create a new task scheduler, not to make use of the standard scheduler.
            _taskScheduler = new ConcurrentExclusiveSchedulerPair().ExclusiveScheduler;
            _cancellation = new CancellationTokenSource();

            Uploader.DownloadProgress += Uploader_DownloadProgress;
            Uploader.Message += Uploader_Message;
        }

        /// <summary>
        ///     The current firmware.
        /// </summary>
        protected Firmware Firmware { get; }

        /// <summary>
        ///     Get the device.
        /// </summary>
        protected Device Device { get; }

        /// <summary>
        ///     Get an value of the estimated duration in minutes.
        /// </summary>
        protected int MinEstimatedDurationMinutes => Uploader.MinEstimatedDurationMinutes;

        protected TUploader Uploader { get; }

        #region IDeviceFirmwareUploader Members

        public void Dispose()
        {
            Dispose(true);
            GC.SuppressFinalize(this);
        }

        public event EventHandler<DeviceFirmwareUploaderMessageEventArgs> Message;

        public event EventHandler<DeviceFirmwareUploaderProgressEventArgs> Progress;

        /// <summary>
        /// Upload the firmware to the device asynchronously.
        /// The task returns when the upload is complete.
        /// The device has to be set into download mode first
        /// </summary>
        public Task UploadAsync()
        {
            // Create a new task from the task factory with task options.
            var token = _cancellation.Token;
            var task = Task.Factory.StartNew(UploadInternalAsync, token, TaskCreationOptions.LongRunning, _taskScheduler);

            // Unwrap the task because it's a Task of a Task.
            return task.Unwrap();
        }

        #endregion

        /// <summary>
        ///     Internal upload that manages the upload process.
        /// </summary>
        /// <returns></returns>
        private async Task UploadInternalAsync()
        {
            try
            {
                if (!Device.SupportsDownloading) throw new NotSupportedException("Firmware can only be updated via USB connection!\r\nConnect via USB cable and try again.");
                Device.EnterDownloadMode();
                OnMessage(FirmwareUploadStatus.Message, $"This process should not take more than {MinEstimatedDurationMinutes} minutes.");
                OnMessage(FirmwareUploadStatus.UploadStarted, "Starting update, do not disconnect!");
                OnUpload(Firmware);
                OnMessage(FirmwareUploadStatus.UploadCompleted, "Upload completed.");
                await OnDownloadComplete();
                LeaveDownloadMode();
                OnMessage(FirmwareUploadStatus.Completed, "Completed uploading new firmware.");
            }
            finally
            {
                // There are devices that do not support CloseAsync()
                Device.Close();
            }
        }

        protected virtual Task OnDownloadComplete()
        {
            return Task.CompletedTask;
        }

        private void LeaveDownloadMode()
        {
            OnMessage(FirmwareUploadStatus.LeaveDownloadMode, "Device is leaving download mode.");
            try
            {
                Device.LeaveDownloadMode();
            }
            catch (Exception exception)
            {
                OnMessage(FirmwareUploadStatus.Failure, $"An error has occurred trying to leave download mode on device: {exception.Message}");
                throw;
            }
        }

        protected abstract void OnUpload(Firmware firmware);

        protected virtual void OnProgress(FirmwareUploadStatus status, int current, int total)
        {
            Progress?.Invoke(this, new DeviceFirmwareUploaderProgressEventArgs(status, current, total));
        }

        protected virtual void Dispose(bool disposing)
        {
            if (!disposing || _isDisposed) return;

            _isDisposed = true;
            Message = null;
            Progress = null;

            // Dispose of the cancellation source and try and cancel the token.
            _cancellation.Cancel(false);
            _cancellation.Dispose();

            Uploader.DownloadProgress -= Uploader_DownloadProgress;
            Uploader.Message -= Uploader_Message;
            Uploader.Dispose();
        }

        protected virtual void OnMessage(FirmwareUploadStatus status, string message)
        {
            Message?.Invoke(this, new DeviceFirmwareUploaderMessageEventArgs(status, message));
        }

        private void Uploader_DownloadProgress(object sender, FirmwareUploader.DownloadProgressEventArgs e)
        {
            OnProgress(FirmwareUploadStatus.Uploading, e.Current, e.Total);
        }

        private void Uploader_Message(string message)
        {
            OnMessage(FirmwareUploadStatus.Message, message);
        }
    }
}
