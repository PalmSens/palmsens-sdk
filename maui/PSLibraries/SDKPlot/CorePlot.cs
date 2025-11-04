using OxyPlot;
using OxyPlot.Annotations;
using OxyPlot.Axes;
using OxyPlot.Series;
using PalmSens.Analysis;
using PalmSens.Core.Simplified;
using PalmSens.Core.Simplified.Data;
using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using PalmSens;
using PalmSens.Core.Simplified.InternalStorage;
using PalmSens.Data;
using PalmSens.Techniques;
using OxyPlot.Legends;

namespace SDKPlot
{
    public class CorePlot: IDisposable
    {
        public CorePlot(IPlotInvoker plotInvoker)
        {
            _plotInvoker = plotInvoker;
            PlotModel = new PlotModel();
            PlotModel.Legends.Add(new Legend() { });

            _cts = new CancellationTokenSource();
            _ = Task.Run(() => ConsumeLiveDataQueue(_cts.Token));
            _signal = new AsyncAutoResetEvent();
        }

        #region Plot Properties
        private readonly IPlotInvoker _plotInvoker;
        private readonly CancellationTokenSource _cts;
        private readonly AsyncAutoResetEvent _signal;

        /// <summary>
        /// The plot model that contains the information for the PlotView
        /// </summary>
        public PlotModel PlotModel { get; }

        /// <summary>
        /// Gets or sets the title.
        /// </summary>
        /// <value>
        /// The title.
        /// </value>
        public string Title
        {
            get { return PlotModel.Title; }
            set { PlotModel.Title = value; }
        }

        #region Axes
        /// <summary>
        /// The x axis
        /// </summary>
        protected Axis _xAxis = new LinearAxis() { Position = AxisPosition.Bottom };

        /// <summary>
        /// The bottom X Axis
        /// </summary>
        public Axis XAxis
        {
            get => _xAxis;
        }

        /// <summary>
        /// Gets or sets the x axis label.
        /// </summary>
        /// <value>
        /// The x axis label.
        /// </value>
        public string XAxisLabel
        {
            get { return _xAxis.Title; }
            set
            {
                _xAxis.Title = value;
                UpdatePlot();
            }
        }

        /// <summary>
        /// The x axis type
        /// </summary>
        private AxisType _xAxisType = AxisType.Linear;

        /// <summary>
        /// Gets or sets the type of the x axis.
        /// </summary>
        /// <value>
        /// The type of the x axis.
        /// </value>
        public AxisType XAxisType
        {
            get { return _xAxisType; }
            set
            {
                if (_xAxisType == value)
                    return;
                _xAxisType = value;
                UpdatePlot();
            }
        }

        /// <summary>
        /// The y axis
        /// </summary>
        protected Axis _yAxis = new LinearAxis() { Position = AxisPosition.Left };

        /// <summary>
        /// The bottom X Axis
        /// </summary>
        public Axis YAxis
        {
            get => _yAxis;
        }

        /// <summary>
        /// Gets or sets the y axis label.
        /// </summary>
        /// <value>
        /// The y axis label.
        /// </value>
        public string YAxisLabel
        {
            get { return _yAxis.Title; }
            set
            {
                _yAxis.Title = value;
                UpdatePlot();
            }
        }

        /// <summary>
        /// The y axis type
        /// </summary>
        private AxisType _yAxisType = AxisType.Linear;

        /// <summary>
        /// Gets or sets the type of the y axis.
        /// </summary>
        /// <value>
        /// The type of the y axis.
        /// </value>
        public AxisType YAxisType
        {
            get { return _yAxisType; }
            set
            {
                _yAxisType = value;
                UpdatePlot();
            }
        }

        /// <summary>
        /// The secondary y axis
        /// </summary>
        protected Axis _yAxisSecondary = new LinearAxis() { Position = AxisPosition.Right, Key = "YSecondary" };

        /// <summary>
        /// Gets or sets the secondary y axis label.
        /// </summary>
        /// <value>
        /// The secondary y axis label.
        /// </value>
        public string YAxisSecondaryLabel
        {
            get { return _yAxisSecondary.Title; }
            set
            {
                _yAxisSecondary.Title = value;
                UpdatePlot();
            }
        }

        /// <summary>
        /// The secondary y axis type
        /// </summary>
        private AxisType _yAxisSecondaryType = AxisType.Linear;

        /// <summary>
        /// Gets or sets the type of the secondary y axis.
        /// </summary>
        /// <value>
        /// The type of the y axis.
        /// </value>
        public AxisType YAxisSecondaryType
        {
            get { return _yAxisSecondaryType; }
            set
            {
                _yAxisSecondaryType = value;
                UpdatePlot();
            }
        }

        /// <summary>
        /// The legend text color
        /// </summary>
        private OxyColor _legendTextColor = OxyColors.Black;

        /// <summary>
        /// Gets or sets the color of the legend text.
        /// </summary>
        /// <value>
        /// The color of the legend text.
        /// </value>
        public OxyColor LegendTextColor
        {
            get { return _legendTextColor; }
            set { _legendTextColor = value; }
        }

        /// <summary>
        /// The axis text color
        /// </summary>
        private OxyColor _axisTextColor = OxyColors.Black;

        /// <summary>
        /// Gets or sets the color of the axis text.
        /// </summary>
        /// <value>
        /// The color of the axis text.
        /// </value>
        public OxyColor AxisTextColor
        {
            get { return _axisTextColor; }
            set { _axisTextColor = value; }
        }

        /// <summary>
        /// The axes color
        /// </summary>
        private OxyColor _axesColor = OxyColors.Black;

        /// <summary>
        /// Gets or sets the color of the axes.
        /// </summary>
        /// <value>
        /// The color of the axis.
        /// </value>
        public OxyColor AxesColor
        {
            get { return _axesColor; }
            set { _axesColor = value; }
        }

        /// <summary>
        /// The datapoint MarkerType
        /// </summary>
        private MarkerType _markerType = MarkerType.Circle;

        /// <summary>
        /// Gets or sets the datapoint MarkerType.
        /// The default MarkerType is a circle.
        /// </summary>
        /// <value>
        /// The marker type.
        /// </value>
        public MarkerType MarkerType
        {
            get { return _markerType; }
            set { _markerType = value; UpdatePlot(); }
        }

        /// <summary>
        /// The marker size
        /// </summary>
        private int _markerSize = 5;

        /// <summary>
        /// The size of the markers indicating the datapoints in the plot.
        /// The default MarkerSize is 5.
        /// </summary>
        /// <value>
        /// The size of the marker used for datapoints.
        /// </value>
        /// <exception cref="System.Exception">Marker size must be a positive number</exception>
        public int MarkerSize
        {
            get { return _markerSize; }
            set
            {
                if (value < 1)
                    throw new Exception("Marker size must be a positive number");
                _markerSize = value;
                UpdatePlot();
            }
        }

        /// <summary>
        /// The show gridlines
        /// </summary>
        private bool _showGridlines = true;

        /// <summary>
        /// The grid line style
        /// </summary>
        private LineStyle _gridLineStyle = LineStyle.Solid;

        /// <summary>
        /// Gets or sets a value indicating whether to [show grid lines].
        /// </summary>
        /// <value>
        ///   <c>true</c> if [show grid lines]; otherwise, <c>false</c>.
        /// </value>
        public bool ShowGridLines
        {
            get { return _showGridlines; }
            set
            {
                _showGridlines = value;
                _gridLineStyle = (_showGridlines) ? LineStyle.Solid : LineStyle.None;
                UpdatePlot();
            }
        }

        /// <summary>
        /// The plot background color
        /// </summary>
        private OxyColor _plotBackgroundColor = OxyColors.White;

        /// <summary>
        /// Gets or sets the color of the plot background.
        /// </summary>
        /// <value>
        /// The color of the plot background.
        /// </value>
        public OxyColor PlotBackgroundColor
        {
            get { return _plotBackgroundColor; }
            set { _plotBackgroundColor = value; }
        }

        #endregion

        /// <summary>
        /// List of data series in the plot model
        /// </summary>
        protected List<Series> _dataSeries = new List<Series>();

        /// <summary>
        /// List of annotations in the plot model
        /// </summary>
        protected List<PointAnnotation> _annotations = new List<PointAnnotation>();

        /// <summary>
        /// The SimpleCurves in the plot with their respective lineseries
        /// </summary>
        protected Dictionary<SimpleCurve, LineSeries> _simpleCurvesInPlot = new Dictionary<SimpleCurve, LineSeries>();

        /// <summary>
        /// The peaks in plot with their respective SimpleCurves
        /// </summary>
        protected Dictionary<SimpleCurve, List<PlotPeak>> _peaksInPlot = new Dictionary<SimpleCurve, List<PlotPeak>>();

        /// <summary>
        /// Gets the amount of dataseries in the plot.
        /// </summary>
        /// <value>
        /// The n series.
        /// </value>
        public int NSeries { get { return _dataSeries.Count(); } }

        /// <summary>
        /// Gets the amount of SimpleCurves in the plot.
        /// </summary>
        /// <value>
        /// The n simple curves.
        /// </value>
        public int NSimpleCurves { get { return _simpleCurvesInPlot.Count; } }
        #endregion

        #region Data Arrays
        /// <summary>
        /// Adds data to the plot.
        /// </summary>
        /// <param name="label">The data label.</param>
        /// <param name="x">array containing the x values.</param>
        /// <param name="y">array containing the y values.</param>
        /// <param name="useSecondaryYAxis">if set to <c>true</c> [use secondary y axis].</param>
        /// <param name="update">if set to <c>true</c> [update] plot.</param>
        /// <returns>
        /// A reference to the lineseries of the data in the plot
        /// </returns>
        /// <exception cref="System.ArgumentException">The x and y data arrays must have equal lengths</exception>
        public LineSeries AddData(string label, double[] x, double[] y, bool useSecondaryYAxis = false, bool update = true)
        {
            if (x.Length != y.Length)
                throw new ArgumentException("The x and y data arrays must have equal lengths");

            int n = x.Length;

            //Create a new lineseries for the plot
            LineSeries data = new LineSeries()
            {
                Title = label,
                MarkerSize = _markerSize,
            };

            //Set lineseries Y-Axis to the secondary Y-Axis if specified
            if (useSecondaryYAxis)
                data.YAxisKey = _yAxisSecondary.Key;

            //Add the data to the lineseries
            for (int i = 0; i < n; i++)
                data.Points.Add(new DataPoint(x[i], y[i]));
            _dataSeries.Add(data); //Add the lineseries to the list of series in the plot

            if (update)
                UpdatePlot(); //Update the plot

            return data;
        }

        /// <summary>
        /// Adds data to the plot.
        /// </summary>
        /// <param name="label">The data label.</param>
        /// <param name="x">array containing the x values.</param>
        /// <param name="xLabel">The x axis label.</param>
        /// <param name="y">array containing the y values.</param>
        /// <param name="yLabel">The y axis label.</param>
        /// <param name="useSecondaryYAxis">if set to <c>true</c> [use secondary y axis].</param>
        /// <param name="update">if set to <c>true</c> [update] plot.</param>
        /// <returns>
        /// A reference to the lineseries of the data in the plot
        /// </returns>
        public LineSeries AddData(string label, double[] x, string xLabel, double[] y, string yLabel, bool useSecondaryYAxis = false, bool update = true)
        {
            XAxisLabel = xLabel;
            if (useSecondaryYAxis)
                YAxisSecondaryLabel = yLabel;
            else
                YAxisLabel = yLabel;
            return AddData(label, x, y, update);
        }

        /// <summary>
        /// Removes the specified data series from the plot.
        /// </summary>
        /// <param name="data">The data series.</param>
        /// <exception cref="System.ArgumentNullException">The specified data series cannot be null</exception>
        /// <exception cref="System.ArgumentException">The plot does not contain the specified data series</exception>
        public void RemoveData(Series data)
        {
            if (data == null)
                throw new ArgumentNullException("The specified data series cannot be null");
            if (!_dataSeries.Contains(data))
                throw new ArgumentException("The plot does not contain the specified data series");

            _dataSeries.Remove(data);
        }
        #endregion

        #region Simple Curves
        /// <summary>
        /// Determines whether the plot [contains] [the specified simple curve].
        /// </summary>
        /// <param name="simpleCurve">The simple curve.</param>
        /// <returns>
        ///   <c>true</c> if the plot [contains] [the specified simple curve]; otherwise, <c>false</c>.
        /// </returns>
        /// <exception cref="ArgumentNullException">The specified SimpleCurve cannot be null</exception>
        public bool ContainsSimpleCurve(SimpleCurve simpleCurve)
        {
            if(simpleCurve == null)
                throw new ArgumentNullException("The specified SimpleCurve cannot be null");
            return _simpleCurvesInPlot.ContainsKey(simpleCurve);
        }

        /// <summary>
        /// Adds the specified SimpleCurve to the plot.
        /// </summary>
        /// <param name="simpleCurve">The simple curve.</param>
        /// <param name="useSecondaryYAxis">if set to <c>true</c> [use secondary y axis].</param>
        /// <param name="update">if set to <c>true</c> the plot is [updated].</param>
        /// <exception cref="System.ArgumentNullException">The specified SimpleCurve cannot be null</exception>
        /// <exception cref="System.ArgumentException">Plot allready contains the specified SimpleCurve</exception>
        public virtual void AddSimpleCurve(SimpleCurve simpleCurve, Method method = null, bool useSecondaryYAxis = false, bool update = true)
        {
            if (simpleCurve == null)
                throw new ArgumentNullException("The specified SimpleCurve cannot be null");
            if (_simpleCurvesInPlot.ContainsKey(simpleCurve))
                throw new ArgumentException("Plot already contains the specified SimpleCurve");

            if (!simpleCurve.IsFinished && update) //Subscribe to the events that allow plot to update in realtime during a measurement
            {
                simpleCurve.NewDataAdded += SimpleCurve_NewDataAdded;
                simpleCurve.CurveFinished += SimpleCurve_CurveFinished;
            }
            simpleCurve.DetectedPeaks += SimpleCurve_DetectedPeaks; //Subscribe to event that updates the plot with detected peaks

            if (_dataSeries.Count == 0 && method != null)
            {
                if (method is CyclicVoltammetry cyclicVoltammetry)
                {
                    if (simpleCurve.XAxisDataType == DataArrayType.Potential)
                    {
                        XAxis.Maximum = Math.Max(cyclicVoltammetry.Vtx1Potential, cyclicVoltammetry.Vtx2Potential);
                        XAxis.Minimum = Math.Min(cyclicVoltammetry.Vtx1Potential, cyclicVoltammetry.Vtx2Potential);
                        if (simpleCurve.YAxisDataType == DataArrayType.Current)
                        {
                            YAxis.Maximum = cyclicVoltammetry.Ranging.MaximumCurrentRange.Factor * 10;
                            YAxis.Minimum = -YAxis.Maximum;
                        }
                    }
                }
                else if (method is PotentialMethod potentialMethod)
                {
                    if (simpleCurve.XAxisDataType == DataArrayType.Potential)
                    {
                        XAxis.Maximum = Math.Max(potentialMethod.BeginPotential, potentialMethod.EndPotential);
                        XAxis.Minimum = Math.Min(potentialMethod.BeginPotential, potentialMethod.EndPotential);
                        if (simpleCurve.YAxisDataType == DataArrayType.Current)
                        {
                            YAxis.Maximum = potentialMethod.Ranging.MaximumCurrentRange.Factor * 10;
                            YAxis.Minimum = -YAxis.Maximum;
                        }
                    }
                }
                else if (method is TimeMethod timeMethod)
                {
                    if (simpleCurve.XAxisDataType == DataArrayType.Time)
                    {
                        XAxis.Maximum = timeMethod.RunTime;
                        XAxis.Minimum = 0;
                    }
                }
            }

            //Set the SimpleCurve units on the axes
            XAxisLabel = $"{simpleCurve.XUnit} [{simpleCurve.Curve.XUnit.ToString()}]";
            if (useSecondaryYAxis)
                YAxisSecondaryLabel = $"{simpleCurve.YUnit} [{simpleCurve.Curve.YUnit.ToString()}]";
            else
                YAxisLabel = $"{simpleCurve.YUnit} [{simpleCurve.Curve.YUnit.ToString()}]";

            //Get the data from the SimpleCurve
            double[] x = simpleCurve.XAxisValues;
            double[] y = simpleCurve.YAxisValues;
            int n = (x.Length < y.Length) ? x.Length : y.Length;

            //Create a new lineseries for the plot
            LineSeries data = new LineSeries()
            {
                Title = simpleCurve.FullTitle.Trim(), //Trimming whitespaces is required for line to be rendered correctly in legend
                MarkerSize = _markerSize,
            };

            //Set lineseries Y-Axis to the secondary Y-Axis if specified
            if (useSecondaryYAxis)
                data.YAxisKey = _yAxisSecondary.Key;

            //Add the SimpleCurve to the dictionary of SimpleCurves in the plot
            _simpleCurvesInPlot.Add(simpleCurve, data);

            //Add the SimpleCurve data to the lineseries for the plot
            for (int i = 0; i < n; i++)
                data.Points.Add(new DataPoint(x[i], y[i]));
            _dataSeries.Add(data); //Add the lineseries to the list of series in the plot

            //Add the SimpleCurve's peaks to the plot
            UpdateSimpleCurvePeaks(simpleCurve, false);

            if (update)
                UpdatePlot(); //Update the plot
        }

        /// <summary>
        /// Adds a collection of SimpleCurves to the plot.
        /// </summary>
        /// <param name="simpleCurves">Array of SimpleCurves.</param>
        /// <param name="useSecondaryYAxis">if set to <c>true</c> [use secondary y axis].</param>
        /// <param name="update">if set to <c>true</c> the plot is [updated].</param>
        /// <exception cref="System.ArgumentNullException">The array of SimpleCurves cannot be null</exception>
        public void AddSimpleCurves(IEnumerable<SimpleCurve> simpleCurves, Method method = null, bool useSecondaryYAxis = false, bool update = true)
        {
            if (simpleCurves == null)
                throw new ArgumentNullException("The array of SimpleCurves cannot be null");
            foreach (SimpleCurve simpleCurve in simpleCurves)
                AddSimpleCurve(simpleCurve, method, useSecondaryYAxis, update);
        }

        /// <summary>
        /// Removes the specified SimpleCurve from the plot.
        /// </summary>
        /// <param name="simpleCurve">The SimpleCurve.</param>
        /// <param name="update">if set to <c>true</c> the plot is [updated].</param>
        /// <exception cref="System.ArgumentNullException">The specified SimpleCurve cannot be null</exception>
        /// <exception cref="System.ArgumentException">The plot does not contain the specified SimpleCurve</exception>
        /// <exception cref="System.Exception">Could not get lineseries associated with the SimpleCurve</exception>
        public virtual void RemoveSimpleCurve(SimpleCurve simpleCurve, bool update = true)
        {
            if (simpleCurve == null)
                throw new ArgumentNullException("The specified SimpleCurve cannot be null");
            if (!_simpleCurvesInPlot.ContainsKey(simpleCurve))
                throw new ArgumentException("The plot does not contain the specified SimpleCurve");

            if (!simpleCurve.IsFinished) //Unsubscribe from events used for realtime plotting
            {
                simpleCurve.NewDataAdded -= SimpleCurve_NewDataAdded;
                simpleCurve.CurveFinished -= SimpleCurve_CurveFinished;
            }
            simpleCurve.DetectedPeaks -= SimpleCurve_DetectedPeaks;

            //Removes the specified SimpleCurve's peaks from the plot
            RemoveSimpleCurvePeaks(simpleCurve, false);

            //Retrieve the SimpleCurve's respective lineseries from the dictionary of SimpleCurves in the plot
            LineSeries data;
            if (!_simpleCurvesInPlot.TryGetValue(simpleCurve, out data))
                throw new Exception("Could not get lineseries associated with the SimpleCurve");

            _dataSeries.Remove(data); //Remove the lineseries from the list of series in the plot
            _simpleCurvesInPlot.Remove(simpleCurve); //Remove the SimpleCurve from the dictionary of SimplCurves in the plot

            if (update)
                UpdatePlot(); //Update the plot
        }

        /// <summary>
        /// Removes a collection of SimpleCurves from the plot.
        /// </summary>
        /// <param name="simpleCurves">List of SimpleCurves.</param>
        /// <param name="update">if set to <c>true</c> the plot is [updated].</param>
        /// <exception cref="System.ArgumentNullException">The list of SimpleCurves cannot be null</exception>
        public void RemoveSimpleCurves(List<SimpleCurve> simpleCurves, bool update = true)
        {
            if (simpleCurves == null)
                throw new ArgumentNullException("The list of SimpleCurves cannot be null");
            RemoveSimpleCurves(simpleCurves.ToArray(), update);
        }

        /// <summary>
        /// Removes a collection of SimpleCurves from the plot.
        /// </summary>
        /// <param name="simpleCurves">Array of SimpleCurves.</param>
        /// <param name="update">if set to <c>true</c> the plot is [updated].</param>
        /// <exception cref="System.ArgumentNullException">The array of SimpleCurves cannot be null</exception>
        public void RemoveSimpleCurves(SimpleCurve[] simpleCurves, bool update = true)
        {
            if (simpleCurves == null)
                throw new ArgumentNullException("The array of SimpleCurves cannot be null");
            foreach (SimpleCurve simpleCurve in simpleCurves)
                RemoveSimpleCurve(simpleCurve, update);
        }

        /// <summary>
        /// Clears all SimpleCurves from the plot.
        /// </summary>
        public virtual void ClearSimpleCurves(bool update = true)
        {
            lock(PlotModel.SyncRoot)
            {
                RemoveSimpleCurves(_simpleCurvesInPlot.Keys.ToArray(), update);
            }
        }

        /// <summary>
        /// Removes the specified SimpleCurve's peaks from the plot.
        /// </summary>
        /// <param name="simpleCurve">The SimpleCurve.</param>
        /// <param name="update">if set to <c>true</c> the plot is [updated].</param>
        /// <exception cref="System.ArgumentNullException">The specified SimpleCurve cannot be null</exception>
        /// <exception cref="System.ArgumentException">The plot does not contain the specified SimpleCurve</exception>
        public void RemoveSimpleCurvePeaks(SimpleCurve simpleCurve, bool update = true)
        {
            if (simpleCurve == null)
                throw new ArgumentNullException("The specified SimpleCurve cannot be null");
            if (!_simpleCurvesInPlot.ContainsKey(simpleCurve))
                throw new ArgumentException("The plot does not contain the specified SimpleCurve");
            if (!_peaksInPlot.ContainsKey(simpleCurve))
                return;

            //Retrieve specified SimpleCurve's peak date in plot
            List<PlotPeak> peaks;
            if (!_peaksInPlot.TryGetValue(simpleCurve, out peaks))
                return;

            //Remove peak data from plot
            foreach (PlotPeak peak in peaks)
            {
                if (_dataSeries.Contains(peak.PeakLines))
                    _dataSeries.Remove(peak.PeakLines);
                if (_annotations.Contains(peak.Label))
                    _annotations.Remove(peak.Label);
            }
            _peaksInPlot.Remove(simpleCurve);

            if (update)
                UpdatePlot(); //Update the plot
        }

        /// <summary>
        /// Removes the specified collection of SimpleCurves' peaks from the plot.
        /// </summary>
        /// <param name="simpleCurve">Collection of SimpleCurves.</param>
        /// <param name="update">if set to <c>true</c> the plot is [updated].</param>
        /// <exception cref="System.ArgumentNullException">The specified SimpleCurve cannot be null</exception>
        /// <exception cref="System.ArgumentException">The plot does not contain the specified SimpleCurve</exception>
        public void RemoveSimpleCurvesPeaks(SimpleCurve[] simpleCurves, bool update = true)
        {
            if (simpleCurves == null)
                throw new ArgumentNullException("The specified collection of SimpleCurves cannot be null");

            foreach (SimpleCurve simpleCurve in simpleCurves)
                RemoveSimpleCurvePeaks(simpleCurve, false);

            if (update)
                UpdatePlot(); //Update the plot
        }

        /// <summary>
        /// Removes the specified collection of SimpleCurves' peaks from the plot.
        /// </summary>
        /// <param name="simpleCurve">Collection of SimpleCurves.</param>
        /// <param name="update">if set to <c>true</c> the plot is [updated].</param>
        /// <exception cref="System.ArgumentNullException">The specified SimpleCurve cannot be null</exception>
        /// <exception cref="System.ArgumentException">The plot does not contain the specified SimpleCurve</exception>
        public void RemoveSimpleCurvesPeaks(List<SimpleCurve> simpleCurves, bool update = true)
        {
            if (simpleCurves == null)
                throw new ArgumentNullException("The specified collection of SimpleCurves cannot be null");

            RemoveSimpleCurvesPeaks(simpleCurves.ToArray());
        }

        /// <summary>
        /// Updates the plot with the peaks of the specified SimpleCurve.
        /// </summary>
        /// <param name="simpleCurve">The SimpleCurve.</param>
        /// <exception cref="System.ArgumentNullException">The specified SimpleCurve cannot be null</exception>
        /// <exception cref="System.ArgumentException">The plot does not contain the specified SimpleCurve</exception>
        public void UpdateSimpleCurvePeaks(SimpleCurve simpleCurve, bool update = true)
        {
            if (simpleCurve == null)
                throw new ArgumentNullException("The specified SimpleCurve cannot be null");
            if (!_simpleCurvesInPlot.ContainsKey(simpleCurve))
                throw new ArgumentException("The plot does not contain the specified SimpleCurve");

            //Retrieve the SimpleCurve's respective lineseries from the dictionary of SimpleCurves in the plot
            LineSeries data;
            if (!_simpleCurvesInPlot.TryGetValue(simpleCurve, out data))
                return;

            //Removes the SimpleCurves previous peaks from the plot
            List<PlotPeak> peaks;
            if (_peaksInPlot.ContainsKey(simpleCurve))
                RemoveSimpleCurvePeaks(simpleCurve, false);

            //Return if the SimpleCurve does not contain peaks
            if (simpleCurve.Peaks == null)
            {
                if (update)
                    UpdatePlot(); //Update the plot
                return;
            }

            //Add the SimpleCurve and a blank list of peaks to the list of peaks in the plot
            peaks = new List<PlotPeak>();
            _peaksInPlot.Add(simpleCurve, peaks);

            //Convert peaks to lineseries for the plot
            foreach (Peak peak in simpleCurve.Peaks)
            {
                PlotPeak plotPeak = new PlotPeak(simpleCurve, data, peak);
                peaks.Add(plotPeak); //Add peak to SimpleCurves list of peaks
                int i = _dataSeries.IndexOf(data);
                _dataSeries.Insert(i, plotPeak.PeakLines); //Add peak's lineseries to the plot, before the SimpleCurves lineseries in order to draw the plot helplines behing the SimpleCurve
                _annotations.Add(plotPeak.Label); //Add peak label to the plot
            }

            if (update)
                UpdatePlot(); //Update the plot
        }

        /// <summary>
        /// Updates the plot with the peaks of the specified collection of SimpleCurves.
        /// </summary>
        /// <param name="simpleCurves">Collection of SimpleCurves to update.</param>
        /// <param name="update">if set to <c>true</c> [update] the plot.</param>
        public void UpdateSimpleCurvesPeaks(SimpleCurve[] simpleCurves, bool update = true)
        {
            if (simpleCurves == null)
                throw new ArgumentNullException("The specified collection of SimpleCurves cannot be null");

            foreach (SimpleCurve simpleCurve in simpleCurves)
                UpdateSimpleCurvePeaks(simpleCurve, false);

            if (update)
                UpdatePlot(); //Update the plot
        }

        /// <summary>
        /// Updates the plot with the peaks of the specified collection of SimpleCurves.
        /// </summary>
        /// <param name="simpleCurves">Collection of SimpleCurves to update.</param>
        /// <param name="update">if set to <c>true</c> [update] the plot.</param>
        public void UpdateSimpleCurvesPeaks(List<SimpleCurve> simpleCurves, bool update = true)
        {
            if (simpleCurves == null)
                throw new ArgumentNullException("The specified collection of SimpleCurves cannot be null");

            UpdateSimpleCurvesPeaks(simpleCurves.ToArray(), update);
        }

        #region SimpleCurve Events
        private ConcurrentDictionary<object, bool> _curvesPlotDataPending = new ConcurrentDictionary<object, bool>();

        /// <summary>
        /// Adds the NewDataAdded of the SimpleCurve to the plot.
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="PalmSens.Data.ArrayDataAddedEventArgs"/> instance containing the event data.</param>
        protected virtual void SimpleCurve_NewDataAdded(object sender, PalmSens.Data.ArrayDataAddedEventArgs e)
        {
            if (!_curvesPlotDataPending.ContainsKey(sender))
            {
                _curvesPlotDataPending.TryAdd(sender, true);
            }

            _signal.Set();
        }

        private void OnSimpleCurveNewData(IEnumerable<SimpleCurve> curves)
        {
            lock (PlotModel.SyncRoot)
            {
                foreach (var simpleCurve in curves)
                {
                    //Retrieve the SimpleCurve's respective lineseries from the dictionary of SimpleCurves in the plot
                    LineSeries data;
                    if (!_simpleCurvesInPlot.TryGetValue(simpleCurve, out data))
                        return;

                    //Gets the data from the SimpleCurve
                    double[] x = simpleCurve.XAxisValues;
                    double[] y = simpleCurve.YAxisValues;

                    int nPoints = (x.Length > y.Length) ? y.Length : x.Length;
                    data.Points.Clear();

                    for (int i = data.Points.Count; i < nPoints; i++)
                    {
                        data.Points.Add(new DataPoint(x[i], y[i]));
                    }

                    data.XAxis.Maximum = data.XAxis.Maximum < data.MaxX ? data.MaxX : data.XAxis.Maximum;
                    data.XAxis.Minimum = data.XAxis.Minimum > data.MinX ? data.MinX : data.XAxis.Minimum;
                    data.YAxis.Maximum = data.YAxis.Maximum < data.MaxY ? data.MaxY : data.YAxis.Maximum;
                    data.YAxis.Maximum = data.YAxis.Minimum > data.MinY ? data.MinY : data.YAxis.Maximum;
                }
            }

            PlotModel.InvalidatePlot(true); //Updates the plot
        }

        private async Task ConsumeLiveDataQueue(CancellationToken cancellationToken)
        {
            try
            {
                while (!cancellationToken.IsCancellationRequested)
                {
                    await _signal.WaitAsync();
                    cancellationToken.ThrowIfCancellationRequested();

                    var keys =
                        _curvesPlotDataPending.Keys.ToArray();
                    var curves = new List<SimpleCurve>();

                    foreach (var key in
                             keys)
                    {
                        if (_curvesPlotDataPending.TryRemove(key, out _))
                        {
                            curves.Add(key as SimpleCurve);
                        }
                    }

                    await _plotInvoker.Invoke(() => { OnSimpleCurveNewData(curves); });
                    _plotInvoker.DoEvents();
                    await Task.Delay(TimeSpan.FromMilliseconds(20), cancellationToken);
                    _signal?.Set();
                }
            }
            catch (OperationCanceledException) { }
        }

        /// <summary>
        /// Updates the SimpleCurve's peaks in the plot.
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="EventArgs"/> instance containing the event data.</param>
        protected void SimpleCurve_DetectedPeaks(object sender, EventArgs e)
        {
            if (_plotInvoker.InvokeIfRequired(new EventHandler(SimpleCurve_DetectedPeaks), sender, e)) //Recast event to UI thread when necessary
                return;
            UpdateSimpleCurvePeaks(sender as SimpleCurve);
        }

        /// <summary>
        /// Handles the CurveFinished event of the SimpleCurve control.
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="EventArgs"/> instance containing the event data.</param>
        protected virtual void SimpleCurve_CurveFinished(object sender, EventArgs e)
        {
            if (_plotInvoker.InvokeIfRequired(new EventHandler(SimpleCurve_CurveFinished), sender, e)) //Recast event to UI thread when necessary
                return;
            SimpleCurve simpleCurve = sender as SimpleCurve;
            simpleCurve.NewDataAdded -= SimpleCurve_NewDataAdded;
            simpleCurve.CurveFinished -= SimpleCurve_CurveFinished;

            if (!_curvesPlotDataPending.ContainsKey(sender))
            {
                _curvesPlotDataPending.TryAdd(sender, true);
            }

            _signal.Set();
        }
        #endregion
        #endregion
        /// <summary>
        /// Clears all data from the plot.
        /// </summary>
        /// <param name="update">if set to <c>true</c> [update].</param>
        public void ClearAll(bool update = true)
        {
            ClearSimpleCurves(false);
            _dataSeries.Clear();
            if (update)
                UpdatePlot();
        }

        public Axis UpdateAxes(Axis axis, AxisType type)
        {
            switch (type)
            {
                case AxisType.Linear:
                    axis = new LinearAxis()
                    {
                        Position = axis.Position,
                        Key = axis.Key,
                        Title = axis.Title,
                        Maximum = axis.Maximum,
                        Minimum = axis.Minimum
                    };
                    break;
                case AxisType.Logarithmic:
                    axis = new LogarithmicAxis()
                    {
                        Position = axis.Position,
                        Key = axis.Key,
                        Title = axis.Title,
                        Maximum = axis.Maximum,
                        Minimum = axis.Minimum
                    };
                    break;
            }
            axis.AxislineColor = _axesColor;
            axis.TicklineColor = _axesColor;
            axis.MinorTicklineColor = _axesColor;
            axis.TextColor = _axisTextColor;
            axis.TitleColor = _axisTextColor;
            axis.MajorGridlineStyle = _gridLineStyle;
            return axis;
        }

        /// <summary>
        /// Updates the plot.
        /// </summary>
        public virtual void UpdatePlot(bool force = false)
        {
            //Clear the the plot
            PlotModel.Series.Clear();
            PlotModel.Annotations.Clear();
            if (!force && (_dataSeries == null || _dataSeries.Count == 0))
            {
                PlotModel.InvalidatePlot(true);
                return;
            }

            bool hideSecondaryAxis = true;
            PlotModel.PlotAreaBackground = _plotBackgroundColor;
            PlotModel.Legends.Select(legend => legend.TextColor = _legendTextColor);

            //Add the data to the plot
            if(_dataSeries != null)
            {
                foreach (Series data in _dataSeries)
                {
                    PlotModel.Series.Add(data);
                    (data as LineSeries).MarkerType = _markerType;
                    (data as LineSeries).MarkerSize = _markerSize;
                    data.Background = _plotBackgroundColor;
                    if ((data as LineSeries).YAxisKey == _yAxisSecondary.Key)
                        hideSecondaryAxis = false;
                }
            }

            //Add annotations to the plot
            foreach (PointAnnotation annotation in _annotations)
                PlotModel.Annotations.Add(annotation);

            //Add the axes to the plot
            PlotModel.Axes.Clear();
            PlotModel.Axes.Add(UpdateAxes(_xAxis, _xAxisType));
            PlotModel.Axes.Add(UpdateAxes(_yAxis, _yAxisType));
            if(!hideSecondaryAxis)
                PlotModel.Axes.Add(UpdateAxes(_yAxisSecondary, _yAxisSecondaryType));

            PlotModel.InvalidatePlot(true);
        }

        public void Dispose()
        {
            _cts?.Cancel();
            _signal?.Set();
            _cts?.Dispose();
        }
    }

    public interface IPlotInvoker : IPlatformInvoker
    {
        /// <summary>
        /// Invokes if required.
        /// </summary>
        /// <param name="method">The method.</param>
        /// <param name="args">The arguments.</param>
        /// <returns></returns>
        Task Invoke(Action action);

        void DoEvents();
    }

    internal class AsyncAutoResetEvent
    {
        private readonly static Task s_completed = Task.FromResult(true);
        private readonly Queue<TaskCompletionSource<bool>> m_waits = new Queue<TaskCompletionSource<bool>>();
        private bool m_signaled;

        public Task WaitAsync()
        {
            lock (m_waits)
            {
                if (m_signaled)
                {
                    m_signaled = false;
                    return s_completed;
                }
                else
                {
                    var tcs = new TaskCompletionSource<bool>();
                    m_waits.Enqueue(tcs);
                    return tcs.Task;
                }
            }
        }

        public void Set()
        {
            TaskCompletionSource<bool> toRelease = null;
            lock (m_waits)
            {
                if (m_waits.Count > 0)
                    toRelease = m_waits.Dequeue();
                else if (!m_signaled)
                    m_signaled = true;
            }
            if (toRelease != null)
            {
                toRelease.SetResult(true);
            }
        }
    }

    public enum AxisType { Linear = 0, Logarithmic = 1 }
}
