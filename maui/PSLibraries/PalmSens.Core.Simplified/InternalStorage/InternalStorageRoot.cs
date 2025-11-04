using System.Collections.Generic;
using System.Threading.Tasks;
using PalmSens.Data;

namespace PalmSens.Core.Simplified.InternalStorage
{
    internal class InternalStorageRoot : IInternalStorageFolder
    {
        private readonly List<IInternalStorageFile> _files;
        private readonly List<IInternalStorageFolder> _subFolders;

        public InternalStorageRoot(char pathSeparator)
        {
            PathSeparator = pathSeparator;
            _subFolders = new List<IInternalStorageFolder>();
            _files = new List<IInternalStorageFile>();
        }

        #region IInternalStorageFolder Members

        public char PathSeparator { get; }

        public string Name => "Root";
        public string FolderPath => string.Empty;
        public string FullPath => string.Empty;
        public DeviceFileType ItemType => DeviceFileType.Folder;
        public IInternalStorageItem Parent => this;

        public IReadOnlyList<IInternalStorageFolder> GetSubFolders()
        {
            return _subFolders;
        }

        public Task<IReadOnlyList<IInternalStorageFolder>> GetSubFoldersAsync()
        {
            return Task.FromResult((IReadOnlyList<IInternalStorageFolder>) _subFolders);
        }

        public IReadOnlyList<IInternalStorageFile> GetFiles()
        {
            return _files;
        }

        public Task<IReadOnlyList<IInternalStorageFile>> GetFilesAsync()
        {
            return Task.FromResult((IReadOnlyList<IInternalStorageFile>) _files);
        }

        public void AddSubFolder(IInternalStorageFolder folder)
        {
            _subFolders.Add(folder);
        }

        public void AddFile(IInternalStorageFile file)
        {
            _files.Add(file);
        }

        #endregion
    }
}