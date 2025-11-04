using PalmSens.Data;

namespace PalmSens.Core.Simplified.InternalStorage
{
    /// <summary>
    ///     Internal storage item
    /// </summary>
    public interface IInternalStorageItem
    {
        /// <summary>
        ///     The folder path to the item.
        /// </summary>
        string FolderPath { get; }

        /// <summary>
        ///     The full path, this will be <see cref="FolderPath" /> + <see cref="PathSeparator" /> + <see cref="Name" />
        /// </summary>
        string FullPath { get; }

        /// <summary>
        ///     The device item type.
        /// </summary>
        DeviceFileType ItemType { get; }

        /// <summary>
        ///     The name of the item.
        /// </summary>
        string Name { get; }

        /// <summary>
        ///     The parent item. For root items this will be itself.
        /// </summary>
        IInternalStorageItem Parent { get; }

        /// <summary>
        ///     The path separator.
        /// </summary>
        char PathSeparator { get; }
    }
}