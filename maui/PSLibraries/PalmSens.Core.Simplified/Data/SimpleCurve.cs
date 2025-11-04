using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using PalmSens.Plottables;
using PalmSens.Data;
using PalmSens.Analysis;
using System.ComponentModel;
using PalmSens.Fitting;
using PalmSens.Fitting.Models;

namespace PalmSens.Core.Simplified.Data
{
    /// <summary>
    /// Predifined smooth settings for the Savitsky-Golay filter
    /// </summary>
    public enum SmoothLevel
    {
        None = -1,
        //Remove spikes
        SpikeRejection = 0,
        //Window of 5 samples
        Low = 1,
        //Window of 9 samples
        Medium = 2,
        //Window of 15 samples
        High = 3,
        //Window of 25 samples
        VeryHigh = 4
    }

    /// <summary>
    /// Peak detect algorithms
    /// </summary>
    public enum PeakTypes
    {
        //Detect peaks using derivative
        Default = 0,
        //Detect peaks using second derivative
        Shoulder = 1,
        //Detect peaks using semiderivative
        LSVCV = 2
    }

    public class SimpleCurve: IDisposable
    {
        /// <summary>
        /// Initializes a new instance of the <see cref="SimpleCurve" /> class.
        /// </summary>
        /// <param name="curve">The Curve.</param>
        /// <exception cref="System.ArgumentNullException">Cannot create an instance of SimpleCurve when curve is null</exception>
        public SimpleCurve(Curve curve, SimpleMeasurement simpleMeasurement)
        {
            if (curve == null)
                throw new ArgumentNullException("Cannot create an instance of SimpleCurve when the specified Curve is null");

            Curve = curve;
            if (!Curve.IsFinished)
            {
                Curve.Finished += Curve_Finished;
                Curve.NewDataAdded += Curve_NewDataAdded;
            }
            _simpleMeasurement = simpleMeasurement;
        }

        #region Properties
        /// <summary>
        /// The original curve
        /// </summary>
        public Curve Curve;

        /// <summary>
        /// The SimpleMeasurement that contains the curve
        /// </summary>
        private SimpleMeasurement _simpleMeasurement;

        /// <summary>
        /// Gets or sets the title of the SimpleCurve.
        /// </summary>
        /// <value>
        /// The title.
        /// </value>
        public string Title
        {
            get { return Curve.Title; }
            set
            {
                if (Curve.Title == value)
                    return;
                Curve.Title = value;
                OnPropertyChanged(nameof(Title));
            }
        }

        /// <summary>
        /// Gets the full title, the title of the SimpleMeasurement and SimpleCurve combined.
        /// </summary>
        /// <value>
        /// The full title.
        /// </value>
        public string FullTitle
        {
            get { return $"{_simpleMeasurement.Title}: {Title}"; }
        }

        /// <summary>
        /// Gets the unit of the X-Axis.
        /// </summary>
        /// <value>
        /// The unit.
        /// </value>
        public string XUnit { get { return Curve.XUnit.Quantity; } }

        /// <summary>
        /// Gets the type data on the X-Axis.
        /// </summary>
        /// <value>
        /// The type data on the X-Axis.
        /// </value>
        public DataArrayType XAxisDataType { get { return Curve.XArrayType; } }

        /// <summary>
        /// Gets the X-Axis value at a specified index.
        /// </summary>
        /// <param name="index">The index.</param>
        /// <returns></returns>
        public double XAxisValue(int index) { return Curve.GetXValue(index); }

        /// <summary>
        /// Gets the X-Axis values.
        /// </summary>
        /// <value>
        /// The X-Axis values.
        /// </value>
        public double[] XAxisValues { get { return Curve.GetXValues(); } }

        /// <summary>
        /// Gets the unit of the Y-Axis.
        /// </summary>
        /// <value>
        /// The unit.
        /// </value>
        public string YUnit { get { return Curve.YUnit.Quantity; } }

        /// <summary>
        /// Gets the type data on the Y-Axis.
        /// </summary>
        /// <value>
        /// The type data on the Y-Axis.
        /// </value>
        public DataArrayType YAxisDataType { get { return Curve.YArrayType; } }

        /// <summary>
        /// Gets the X-Axis value at a specified index.
        /// </summary>
        /// <param name="index">The index.</param>
        /// <returns></returns>
        public double YAxisValue(int index) { return Curve.GetYValue(index); }

        /// <summary>
        /// Gets the Y-Axis values.
        /// </summary>
        /// <value>
        /// The Y-Axis values.
        /// </value>
        public double[] YAxisValues { get { return Curve.GetYValues(); } }

        /// <summary>
        /// Gets the amount of data points in the SimpleCurve.
        /// </summary>
        /// <value>
        /// The amount of data points.
        /// </value>
        public int NDataPoints { get { return (XAxisValues.Length < YAxisValues.Length) ? XAxisValues.Length : YAxisValues.Length; } }

        /// <summary>
        /// Gets the list of peaks detected in this curve.
        /// </summary>
        /// <value>
        /// The peaklist.
        /// </value>
        public PeakList Peaks { get { return Curve.Peaks; } }

        /// <summary>
        /// Gets the list of levels detected in this curve.
        /// </summary>
        /// <value>
        /// The peaklist.
        /// </value>
        public CFALevelList Levels { get { return Curve.Levels; } }

        /// <summary>
        /// Gets the mux channel that the curve was measured on.
        /// </summary>
        /// <value>
        /// The mux channel.
        /// </value>
        public int MuxChannel { get { return Curve.MuxChannel; } }

        /// <summary>
        /// Gets the channel that the measurement was measured on.
        /// </summary>
        /// <value>
        /// The channel.
        /// </value>
        public int Channel { get { return _simpleMeasurement == null ? -1 : _simpleMeasurement.Channel; } }

        /// <summary>
        /// Gets a value indicating whether this SimpleCurve is finished measuring.
        /// </summary>
        /// <value>
        /// <c>true</c> if SimpleCurve is finished measuring; otherwise, <c>false</c>.
        /// </value>
        public bool IsFinished
        {
            get { return Curve.IsFinished; }
        }
        #endregion

        #region Functions
        /// <summary>
        /// Clones this instance.
        /// </summary>
        /// <returns>A copy of this SimpleCurve</returns>
        /// <exception cref="System.Exception">Wait untill SimpleCurve is finished before cloning</exception>
        public SimpleCurve Clone()
        {
            if (!IsFinished)
                throw new Exception("Wait untill SimpleCurve is finished before cloning");
            Curve clonedCurve = new Curve(this.Curve); //Clones the base Curve
            clonedCurve.Title = $"{Title}, Copy";
            clonedCurve.Finish();
            return new SimpleCurve(clonedCurve, _simpleMeasurement);
        }

        /// <summary>
        /// Detects peaks.
        /// </summary>
        /// <param name="minPeakWidth">Minimum width of the peak.</param>
        /// <param name="minPeakHeight">Minimum height of the peak.</param>
        /// <param name="clearPeaks">if set to <c>true</c> [clear existing peaks].</param>
        /// <param name="useHiddenPeakDetectionAlgorithm">if set to <c>true</c> [use hidden peak detection algorithm].</param>
        /// <param name="mergeOverlappingPeaks">if set to <c>true</c> [merge overlapping peaks].</param>
        /// <exception cref="Exception">Wait untill SimpleCurve is finished before detecting peaks</exception>
        /// <exception cref="System.Exception">Wait untill SimpleCurve is finished before detecting peaks</exception>
        public void DetectPeaks(double minPeakWidth = 0.0, double minPeakHeight = 0.0, bool clearPeaks = true, bool useHiddenPeakDetectionAlgorithm = false, bool mergeOverlappingPeaks = false)
        {
            if (!IsFinished)
                throw new Exception("Wait untill SimpleCurve is finished before detecting peaks");
            if(clearPeaks)
                Curve.ClearPeaks(); //Clear previous peaks from curve
            Curve.FindPeaks(minPeakWidth, minPeakHeight, useHiddenPeakDetectionAlgorithm, mergeOverlappingPeaks); //Detect peaks
            OnDetectedPeaks();
        }

        /// <summary>
        /// Detects the peaks asynchronous.
        /// </summary>
        /// <param name="minPeakWidth">Minimum width of the peak.</param>
        /// <param name="minPeakHeight">Minimum height of the peak.</param>
        /// <param name="clearPeaks">if set to <c>true</c> [clear existing peaks].</param>
        /// <param name="peakType">Type of peak.</param>
        /// <returns></returns>
        /// <exception cref="Exception">Wait untill SimpleCurve is finished before detecting peaks</exception>
        public async Task DetectPeaksAsync(double minPeakWidth = 0.0, double minPeakHeight = 0.0, bool clearPeaks = true, PeakTypes peakType = PeakTypes.Default, PeakDetectProgress peakDetectProgress = null)
        {
            if (!IsFinished)
                throw new Exception("Wait untill SimpleCurve is finished before detecting peaks");
            if (clearPeaks)
                Curve.ClearPeaks(); //Clear previous peaks from curve

            switch (peakType)
            {
                case PeakTypes.Default:
                    if (peakDetectProgress != null) throw new Exception($"Peak progress detection not supported for '{peakType}");
                    await Task.Run(() => Curve.FindPeaks(minPeakWidth, minPeakHeight, false, false)); //Detect peaks
                    break;
                case PeakTypes.Shoulder:
                    if (peakDetectProgress != null) throw new Exception($"Peak progress detection not supported for '{peakType}");
                    await Task.Run(() => Curve.FindPeaks(minPeakWidth, minPeakHeight, true, false)); //Detect peaks
                    break;
                case PeakTypes.LSVCV:
                    SemiDerivativePeakDetection semiDerivativePeakDetection = new SemiDerivativePeakDetection();
                    Dictionary<Curve, double> curves = new Dictionary<Curve, double>();
                    curves.Add(Curve, minPeakHeight);
                    await semiDerivativePeakDetection.GetNonOverlappingPeaksAsync(curves, peakDetectProgress); //Detect peaks
                    break;
            }

            OnDetectedPeaks();
        }

        /// <summary>
        /// Detects the levels asynchronous.
        /// </summary>
        /// <param name="minLevelWidth">Minimum width of the level.</param>
        /// <param name="minLevelHeight">Minimum height of the level.</param>
        /// <param name="clearLevels">if set to <c>true</c> [clear existing levels].</param>
        /// <returns></returns>
        /// <exception cref="Exception">Wait untill SimpleCurve is finished before detecting peaks</exception>
        public async Task DetectLevelsAsync(double minLevelWidth, double minLevelHeight, bool clearLevels = true, LevelDetectProgress levelDetectProgress = null)
        {
            if (!IsFinished)
                throw new Exception("Wait untill SimpleCurve is finished before detecting levels");
            if (clearLevels)
                Curve.ClearLevels(); //Clear previous levels from curve

            CFALevelList levelList = new CFALevelList(Curve, minLevelWidth, minLevelHeight);
            await levelList.FindLevelsAsync(minLevelWidth, minLevelHeight, levelDetectProgress);
            Curve.Levels = levelList;
        }

        /// <summary>
        /// Fits the equivalent circuit.
        /// </summary>
        /// <param name="cdc">The circuit descriptor code (CDC) defining the circuit.</param>
        /// <param name="initialParameters">The initial parameters.</param>
        /// <param name="fitOptions">The fit options.</param>
        /// <param name="fitProgress">The fit progress.</param>
        /// <returns></returns>
        /// <exception cref="Exception">
        /// Wait untill SimpleCurve is finished before detecting peaks
        /// or
        /// No impedimetric readings available in parent SimpleMeasurement
        /// </exception>
        /// <exception cref="ArgumentNullException">The circuit descriptor code (cdc) must be specified</exception>
        /// <exception cref="ArgumentException">
        /// Invalid circuit descriptor code (cdc)
        /// or
        /// The amount of parameters in the model does not match the number of parameters specified in the initial parameter array
        /// </exception>
        public async Task<FitResult> FitEquivalentCircuit(string cdc, double[] initialParameters = null, FitOptionsCircuit fitOptions = null, FitProgress fitProgress = null)
        {
            if (!IsFinished)
                throw new Exception("Wait untill SimpleCurve is finished before fitting equivalent circuits");
            if(_simpleMeasurement.Measurement.nEISdata == 0)
                throw new Exception("No impedimetric readings available in parent SimpleMeasurement");
            if (string.IsNullOrEmpty(cdc))
                throw new ArgumentNullException("The circuit descriptor code (cdc) must be specified");

            CircuitModel circuitModel = new CircuitModel();
            circuitModel.SetEISdata(_simpleMeasurement.Measurement.EISdata[0]); //Sets reference to measured data
            try
            {
                circuitModel.SetCircuit(cdc); //Sets the circuit defined in the CDC code string, in this case a Randles circuit 
            }
            catch
            {
                throw new ArgumentException("Invalid circuit descriptor code (cdc)");
            }

            if (initialParameters != null)
            {
                if (circuitModel.InitialParameters.Count != initialParameters.Length)
                    throw new ArgumentException("The amount of parameters in the model does not match the number of parameters specified in the initial parameter array");
                circuitModel.SetInitialParameters(initialParameters);
            }

            return await FitEquivalentCircuit(circuitModel, fitOptions, fitProgress);
        }

        /// <summary>
        /// Fits the equivalent circuit.
        /// </summary>
        /// <param name="circuitModel">The circuit model.</param>
        /// <param name="fitOptions">The fit options.</param>
        /// <param name="fitProgress">The fit progress.</param>
        /// <returns></returns>
        /// <exception cref="Exception">
        /// Wait untill SimpleCurve is finished before detecting peaks
        /// or
        /// No impedimetric readings available in parent SimpleMeasurement
        /// or
        /// The circuit model must be defined
        /// </exception>
        public async Task<FitResult> FitEquivalentCircuit(CircuitModel circuitModel, FitOptionsCircuit fitOptions = null, FitProgress fitProgress = null)
        {
            if (!IsFinished)
                throw new Exception("Wait untill SimpleCurve is finished before detecting peaks");
            if (_simpleMeasurement.Measurement.nEISdata == 0)
                throw new Exception("No impedimetric readings available in parent SimpleMeasurement");
            if (circuitModel == null)
                throw new Exception("The circuit model must be defined");

            if (fitOptions == null)
            {
                fitOptions = new FitOptionsCircuit();
                fitOptions.Model = circuitModel;
                fitOptions.RawData = _simpleMeasurement.Measurement.EISdata[0];
            }

            FitAlgorithm fit = FitAlgorithm.FromAlgorithm(fitOptions);
            return await fit.ApplyFitCircuitAsync(fitProgress);
        }

        /// <summary>
        /// Clears the peaks.
        /// </summary>
        /// <exception cref="System.Exception">Wait untill SimpleCurve is finished before detecting peaks</exception>
        public void ClearPeaks()
        {
            if (!IsFinished)
                throw new Exception("Wait untill SimpleCurve is finished before detecting peaks");
            Curve.ClearPeaks();
            OnDetectedPeaks();
        }

        /// <summary>
        /// Smoothes the data on the Y-axis with the Savitzky-Golay filter.
        /// Smooth levels are: spike rejection = 0, low = 1, medium = 2, high = 3, very high = 4.
        /// </summary>
        /// <param name="smoothLevel">The smooth level.</param>
        /// <returns>A smoothed copy of this SimpleCurve</returns>
        /// <exception cref="System.Exception">Wait untill SimpleCurve is finished before smoothing</exception>
        public SimpleCurve Smooth(SmoothLevel smoothLevel)
        {
            if (!IsFinished)
                throw new Exception("Wait untill SimpleCurve is finished before smoothing");

            Curve smoothedCurve = new Curve(Curve, true);
            smoothedCurve.Smooth((int)smoothLevel);
            smoothedCurve.Title = $"{Curve.Title}, smooth level {smoothLevel}";
            return new SimpleCurve(smoothedCurve, _simpleMeasurement);
        }

        /// <summary>
        /// Smoothes the data on the Y-axis with the Savitzky-Golay filter.
        /// </summary>
        /// <param name="smoothLevel">The window size for filtering.</param>
        /// <returns>A smoothed copy of this SimpleCurve</returns>
        /// <exception cref="System.Exception">Wait untill SimpleCurve is finished before smoothing</exception>
        public SimpleCurve Smooth(int windowSize)
        {
            if (!IsFinished)
                throw new Exception("Wait untill SimpleCurve is finished before smoothing");

            Curve smoothedCurve = new Curve(Curve, true);
            smoothedCurve.SavitskyGolay(windowSize);
            smoothedCurve.Title = $"{Curve.Title}, smooth window {windowSize}";
            return new SimpleCurve(smoothedCurve, _simpleMeasurement);
        }

        /// <summary>
        /// Differentiates this SimpleCurve.
        /// </summary>
        /// <returns>A new SimpleCurve with the result</returns>
        /// <exception cref="System.Exception">
        /// Wait untill SimpleCurve is finished before differntiating
        /// or
        /// At least two datapoints are required for differentiation
        /// </exception>
        public SimpleCurve Differentiate()
        {
            if (!IsFinished)
                throw new Exception("Wait untill SimpleCurve is finished before differntiating");
            if (NDataPoints < 2)
                throw new Exception("At least two datapoints are required for differentiation");

            //Create a copy of the Y Axis data to prevent the raw measurement data from being overwritten
            DataArray diffArray = Curve.YAxisDataArray.Clone(true);
            
            //Forward derivative of first point
            diffArray[0].Value = 
                (Curve.YAxisDataArray[1].Value - Curve.YAxisDataArray[0].Value) / 
                (Curve.XAxisDataArray[1].Value - Curve.XAxisDataArray[0].Value);
            //Backward derivative of last point
            diffArray[NDataPoints - 1].Value = 
                (Curve.YAxisDataArray[NDataPoints - 1].Value - Curve.YAxisDataArray[NDataPoints - 2].Value) / 
                (Curve.XAxisDataArray[NDataPoints - 1].Value - Curve.XAxisDataArray[NDataPoints - 2].Value);
            //Centered derivative of interior points
            for (int i = 1; i < NDataPoints - 1; i++)
            {
                diffArray[i].Value = 
                    (Curve.YAxisDataArray[i + 1].Value - Curve.YAxisDataArray[i - 1].Value) / 
                    (Curve.XAxisDataArray[i + 1].Value - Curve.XAxisDataArray[i - 1].Value);
            }
            Curve differentiatedCurve = new Curve(Curve.XAxisDataArray, diffArray, $"{Title}, d{YUnit}/d{XUnit}");
            differentiatedCurve.Finish();
            return new SimpleCurve(differentiatedCurve, _simpleMeasurement);
        }

        /// <summary>
        /// Converts this SimpleCurve to 10 base logarithm.
        /// </summary>
        /// <returns>A new SimpleCurve with the result</returns>
        /// <exception cref="System.Exception">Wait untill SimpleCurve is finished before converting it to the 10 base logarithm</exception>
        public SimpleCurve Log10()
        {
            if (!IsFinished)
                throw new Exception("Wait untill SimpleCurve is finished before converting it to the 10 base logarithm");

            //Create a copy of the Y Axis data to prevent the raw measurement data from being overwritten
            DataArray log10Array = Curve.YAxisDataArray.Clone(true);
            for (int i = 0; i < NDataPoints; i++)
                log10Array[i].Value = Math.Log10(Math.Abs(log10Array[i].Value));
            Curve log10Curve = new Curve(Curve.XAxisDataArray, log10Array, $"{Title}, Log10");
            log10Curve.Finish();
            return new SimpleCurve(log10Curve, _simpleMeasurement);
        }

        /// <summary>
        /// Exponentiates this SimpleCurve to the specified power.
        /// </summary>
        /// <param name="power">The power.</param>
        /// <returns>A new SimpleCurve with the result</returns>
        /// <exception cref="System.Exception">Wait untill SimpleCurve is finished before exponentiating</exception>
        public SimpleCurve Exponentiate(double power)
        {
            if (!IsFinished)
                throw new Exception("Wait untill SimpleCurve is finished before exponentiating");

            //Create a copy of the Y Axis data to prevent the raw measurement data from being overwritten
            DataArray expArray = Curve.YAxisDataArray.Clone(true);
            for (int i = 0; i < NDataPoints; i++)
                expArray[i].Value = Math.Pow(expArray[i].Value, power);
            Curve expCurve = new Curve(Curve.XAxisDataArray, expArray, $"{Title}, ^ {power}");
            expCurve.Finish();
            return new SimpleCurve(expCurve, _simpleMeasurement);
        }

        /// <summary>
        /// Adds the specified value to this SimpleCurve.
        /// </summary>
        /// <param name="add">The value to add.</param>
        /// <returns>A new SimpleCurve with the result</returns>
        /// <exception cref="System.Exception">Wait untill SimpleCurve is finished before exponentiating</exception>
        public SimpleCurve Add(double add)
        {
            if (!IsFinished)
                throw new Exception("Wait untill SimpleCurve is finished before adding");

            //Create a copy of the Y Axis data to prevent the raw measurement data from being overwritten
            DataArray newArray = Curve.YAxisDataArray.Clone(true);
            for (int i = 0; i < NDataPoints; i++)
                newArray[i].Value += add;
            Curve newCurve = new Curve(Curve.XAxisDataArray, newArray, $"{Title}, + {add}");
            newCurve.Finish();
            return new SimpleCurve(newCurve, _simpleMeasurement);
        }

        /// <summary>
        /// Adds the specified SimpleCurve to this SimpleCurve.
        /// </summary>
        /// <param name="add">The SimpleCurve to add.</param>
        /// <returns>A new SimpleCurve with the result</returns>
        /// <exception cref="System.Exception">
        /// Wait untill SimpleCurves are finished before adding
        /// or
        /// SimpleCurves must have the same number of data points
        /// </exception>
        public SimpleCurve Add(SimpleCurve add)
        {
            if (!IsFinished && !add.IsFinished)
                throw new Exception("Wait untill SimpleCurves are finished before adding");
            if (NDataPoints != add.NDataPoints)
                throw new Exception("SimpleCurves must have the same number of data points");

            return Add(add, 0, NDataPoints);
        }

        /// <summary>
        /// Adds the specified SimpleCurve to this SimpleCurve starting from a specified index.
        /// </summary>
        /// <param name="add">The SimpleCurve to add.</param>
        /// <param name="from">The index to start adding from.</param>
        /// <returns>A new SimpleCurve with the result</returns>
        /// <exception cref="System.Exception">
        /// Wait untill SimpleCurves are finished before adding
        /// or
        /// The index to start adding from exceeds the bounds of the SimpleCurves
        /// </exception>
        public SimpleCurve Add(SimpleCurve add, int from)
        {
            if (!IsFinished && !add.IsFinished)
                throw new Exception("Wait untill SimpleCurves are finished before adding");
            if ((from > NDataPoints || from > add.NDataPoints) && from >= 0)
                throw new Exception("The index to start adding from exceeds the bounds of the SimpleCurves");

            int count = (NDataPoints > add.NDataPoints) ? add.NDataPoints - from : NDataPoints - from;
            return Add(add, from, count);
        }

        /// <summary>
        /// Adds the specified SimpleCurve to this SimpleCurve over a specified range.
        /// </summary>
        /// <param name="add">The SimpleCurve to add.</param>
        /// <param name="from">The index to start adding from.</param>
        /// <param name="count">The number of datapoints in the range.</param>
        /// <returns>A new SimpleCurve with the result</returns>
        /// <exception cref="System.Exception">
        /// Wait untill SimpleCurves are finished before adding
        /// or
        /// The range to add exceeds the bounds of the SimpleCurves
        /// </exception>
        public SimpleCurve Add(SimpleCurve add, int from, int count)
        {
            if (!IsFinished && !add.IsFinished)
                throw new Exception("Wait untill SimpleCurves are finished before adding");
            if ((from + count > NDataPoints || from + count > add.NDataPoints) && from >= 0)
                throw new Exception("The range to add exceeds the bounds of the SimpleCurves");

            //Create a copy of the Y Axis data to prevent the raw measurement data from being overwritten
            DataArray newArray = Curve.YAxisDataArray.Clone(true);
            for (int i = from; i < from + count; i++)
                newArray[i].Value += add.Curve.YAxisDataArray[i].Value;
            Curve newCurve = new Curve(Curve.XAxisDataArray, newArray, $"{Title}, + {add.Title}");
            newCurve.Finish();
            return new SimpleCurve(newCurve, _simpleMeasurement);
        }

        /// <summary>
        /// Subtracts the specified value from this SimpleCurve.
        /// </summary>
        /// <param name="subtract">The value to subtract.</param>
        /// <returns>A new SimpleCurve with the result</returns>
        /// <exception cref="System.Exception">Wait untill SimpleCurve is finished before subtracting</exception>
        public SimpleCurve Subtract(double subtract)
        {
            if (!IsFinished)
                throw new Exception("Wait untill SimpleCurve is finished before subtracting");

            //Create a copy of the Y Axis data to prevent the raw measurement data from being overwritten
            DataArray newArray = Curve.YAxisDataArray.Clone(true);
            for (int i = 0; i < NDataPoints; i++)
                newArray[i].Value += subtract;
            Curve newCurve = new Curve(Curve.XAxisDataArray, newArray, $"{Title}, - {subtract}");
            newCurve.Finish();
            return new SimpleCurve(newCurve, _simpleMeasurement);
        }

        /// <summary>
        /// Subtracts the specified SimpleCurve to this SimpleCurve.
        /// </summary>
        /// <param name="subtract">The SimpleCurve to subtract.</param>
        /// <returns>
        /// A new SimpleCurve with the result
        /// </returns>
        /// <exception cref="System.Exception">
        /// Wait untill SimpleCurves are finished before subtracting
        /// or
        /// SimpleCurves must have the same number of data points
        /// </exception>
        public SimpleCurve Subtract(SimpleCurve subtract)
        {
            if (!IsFinished && !subtract.IsFinished)
                throw new Exception("Wait untill SimpleCurves are finished before subtracting");
            if (NDataPoints != subtract.NDataPoints)
                throw new Exception("SimpleCurves must have the same number of data points");

            return Subtract(subtract, 0, NDataPoints);
        }

        /// <summary>
        /// Subtracts the specified SimpleCurve from this SimpleCurve starting from a specified index.
        /// </summary>
        /// <param name="subtract">The SimpleCurve to subtract.</param>
        /// <param name="from">The index to start subtracting from.</param>
        /// <returns>
        /// A new SimpleCurve with the result
        /// </returns>
        /// <exception cref="System.Exception">
        /// Wait untill SimpleCurves are finished before subtracting
        /// or
        /// The index to start adding from exceeds the bounds of the SimpleCurves
        /// </exception>
        public SimpleCurve Subtract(SimpleCurve subtract, int from)
        {
            if (!IsFinished && !subtract.IsFinished)
                throw new Exception("Wait untill SimpleCurves are finished before subtracting");
            if ((from > NDataPoints || from > subtract.NDataPoints) && from > 0)
                throw new Exception("The index to start adding from exceeds the bounds of the SimpleCurves");

            int count = (NDataPoints > subtract.NDataPoints) ? subtract.NDataPoints - from : NDataPoints - from;
            return Subtract(subtract, from, count);
        }

        /// <summary>
        /// Subtracts the specified SimpleCurve from this SimpleCurve over a specified range.
        /// </summary>
        /// <param name="subtract">The SimpleCurve to subtract.</param>
        /// <param name="from">The index to start subtracting from.</param>
        /// <param name="count">The number of datapoints in the range.</param>
        /// <returns>
        /// A new SimpleCurve with the result
        /// </returns>
        /// <exception cref="System.Exception">
        /// Wait untill SimpleCurves are finished before subtracting
        /// or
        /// The range to add exceeds the bounds of the SimpleCurves
        /// </exception>
        public SimpleCurve Subtract(SimpleCurve subtract, int from, int count)
        {
            if (!IsFinished && !subtract.IsFinished)
                throw new Exception("Wait untill SimpleCurves are finished before subtracting");
            if ((from + count > NDataPoints || from + count > subtract.NDataPoints) && from >= 0)
                throw new Exception("The range to add exceeds the bounds of the SimpleCurves");

            //Create a copy of the Y Axis data to prevent the raw measurement data from being overwritten
            DataArray newArray = Curve.YAxisDataArray.Clone(true);
            for (int i = from; i < from + count; i++)
                newArray[i].Value -= subtract.Curve.YAxisDataArray[i].Value;
            Curve newCurve = new Curve(Curve.XAxisDataArray, newArray, $"{Title}, - {subtract.Title}");
            newCurve.Finish();
            return new SimpleCurve(newCurve, _simpleMeasurement);
        }

        /// <summary>
        /// Multiplies this SimpleCurve by the specified value.
        /// </summary>
        /// <param name="multiply">The value to multiply by.</param>
        /// <returns>
        /// A new SimpleCurve with the result
        /// </returns>
        /// <exception cref="System.Exception">Wait untill SimpleCurve is finished before multiplying</exception>
        public SimpleCurve Multiply(double multiply)
        {
            if (!IsFinished)
                throw new Exception("Wait untill SimpleCurve is finished before multiplying");

            //Create a copy of the Y Axis data to prevent the raw measurement data from being overwritten
            DataArray newArray = Curve.YAxisDataArray.Clone(true);
            for (int i = 0; i < NDataPoints; i++)
                newArray[i].Value *= multiply;
            Curve newCurve = new Curve(Curve.XAxisDataArray, newArray, $"{Title}, * {multiply}");
            return new SimpleCurve(newCurve, _simpleMeasurement);
        }

        /// <summary>
        /// Multiplies the specified SimpleCurve with this SimpleCurve.
        /// </summary>
        /// <param name="multiply">The SimpleCurve to multiply by.</param>
        /// <returns>
        /// A new SimpleCurve with the result
        /// </returns>
        /// <exception cref="System.Exception">
        /// Wait untill SimpleCurves are finished before multiplying
        /// or
        /// SimpleCurves must have the same number of data points
        /// </exception>
        public SimpleCurve Multiply(SimpleCurve multiply)
        {
            if (!IsFinished && !multiply.IsFinished)
                throw new Exception("Wait untill SimpleCurves are finished before multiplying");
            if (NDataPoints != multiply.NDataPoints)
                throw new Exception("SimpleCurves must have the same number of data points");

            return Multiply(multiply, 0, NDataPoints);
        }

        /// <summary>
        /// Multiplies the specified SimpleCurve with this SimpleCurve starting from a specified index.
        /// </summary>
        /// <param name="multiply">The multiply.</param>
        /// <param name="from">The index to start multiplying by.</param>
        /// <returns>
        /// A new SimpleCurve with the result
        /// </returns>
        /// <exception cref="System.Exception">
        /// Wait untill SimpleCurves are finished before multiplying
        /// or
        /// The index to start adding from exceeds the bounds of the SimpleCurves
        /// </exception>
        public SimpleCurve Multiply(SimpleCurve multiply, int from)
        {
            if (!IsFinished && !multiply.IsFinished)
                throw new Exception("Wait untill SimpleCurves are finished before multiplying");
            if ((from > NDataPoints || from > multiply.NDataPoints) && from >= 0)
                throw new Exception("The index to start adding from exceeds the bounds of the SimpleCurves");

            int count = (NDataPoints > multiply.NDataPoints) ? multiply.NDataPoints - from : NDataPoints - from;
            return Multiply(multiply, from, count);
        }

        /// <summary>
        /// Multiplies the specified SimpleCurve with this SimpleCurve over a specified range.
        /// </summary>
        /// <param name="multiply">The multiply.</param>
        /// <param name="from">The index to start multiplying by.</param>
        /// <returns>
        /// <param name="count">The number of datapoints in the range.</param>
        /// <returns>
        /// A new SimpleCurve with the result
        /// </returns>
        /// <exception cref="System.Exception">
        /// Wait untill SimpleCurves are finished before multiplying
        /// or
        /// The range to add exceeds the bounds of the SimpleCurves
        /// </exception>
        public SimpleCurve Multiply(SimpleCurve multiply, int from, int count)
        {
            if (!IsFinished && !multiply.IsFinished)
                throw new Exception("Wait untill SimpleCurves are finished before multiplying");
            if ((from + count > NDataPoints || from + count > multiply.NDataPoints) && from >= 0)
                throw new Exception("The range to add exceeds the bounds of the SimpleCurves");

            //Create a copy of the Y Axis data to prevent the raw measurement data from being overwritten
            DataArray newArray = Curve.YAxisDataArray.Clone(true);
            for (int i = from; i < from + count; i++)
                newArray[i].Value *= multiply.Curve.YAxisDataArray[i].Value;
            Curve newCurve = new Curve(Curve.XAxisDataArray, newArray, $"{Title}, * {multiply.Title}");
            newCurve.Finish();
            return new SimpleCurve(newCurve, _simpleMeasurement);
        }

        /// <summary>
        /// Determines the moving average baseline of this SimpleCurve.
        /// </summary>
        /// <param name="windowSize">Number of data points in the averaging window.</param>
        /// <param name="maxSweeps">The maximum sweeps.</param>
        /// <returns>
        /// A new SimpleCurve with the result
        /// </returns>
        /// <exception cref="System.Exception">
        /// Wait untill SimpleCurve is finished before determining its moving average baseline
        /// or
        /// The PalmSens SDK does not support determing the moving average baseline for Cyclic Voltammetry, Impedance and Mixed Mode measurements
        /// </exception>
        public SimpleCurve MovingAverageBaseline(int windowSize = 2, int maxSweeps = 1000)
        {
            if (!IsFinished)
                throw new Exception("Wait untill SimpleCurve is finished before determining its moving average baseline");
            if (_simpleMeasurement.MeasurementType == MeasurementTypes.CyclicVoltammetry || _simpleMeasurement.MeasurementType == MeasurementTypes.ImpedanceSpectroscopy || _simpleMeasurement.MeasurementType == MeasurementTypes.MixedMode)
                throw new Exception("The PalmSens SDK does not support determing the moving average baseline for Cyclic Voltammetry, Impedance and Mixed Mode measurements");

            Curve baseline = PalmSens.Analysis.BaselineCorrection.GetMovingAverageBaselineCorrected(Curve, windowSize, maxSweeps, true);
            baseline.Title = $"{Title}, moving average baseline";
            baseline.Finish();
            return new SimpleCurve(baseline, _simpleMeasurement);
        }

        /// <summary>
        /// The average of this SimpleCurve.
        /// </summary>
        /// <returns>The average value on the Y axis</returns>
        /// <exception cref="System.Exception">Wait untill SimpleCurve is finished before determining its average</exception>
        public double Average()
        {
            if (!IsFinished)
                throw new Exception("Wait untill SimpleCurve is finished before determining its average");

            double sum = Sum();
            return sum / NDataPoints;
        }

        /// <summary>
        /// The sum of this SimpleCurve.
        /// </summary>
        /// <returns>The sum of the values on the Y axis</returns>
        /// <exception cref="System.Exception">Wait untill SimpleCurve is finished before determining its sum</exception>
        public double Sum()
        {
            if (!IsFinished)
                throw new Exception("Wait untill SimpleCurve is finished before determining its sum");

            double sum = 0;
            for (int i = 0; i < NDataPoints; i++)
                sum += Curve.YAxisDataArray[i].Value;
            return sum;
        }

        /// <summary>
        /// The minimum of this SimpleCurve.
        /// </summary>
        /// <returns>The minimum value on the Y axis</returns>
        /// <exception cref="System.Exception">Wait untill SimpleCurve is finished before determining its minimum</exception>
        public double Minimum()
        {
            if (!IsFinished)
                throw new Exception("Wait untill SimpleCurve is finished before determining its minimum");
            return YAxisValues.Min();
        }

        /// <summary>
        /// The maximum of this SimpleCurve.
        /// </summary>
        /// <returns>The maximum value on the Y axis</returns>
        /// <exception cref="System.Exception">Wait untill SimpleCurve is finished before determining its maximum</exception>
        public double Maximum()
        {
            if (!IsFinished)
                throw new Exception("Wait untill SimpleCurve is finished before determining its maximum");
            return YAxisValues.Max();
        }

        /// <summary>
        /// Integrates this SimpleCurve.
        /// </summary>
        /// <returns>
        /// A new SimpleCurve with the result
        /// </returns>
        /// <exception cref="System.Exception">Wait untill SimpleCurve is finished before integration</exception>
        public double Integrate()
        {
            if (!IsFinished)
                throw new Exception("Wait untill SimpleCurve is finished before integration");
            return Integrate(0, NDataPoints);
        }

        /// <summary>
        /// Integrates this SimpleCurve from a specified index.
        /// </summary>
        /// <param name="from">The index to start integrating from.</param>
        /// <returns>
        /// A new SimpleCurve with the result
        /// </returns>
        /// <exception cref="System.Exception">
        /// Wait untill SimpleCurve is finished before integration
        /// or
        /// The index to start adding from exceeds the bounds of the SimpleCurve
        /// </exception>
        public double Integrate(int from)
        {
            if (!IsFinished)
                throw new Exception("Wait untill SimpleCurve is finished before integration");
            if (from > NDataPoints && from >= 0)
                throw new Exception("The index to start adding from exceeds the bounds of the SimpleCurve");
            return Integrate(from, NDataPoints - 1 - from);
        }

        /// <summary>
        /// Integrates this SimpleCurve over a specified range
        /// </summary>
        /// <param name="from">The index to start integrating from.</param>
        /// <param name="count">The number of datapoints in the range.</param>
        /// <returns>
        /// A new SimpleCurve with the result
        /// </returns>
        /// <exception cref="System.Exception">
        /// Wait untill SimpleCurve is finished before integration
        /// or
        /// The range to add exceeds the bounds of the SimpleCurve
        /// </exception>
        public double Integrate(int from, int count)
        {
            if (!IsFinished)
                throw new Exception("Wait untill SimpleCurve is finished before integration");
            if (from + count > NDataPoints && from >= 0)
                throw new Exception("The range to add exceeds the bounds of the SimpleCurve");

            double area = 0;
            for (int i = from + 1; i <= from + count; i++)
                area += ((Curve.YAxisDataArray[i - 1].Value + Curve.YAxisDataArray[i].Value) / 2) * (Curve.XAxisDataArray[i].Value - Curve.XAxisDataArray[i - 1].Value);
            return area;
        }
        #endregion

        #region Events
        /// <summary>
        /// Occurs when the SimpleCurve is [finished] measuring.
        /// </summary>
        public event EventHandler CurveFinished;

        /// <summary>
        /// Handles the Finished event of the Curve.
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="EventArgs"/> instance containing the event data.</param>
        private void Curve_Finished(object sender, EventArgs e)
        {
            Curve.NewDataAdded -= Curve_NewDataAdded;
            Curve.Finished -= Curve_Finished;
            CurveFinished?.Invoke(this, EventArgs.Empty);
        }

        /// <summary>
        /// Occurs when a [property changed].
        /// </summary>
        public event PropertyChangedEventHandler PropertyChanged;

        /// <summary>
        /// Called when a [property changed].
        /// </summary>
        /// <param name="propertyName">Name of the property.</param>
        private void OnPropertyChanged(string propertyName)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }

        /// <summary>
        /// Occurs when [new data is added] to the SimpleCurve.
        /// </summary>
        public event Curve.NewDataAddedEventHandler NewDataAdded;

        /// <summary>
        /// Raises the <see cref="E:NewDataAdded" /> event.
        /// </summary>
        /// <param name="e">The <see cref="PalmSens.Data.ArrayDataAddedEventArgs"/> instance containing the event data.</param>
        private void OnNewDataAdded(PalmSens.Data.ArrayDataAddedEventArgs e)
        {
            NewDataAdded?.Invoke(this, e);
        }

        /// <summary>
        /// Handles the NewDataAdded event of the Curve control.
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="ArrayDataAddedEventArgs"/> instance containing the event data.</param>
        /// <exception cref="System.NotImplementedException"></exception>
        private void Curve_NewDataAdded(object sender, ArrayDataAddedEventArgs e)
        {
            OnNewDataAdded(e);
        }

        /// <summary>
        /// Occurs when SimpleCurve [detected peaks].
        /// </summary>
        public event EventHandler DetectedPeaks;

        /// <summary>
        /// Called when [detected peaks].
        /// </summary>
        private void OnDetectedPeaks()
        {
            DetectedPeaks?.Invoke(this, EventArgs.Empty);
        }
        #endregion

        /// <summary>
        /// Performs application-defined tasks associated with freeing, releasing, or resetting unmanaged resources.
        /// </summary>
        public void Dispose()
        {
            Curve.NewDataAdded -= Curve_NewDataAdded;
            Curve.Finished -= Curve_Finished;
            Curve.Dispose();
        }
    }
}
