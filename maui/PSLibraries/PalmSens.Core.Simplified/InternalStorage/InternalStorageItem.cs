using System;
using PalmSens.Data;

namespace PalmSens.Core.Simplified.InternalStorage
{
    internal abstract class InternalStorageItem : IInternalStorageItem
    {
        protected InternalStorageItem(IInternalStorageItem parent, string name, DeviceFileType itemType)
        {
            Parent = parent ?? throw new ArgumentNullException(nameof(parent));
            Name = name ?? throw new ArgumentNullException(nameof(name));
            ItemType = itemType;
            FullPath = GenerateFullPath(parent.FullPath, name, parent.PathSeparator);
        }

        #region IInternalStorageItem Members

        /// <summary>
        ///     The folder path to the item.
        /// </summary>
        public string FolderPath => Parent.FullPath;

        /// <summary>
        ///     The full path, this will be <see cref="FolderPath" /> + <see cref="PathSeparator" /> + <see cref="Name" />
        /// </summary>
        public string FullPath { get; }

        /// <summary>
        ///     The device item type.
        /// </summary>
        public DeviceFileType ItemType { get; }

        /// <summary>
        ///     The name of the item.
        /// </summary>
        public string Name { get; }

        /// <summary>
        ///     The parent item. For root items this will be itself.
        /// </summary>
        public IInternalStorageItem Parent { get; }

        /// <summary>
        ///     The path separator.
        /// </summary>
        public char PathSeparator => Parent.PathSeparator;

        #endregion

        public override string ToString()
        {
            return $"{ItemType}:{FullPath}";
        }

        internal static string GenerateFullPath(string folderPath, string name, char pathSeparator)
        {
            return folderPath == string.Empty ? name : folderPath + pathSeparator + name;
        }
    }
}