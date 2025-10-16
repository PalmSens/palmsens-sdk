using OxyPlot;
using PalmSens;
using PalmSens.Core.Simplified.Data;
using PalmSens.Data;
using SDKPlot;
using System.Collections.ObjectModel;

#if WINDOWS
using PalmSens.Windows;
#endif

namespace DataProcessingExample
{
    public partial class MainPage : ContentPage
    {
        public MainPage()
        {
            InitializeComponent();
            BindingContext = this;
        }

        private List<SimpleMeasurement> _measurements = [];
        private SimpleMeasurement _activeMeasurement;
        private SimpleCurve _activeCurve;
        private SimpleCurve _baselineCurve;
        private PlotModel _plotmodel;

        public ObservableCollection<string> Log
        {
            get { return _log; }
            set { _log = value; }
        }

        private ObservableCollection<string> _log = [];

        private void LoadData(object? sender, EventArgs e)
        {
            LoadDataBtn.IsEnabled = false;
            Log.Add($"Loading example data...");

            SessionManager session = null;

            // TODO: Use Platform agnostic function
#if WINDOWS
            session = LoadSaveHelperFunctions.LoadSessionFile("Example.pssession");
#else
            session = [];
#endif

            foreach (Measurement measurement in session)
                _measurements.Add(new SimpleMeasurement(measurement));

            SimpleMeasurement dpvExample = _measurements.FirstOrDefault(meas => meas.Title == "DPV Example");
            _activeMeasurement = dpvExample;

            _activeCurve = dpvExample.SimpleCurveCollection[0];

            Log.Add($"Showing DPV example data...");

            plotView1.CorePlot.ClearAll();
            plotView1.CorePlot.AddSimpleCurve(_activeCurve);

            SmoothCurveBtn.IsEnabled = true;
        }

        private void SmoothCurve(object? sender, EventArgs e)
        {
            SmoothCurveBtn.IsEnabled = false;
            Log.Add($"Smoothing DPV curve...");

            SimpleCurve smoothedCurve = _activeCurve.Smooth(SmoothLevel.High);

            plotView1.CorePlot.AddSimpleCurve(smoothedCurve);

            FindBaselineBtn.IsEnabled = true;
        }

        private void FindBaseline(object? sender, EventArgs e)
        {
            FindBaselineBtn.IsEnabled = false;

            Log.Add($"Finding baseline for SWV curve...");

            SimpleMeasurement swvExample = _measurements.FirstOrDefault(meas => meas.Title == "SWV Example");
            _activeMeasurement = swvExample;

            _activeCurve = swvExample.SimpleCurveCollection[0];
            _baselineCurve = _activeCurve.MovingAverageBaseline();

            plotView1.CorePlot.ClearAll();
            plotView1.CorePlot.AddSimpleCurve(_activeCurve);
            plotView1.CorePlot.AddSimpleCurve(_baselineCurve);

            SubtractBaselineBtn.IsEnabled = true;
        }

        private void SubtractBaseline(object? sender, EventArgs e)
        {
            SubtractBaselineBtn.IsEnabled = false;
            Log.Add($"Subtracting baseline...");

            var correctedCurve = _activeCurve.Subtract(_baselineCurve);

            plotView1.CorePlot.AddSimpleCurve(correctedCurve);

            DetectPeaksBtn.IsEnabled = true;
        }

        private void DetectPeaks(object? sender, EventArgs e)
        {
            DetectPeaksBtn.IsEnabled = false;
            Log.Add($"Detecting peaks in baseline-corrected curve...");

            _activeCurve.DetectPeaks();

            Log.Add($"Found {_activeCurve.Peaks.nPeaks} peaks");

            plotView1.CorePlot.ClearAll();
            plotView1.CorePlot.AddSimpleCurve(_activeCurve);

            MakeCurveBtn.IsEnabled = true;
        }

        private void MakeCurve(object? sender, EventArgs e)
        {
            MakeCurveBtn.IsEnabled = false;
            Log.Add($"Making Charge over Time curve for each CV scan...");

            SimpleMeasurement cvExample = _measurements.FirstOrDefault(meas => meas.Title == "CV Example");
            _activeMeasurement = cvExample;

            List<SimpleCurve> chargeCurves = cvExample.NewSimpleCurve(PalmSens.Data.DataArrayType.Time, PalmSens.Data.DataArrayType.Charge, "Charge/Potential");

            _activeCurve = chargeCurves[0];

            plotView1.CorePlot.ClearAll();
            plotView1.CorePlot.AddSimpleCurves(chargeCurves);

            DifferentiateCurveBtn.IsEnabled = true;
        }

        private void DifferentiateCurve(object? sender, EventArgs e)
        {
            DifferentiateCurveBtn.IsEnabled = false;
            Log.Add($"Differentiating Charge over Time curve...");

            SimpleCurve diffCharge = _activeCurve.Differentiate();

            plotView1.CorePlot.ClearAll();
            plotView1.CorePlot.AddSimpleCurve(diffCharge, useSecondaryYAxis: true);
            plotView1.CorePlot.YAxisSecondaryLabel = "dC(µC)/dt(s)";

            ShowBodePlotBtn.IsEnabled = true;
        }

        private void ShowBodePlot(object? sender, EventArgs e)
        {
            ShowBodePlotBtn.IsEnabled = false;
            Log.Add($"Generating Bode Plot for EIS measurement...");

            SimpleMeasurement eisExample = _measurements.FirstOrDefault(meas => meas.Title == "EIS Example");
            _activeMeasurement = eisExample;

            SimpleCurve impedance = (eisExample.NewSimpleCurve(PalmSens.Data.DataArrayType.Frequency, PalmSens.Data.DataArrayType.Z, "Impedance"))[0];
            SimpleCurve phase = (eisExample.NewSimpleCurve(PalmSens.Data.DataArrayType.Frequency, PalmSens.Data.DataArrayType.Phase, "-Phase"))[0];

            plotView1.CorePlot.ClearAll();
            plotView1.CorePlot.AddSimpleCurve(impedance);
            plotView1.CorePlot.AddSimpleCurve(phase, useSecondaryYAxis: true);
            plotView1.CorePlot.XAxisType = AxisType.Logarithmic;
            plotView1.CorePlot.YAxisType = AxisType.Logarithmic;

            Log.Add("Example finished!");
        }
    }
}
