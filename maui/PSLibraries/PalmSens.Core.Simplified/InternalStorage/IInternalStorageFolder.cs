using System.Collections.Generic;
using System.Threading.Tasks;

namespace PalmSens.Core.Simplified.InternalStorage
{
    /// <summary>
    ///     Internal storage folder.
    /// </summary>
    public interface IInternalStorageFolder : IInternalStorageItem
    {
        /// <summary>
        ///     Add a file to this folder.
        /// </summary>
        /// <param name="file">The file to be added.</param>
        void AddFile(IInternalStorageFile file);

        /// <summary>
        ///     Add a sub folder to this folder.
        /// </summary>
        /// <param name="folder">The folder to be added.</param>
        void AddSubFolder(IInternalStorageFolder folder);

        /// <summary>
        ///     Get a list of files for this folder.
        /// </summary>
        /// <returns>A list of files.</returns>
        IReadOnlyList<IInternalStorageFile> GetFiles();

        /// <summary>
        ///     Get a list of files for this folder.
        /// </summary>
        /// <returns>A list of files.</returns>
        Task<IReadOnlyList<IInternalStorageFile>> GetFilesAsync();

        /// <summary>
        ///     Get a list of subfolders for this folder
        /// </summary>
        /// <returns>A list of folders</returns>
        IReadOnlyList<IInternalStorageFolder> GetSubFolders();

        /// <summary>
        ///     Get a list of subfolders for this folder
        /// </summary>
        /// <returns>A list of folders</returns>
        Task<IReadOnlyList<IInternalStorageFolder>> GetSubFoldersAsync();
    }
}