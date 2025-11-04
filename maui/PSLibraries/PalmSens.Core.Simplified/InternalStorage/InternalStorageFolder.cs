using System.Collections.Generic;
using System.Threading.Tasks;
using PalmSens.Data;

namespace PalmSens.Core.Simplified.InternalStorage
{
    internal class InternalStorageFolder : InternalStorageItem, IInternalStorageFolder
    {
        private readonly List<IInternalStorageFile> _files;
        private readonly List<IInternalStorageFolder> _subFolders;

        public InternalStorageFolder(IInternalStorageItem parent, string name) : base(parent, name, DeviceFileType.Folder)
        {
            _subFolders = new List<IInternalStorageFolder>();
            _files = new List<IInternalStorageFile>();
        }

        #region IInternalStorageFolder Members
        
        /// <summary>
        ///     Add a file to this folder.
        /// </summary>
        /// <param name="file">The file to be added.</param>
        public void AddFile(IInternalStorageFile file)
        {
            _files.Add(file);
        }
        
        /// <summary>
        ///     Add a sub folder to this folder.
        /// </summary>
        /// <param name="folder">The folder to be added.</param>
        public void AddSubFolder(IInternalStorageFolder folder)
        {
            _subFolders.Add(folder);
        }
        
        /// <summary>
        ///     Get a list of files for this folder.
        /// </summary>
        /// <returns>A list of files.</returns>
        public IReadOnlyList<IInternalStorageFile> GetFiles()
        {
            return _files;
        }
        
        /// <summary>
        ///     Get a list of files for this folder.
        /// </summary>
        /// <returns>A list of files.</returns>
        public Task<IReadOnlyList<IInternalStorageFile>> GetFilesAsync()
        {
            return Task.FromResult((IReadOnlyList<IInternalStorageFile>) _files);
        }
        
        /// <summary>
        /// Get a list of subfolders for this folder
        /// </summary>
        /// <returns>A list of folders</returns>
        public IReadOnlyList<IInternalStorageFolder> GetSubFolders()
        {
            return _subFolders;
        }
        
        /// <summary>
        /// Get a list of subfolders for this folder
        /// </summary>
        /// <returns>A list of folders</returns>
        public Task<IReadOnlyList<IInternalStorageFolder>> GetSubFoldersAsync()
        {
            return Task.FromResult((IReadOnlyList<IInternalStorageFolder>) _subFolders);
        }

        #endregion
    }
}