using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using PalmSens.Data;

namespace PalmSens.Core.Simplified.InternalStorage
{
    internal class InternalStorageFolderLazy : InternalStorageItem, IInternalStorageFolder
    {
        private readonly IInternalStorageBrowser _browser;
        private readonly Lazy<List<IInternalStorageFile>> _files;
        private readonly Lazy<List<IInternalStorageFolder>> _subFolders;
        private IList<IInternalStorageItem> _folderItems;

        public InternalStorageFolderLazy(IInternalStorageItem parent, string name, IInternalStorageBrowser browser) : base(parent, name, DeviceFileType.Folder)
        {
            _browser = browser ?? throw new ArgumentNullException(nameof(browser));

            _subFolders = new Lazy<List<IInternalStorageFolder>>(GetSubFoldersInternal, LazyThreadSafetyMode.ExecutionAndPublication);
            _files = new Lazy<List<IInternalStorageFile>>(GetFilesInternal, LazyThreadSafetyMode.ExecutionAndPublication);
        }

        #region IInternalStorageFolder Members
        
        /// <summary>
        ///     Add a file to this folder.
        /// </summary>
        /// <param name="file">The file to be added.</param>
        public void AddFile(IInternalStorageFile file)
        {
            _files.Value.Add(file);
        }
        
        /// <summary>
        ///     Add a sub folder to this folder.
        /// </summary>
        /// <param name="folder">The folder to be added.</param>
        public void AddSubFolder(IInternalStorageFolder folder)
        {
            _subFolders.Value.Add(folder);
        }
        
        /// <summary>
        ///     Get a list of files for this folder.
        /// </summary>
        /// <returns>A list of files.</returns>
        public IReadOnlyList<IInternalStorageFile> GetFiles()
        {
            return _files.Value;
        }
        
        /// <summary>
        ///     Get a list of files for this folder.
        /// </summary>
        /// <returns>A list of files.</returns>
        public async Task<IReadOnlyList<IInternalStorageFile>> GetFilesAsync()
        {
            await EnsureFolderItemsLoadedAsync();

            return _files.Value;
        }
        
        /// <summary>
        /// Get a list of subfolders for this folder
        /// </summary>
        /// <returns>A list of folders</returns>
        public IReadOnlyList<IInternalStorageFolder> GetSubFolders()
        {
            return _subFolders.Value;
        }
        
        /// <summary>
        /// Get a list of subfolders for this folder
        /// </summary>
        /// <returns>A list of folders</returns>
        public async Task<IReadOnlyList<IInternalStorageFolder>> GetSubFoldersAsync()
        {
            await EnsureFolderItemsLoadedAsync();

            return _subFolders.Value;
        }

        #endregion

        private async Task EnsureFolderItemsLoadedAsync()
        {
            if (_folderItems != null) return;

            _folderItems = await _browser.GetPathItemsAsync(this);
        }

        private List<IInternalStorageFile> GetFilesInternal()
        {
            var items = GetFolderItems();
            return items.Where(i => i.ItemType == DeviceFileType.Measurement).Cast<IInternalStorageFile>().ToList();
        }

        private IEnumerable<IInternalStorageItem> GetFolderItems()
        {
            if (_folderItems != null) return _folderItems;

            _folderItems = _browser.GetPathItems(this);

            return _folderItems;
        }

        private List<IInternalStorageFolder> GetSubFoldersInternal()
        {
            var items = GetFolderItems();
            return items.Where(i => i.ItemType == DeviceFileType.Folder).Cast<IInternalStorageFolder>().ToList();
        }
    }
}