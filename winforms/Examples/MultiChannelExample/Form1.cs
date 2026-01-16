using System;
using System.Collections.Generic;
using System.Drawing;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Forms;
using PalmSens;
using PalmSens.Comm;
using PalmSens.Core.Simplified.Data;
using PalmSens.Devices;
using PalmSens.Techniques;
using PalmSens.Windows.Devices;

namespace MultiChannelExample
{
    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();

            InitCVMethod(); //Create the cyclic voltammetry method that defines the measurement parameters
            InitPlot(); //Resets and initiates the plot control
            _ = DiscoverConnectedDevicesAsync(); //Populate the connected device combobox control
        }

        /// <summary>
        /// The instance of method class containing the Cyclic Voltammetry parameters
        /// </summary>
        private CyclicVoltammetry _methodCV;

        /// <summary>
        /// The connected PalmSens & EmStat devices
        /// </summary>
        private IReadOnlyList<Device> _connectedDevices = new Device[0];

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
                if (chkLBDevices.Items.Count == 0)
                    return new int[0];

                var selectedLBItems = chkLBDevices.CheckedIndices;
                int n = selectedLBItems.Count;
                int[] selectedChannels = new int[n];

                for (int i = 0; i < n; i++)
                    selectedChannels[i] = selectedLBItems[i];

                return selectedChannels;
            }
        }

        private Device[] _selectedDevices = null;

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
                if(!psMultiCommSimpleWinForms.Connected)
                {
                    int[] selectedChannels = SelectedChannels;
                    int n = selectedChannels.Length;
                    Device[] devices = new Device[n];
                    for (int i = 0; i < n; i++)
                        devices[i] = _connectedDevices[selectedChannels[i]];
                    return _selectedDevices = devices;
                }
                else
                {
                    return _selectedDevices;
                }
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
            _methodCV.StepPotential = 0.05f; //Sets the step size
            _methodCV.Scanrate = 1f; //Sets the scan rate to 1 V/s
            _methodCV.nScans = 5; //Sets the number of scans

            _methodCV.EquilibrationTime = 1f; //Equilabrates the cell at the defined potential for 1 second before starting the measurement
            _methodCV.Ranging.StartCurrentRange = new CurrentRange(CurrentRanges.cr1uA); //Starts equilabration in the 1µA current range
            _methodCV.Ranging.MinimumCurrentRange = new CurrentRange(CurrentRanges.cr10nA); //Min current range 10nA
            _methodCV.Ranging.MaximumCurrentRange = new CurrentRange(CurrentRanges.cr1mA); //Max current range 1mA
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
            btnRefresh.Enabled = false;
            btnConnect.Enabled = false;
            btnToggleSelectAll.Enabled = false;

            lbConsole.Items.Add("Searching for connected devices.");
            chkLBDevices.Items.Clear();
            _connectedDevices = await psMultiCommSimpleWinForms.GetConnectedDevicesAsync(); //Discover connected devices

            foreach (Device d in _connectedDevices)
                chkLBDevices.Items.Add(d.ToString()); //Add connected devices to control

            int nDevices = chkLBDevices.Items.Count;
            lbConsole.Items.Add($"Found {nDevices} device(s).");

            btnConnect.Enabled = nDevices > 0;
            btnToggleSelectAll.Enabled = nDevices > 0;
            btnRefresh.Enabled = true;
        }

        /// <summary>
        /// Handles the Click event of the btnRefresh control.
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="EventArgs"/> instance containing the event data.</param>
        private async void btnRefresh_Click(object sender, EventArgs e)
        {
            await DiscoverConnectedDevicesAsync(); //Add connected devices to the devices combobox control
        }

        /// <summary>
        /// (De)selects all of the devices in the list.
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="EventArgs"/> instance containing the event data.</param>
        private void btnToggleSelectAll_Click(object sender, EventArgs e)
        {
            if(chkLBDevices.CheckedIndices.Count > 0)
            {
                for (int i = 0; i < chkLBDevices.Items.Count; i++)
                    chkLBDevices.SetItemChecked(i, false);
            }
            else
            {
                for (int i = 0; i < chkLBDevices.Items.Count; i++)
                    chkLBDevices.SetItemChecked(i, true);
            }
        }

        /// <summary>
        /// Handles the Click event of the btnConnect control.
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="EventArgs"/> instance containing the event data.</param>
        private async void btnConnect_Click(object sender, EventArgs e)
        {
            btnConnect.Enabled = false;
            if (!psMultiCommSimpleWinForms.Connected) //Determine whether a device is currently connected
            {
                if (SelectedChannels.Length == 0)
                    return;

                try
                {
                    //Connect to the device selected in the devices listbox control
                    await psMultiCommSimpleWinForms.ConnectAsync(SelectedDevices);
                    lbConsole.Items.Add($"Connected to {psMultiCommSimpleWinForms.NConnectedChannels} channels");
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
                    await psMultiCommSimpleWinForms.DisconnectAsync(); //Disconnect from the connected device
                    lbConsole.Items.Add("Disconnected");
                }
                catch (Exception exception)
                {
                    lbConsole.Items.Add(exception.Message);
                }
            }

            //Update UI based on connection status
            if (psMultiCommSimpleWinForms.Connected)
            {
                //Updated selected channel list and connected device combobox
                chkLBDevices.Items.Clear();
                cmbDevices.Items.Clear();
                for (int i = 0; i < psMultiCommSimpleWinForms.NConnectedChannels; i++)
                {
                    string chnl = $"{i + 1}: {SelectedDevices[i].ToString()}";
                    chkLBDevices.Items.Add(chnl);
                    cmbDevices.Items.Add(chnl);
                }
                cmbDevices.SelectedIndex = 0;
            }

            lblDevices.Text = psMultiCommSimpleWinForms.Connected ? "Connected channels:" : "Available devices";
            cmbDevices.Enabled = psMultiCommSimpleWinForms.Connected;
            btnRefresh.Enabled = !psMultiCommSimpleWinForms.Connected;
            btnConnect.Text = psMultiCommSimpleWinForms.Connected ? "Disconnect" : "Connect";
            btnMeasure.Enabled = psMultiCommSimpleWinForms.Connected;
            btnConnect.Enabled = true;
        }

        /// <summary>
        /// Handles the Click event of the btnMeasure control.
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="EventArgs"/> instance containing the event data.</param>
        private async void btnMeasure_Click(object sender, EventArgs e)
        {
            int[] selectedChannels = SelectedChannels;

            btnMeasure.Enabled = false;
            chkLBDevices.Enabled = false;

            if (psMultiCommSimpleWinForms.NConnectedChannels == selectedChannels.Length && selectedChannels.All(c => psMultiCommSimpleWinForms.CommsByChannelIndex[c].State == CommManager.DeviceState.Idle)) //Determine whether the devices are currently disconnected, idle or measuring
            {
                if (selectedChannels.Length == 0) return;

                try
                {
                    plot.ClearAll(); //Clears data from previous measurements from the plot
                    IEnumerable<(SimpleMeasurement measurement, int channelIndex, Exception exception)> result = await psMultiCommSimpleWinForms.MeasureAsync(_methodCV, selectedChannels); //Start measurement defined in the method
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
                    await psMultiCommSimpleWinForms.AbortAllActiveMeasurementsAsync(); //Abort the active measurement
                    chkLBDevices.Enabled = true;
                }
                catch (Exception ex)
                {
                    lbConsole.Items.Add(ex.Message);
                }
            }
            btnMeasure.Enabled = true;
        }

        /// <summary>
        /// Raised when device status package is received (the device does not send status packages while measuring)
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="PalmSens.Comm.StatusEventArgs"/> instance containing the event data.</param>
        private void psMultiCommSimpleWinForms_ReceiveStatus(object sender, StatusEventArgs e, int channel)
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
                switch (currentStatus)
                {
                    case PalmSens.Comm.ReadingStatus.OK:
                        tbCurrent.ForeColor = Color.Black;
                        break;
                    case PalmSens.Comm.ReadingStatus.Overload:
                        tbCurrent.ForeColor = Color.Red;
                        break;
                    case PalmSens.Comm.ReadingStatus.Underload:
                        tbCurrent.ForeColor = Color.Yellow;
                        break;
                }
                lblCurrentRange.Text = $"* {cr.ToString()}";
            }
        }

        /// <summary>
        /// Raised when the connected device's status changes
        /// </summary>
        /// <param name="sender">The sender.</param>
        /// <param name="CurrentState">State of the current.</param>
        private void psMultiCommSimpleWinForms_StateChanged(object sender, CommManager.DeviceState ChannelState, int channel)
        {
            if (cmbDevices.SelectedIndex == channel)
                tbDeviceStatus.Text = ChannelState.ToString(); //Updates the device state indicator textbox

            if (SelectedChannels.Contains(channel))
            {
                btnConnect.Enabled = ChannelState == PalmSens.Comm.CommManager.DeviceState.Idle;
                btnMeasure.Text = ChannelState == PalmSens.Comm.CommManager.DeviceState.Idle ? "Measure" : "Abort";
            }
        }

        /// <summary>
        /// Raised when the measurement is ended
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="EventArgs"/> instance containing the event data.</param>
        private void psMultiCommSimpleWinForms_MeasurementEnded(object sender, int channel, Exception exception)
        {
            if (exception == null)
            {
                lbConsole.Items.Add($"Channel {channel + 1}: Measurement ended.");
            }
            else
            {
                lbConsole.Items.Add($"Channel {channel + 1}: Measurement ended abruptly. {exception.Message}");
                chkLBDevices.Enabled = psMultiCommSimpleWinForms.ChannelStates.Count(c => c == CommManager.DeviceState.Idle) == psMultiCommSimpleWinForms.NConnectedChannels;
            }
        }

        /// <summary>
        /// Raised when the measurement is started
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="EventArgs"/> instance containing the event data.</param>
        private void psMultiCommSimpleWinForms_MeasurementStarted(object sender, int channel, Exception exception)
        {
            lbConsole.Items.Add($"Channel {channel + 1}: Cyclic voltammetry measurement started.");
        }

        /// <summary>
        /// Raised when a Simple Curve in the active SimpleMeasurement starts receiving data
        /// </summary>
        /// <param name="sender">The sender.</param>
        /// <param name="activeSimpleCurve">The active simple curve.</param>
        private void psMultiCommSimpleWinForms_SimpleCurveStartReceivingData(object sender, SimpleCurve activeSimpleCurve)
        {
            activeSimpleCurve.Title = $"{activeSimpleCurve.Channel}: " + activeSimpleCurve.Title;
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
            if (InvokeRequired) //Data is parsed asynchronously in the case this event was raised on a different thread it must be invoked back onto the UI thread
            {
                BeginInvoke(new EventHandler(activeSimpleCurve_CurveFinished), sender, e);
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
        private void psMultiCommSimpleWinForms_Disconnected(object sender, Exception exception, int channel, Device device)
        {
            if (exception != null)
            {
                lbConsole.Items.Add($"Channel {channel + 1}: {exception.Message}");
            }

            lbConsole.Items.Add($"Channel {channel + 1} disconnected.");
            btnConnect.Text = psMultiCommSimpleWinForms.Connected ? "Disconnect" : "Connect";
            btnConnect.Enabled = true;
            btnMeasure.Text = "Measure";
        }
    }
}
