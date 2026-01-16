using OxyPlot;
using OxyPlot.Series;
using PalmSens.Core.Simplified;
using PalmSens.Core.Simplified.Data;
using System;
using System.Collections.Generic;
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
using OxyPlot.Axes;

namespace SDKPlot.WPF
{
    /// <summary>
    /// Interaction logic for Plot.xaml
    /// </summary>
    public partial class Plot : UserControl, IPlatformInvoker
    {
        public Plot()
        {
            InitializeComponent();
            _corePlot = new CorePlot(this as IPlatformInvoker);
            this.plotView.Model = _corePlot.PlotModel;
        }

        #region Plot Properties
        /// <summary>
        /// The platform independent plot class that handles functionality of the plot
        /// </summary>
        private CorePlot _corePlot;

        /// <summary>
        /// Reference to the OxyPlot PlotModel
        /// </summary>
        public PlotModel PlotModel { get { return _corePlot.PlotModel; } }

        /// <summary>
        /// Gets or sets the title.
        /// </summary>
        /// <value>
        /// The title.
        /// </value>
        public string Title
        {
            get { return _corePlot.Title; }
            set { _corePlot.Title = value; }
        }

        #region Axes
        /// <summary>
        /// Gets the bottom x axis object
        /// Manages settings such as range, ticks, label etc.
        /// </summary>
        public Axis XAxis => _corePlot.XAxis;

        /// <summary>
        /// Gets or sets the x axis label.
        /// </summary>
        /// <value>
        /// The x axis label.
        /// </value>
        public string XAxisLabel
        {
            get { return _corePlot.XAxisLabel; }
            set { _corePlot.XAxisLabel = value; }
        }

        /// <summary>
        /// Gets or sets the type of the x axis.
        /// </summary>
        /// <value>
        /// The type of the x axis.
        /// </value>
        public AxisType XAxisType
        {
            get { return _corePlot.XAxisType; }
            set { _corePlot.XAxisType = value; }
        }

        /// <summary>
        /// Gets the bottom x axis object
        /// Manages settings such as range, ticks, label etc.
        /// </summary>
        public Axis YAxis => _corePlot.YAxis;

        /// <summary>
        /// Gets or sets the y axis label.
        /// </summary>
        /// <value>
        /// The y axis label.
        /// </value>
        public string YAxisLabel
        {
            get { return _corePlot.YAxisLabel; }
            set { _corePlot.YAxisLabel = value; }
        }

        /// <summary>
        /// Gets or sets the type of the y axis.
        /// </summary>
        /// <value>
        /// The type of the y axis.
        /// </value>
        public AxisType YAxisType
        {
            get { return _corePlot.YAxisType; }
            set { _corePlot.YAxisType = value; }
        }

        /// <summary>
        /// Gets or sets the secondary y axis label.
        /// </summary>
        /// <value>
        /// The secondary y axis label.
        /// </value>
        public string YAxisSecondaryLabel
        {
            get { return _corePlot.YAxisSecondaryLabel; }
            set { _corePlot.YAxisSecondaryLabel = value; }
        }

        /// <summary>
        /// Gets or sets the type of the secondary y axis.
        /// </summary>
        /// <value>
        /// The type of the y axis.
        /// </value>
        public AxisType YAxisSecondaryType
        {
            get { return _corePlot.YAxisSecondaryType; }
            set { _corePlot.YAxisSecondaryType = value; }
        }

        /// <summary>
        /// Gets or sets the datapoint MarkerType.
        /// The default MarkerType is a circle.
        /// </summary>
        /// <value>
        /// The marker type used for datapoints.
        /// </value>
        public OxyPlot.MarkerType MarkerType
        {
            get { return _corePlot.MarkerType; }
            set { _corePlot.MarkerType = value; }
        }

        /// <summary>
        /// The size of the markers indicating the datapoints in the plot.
        /// The default MarkerSize is 5.
        /// </summary>
        /// <value>
        /// The size of the marker used for datapoints.
        /// </value>
        public int MarkerSize
        {
            get { return _corePlot.MarkerSize; }
            set { _corePlot.MarkerSize = value; }
        }

        /// <summary>
         /// Gets or sets the color of the plot background.
         /// </summary>
         /// <value>
         /// The color of the plot background.
         /// </value>
        public SolidColorBrush PlotBackgroundColor
        {
            get { return (SolidColorBrush)GetValue(PlotBackgroundColorProperty); }
            set
            {
                SetValue(PlotBackgroundColorProperty, value);
                Color c = (value as SolidColorBrush).Color;
                _corePlot.PlotBackgroundColor = OxyColor.FromArgb(c.A, c.R, c.G, c.B);
            }
        }

        /// <summary>
        /// The plot background color property
        /// </summary>
        public static readonly DependencyProperty PlotBackgroundColorProperty =
            DependencyProperty.Register("PlotBackgroundColor", typeof(SolidColorBrush), typeof(Plot), new PropertyMetadata(null));

        /// <summary>
        /// Gets or sets the plot background color.
        /// </summary>
        /// <value>
        /// The background color.
        /// </value>
        public new SolidColorBrush Background
        {
            get { return (SolidColorBrush)GetValue(BackgroundProperty); }
            set { SetValue(BackgroundProperty, value); }
        }

        /// <summary>
        /// Gets or sets the color of the legend text.
        /// </summary>
        /// <value>
        /// The color of the legend text.
        /// </value>
        public OxyColor LegendTextColor
        {
            get { return _corePlot.LegendTextColor; }
            set { _corePlot.LegendTextColor = value; }
        }
        #endregion

        /// <summary>
        /// Gets the amount of dataseries in the plot.
        /// </summary>
        /// <value>
        /// The n series.
        /// </value>
        public int NSeries { get { return _corePlot.NSeries; } }

        /// <summary>
        /// Gets the amount of SimpleCurves in the plot.
        /// </summary>
        /// <value>
        /// The n simple curves.
        /// </value>
        public int NSimpleCurves { get { return _corePlot.NSimpleCurves; } }
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
        public LineSeries AddData(string label, double[] x, double[] y, bool useSecondaryYAxis = false, bool update = true)
        {
            return _corePlot.AddData(label, x, y, useSecondaryYAxis, update);
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
            return _corePlot.AddData(label, x, xLabel, y, yLabel, useSecondaryYAxis, update);
        }

        /// <summary>
        /// Removes the specified data series from the plot.
        /// </summary>
        /// <param name="data">The data series.</param>
        public void RemoveData(Series data)
        {
            _corePlot.RemoveData(data);
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
        public bool ContainsSimpleCurve(SimpleCurve simpleCurve)
        {
            return _corePlot.ContainsSimpleCurve(simpleCurve);
        }

        /// <summary>
        /// Adds the specified SimpleCurve to the plot.
        /// </summary>
        /// <param name="simpleCurve">The simple curve.</param>
        /// <param name="useSecondaryYAxis">if set to <c>true</c> [use secondary y axis].</param>
        /// <param name="update">if set to <c>true</c> the plot is [updated].</param>
        public void AddSimpleCurve(SimpleCurve simpleCurve, bool useSecondaryYAxis = false, bool update = true)
        {
            _corePlot.AddSimpleCurve(simpleCurve, useSecondaryYAxis, update);
        }

        /// <summary>
        /// Adds a collection of SimpleCurves to the plot.
        /// </summary>
        /// <param name="simpleCurves">List of SimpleCurves.</param>
        /// <param name="useSecondaryYAxis">if set to <c>true</c> [use secondary y axis].</param>
        /// <param name="update">if set to <c>true</c> the plot is [updated].</param>
        public void AddSimpleCurves(List<SimpleCurve> simpleCurves, bool useSecondaryYAxis = false, bool update = true)
        {
            _corePlot.AddSimpleCurves(simpleCurves, useSecondaryYAxis, update);
        }

        /// <summary>
        /// Adds a collection of SimpleCurves to the plot.
        /// </summary>
        /// <param name="simpleCurves">Array of SimpleCurves.</param>
        /// <param name="useSecondaryYAxis">if set to <c>true</c> [use secondary y axis].</param>
        /// <param name="update">if set to <c>true</c> the plot is [updated].</param>
        public void AddSimpleCurves(SimpleCurve[] simpleCurves, bool useSecondaryYAxis = false, bool update = true)
        {
            _corePlot.AddSimpleCurves(simpleCurves, useSecondaryYAxis, update);
        }

        /// <summary>
        /// Removes the specified SimpleCurve from the plot.
        /// </summary>
        /// <param name="simpleCurve">The SimpleCurve.</param>
        /// <param name="update">if set to <c>true</c> the plot is [updated].</param>
        public void RemoveSimpleCurve(SimpleCurve simpleCurve, bool update = true)
        {
            _corePlot.RemoveSimpleCurve(simpleCurve, update);
        }

        /// <summary>
        /// Removes a collection of SimpleCurves from the plot.
        /// </summary>
        /// <param name="simpleCurves">List of SimpleCurves.</param>
        /// <param name="update">if set to <c>true</c> the plot is [updated].</param>
        public void RemoveSimpleCurves(List<SimpleCurve> simpleCurves, bool update = true)
        {
            _corePlot.RemoveSimpleCurves(simpleCurves, update);
        }

        /// <summary>
        /// Removes a collection of SimpleCurves from the plot.
        /// </summary>
        /// <param name="simpleCurves">Array of SimpleCurves.</param>
        /// <param name="update">if set to <c>true</c> the plot is [updated].</param>
        public void RemoveSimpleCurves(SimpleCurve[] simpleCurves, bool update = true)
        {
            _corePlot.RemoveSimpleCurves(simpleCurves, update);
        }

        /// <summary>
        /// Clears all SimpleCurves from the plot.
        /// </summary>
        public void ClearSimpleCurves(bool update = true)
        {
            _corePlot.ClearSimpleCurves(update);
        }

        /// <summary>
        /// Removes the specified SimpleCurve's peaks from the plot.
        /// </summary>
        /// <param name="simpleCurve">The SimpleCurve.</param>
        /// <param name="update">if set to <c>true</c> the plot is [updated].</param>
        public void RemoveSimpleCurvePeaks(SimpleCurve simpleCurve, bool update = true)
        {
            _corePlot.RemoveSimpleCurvePeaks(simpleCurve, update);
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
            _corePlot.RemoveSimpleCurvesPeaks(simpleCurves, update);
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
            _corePlot.RemoveSimpleCurvesPeaks(simpleCurves, update);
        }

        /// <summary>
        /// Updates the plot with the peaks of the specified SimpleCurve.
        /// </summary>
        /// <param name="simpleCurve">The SimpleCurve.</param>
        /// <exception cref="System.ArgumentNullException">The specified SimpleCurve cannot be null</exception>
        /// <exception cref="System.ArgumentException">The plot does not contain the specified SimpleCurve</exception>
        public void UpdateSimpleCurvePeaks(SimpleCurve simpleCurve, bool update = true)
        {
            _corePlot.UpdateSimpleCurvePeaks(simpleCurve, update);
        }

        /// <summary>
        /// Updates the plot with the peaks of the specified collection of SimpleCurves.
        /// </summary>
        /// <param name="simpleCurves">Collection of SimpleCurves to update.</param>
        /// <param name="update">if set to <c>true</c> [update] the plot.</param>
        public void UpdateSimpleCurvesPeaks(SimpleCurve[] simpleCurves, bool update = true)
        {
            _corePlot.UpdateSimpleCurvesPeaks(simpleCurves, update);
        }

        /// <summary>
        /// Updates the plot with the peaks of the specified collection of SimpleCurves.
        /// </summary>
        /// <param name="simpleCurves">Collection of SimpleCurves to update.</param>
        /// <param name="update">if set to <c>true</c> [update] the plot.</param>
        public void UpdateSimpleCurvesPeaks(List<SimpleCurve> simpleCurves, bool update = true)
        {
            _corePlot.UpdateSimpleCurvesPeaks(simpleCurves, update);
        }
        #endregion

        /// <summary>
        /// Clears all data from the plot.
        /// </summary>
        /// <param name="update">if set to <c>true</c> [update].</param>
        public void ClearAll(bool update = true)
        {
            _corePlot.ClearAll(update);
        }

        /// <summary>
        /// Updates the plot.
        /// </summary>
        public void UpdatePlot(bool force = false)
        {
            _corePlot.UpdatePlot(force);
        }

        #region Platform interface
        /// <summary>
        /// Invokes event to UI thread if required.
        /// </summary>
        /// <param name="method">The method.</param>
        /// <param name="args">The arguments.</param>
        /// <returns></returns>
        /// <exception cref="System.NullReferenceException">Parent control not set.</exception>
        public bool InvokeIfRequired(Delegate method, params object[] args)
        {
            if (!Dispatcher.CheckAccess()) //Check if event needs to be cast to the UI thread
            {
                Dispatcher.BeginInvoke(method, args); //Recast event to UI thread
                return true;
            }
            return false;
        }
        #endregion
    }
}
