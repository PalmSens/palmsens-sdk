using PalmSens;
using PalmSens.Core.Simplified;
using PalmSens.Core.Simplified.InternalStorage;
using PalmSens.Data;
using System.Collections.ObjectModel;
using PalmSens.Core.Simplified.MAUI;
using Device = PalmSens.Devices.Device;

namespace PalmSensInternalStorage
{
    public partial class MainPage : ContentPage
    {
        public IPlatformInvoker PlatformInvoker { get; }
        private IReadOnlyList<Device> _availableDevices;
        private Device _selectedDevice;
        private readonly PSCommSimple _psCommSimple;
        private string _selectedFile;

        public MainPage(
            PSCommSimpleMaui psCommSimple,
            IPlatformInvoker platformInvoker)
        {
            PlatformInvoker = platformInvoker;
            InitializeComponent();
            BindingContext = this;

            psCommSimple.Initialize();  // This needs to be called after the main page has been initialized
            this._psCommSimple = psCommSimple;

            _contents = new Dictionary<string, IInternalStorageItem>();
        }

        private readonly IDictionary<string, IInternalStorageItem> _contents;

        private IInternalStorageFolder _root;

        public ObservableCollection<string> Log
        {
            get { return _log; }
            set { _log = value; }
        }

        private ObservableCollection<string> _log = [];

        public ObservableCollection<string> InternalStorage
        {
            get { return _internalStorage; }
            set { _internalStorage = value; }
        }

        private ObservableCollection<string> _internalStorage = [];

        public string SelectedFile
        {
            get => _selectedFile;
            set
            {
                _selectedFile = value;
                OnPropertyChanged();
            }
        }

        public IReadOnlyList<Device> AvailableDevices
        {
            get => _availableDevices;
            set
            {
                _availableDevices = value;
                OnPropertyChanged();
            }
        }

        public Device? SelectedDevice
        {
            get => _selectedDevice;
            set
            {
                _selectedDevice = value;
                OnPropertyChanged();
            }
        }

        private async void DiscoverClicked(object? sender, EventArgs e)
        {
            DiscoverBtn.IsEnabled = false;
            try
            {
                AvailableDevices = await _psCommSimple.GetAvailableDevices();
                SelectedDevice = AvailableDevices.FirstOrDefault();
            }
            finally
            {
                DiscoverBtn.IsEnabled = true;
                ConnectBtn.IsEnabled = true;
            }
        }

        private async void ConnectClicked(object? sender, EventArgs e)
        {
            Log.Add($"Connecting to {SelectedDevice}...");


            if (_psCommSimple.Connected)
            {
                await _psCommSimple.Disconnect();

            }
            else
            {
                try
                {
                    await _psCommSimple.Connect(SelectedDevice);
                }
                catch (Exception ex)
                {
                    Log.Add(ex.Message);
                }
            }

            ListFilesBtn.IsEnabled = _psCommSimple.Connected;
            OpenFileBtn.IsEnabled = _psCommSimple.Connected;
            ConnectBtn.Text = _psCommSimple.Connected ? "Disconnect" : "Connect";
            Log.Add(_psCommSimple.Connected ? $"Connected to {_psCommSimple.ConnectedDevice}" : "Nothing is connected");

            if (_psCommSimple.Connected && _psCommSimple.Capabilities.SupportsStorage)
            {
                GetSpaceUsed();
                ListFiles();
            }
            else if (_psCommSimple.Connected)
                Log.Add("The connected device does not support internal storage features");
        }


        private void ListFilesClicked(object? sender, EventArgs e)
        {
            ListFilesBtn.IsEnabled = false;
            ListFiles();
            ListFilesBtn.IsEnabled = true;
        }

        private async void ListFiles()
        {
            Log.Add("Reading contents from: Root");

            var browser = _psCommSimple.GetInternalStorageBrowser();

            _root = browser.GetRoot();

            LoadChildren(_root);

            OpenFileBtn.IsEnabled = true;
        }

        private void OpenFileClicked(object? sender, EventArgs e)
        {
            OpenFileBtn.IsEnabled = false;
            ListFilesBtn.IsEnabled = false;
            try
            {
                var name = _selectedFile;

                var item = _contents[name];

                if (item.ItemType == DeviceFileType.Folder)
                {
                    Log.Add($"Opening path: {item.Name}");
                    LoadChildren(item);
                }
                else
                {
                    var file = (IInternalStorageFile)item;

                    var m = file.GetMeasurement(MeasType.Overlay);

                    Log.Add(m != null ? $"Load file '{item.Name}', with method '{m.Method}'" : $"Could not load file '{item.Name}'");
                }
            }
            catch (Exception exception)
            {
                Log.Add($"{exception}");
            }
            OpenFileBtn.IsEnabled = true;
            ListFilesBtn.IsEnabled = true;
        }

        private void GetSpaceUsed()
        {
            var total = (int)_psCommSimple.Comm.ClientConnection.GetDeviceSize();
            var free = (int)_psCommSimple.Comm.ClientConnection.GetDeviceFree();

            var perc = Math.Min((total - free) / (double)total, 1.0);
            Log.Add($"{(int)Math.Round(perc * 100.0):F2}% of storage space used.");
        }

        private void LoadChildren(IInternalStorageItem item)
        {
            if (item.ItemType == DeviceFileType.Measurement) return;

            InternalStorage.Clear();
            _contents.Clear();

            var folder = (IInternalStorageFolder)item;
            var files = folder.GetFiles();
            var subFolders = folder.GetSubFolders();
            var totalItems = files.Count + subFolders.Count;
            var hasParent = !ReferenceEquals(item, _root);

            Log.Add($"Loading {totalItems} storage items.");

            if (hasParent)
                ListPreviousItem(folder.Parent);
            var currentIndex = LoadChildrenItems(subFolders, 1);
            LoadChildrenItems(files, currentIndex);

            SelectedFile = InternalStorage.FirstOrDefault();
        }

        private void ListPreviousItem(IInternalStorageItem parent)
        {
            string name = $"<Back> {parent.Name}";
            _contents[name] = parent;
            InternalStorage.Add(name);
        }

        private int LoadChildrenItems(IEnumerable<IInternalStorageItem> items, int index)
        {
            foreach (var item in items.OrderBy(i => i.Name))
            {
                var type = item.ItemType == DeviceFileType.Folder ? "<Dir>" : "<File>";
                string name = $"{type} {item.Name}";

                _contents[name] = item;
                InternalStorage.Add(name);
                index++;
            }

            return index;
        }

    }
}
