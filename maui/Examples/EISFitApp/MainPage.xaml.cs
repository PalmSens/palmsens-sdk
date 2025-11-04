using PalmSens;
using PalmSens.Comm;
using PalmSens.Core.Simplified;
using PalmSens.Core.Simplified.Data;
using PalmSens.Fitting;
using PalmSens.Fitting.Models;
using PalmSens.Techniques;
using PalmSens.Techniques.Impedance;
using System.Collections.ObjectModel;
using PalmSens.Core.Simplified.MAUI;
using Device = PalmSens.Devices.Device;

namespace PalmSensEISFIt
{
    public partial class MainPage : ContentPage
    {
        public IPlatformInvoker PlatformInvoker { get; }
        private IReadOnlyList<Device> _availableDevices;
        private Device _selectedDevice;
        private readonly PSCommSimple _psCommSimple;

        public MainPage(
            PSCommSimpleMaui psCommSimple,
            IPlatformInvoker platformInvoker)
        {
            PlatformInvoker = platformInvoker;
            InitializeComponent();
            BindingContext = this;

            psCommSimple.Initialize();  // This needs to be called after the main page has been initialized
            this._psCommSimple = psCommSimple;

            InitPlot();

            _psCommSimple.StateChanged += OnStateChanged;
            _psCommSimple.ReceiveStatus += OnReceiveStatus;
            _psCommSimple.MeasurementStarted += OnMeasurementStarted;
            _psCommSimple.MeasurementEnded += OnMeasurementEnded;
            _psCommSimple.SimpleCurveStartReceivingData += OnSimpleCurveStartReceivingData;
            _psCommSimple.Disconnected += OnDisconnected;
        }

        private SimpleCurve[] _fitResultCurves = null;

        private FitProgress _fitProgress = null;

        private FitAlgorithm _fitAlgorithm = null;

        private FitOptionsCircuit _fitOptions = null;

        private CircuitModel _circuitModel = null;

        private SimpleMeasurement _activeMeasurement = null;

        public ObservableCollection<string> Log
        {
            get { return _log; }
            set { _log = value; }
        }

        private ObservableCollection<string> _log = [];

        public ObservableCollection<string> Results
        {
            get { return _results; }
            set { _results = value; }
        }

        private ObservableCollection<string> _results = [];

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
        private Method InitMethod()
        {
            Method method = new ImpedimetricMethod
            {
                EquilibrationTime = 0f,
                Potential = 0f,
                Eac = 0.01f,
                ScanType = enumScanType.Fixed,
                FreqType = enumFrequencyType.Scan,
                MaxFrequency = 200000,
                MinFrequency = 100,
                nFrequencies = 50,
            };

            method.Ranging.StartCurrentRange = new CurrentRange(CurrentRanges.cr10mA);
            method.Ranging.MinimumCurrentRange = new CurrentRange(CurrentRanges.cr1uA);
            method.Ranging.MaximumCurrentRange = new CurrentRange(CurrentRanges.cr10mA);

            return method;
        }

        private void InitPlot()
        {
            plotView1.CorePlot.ClearAll();
            plotView1.CorePlot.XAxisLabel = "Log Frequency (Hz)";
            plotView1.CorePlot.XAxisType = SDKPlot.AxisType.Logarithmic;
            plotView1.CorePlot.YAxisLabel = "Log Z (Ω)";
            plotView1.CorePlot.YAxisType = SDKPlot.AxisType.Logarithmic;
            plotView1.CorePlot.YAxisSecondaryLabel = "-Phase (°)";
            plotView1.CorePlot.YAxisSecondaryType = SDKPlot.AxisType.Linear;
            plotView1.CorePlot.AddData("", new double[0], new double[0]);
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

            MeasureBtn.IsEnabled = _psCommSimple.Connected;
            ConnectBtn.Text = _psCommSimple.Connected ? "Disconnect" : "Connect";
            Log.Add(_psCommSimple.Connected ? $"Connected to {_psCommSimple.ConnectedDevice}" : "Nothing is connected");
        }

        private async void MeasureClicked(object? sender, EventArgs e)
        {
            Method method = InitMethod();

            switch (_psCommSimple.DeviceState)
            {
                case PalmSens.Comm.CommManager.DeviceState.Idle:
                    plotView1.CorePlot.ClearAll();

                    Log.Add($"Starting measurement...");
                    try
                    {
                        _activeMeasurement = await _psCommSimple.StartMeasurement(method);
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

        private void StartFitClicked(object? sender, EventArgs e)
        {
            FitEquivalentCircuit();
        }

        private void CancelFitlClicked(object? sender, EventArgs e)
        {
            if (_fitProgress != null) _fitProgress.Cancel();
        }

        private void FitEquivalentCircuit()
        {
            _circuitModel = BuildEquivalentCircuitModel();
            _fitOptions = InitFitOptions(_circuitModel);
            _fitAlgorithm = FitAlgorithm.FromAlgorithm(_fitOptions);
            _fitProgress = new FitProgress();
            _fitProgress.ProgressChanged += OnProgressChanged;
            _fitAlgorithm.ApplyFitCircuit(_fitProgress);
        }

        private FitOptionsCircuit InitFitOptions(CircuitModel circuitModel)
        {
            FitOptionsCircuit fitOptions = new FitOptionsCircuit
            {
                Model = circuitModel,
                RawData = _activeMeasurement.Measurement.EISdata[0],
                SelectedAlgorithm = Algorithm.LevenbergMarquardt,
                MaxIterations = 100,
                MinimumDeltaErrorTerm = 1e-9,
                EnableMinimunDeltaErrorTerm = true,
                MinimumDeltaParameters = 1e-12,
                EnableMinimunDeltaParameters = true,
                Lambda = 1e-2,
                LambdaFactor = 10,

            };

            return fitOptions;
        }

        private CircuitModel BuildEquivalentCircuitModel()
        {
            CircuitModel circuitModel = new CircuitModel();
            circuitModel.SetEISdata(_activeMeasurement.Measurement.EISdata[0]);
            circuitModel.SetCircuit("R(RC)");
            circuitModel.SetInitialParameters(
                new double[] {
                    100,
                    8000,
                    1e-8
                });

            return circuitModel;
        }

        private void SetFitResults(FitResult result)
        {
            Log.Add($"Rs = {result.FinalParameters[0]:E3} Ω (±{result.ParameterSDs[0]:E3} %)");
            Log.Add($"Rct = {result.FinalParameters[1]:E3} Ω (±{result.ParameterSDs[1]:E3} %)");
            Log.Add($"Cdl = {result.FinalParameters[2]:E3} F (±{result.ParameterSDs[2]:E3} %)");
            Log.Add($"Chi² = {result.ChiSq}");

            switch (result.ExitCode)
            {
                case ExitCodes.MinimumDeltaErrorTerm:
                    Log.Add("Reached min delta error sum squares");
                    break;
                case ExitCodes.MinimumDeltaParameters:
                    Log.Add("Reached min delta parameter step size");
                    break;
                case ExitCodes.MaxIterations:
                    Log.Add("Reached max iterations");
                    break;
                case ExitCodes.HessianNonPositive:
                    Log.Add("Error determing step for next iteration");
                    break;
            }

            if (_fitResultCurves != null)
                foreach (SimpleCurve sc in _fitResultCurves)
                    if (plotView1.CorePlot.ContainsSimpleCurve(sc))
                        plotView1.CorePlot.RemoveSimpleCurve(sc);

            _circuitModel.SetInitialParameters(result.FinalParameters);
            _fitResultCurves = new SimpleCurve[2];
            _fitResultCurves[0] = new SimpleCurve(_circuitModel.GetCurveZabsOverFrequency(false)[0], _activeMeasurement);
            _fitResultCurves[0].Title = "Z Abs Fit";
            _fitResultCurves[1] = new SimpleCurve(_circuitModel.GetCurvePhaseOverFrequency(false)[0], _activeMeasurement);
            _fitResultCurves[1].Title = "-Phase Fit";

            plotView1.CorePlot.AddSimpleCurve(_fitResultCurves[0], useSecondaryYAxis: false, update: false);
            plotView1.CorePlot.AddSimpleCurve(_fitResultCurves[1], useSecondaryYAxis: true, update: true);
        }

        private void OnProgressChanged(object sender, FitProgressUpdate e)
        {
            switch (e.Progress)
            {
                case EnumFitProgress.Started:
                    Log.Add("Started circuit fit.");
                    ProgressBarView.Progress = 0.0;
                    CancelFitBtn.IsEnabled = true;
                    break;
                case EnumFitProgress.FitIterated:
                    ProgressBarView.Progress = (e.NIterations / _fitOptions.MaxIterations);
                    break;
                case EnumFitProgress.Cancelled:
                case EnumFitProgress.Finished:
                    Log.Add("Circuit fit completed.");
                    SetFitResults(e.Result);
                    ProgressBarView.Progress = 1.0;
                    CancelFitBtn.IsEnabled = false;
                    _fitProgress.ProgressChanged -= OnProgressChanged;
                    _fitProgress = null;
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
            StartFitBtn.IsEnabled = false;
        }

        private void OnMeasurementEnded(object sender, Exception e)
        {
            Log.Add("Measurement ended");
            StartFitBtn.IsEnabled = _activeMeasurement.Measurement.EISdata.Count > 0 && _activeMeasurement.Measurement.EISdata[0].NPoints > 0;
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
            // `CorePlot.AddSimpleCurve()` subscribes to the `NewDataAdded` event and auto-updates the plot
            plotView1.CorePlot.AddSimpleCurve(activeSimpleCurve);

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

            for (int i = startIndex; i < startIndex + count; i++)
            {
                double xValue = activeSimpleCurve.XAxisValue(i);
                double yValue = activeSimpleCurve.YAxisValue(i);
            }

            PotentialValue.Text = $"{activeSimpleCurve.XAxisValue(startIndex + count - 1):F3}";
            CurrentValue.Text = $"{activeSimpleCurve.YAxisValue(startIndex + count - 1):F3}";
        }

        private void OnCurveFinished(object sender, EventArgs e)
        {
            SimpleCurve activeSimpleCurve = sender as SimpleCurve;

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
}
