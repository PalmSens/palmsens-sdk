using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using PalmSens.Comm;
using PalmSens.Data;
using PalmSens.Devices;

namespace PalmSens.Core.Simplified.InternalStorage
{
    /// <summary>
    ///     Internal storage browser that is used for browsing device folders and files.
    /// </summary>
    public interface IInternalStorageBrowser
    {
        IInternalStorageFileLoader GetLoader(DeviceFile rawData);

        /// <summary>
        ///     Get the path items for the parent folder.
        /// </summary>
        /// <param name="parent">The parent folder.</param>
        /// <returns>A list of storage items, can be folders and/or measurements.</returns>
        IList<IInternalStorageItem> GetPathItems(IInternalStorageFolder parent);

        /// <summary>
        ///     Get the path items for the parent folder.
        /// </summary>
        /// <param name="parent">The parent folder.</param>
        /// <returns>A list of storage items, can be folders and/or measurements.</returns>
        Task<IList<IInternalStorageItem>> GetPathItemsAsync(IInternalStorageFolder parent);

        /// <summary>
        ///     Get the root folder for the device.
        /// </summary>
        IInternalStorageFolder GetRoot();

        /// <summary>
        ///     Get the root folder for the device.
        /// </summary>
        Task<IInternalStorageFolder> GetRootAsync();

        /// <summary>
        ///     Run a function on the client connection. This is required to ensure that when interacting on the device that the
        ///     correct locking is used.
        /// </summary>
        /// <typeparam name="TResult">The expected result.</typeparam>
        /// <param name="funcToRun">The function to run.</param>
        /// <returns>Returns the <typeparamref name="TResult" /></returns>
        TResult Run<TResult>(Func<ClientConnection, TResult> funcToRun);

        /// <summary>
        ///     Run a function on the client connection. This is required to ensure that when interacting on the device that the
        ///     correct locking is used.
        /// </summary>
        /// <typeparam name="TResult">The expected result.</typeparam>
        /// <param name="funcToRun">The function to run.</param>
        /// <returns>Returns a <see cref="Task" /> of the <typeparamref name="TResult" /></returns>
        Task<TResult> RunAsync<TResult>(Func<ClientConnection, Task<TResult>> funcToRun);
    }

    /// <summary>
    ///     Internal storage browser that is used for browsing device folders and files.
    /// </summary>
    public class InternalStorageBrowser : IInternalStorageBrowser
    {
        private readonly ClientConnection _clientConnection;

        public InternalStorageBrowser(ClientConnection clientConnection)
        {
            _clientConnection = clientConnection ?? throw new ArgumentNullException(nameof(clientConnection));
        }

        #region IInternalStorageBrowser Members

        public IInternalStorageFileLoader GetLoader(DeviceFile rawData)
        {
            return _clientConnection.Capabilities is MethodScriptDeviceCapabilities ? (IInternalStorageFileLoader) new InternalStorageFileMethodScriptLoader(rawData, _clientConnection) : new InternalStorageFileNormalLoader(rawData, _clientConnection);
        }

        /// <summary>
        ///     Get the path items for the parent folder.
        /// </summary>
        /// <param name="parent">The parent folder.</param>
        /// <returns>A list of storage items, can be folders and/or measurements.</returns>
        public IList<IInternalStorageItem> GetPathItems(IInternalStorageFolder parent)
        {
            ValidateConnectionTypeLazy();

            var deviceFiles = GetDeviceFiles(parent.FullPath);
            return CreatePathItemsFromDeviceFiles(parent, deviceFiles);
        }

        /// <summary>
        ///     Get the path items for the parent folder.
        /// </summary>
        /// <param name="parent">The parent folder.</param>
        /// <returns>A list of storage items, can be folders and/or measurements.</returns>
        public async Task<IList<IInternalStorageItem>> GetPathItemsAsync(IInternalStorageFolder parent)
        {
            ValidateConnectionTypeLazy();

            var deviceFiles = await GetDeviceFilesAsync(parent.FullPath);
            return CreatePathItemsFromDeviceFiles(parent, deviceFiles);
        }

        /// <summary>
        ///     Get the root folder for the device.
        /// </summary>
        public IInternalStorageFolder GetRoot()
        {
            var rootList = GetDeviceFiles("");
            return ProcessDeviceFiles(rootList);
        }

        /// <summary>
        ///     Get the root folder for the device.
        /// </summary>
        public async Task<IInternalStorageFolder> GetRootAsync()
        {
            var rootList = await GetDeviceFilesAsync("");
            return ProcessDeviceFiles(rootList);
        }

        /// <summary>
        ///     Run a function on the client connection. This is required to ensure that when interacting on the device that the
        ///     correct locking is used.
        /// </summary>
        /// <typeparam name="TResult">The expected result.</typeparam>
        /// <param name="funcToRun">The function to run.</param>
        /// <returns>Returns the <typeparamref name="TResult" /></returns>
        public TResult Run<TResult>(Func<ClientConnection, TResult> funcToRun)
        {
            var command = new CommSimpleCommand<TResult>(_clientConnection, funcToRun);
            return command.Execute();
        }

        /// <summary>
        ///     Run a function on the client connection. This is required to ensure that when interacting on the device that the
        ///     correct locking is used.
        /// </summary>
        /// <typeparam name="TResult">The expected result.</typeparam>
        /// <param name="funcToRun">The function to run.</param>
        /// <returns>Returns a <see cref="Task" /> of the <typeparamref name="TResult" /></returns>
        public Task<TResult> RunAsync<TResult>(Func<ClientConnection, Task<TResult>> funcToRun)
        {
            var command = new CommSimpleAsyncCommand<TResult>(_clientConnection, funcToRun);
            return command.ExecuteAsync();
        }

        #endregion

        /// <summary>
        /// Add a new subfolder to the <paramref name="folderMapping"/>. This used when building the file system to return existing folders or add when not existing.
        /// </summary>
        /// <param name="folderMapping">The folder mapping</param>
        /// <param name="parentFolder">The parent folder.</param>
        /// <param name="subFolderName">The sub folder name</param>
        /// <returns></returns>
        private static InternalStorageFolder GetOrAddSubFolder(IDictionary<string, IInternalStorageItem> folderMapping, IInternalStorageFolder parentFolder, string subFolderName)
        {
            var fullPath = InternalStorageItem.GenerateFullPath(parentFolder.FullPath, subFolderName, parentFolder.PathSeparator);
            if (folderMapping.TryGetValue(fullPath, out var existing)) return (InternalStorageFolder) existing;

            var subFolder = new InternalStorageFolder(parentFolder, subFolderName);
            folderMapping[subFolder.FullPath] = subFolder;
            parentFolder.AddSubFolder(subFolder);

            return subFolder;
        }

        /// <summary>
        /// Build a lazy loaded file system.
        /// </summary>
        /// <param name="rootList">The list of root items</param>
        private IInternalStorageFolder BuildLazyFileSystem(IEnumerable<DeviceFile> rootList)
        {
            var root = new InternalStorageRoot('\\');

            foreach (var deviceFile in rootList)
            {
                if (deviceFile.Type == DeviceFileType.Folder)
                {
                    root.AddSubFolder(new InternalStorageFolderLazy(root, deviceFile.Name, this));
                    continue;
                }

                root.AddFile(new InternalStorageFile(root, deviceFile.Name, this));
            }

            return root;
        }

        /// <summary>
        /// Build up a complete file system from the file list. This is used with method script devices that return all files instead of the a file path items only
        /// </summary>
        /// <param name="fileList">The list of file items.</param>
        private IInternalStorageFolder BuildUpFileSystem(IEnumerable<DeviceFile> fileList)
        {
            var folderMapping = new Dictionary<string, IInternalStorageItem>();
            var root = new InternalStorageRoot('/');

            foreach (var deviceFile in fileList)
            {
                if (!deviceFile.Dir.Contains(root.PathSeparator))
                {
                    root.AddFile(new InternalStorageFile(root, deviceFile.Name, this));
                    continue;
                }

                var split = deviceFile.Dir.Split(root.PathSeparator);
                var folderName = split[0];

                var folder = GetOrAddSubFolder(folderMapping, root, folderName);

                for (var i = 1; i < split.Length; i++)
                {
                    folderName = split[i];
                    folder = GetOrAddSubFolder(folderMapping, folder, folderName);
                }

                folder.AddFile(new InternalStorageFile(folder, deviceFile.Name, this));
            }

            return root;
        }

        /// <summary>
        /// Create the Internal storage items for the device files. This will create lazy loaded folders when <see cref="DeviceFile"/> is <see cref="DeviceFileType.Folder"/>
        /// </summary>
        /// <param name="parent">The parent folder.</param>
        /// <param name="deviceFiles">The list of device files</param>
        private List<IInternalStorageItem> CreatePathItemsFromDeviceFiles(IInternalStorageFolder parent, List<DeviceFile> deviceFiles)
        {
            return deviceFiles.Select(d => d.Type == DeviceFileType.Folder ? (IInternalStorageItem) new InternalStorageFolderLazy(parent, d.Name, this) : new InternalStorageFile(parent, d.Name, this)).ToList();
        }
        
        /// <summary>
        /// Get the device files for the path.
        /// </summary>
        /// <param name="path">The path to return</param>
        /// <returns>A list of <see cref="DeviceFile"/></returns>
        private List<DeviceFile> GetDeviceFiles(string path)
        {
            var command = new CommSimpleCommand<List<DeviceFile>>(_clientConnection, connection => connection.GetDeviceFiles(path));
            return command.Execute();
        }

        /// <summary>
        /// Get the device files for the path.
        /// </summary>
        /// <param name="path">The path to return</param>
        /// <returns>A list of <see cref="DeviceFile"/></returns>
        private Task<List<DeviceFile>> GetDeviceFilesAsync(string path)
        {
            var command = new CommSimpleAsyncCommand<List<DeviceFile>>(_clientConnection, connection => connection.GetDeviceFilesAsync(path));
            return command.ExecuteAsync();
        }

        /// <summary>
        /// Process the root file list. For method script devices, return a fully loaded file system, otherwise a lazy loaded file system.
        /// </summary>
        /// <param name="rootList"></param>
        /// <returns></returns>
        private IInternalStorageFolder ProcessDeviceFiles(IEnumerable<DeviceFile> rootList)
        {
            return _clientConnection.Capabilities is MethodScriptDeviceCapabilities ? BuildUpFileSystem(rootList) : BuildLazyFileSystem(rootList);
        }

        /// <summary>
        /// Validate that the connection is loaded lazy
        /// </summary>
        private void ValidateConnectionTypeLazy()
        {
            if (_clientConnection is ClientConnectionMS)
                throw new InvalidOperationException($"The current device '{_clientConnection.DeviceType}' is not valid for lazy loading.");
        }
    }
}