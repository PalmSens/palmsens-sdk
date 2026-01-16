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

namespace BasicExample
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        public MainWindow()
        {
            InitializeComponent();
            DataContext = this; //Set the DataContext, needed to bind the measured data to the DataGrid control
            InitLSVMethod(); //Create the linear sweep voltammetry method that defines the measurement parameters
            _ = DiscoverConnectedDevicesAsync(); //Populate the connected device combobox control
        }

        /// <summary>
        /// The instance of method class containing the Linear Sweep Voltammetry parameters
        /// </summary>
        private LinearSweep _methodLSV;

        /// <summary>
        /// The connected PalmSens & EmStat devices
        /// </summary>
        private Device[] _connectedDevices = new Device[0];

        /// <summary>
        /// The active SimpleMeasurement
        /// </summary>
        private SimpleMeasurement _activeMeasurement = null;

        /// <summary>
        /// The collection of measured data points that is binded to the datagrid.
        /// </summary>
        public ObservableCollection<DataPoint> DataPoints
        {
            get { return _dataPoints; }
            set { _dataPoints = value; }
        }

        /// <summary>
        /// The measured data points
        /// </summary>
        private ObservableCollection<DataPoint> _dataPoints = new ObservableCollection<DataPoint>();

        /// <summary>
        /// Initializes the LSV method.
        /// </summary>
        private void InitLSVMethod()
        {
            _methodLSV = new LinearSweep(); //Create a new linear sweep method with the default settings
            _methodLSV.BeginPotential = -0.5f; //Sets the potential to start the sweep from
            _methodLSV.EndPotential = 0.5f; //Sets the potential for the sweep to stop at
            _methodLSV.StepPotential = 0.05f; //Sets the step size
            _methodLSV.Scanrate = 0.1f; //Sets the scan rate to 0.1 V/s

            _methodLSV.EquilibrationTime = 1f; //Equilabrates the cell at the defined potential for 1 second before starting the measurement
            _methodLSV.Ranging.StartCurrentRange = new CurrentRange(CurrentRanges.cr1uA); //Starts equilabration in the 1µA current range
            _methodLSV.Ranging.MinimumCurrentRange = new CurrentRange(CurrentRanges.cr10nA); //Min current range 10nA
            _methodLSV.Ranging.MaximumCurrentRange = new CurrentRange(CurrentRanges.cr1mA); //Max current range 1mA
        }

        /// <summary>
        /// Discovers the connected PalmSens & EmStat devices and adds them to the combobox control.
        /// </summary>
        private async Task DiscoverConnectedDevicesAsync()
        {
            cmbDevices.Items.Clear();
            _connectedDevices = await psCommSimpleWPF.GetConnectedDevicesAsync(); //Discover connected devices

            foreach (Device d in _connectedDevices)
                cmbDevices.Items.Add(d.ToString()); //Add connected devices to control

            int nDevices = cmbDevices.Items.Count;
            cmbDevices.SelectedIndex = nDevices > 0 ? 0 : -1;
            lbConsole.Items.Add($"Found {nDevices} device(s).");

            btnConnect.IsEnabled = nDevices > 0;
        }

        /// <summary>
        /// Handles the Click event of the btnRefresh control.
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="RoutedEventArgs"/> instance containing the event data.</param>
        private async void btnRefresh_Click(object sender, RoutedEventArgs e)
        {
            btnRefresh.IsEnabled = false;
            await DiscoverConnectedDevicesAsync(); //Add connected devices to the devices combobox control
            btnRefresh.IsEnabled = true;
        }

        /// <summary>
        /// Handles the Click event of the btnConnect control.
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="RoutedEventArgs"/> instance containing the event data.</param>
        private async void btnConnect_Click(object sender, RoutedEventArgs e)
        {
            btnConnect.IsEnabled = false;
            if (!psCommSimpleWPF.Connected) //Determine whether a device is currently connected
            {
                if (cmbDevices.SelectedIndex == -1)
                    return;

                try
                {
                    //Connect to the device selected in the devices combobox control
                    await psCommSimpleWPF.ConnectAsync(_connectedDevices[cmbDevices.SelectedIndex]);
                    lbConsole.Items.Add($"Connected to {psCommSimpleWPF.ConnectedDevice.ToString()}");
                }
                catch (Exception ex)
                {
                    lbConsole.Items.Add(ex.Message);
                }
            }
            else
            {
                await psCommSimpleWPF.DisconnectAsync(); //Disconnect from the connected device
            }

            //Update UI based on connection status
            cmbDevices.IsEnabled = !psCommSimpleWPF.Connected;
            btnRefresh.IsEnabled = !psCommSimpleWPF.Connected;
            btnConnect.Content = psCommSimpleWPF.Connected ? "Disconnect" : "Connect";
            btnMeasure.IsEnabled = psCommSimpleWPF.Connected;
            btnConnect.IsEnabled = true;
        }

        /// <summary>
        /// Handles the Click event of the btnMeasure control.
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="RoutedEventArgs"/> instance containing the event data.</param>
        private async void btnMeasure_Click(object sender, RoutedEventArgs e)
        {
            btnMeasure.IsEnabled = false;
            if (psCommSimpleWPF.DeviceState == PalmSens.Comm.CommManager.DeviceState.Idle) //Determine whether the device is currently idle or measuring
            {
                try
                {
                    _dataPoints.Clear(); //Reset the content of the data grid control
                    _activeMeasurement = await psCommSimpleWPF.MeasureAsync(_methodLSV); //Start measurement defined in the method
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
                    await psCommSimpleWPF.AbortMeasurementAsync(); //Abort the active measurement
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
        private void psCommSimpleWPF_ReceiveStatus(object sender, PalmSens.Comm.StatusEventArgs e)
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

        /// <summary>
        /// Raised when the connected device's status changes
        /// </summary>
        /// <param name="sender">The sender.</param>
        /// <param name="CurrentState">State of the current.</param>
        private void psCommSimpleWPF_StateChanged(object sender, PalmSens.Comm.CommManager.DeviceState CurrentState)
        {
            tbStatus.Text = CurrentState.ToString(); //Updates the device state indicator textbox
            btnConnect.IsEnabled = CurrentState == PalmSens.Comm.CommManager.DeviceState.Idle;
            btnMeasure.Content = CurrentState == PalmSens.Comm.CommManager.DeviceState.Idle ? "Measure" : "Abort";
        }

        /// <summary>
        /// Raised when the measurement is ended
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="EventArgs"/> instance containing the event data.</param>
        private void psCommSimpleWPF_MeasurementEnded(object sender, Exception e)
        {
            lbConsole.Items.Add("Measurement ended.");
        }

        /// <summary>
        /// Raised when the measurement is started
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="EventArgs"/> instance containing the event data.</param>
        private void psCommSimpleWPF_MeasurementStarted(object sender, EventArgs e)
        {
            lbConsole.Items.Add("Linear sweep voltammetry measurement started.");
        }

        /// <summary>
        /// Raised when a Simple Curve in the active SimpleMeasurement starts receiving data
        /// </summary>
        /// <param name="sender">The sender.</param>
        /// <param name="activeSimpleCurve">The active simple curve.</param>
        private void psCommSimpleWPF_SimpleCurveStartReceivingData(object sender, SimpleCurve activeSimpleCurve)
        {
            //Subscribe to the curve's events to receive updates when new data is available and when it iss finished receiving data
            activeSimpleCurve.NewDataAdded += activeSimpleCurve_NewDataAdded;
            activeSimpleCurve.CurveFinished += activeSimpleCurve_CurveFinished;

            lbConsole.Items.Add("Curve is receiving new data...");
        }

        /// <summary>
        /// Raised when new data points are added to the active SimpleCurve
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="PalmSens.Data.ArrayDataAddedEventArgs"/> instance containing the event data.</param>
        private void activeSimpleCurve_NewDataAdded(object sender, PalmSens.Data.ArrayDataAddedEventArgs e)
        {
            if (!Dispatcher.CheckAccess()) //Data is parsed asynchronously in the case this event was raised on a different thread it must be invoked back onto the UI thread
            {
                Dispatcher.BeginInvoke(new PalmSens.Plottables.Curve.NewDataAddedEventHandler(activeSimpleCurve_NewDataAdded), sender, e);
                return;
            }
            SimpleCurve activeSimpleCurve = sender as SimpleCurve;
            int startIndex = e.StartIndex; //The index of the first new data point added to the curve
            int count = e.Count; //The number of new data points added to the curve

            for (int i = startIndex; i < startIndex + count; i++)
            {
                double xValue = activeSimpleCurve.XAxisValue(i); //Get the value on Curve's X-Axis (potential) at the specified index
                double yValue = activeSimpleCurve.YAxisValue(i); //Get the value on Curve's Y-Axis (current) at the specified index
                _dataPoints.Add(new DataPoint(i + 1, xValue, yValue));
            }

            tbPotential.Text = activeSimpleCurve.XAxisValue(startIndex + count - 1).ToString("F3");
            tbCurrent.Text = activeSimpleCurve.YAxisValue(startIndex + count - 1).ToString("F3");
        }

        /// <summary>
        /// Raised when a SimpleCurve stops receiving new data points
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="EventArgs"/> instance containing the event data.</param>
        private void activeSimpleCurve_CurveFinished(object sender, EventArgs e)
        {
            if (!Dispatcher.CheckAccess()) //Data is parsed asynchronously in the case this event was raised on a different thread it must be invoked back onto the UI thread
            {
                Dispatcher.BeginInvoke(new EventHandler(activeSimpleCurve_CurveFinished), sender, e);
                return;
            }
            SimpleCurve activeSimpleCurve = sender as SimpleCurve;

            //Unsubscribe from the curves events to avoid memory leaks
            activeSimpleCurve.NewDataAdded -= activeSimpleCurve_NewDataAdded;
            activeSimpleCurve.CurveFinished -= activeSimpleCurve_CurveFinished;

            int nDataPointsReceived = activeSimpleCurve.NDataPoints;
            lbConsole.Items.Add($"{nDataPointsReceived} data point(s) received.");

            lbConsole.Items.Add("Curve Finished");
        }

        /// <summary>
        /// Raised when the instrument has been disconnected.
        /// If the instrument was disconnected due to a communication the exception is provided.
        /// In the case of a regular disconnect the exception will be set to null.
        /// </summary>
        /// <param name="sender">The sender.</param>
        /// <param name="exception">The exception.</param>
        private void psCommSimpleWPF_Disconnected(object sender, Exception exception)
        {
            if (exception != null)
            {
                lbConsole.Items.Add(exception.Message);
            }

            lbConsole.Items.Add("Disconnected.");
            btnConnect.Content = "Connect";
            btnConnect.IsEnabled = true;
            btnMeasure.Content = "Measure";
        }
    }

    /// <summary>
    /// Defines the row structure for the DataGrid items
    /// </summary>
    public class DataPoint
    {
        public int ID { get; }
        public double Potential { get; }
        public double Current { get; }

        public DataPoint(int id, double potential, double current)
        {
            ID = id;
            Potential = potential;
            Current = current;
        }
    }
}
