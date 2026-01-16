using System;

namespace PalmSens.Core.Simplified.WinForms.DeviceFirmware
{
    /// <summary>
    /// Device uploader progress event args
    /// </summary>
    public class DeviceFirmwareUploaderProgressEventArgs : EventArgs
    {
        public DeviceFirmwareUploaderProgressEventArgs(FirmwareUploadStatus status, int current, int total)
        {
            Status = status;
            Current = current;
            Total = total;
        }

        /// <summary>
        /// The current progress
        /// </summary>
        public int Current { get; }
        /// <summary>
        /// The current status of the upload.
        /// </summary>
        public FirmwareUploadStatus Status { get; }
        /// <summary>
        /// The total of the upload.
        /// </summary>
        public int Total { get; }
    }
}
