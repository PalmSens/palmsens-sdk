using PalmSens;
using PalmSens.Comm;
using PalmSens.Core.Simplified;
using PalmSens.Core.Simplified.Data;
using PalmSens.Techniques;
using System.Collections.ObjectModel;
using PalmSens.Core.Simplified.MAUI;
using Device = PalmSens.Devices.Device;

namespace BiPotAuxApp
{
    public partial class MainPage : ContentPage
    {
        public IPlatformInvoker PlatformInvoker { get; }
        private IReadOnlyList<Device> _availableDevices;
        private Device _selectedDevice;
        private readonly PSCommSimple _psCommSimple;
        private bool _isBiPotSupported = false;

        public MainPage(
            PSCommSimpleMaui psCommSimple,
            IPlatformInvoker platformInvoker)
        {
            PlatformInvoker = platformInvoker;
            InitializeComponent();
            BindingContext = this;

            psCommSimple.Initialize(this);  // This needs to be called after the main page has been initialized
            this._psCommSimple = psCommSimple;

            _psCommSimple.StateChanged += OnStateChanged;
            _psCommSimple.ReceiveStatus += OnReceiveStatus;
            _psCommSimple.MeasurementStarted += OnMeasurementStarted;
            _psCommSimple.MeasurementEnded += OnMeasurementEnded;
            _psCommSimple.SimpleCurveStartReceivingData += OnSimpleCurveStartReceivingData;
            _psCommSimple.Disconnected += OnDisconnected;
        }

        private SimpleCurve _extraValueCurve;

        public string SelectedBiPotMode { get; set; }

        public string SelectedMeasurement { get; set; }

        private SimpleMeasurement _activeMeasurement;

        public ObservableCollection<DataPoint> DataPoints
        {
            get { return _dataPoints; }
            set { _dataPoints = value; }
        }

        private ObservableCollection<DataPoint> _dataPoints = [];

        public ObservableCollection<string> Log
        {
            get { return _log; }
            set { _log = value; }
        }

        private ObservableCollection<string> _log = [];

        public bool IsBiPotSupported
        {
            get => _isBiPotSupported;
            set
            {
                _isBiPotSupported = value;
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

        private Method InitMethodAux()
        {
            Method method = new AmperometricDetection
            {
                Potential = 1f,
                IntervalTime = 0.1f,
                RunTime = 3f
            };

            method.EquilibrationTime = 1f;
            method.Ranging.StartCurrentRange = new CurrentRange(CurrentRanges.cr1uA);
            method.Ranging.MinimumCurrentRange = new CurrentRange(CurrentRanges.cr10nA);
            method.Ranging.MaximumCurrentRange = new CurrentRange(CurrentRanges.cr1mA);

            method.ExtraValueMsk = ExtraValueMask.AuxInput;

            return method;
        }

        private Method InitMethodBiPot()
        {
            Method method = new AmperometricDetection
            {
                Potential = 1f,
                IntervalTime = 0.1f,
                RunTime = 3f
            };

            method.EquilibrationTime = 1f;
            method.Ranging.StartCurrentRange = new CurrentRange(CurrentRanges.cr1uA);
            method.Ranging.MinimumCurrentRange = new CurrentRange(CurrentRanges.cr10nA);
            method.Ranging.MaximumCurrentRange = new CurrentRange(CurrentRanges.cr1mA);

            method.ExtraValueMsk = ExtraValueMask.BipotWE;

            method.BipotModePS = (SelectedBiPotMode == "Constant") ? Method.EnumPalmSensBipotMode.constant : Method.EnumPalmSensBipotMode.offset;

            method.BiPotPotential = 0;
            method.BiPotCR = new CurrentRange(CurrentRanges.cr1uA);

            method.PGStatMode = MethodScript.PGStatModes.LowSpeed;
            method.SelectedPotentiostatChannel = PotentionstatChannels.Ch0;

            float potentialBiPot;
            if (!float.TryParse(BiPotEntry.Text, out potentialBiPot))
            {
                string msg = $"Could not parse BiPot potential {BiPotEntry.Text}.";
                Log.Add(msg);
                throw new Exception(msg);
            }

            return method;
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

                if (!(IsBiPotSupported = _psCommSimple.Capabilities.BiPotPresent))
                {
                    Log.Add($"Device {_psCommSimple.ConnectedDevice} does not support BiPot");
                }
            }

            MeasureBtn.IsEnabled = _psCommSimple.Connected;
            ConnectBtn.Text = _psCommSimple.Connected ? "Disconnect" : "Connect";
            Log.Add(_psCommSimple.Connected ? $"Connected to {_psCommSimple.ConnectedDevice}" : "Nothing is connected");
        }

        private void MeasureClicked(object? sender, EventArgs e)
        {

            if (SelectedMeasurement == "Aux")
            {
                MeasureAux();
            }
            else
            {
                MeasureBiPot();
            }
        }

        private async void MeasureAux()
        {
            Method method = InitMethodAux();

            switch (_psCommSimple.DeviceState)
            {
                case PalmSens.Comm.CommManager.DeviceState.Idle:
                    _dataPoints.Clear();
                    Log.Add($"Starting Aux measurement...");
                    try
                    {
                        _activeMeasurement = await _psCommSimple.StartMeasurement(method);
                        _extraValueCurve = (_activeMeasurement.NewSimpleCurve(
                            PalmSens.Data.DataArrayType.Time,
                            PalmSens.Data.DataArrayType.AuxInput,
                            "",
                            true))[0];
                    }
                    catch (Exception ex)
                    {
                        Log.Add(ex.Message);
                    }
                    break;

                case PalmSens.Comm.CommManager.DeviceState.Pretreatment:
                case PalmSens.Comm.CommManager.DeviceState.Measurement:
                    Log.Add($"Aborting measurement...");
                    try
                    {
                        await _psCommSimple.AbortMeasurement();
                    }
                    catch (Exception ex)
                    {
                        Log.Add(ex.Message);
                    }
                    break;

                default:
                    Log.Add($"Unknown state : {_psCommSimple.DeviceState}.");
                    break;
            }
        }

        private async void MeasureBiPot()
        {
            Method method = InitMethodBiPot();

            switch (_psCommSimple.DeviceState)
            {
                case PalmSens.Comm.CommManager.DeviceState.Idle:
                    _dataPoints.Clear();
                    Log.Add($"Starting BiPot measurement...");
                    try
                    {
                        _activeMeasurement = await _psCommSimple.StartMeasurement(method);
                        _extraValueCurve = (_activeMeasurement.NewSimpleCurve(
                            PalmSens.Data.DataArrayType.Time,
                            PalmSens.Data.DataArrayType.Current, // BipotCurrent ?
                            "",
                            true))[0];
                    }
                    catch (Exception ex)
                    {
                        Log.Add(ex.Message);
                    }
                    break;

            case PalmSens.Comm.CommManager.DeviceState.Pretreatment:
            case PalmSens.Comm.CommManager.DeviceState.Measurement:
                Log.Add($"Aborting measurement...");
                try
                {
                    await _psCommSimple.AbortMeasurement();
                }
                catch (Exception ex)
                {
                    Log.Add(ex.Message);
                }
                break;

            default:
                    Log.Add($"Unknown state : {_psCommSimple.DeviceState}.");
                break;
            }
        }

        private void OnReceiveStatus(object sender, PalmSens.Comm.StatusEventArgs e)
        {
            Status status = e.GetStatus();

            double potential = status.PotentialReading.Value;
            double currentInRange = status.CurrentReading.ValueInRange;

            PalmSens.Comm.ReadingStatus currentStatus = status.CurrentReading.ReadingStatus;
            CurrentRange cr = status.CurrentReading.CurrentRange;

            PotentialValue.Text = $"{potential:F3} V";
            CurrentValue.Text = $"{currentInRange:F3} * {cr}";

            if (IsBiPotSupported)
            {
                double bipot = status.GetCorrectedBiPotCurrent();
                ExtraValueBiPot.Text = $"{bipot} * {cr}";
            }

            double aux = status.GetAuxInputAsVoltage();
            ExtraValueAux.Text = $"{aux:F3} V";
        }

        private void OnStateChanged(object sender, PalmSens.Comm.CommManager.DeviceState CurrentState)
        {
            StatusValue.Text = $"{CurrentState}";

            var isIdle = CurrentState == PalmSens.Comm.CommManager.DeviceState.Idle;
            var isEnabled = isIdle;

            ConnectBtn.IsEnabled = isEnabled;
            DiscoverBtn.IsEnabled = isEnabled;

            MeasureBtn.Text = isIdle ? "Measure" : "Abort";
        }

        private void OnMeasurementStarted(object sender, EventArgs e)
        {
            Log.Add("Measurement started");
        }

        private void OnMeasurementEnded(object sender, Exception e)
        {
            Log.Add("Measurement ended");
        }

        private void OnDisconnected(object sender, Exception exception)
        {
            if (exception != null)
            {
                Log.Add(exception.Message);
            }
            else
            {
                Log.Add("Disconnected");
            }

            ConnectBtn.Text = "Connect";
            ConnectBtn.IsEnabled = true;
            MeasureBtn.Text = "Measure";
        }

        private void OnSimpleCurveStartReceivingData(object sender, SimpleCurve activeSimpleCurve)
        {
            if (activeSimpleCurve.YAxisDataType != PalmSens.Data.DataArrayType.Current)
                return;

            activeSimpleCurve.NewDataAdded += OnNewDataAdded;
            activeSimpleCurve.CurveFinished += OnCurveFinished;

            Log.Add("Curve is receiving new data...");
        }

        private void OnNewDataAdded(object sender, PalmSens.Data.ArrayDataAddedEventArgs e)
        {
            if (PlatformInvoker.InvokeIfRequired(() => OnNewDataAdded(sender, e)))
            {
                return;
            }

            SimpleCurve activeSimpleCurve = sender as SimpleCurve;
            int startIndex = e.StartIndex;
            int count = e.Count;

            string extraValueUnit = _activeMeasurement.Measurement.Method.ExtraValueMsk == ExtraValueMask.BipotWE ? "µA" : "V";

            for (int i = startIndex; i < startIndex + count; i++)
            {
                double xValue = activeSimpleCurve.XAxisValue(i);
                double yValue = activeSimpleCurve.YAxisValue(i);

                double extraValue = _extraValueCurve.YAxisValue(i);

                _dataPoints.Add(new DataPoint(i + 1, xValue, yValue, $"{extraValue:E3} {extraValueUnit}"));
            }
        }

        private void OnCurveFinished(object sender, EventArgs e)
        {
            SimpleCurve activeSimpleCurve = sender as SimpleCurve;

            activeSimpleCurve.NewDataAdded -= OnNewDataAdded;
            activeSimpleCurve.CurveFinished -= OnCurveFinished;

            CurveFinished(activeSimpleCurve);
        }

        private void CurveFinished(SimpleCurve activeSimpleCurve)
        {
            if (PlatformInvoker.InvokeIfRequired(() => CurveFinished(activeSimpleCurve)))
            {
                return;
            }

            int nDataPointsReceived = activeSimpleCurve.NDataPoints;
            Log.Add($"{nDataPointsReceived} data point(s) received");
        }
    }

    public class DataPoint
    {
        public int ID { get; }
        public double Time { get; }
        public double Current { get; }
        public string Extra { get; }
        public DataPoint(int id, double time, double current, string extra)
        {
            ID = id;
            Time = time;
            Current = current;
            Extra = extra;
        }
    }
}
