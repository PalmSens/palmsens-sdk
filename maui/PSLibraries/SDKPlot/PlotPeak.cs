using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using OxyPlot.Annotations;
using OxyPlot.Series;
using PalmSens.Analysis;
using PalmSens.Core.Simplified.Data;
using OxyPlot;

namespace SDKPlot
{
    public class PlotPeak
    {
        /// <summary>
        /// Initializes a new instance of the <see cref="PlotPeak"/> class.
        /// </summary>
        /// <param name="simpleCurve">The SimpleCurve.</param>
        /// <param name="simpleCurvePlotData">The lineseries of the SimpleCurve in the plot.</param>
        /// <param name="peak">The peak.</param>
        /// <exception cref="System.ArgumentNullException">
        /// SimpleCurve cannot be null
        /// or
        /// The lineseries of the SimpleCurve cannot be null
        /// or
        /// The peak cannot be null
        /// </exception>
        internal PlotPeak(SimpleCurve simpleCurve, LineSeries simpleCurvePlotData, Peak peak)
        {
            if (simpleCurve == null)
                throw new ArgumentNullException("SimpleCurve cannot be null");
            if (simpleCurvePlotData == null)
                throw new ArgumentNullException("The lineseries of the SimpleCurve cannot be null");
            if (peak == null)
                throw new ArgumentNullException("The peak cannot be null");

            SimpleCurve = simpleCurve;
            InitPlotData(simpleCurvePlotData, peak);
        }

        /// <summary>
        /// Gets the simple curve.
        /// </summary>
        /// <value>
        /// The simple curve.
        /// </value>
        public SimpleCurve SimpleCurve { get; private set; }

        /// <summary>
        /// Gets the peak lines.
        /// </summary>
        /// <value>
        /// The peak lines.
        /// </value>
        public LineSeries PeakLines { get; private set; }

        /// <summary>
        /// Gets the label.
        /// </summary>
        /// <value>
        /// The label.
        /// </value>
        public PointAnnotation Label { get; private set; }

        /// <summary>
        /// Initializes the plot data for the peak.
        /// </summary>
        /// <param name="simpleCurvePlotData">The lineseries of the SimpleCurve in the plot.</param>
        /// <param name="peak">The peak.</param>
        private void InitPlotData(LineSeries simpleCurvePlotData, Peak peak)
        {
            //Create a new lineseries for the peak based on that of its respective SimpleCurve
            PeakLines = new LineSeries()
            {
                RenderInLegend = false,
                Color = OxyColors.Gray,
                BrokenLineStyle = LineStyle.Dash,
                MarkerType = MarkerType.None,
                YAxisKey = simpleCurvePlotData.YAxisKey
            };

            //Adds the data for the lines used to draw the peak
            PeakLines.Points.Add(new DataPoint(peak.LeftX, peak.LeftY));
            PeakLines.Points.Add(new DataPoint(peak.PeakX, peak.OffsetY));
            PeakLines.Points.Add(new DataPoint(peak.PeakX, peak.PeakY));
            PeakLines.Points.Add(new DataPoint(peak.PeakX, peak.OffsetY));
            PeakLines.Points.Add(new DataPoint(peak.RightX, peak.RightY));

            //Sets the peak height as the label
            Label = new PointAnnotation()
            {
                YAxisKey = simpleCurvePlotData.YAxisKey,
                X = peak.PeakX,
                Y = peak.PeakY,
                Shape = MarkerType.None,
                Text = peak.PeakValue.ToString(),
                TextVerticalAlignment = VerticalAlignment.Bottom,
                TextHorizontalAlignment = HorizontalAlignment.Left
            };
        }
    }
}
