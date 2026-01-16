using System;

namespace PalmSens.Core.Simplified.WinForms.DeviceFirmware
{
    /// <summary>
    /// Device firmware message events args.
    /// </summary>
    public class DeviceFirmwareUploaderMessageEventArgs : EventArgs
    {
        public DeviceFirmwareUploaderMessageEventArgs(FirmwareUploadStatus status, string message)
        {
            Status = status;
            Message = message;
        }

        /// <summary>
        /// The message sent from the uploader
        /// </summary>
        public string Message { get; }

        /// <summary>
        /// The current status of the uploader.
        /// </summary>
        public FirmwareUploadStatus Status { get; }

        /// <summary>
        /// Overridden the <see cref="ToString"/> method to return the 'Status:Message'.
        /// </summary>
        /// <returns></returns>
        public override string ToString()
        {
            return $"{Status}:{Message}";
        }
    }
}
