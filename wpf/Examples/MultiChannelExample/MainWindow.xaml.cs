using PalmSens;
using PalmSens.Comm;
using PalmSens.Core.Simplified.Data;
using PalmSens.Devices;
using PalmSens.Techniques;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;
using PalmSens.Core.Simplified;

namespace MultiChannelExample
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        public MainWindow()
        {
            InitializeComponent();

            InitCVMethod(); //Create the cyclic voltammetry method that defines the measurement parameters
            InitPlot(); //Resets and initiates the plot control
            lbDevices.ItemsSource = _connectedDevices;
            _ = DiscoverConnectedDevicesAsync(); //Populate the connected device combobox control
        }

        /// <summary>
        /// The instance of method class containing the Cyclic Voltammetry parameters
        /// </summary>
        private CyclicVoltammetry _methodCV;

        /// <summary>
        /// The connected PalmSens & EmStat devices
        /// </summary>
        private ObservableCollection<DeviceItem> _connectedDevices = new ObservableCollection<DeviceItem>();

        /// <summary>
        /// The collection of measured data points that is binded to the datagrid.
        /// </summary>
        public ObservableCollection<DeviceItem> ConnectedDevices
        {
            get { return _connectedDevices; }
            set { _connectedDevices = value; }
        }

        /// <summary>
        /// Gets the selected channels.
        /// </summary>
        /// <value>
        /// The selected channels.
        /// </value>
        private int[] SelectedChannels
        {
            get
            {
                List<int> selectedChannels = new List<int>();

                for (int i = 0; i < _connectedDevices.Count; i++)
                    if (_connectedDevices[i].Checked)
                        selectedChannels.Add(i);

                return selectedChannels.ToArray();
            }
        }

        /// <summary>
        /// Gets the selected devices.
        /// </summary>
        /// <value>
        /// The selected devices.
        /// </value>
        private Device[] SelectedDevices
        {
            get
            {
                int[] selectedChannels = SelectedChannels;
                int n = selectedChannels.Length;
                Device[] devices = new Device[n];
                for (int i = 0; i < n; i++)
                    devices[i] = _connectedDevices[selectedChannels[i]].Device;
                return devices;
            }
        }

        /// <summary>
        /// Initializes the CV method.
        /// </summary>
        private void InitCVMethod()
        {
            _methodCV = new CyclicVoltammetry(); //Create a new cyclic voltammetry method with the default settings
            _methodCV.BeginPotential = -.5f; //Sets the potential to start the scan from
            _methodCV.Vtx1Potential = -.5f; //Sets the first potential where the scan direction reverses
            _methodCV.Vtx2Potential = .5f; //Sets the second potential where the scan direction reverses
            _methodCV.StepPotential = 0.005f; //Sets the step size
            _methodCV.Scanrate = 1f; //Sets the scan rate to 1 V/s
            _methodCV.nScans = 3; //Sets the number of scans

            _methodCV.EquilibrationTime = 1f; //Equilabrates the cell at the defined potential for 1 second before starting the measurement
            _methodCV.Ranging.StartCurrentRange = new CurrentRange(CurrentRanges.cr1uA); //Starts equilabration in the 1µA current range
            _methodCV.Ranging.MinimumCurrentRange = new CurrentRange(CurrentRanges.cr1uA); //Min current range 10nA
            _methodCV.Ranging.MaximumCurrentRange = new CurrentRange(CurrentRanges.cr1uA); //Max current range 1mA
        }

        /// <summary>
        /// Initializes the plot control.
        /// </summary>
        private void InitPlot()
        {
            plot.ClearAll(); //Clear all curves and data from plot
            //Set the Axis labels
            plot.XAxisLabel = "V";
            plot.YAxisLabel = "µA";
            plot.AddData("", new double[0], new double[0]); //Add a empty data array to draw an empty plot
        }

        /// <summary>
        /// Discovers the connected PalmSens & EmStat devices and adds them to the combobox control.
        /// </summary>
        private async Task DiscoverConnectedDevicesAsync()
        {
            btnRefresh.IsEnabled = false;
            _connectedDevices.Clear();
            Device[] devices = await psMultiCommSimpleWPF.GetConnectedDevicesAsync(); //Discover connected devices

            foreach (Device d in devices)
                _connectedDevices.Add(new DeviceItem() { Checked = false, Device = d, Title = d.ToString() }); //Add connected devices to control

            int nDevices = _connectedDevices.Count;
            lbConsole.Items.Add($"Found {nDevices} device(s).");
            btnConnect.IsEnabled = nDevices > 0;
            btnRefresh.IsEnabled = true;
        }

        /// <summary>
        /// Handles the Click event of the btnRefresh control.
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="RoutedEventArgs"/> instance containing the event data.</param>
        private async void btnRefresh_Click(object sender, RoutedEventArgs e)
        {
            await DiscoverConnectedDevicesAsync(); //Add connected devices to the devices combobox control
        }

        /// <summary>
        /// Handles the Click event of the btnConnect control.
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="RoutedEventArgs"/> instance containing the event data.</param>
        private async void btnConnect_Click(object sender, RoutedEventArgs e)
        {
            btnConnect.IsEnabled = false;
            if (!psMultiCommSimpleWPF.Connected) //Determine whether a device is currently connected
            {
                if (SelectedChannels.Length == 0)
                    return;

                try
                {
                    //Connect to the device selected in the devices listbox control
                    await psMultiCommSimpleWPF.ConnectAsync(SelectedDevices);
                    lbConsole.Items.Add($"Connected to {psMultiCommSimpleWPF.NConnectedChannels} channels");
                }
                catch (Exception ex)
                {
                    lbConsole.Items.Add(ex.Message);
                }
            }
            else
            {
                await psMultiCommSimpleWPF.DisconnectAsync(); //Disconnect from the connected device
                await DiscoverConnectedDevicesAsync();
            }

            //Update UI based on connection status
            if (psMultiCommSimpleWPF.Connected)
            {
                //Updated selected channel list and connected device combobox
                _connectedDevices.Clear();
                cmbDevices.Items.Clear();
                for (int i = 0; i < psMultiCommSimpleWPF.NConnectedChannels; i++)
                {
                    string chnl = $"{i + 1}: {psMultiCommSimpleWPF.ConnectedDevices[i].ToString()}";
                    _connectedDevices.Add(new DeviceItem() { Checked = false, Device = psMultiCommSimpleWPF.ConnectedDevices[i], Title = chnl });
                    cmbDevices.Items.Add(chnl);
                }
                cmbDevices.SelectedIndex = 0;
            }

            lblDevices.Content = psMultiCommSimpleWPF.Connected ? "Connected channels:" : "Available devices";
            cmbDevices.IsEnabled = psMultiCommSimpleWPF.Connected;
            btnRefresh.IsEnabled = !psMultiCommSimpleWPF.Connected;
            btnConnect.Content = psMultiCommSimpleWPF.Connected ? "Disconnect" : "Connect";
            btnMeasure.IsEnabled = psMultiCommSimpleWPF.Connected;
            btnConnect.IsEnabled = true;
        }

        /// <summary>
        /// Handles the Click event of the btnMeasure control.
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="RoutedEventArgs"/> instance containing the event data.</param>
        private async void btnMeasure_Click(object sender, RoutedEventArgs e)
        {
            int[] selectedChannels = SelectedChannels;
            if (selectedChannels.Length == 0) return;

            btnMeasure.IsEnabled = false;
            lbDevices.IsEnabled = false;

            if (selectedChannels.Count(c => psMultiCommSimpleWPF.ChannelStates[c] == CommManager.DeviceState.Idle) == selectedChannels.Length) //Determine whether the devices are currently idle or measuring
            {
                try
                {
                    plot.ClearAll(); //Clears data from previous measurements from the plot
                    IEnumerable<(SimpleMeasurement measurement, int channelIndex, Exception exception)> result = await psMultiCommSimpleWPF.MeasureAsync(_methodCV, selectedChannels); //Start measurement defined in the method
                    foreach (var channel in result)
                        if (channel.exception != null)
                            lbConsole.Items.Add(channel.exception.Message);
                }
                catch (Exception ex)
                {
                    lbConsole.Items.Add(ex.Message);
                }
            }
            else
            {
                try
                {
                    await psMultiCommSimpleWPF.AbortAllActiveMeasurementsAsync(); //Abort the active measurement
                }
                catch (Exception ex)
                {
                    lbConsole.Items.Add(ex.Message);
                }
            }
            btnMeasure.IsEnabled = true;
        }

        /// <summary>
        /// Raised when device status package is received (the device does not send status packages while measuring)
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="PalmSens.Comm.StatusEventArgs"/> instance containing the event data.</param>
        private void PsMultiCommSimpleWPF_ReceiveStatus(object sender, StatusEventArgs e, int channel)
        {
            if (cmbDevices.SelectedIndex == channel)
            {
                Status status = e.GetStatus(); //Get the PalmSens.Comm.Status instance from the event data
                double potential = status.PotentialReading.Value; //Get the potential
                double currentInRange = status.CurrentReading.ValueInRange; //Get the current expressed inthe active current range
                PalmSens.Comm.ReadingStatus currentStatus = status.CurrentReading.ReadingStatus; //Get the status of the current reading
                CurrentRange cr = status.CurrentReading.CurrentRange; //Get the active current range

                tbPotential.Text = potential.ToString("F3");
                tbCurrent.Text = currentInRange.ToString("F3");
                lblCurrentRange.Content = $"* {cr.ToString()}";
            }
        }

        /// <summary>
        /// Raised when the connected device's status changes
        /// </summary>
        /// <param name="sender">The sender.</param>
        /// <param name="CurrentState">State of the current.</param>
        private void PsMultiCommSimpleWPF_StateChanged(object sender, CommManager.DeviceState ChannelState, int channel)
        {
            if (cmbDevices.SelectedIndex == channel)
            {
                tbStatus.Text = ChannelState.ToString(); //Updates the device state indicator textbox
            }

            if (SelectedChannels.Contains(channel))
            {
                btnConnect.IsEnabled = ChannelState == PalmSens.Comm.CommManager.DeviceState.Idle;
                btnMeasure.Content = ChannelState == PalmSens.Comm.CommManager.DeviceState.Idle ? "Measure" : "Abort";
            }
        }

        /// <summary>
        /// Raised when the measurement is started
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="EventArgs"/> instance containing the event data.</param>
        private void PsMultiCommSimpleWPF_MeasurementStarted(object sender, int channel, Exception ex)
        {
            if (ex != null)
            {
                lbConsole.Items.Add(ex.Message);
            }
            else
            {
                lbConsole.Items.Add($"Channel {channel + 1}: Cyclic voltammetry measurement started.");
            }
        }

        /// <summary>
        /// Raised when the measurement is ended
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="EventArgs"/> instance containing the event data.</param>
        private void PsMultiCommSimpleWPF_MeasurementEnded(object sender, int channel, Exception ex)
        {
            if (ex != null)
            {
                lbConsole.Items.Add($"Channel {channel + 1}: Measurement ended abruptly, {ex.Message}.");
            }
            else
            {
                lbConsole.Items.Add($"Channel {channel + 1}: Measurement ended.");
                lbDevices.IsEnabled = psMultiCommSimpleWPF.ChannelStates.Count(c => c == CommManager.DeviceState.Idle) == psMultiCommSimpleWPF.NConnectedChannels;
            }
        }

        /// <summary>
        /// Raised when a Simple Curve in the active SimpleMeasurement starts receiving data
        /// </summary>
        /// <param name="sender">The sender.</param>
        /// <param name="activeSimpleCurve">The active simple curve.</param>
        private void PsMultiCommSimpleWPF_SimpleCurveStartReceivingData(object sender, SimpleCurve activeSimpleCurve)
        {
            plot.AddSimpleCurve(activeSimpleCurve);

            //Subscribe to the event indicating when the curve stops receiving new data points
            activeSimpleCurve.CurveFinished += activeSimpleCurve_CurveFinished;

            lbConsole.Items.Add("Curve is receiving new data...");
        }

        /// <summary>
        /// Raised when a SimpleCurve stops receiving new data points
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="System.EventArgs" /> instance containing the event data.</param>
        private void activeSimpleCurve_CurveFinished(object sender, EventArgs e)
        {
            if (!Dispatcher.CheckAccess()) //Data is parsed asynchronously in the case this event was raised on a different thread it must be invoked back onto the UI thread
            {
                Dispatcher.BeginInvoke(new EventHandler(activeSimpleCurve_CurveFinished), sender, e);
                return;
            }
            SimpleCurve activeCurve = sender as SimpleCurve;
            int nDataPointsReceived = activeCurve != null ? activeCurve.NDataPoints : 0;
            lbConsole.Items.Add($"{nDataPointsReceived} data point(s) received.");

            //Unsubscribe from the curves events to avoid memory leaks
            activeCurve.CurveFinished -= activeSimpleCurve_CurveFinished;
        }

        /// <summary>
        /// Raised when a channel disconnects
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="System.EventArgs" /> instance containing the event data.</param>
        private void PsMultiCommSimpleWPF_Disconnected(object sender, Exception exception, int channel, Device device)
        {
            if (exception != null)
            {
                lbConsole.Items.Add($"Channel {channel + 1}: {exception.Message}");
            }

            lbConsole.Items.Add($"Channel {channel + 1} disconnected.");
            btnConnect.Content = psMultiCommSimpleWPF.Connected ? "Disconnect" : "Connect";
            btnConnect.IsEnabled = true;
            btnMeasure.Content = "Measure";
        }
    }

    /// <summary>
    /// Object class for available/connected devices in lbDevices with checkbox and label
    /// </summary>
    public class DeviceItem
    {
        public bool Checked { get; set; }
        public string Title { get; set; }
        public Device Device { get; set; }
    }
}
