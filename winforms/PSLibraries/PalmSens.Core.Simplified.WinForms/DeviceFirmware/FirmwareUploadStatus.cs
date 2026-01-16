namespace PalmSens.Core.Simplified.WinForms.DeviceFirmware
{
    /// <summary>
    /// Upload status enum.
    /// </summary>
    public enum FirmwareUploadStatus
    {
        None = 0,
        Message,
        EnterDownloadMode,
        UploadStarted,
        Uploading,
        UploadCompleted,
        LeaveDownloadMode,
        Completed,
        Failure
    }
}
