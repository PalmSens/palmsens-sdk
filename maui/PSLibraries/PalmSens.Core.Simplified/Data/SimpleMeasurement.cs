using PalmSens.Data;
using PalmSens.Plottables;
using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PalmSens.Core.Simplified.Data
{
    public class SimpleMeasurement: IDisposable
    {
        /// <summary>
        /// Initializes a new instance of the <see cref="SimpleMeasurement" /> class.
        /// </summary>
        /// <param name="measurement">The Measurement.</param>
        /// <exception cref="System.ArgumentNullException">Cannot create an instance of simple measurement when measurement is null</exception>
        public SimpleMeasurement(Measurement measurement)
        {
            if (measurement == null || measurement.Method == null)
                throw new ArgumentNullException("Cannot create an instance of SimpleMeasurement when the specified Measurement or its Method is null");
            Measurement = measurement;

            if (!Measurement.DataSet.IsFinished)
            {
                Measurement.EndMeasurement += Measurement_EndMeasurement;
                Measurement.EndMeasurementAsync += Measurement_EndMeasurementAsync;
            }

            MeasurementType = GetTypeFromMethod(Measurement.Method); //Determine the type of measurement
            InitSimpleCurveCollection();
        }

        #region Properties
        /// <summary>
        /// Gets or sets the title of the measurement.
        /// </summary>
        /// <value>
        /// The title.
        /// </value>
        public string Title
        {
            get { return Measurement.Title; }
            set { Measurement.Title = value; }
        }

        /// <summary>
        /// The original measurement
        /// </summary>
        public Measurement Measurement;

        /// <summary>
        /// Gets the type of measurement.
        /// </summary>
        /// <value>
        /// The type of measurement.
        /// </value>
        public MeasurementTypes MeasurementType { get; private set; }

        /// <summary>
        /// Gets the Method defining the measurement's parameters.
        /// </summary>
        /// <value>
        /// The method.
        /// </value>
        public Method Method => Measurement?.Method;

        /// <summary>
        /// Gets the collection of SimpleCurves stored in the measurement.
        /// </summary>
        /// <value>
        /// The simple curve collection.
        /// </value>
        public List<SimpleCurve> SimpleCurveCollection { get; private set; }

        /// <summary>
        /// List of the available data types in the measurement
        /// </summary>
        public List<DataArrayType> AvailableDataTypes
        {
            get
            {
                List<DataArrayType> availableDataTypes = new List<DataArrayType>();
                DataArray[] dataArrays = Measurement.DataSet.GetDataArrays();
                foreach (DataArray array in dataArrays)
                    availableDataTypes.Add((DataArrayType)array.ArrayType);
                return availableDataTypes;
            }
        }

        /// <summary>
        /// Gets the channel that the measurement was measured on.
        /// </summary>
        /// <value>
        /// The channel.
        /// </value>
        public int Channel { get { return Measurement.Channel; } internal set { Measurement.Channel = value; } }
        #endregion

        #region Functions
        /// <summary>
        /// Gets the type of measurement from the method.
        /// </summary>
        /// <param name="method">The measurements method.</param>
        /// <returns></returns>
        private MeasurementTypes GetTypeFromMethod(Method method)
        {
            if (method is PalmSens.Techniques.LinearSweep)
                return MeasurementTypes.LinearSweepVoltammetry;
            else if (method is PalmSens.Techniques.CyclicVoltammetry)
                return MeasurementTypes.CyclicVoltammetry;
            else if (method is PalmSens.Techniques.ACVoltammetry)
                return MeasurementTypes.ACVoltammetry;
            else if (method is PalmSens.Techniques.DifferentialPulse)
                return MeasurementTypes.DifferentialPulseVoltammetry;
            else if (method is PalmSens.Techniques.SquareWave)
                return MeasurementTypes.SquareWaveVoltammetry;
            else if (method is PalmSens.Techniques.NormalPulse)
                return MeasurementTypes.NormalPulseVoltammetry;
            else if (method is PalmSens.Techniques.AmperometricDetection)
                return MeasurementTypes.ChronoAmperometry;
            else if (method is PalmSens.Techniques.MultistepAmperometry)
                return MeasurementTypes.MultiStepAmperometry;
            else if (method is PalmSens.Techniques.FastAmperometry)
                return MeasurementTypes.FastAmperometry;
            else if (method is PalmSens.Techniques.PulsedAmpDetection)
                return MeasurementTypes.PulsedAmperometricDetection;
            else if (method is PalmSens.Techniques.MultiplePulseAmperometry)
                return MeasurementTypes.MultiplePulseAmperometry;
            else if (method is PalmSens.Techniques.OpenCircuitPotentiometry)
                return MeasurementTypes.OpenCircuitPotentiometry;
            else if (method is PalmSens.Techniques.Potentiometry)
                return MeasurementTypes.ChronoPotentiometry;
            else if (method is PalmSens.Techniques.MultistepPotentiometry)
                return MeasurementTypes.MultiStepPotentiometry;
            else if (method is PalmSens.Techniques.ChronoPotStripping)
                return MeasurementTypes.ChronoPotentiometricStripping;
            else if (method is PalmSens.Techniques.ImpedimetricMethod)
                return MeasurementTypes.ImpedanceSpectroscopy;
            else if (method is PalmSens.Techniques.MixedMode)
                return MeasurementTypes.MixedMode;
            else return MeasurementTypes.NotSpecified;
        }

        /// <summary>
        /// Gets the raw data of the specified type from this measurement.
        /// </summary>
        /// <param name="arrayType">The data type of the array.</param>
        /// <returns></returns>
        /// <exception cref="System.ArgumentException">This SimpleMeasurement does not contain data of the specified array type</exception>
        public double[] GetRawData(DataArrayType arrayType)
        {
            if (!AvailableDataTypes.Contains(arrayType))
                throw new ArgumentException("This SimpleMeasurement does not contain data of the specified array type");

            DataArray[] dataArrays = Measurement.DataSet.GetDataArrays().Where(a => a.ArrayType == (int)arrayType).ToArray();

            return dataArrays[0].GetValues();
        }

        /// <summary>
        /// Handles the EndMeasurement event of the Measurement class.
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="EventArgs"/> instance containing the event data.</param>
        /// <exception cref="NotImplementedException"></exception>
        private void Measurement_EndMeasurement(object sender, EventArgs e)
        {
            OnMeasurementEnded();
        }

        /// <summary>
        /// Handles the EndMeasurementAsync event of the Measurement class.
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="EventArgs"/> instance containing the event data.</param>
        private Task Measurement_EndMeasurementAsync(object sender, EventArgs e)
        {
            OnMeasurementEnded();
            return Task.CompletedTask;
        }

        #region Curve functions
        /// <summary>
        /// Initializes the simple curve collection.
        /// </summary>
        private void InitSimpleCurveCollection()
        {
            SimpleCurveCollection = new List<SimpleCurve>();
            foreach (Curve c in Measurement.GetCurveArray())
                AddSimpleCurve(new SimpleCurve(c, this), true);
        }

        /// <summary>
        /// Determines whether this SimpleMeasurement contains [the specified simple curve].
        /// </summary>
        /// <param name="simpleCurve">The simple curve.</param>
        /// <returns>
        ///   <c>true</c> if the measurement contains [the specified simple curve]; otherwise, <c>false</c>.
        /// </returns>
        public bool ContainsSimpleCurve(SimpleCurve simpleCurve)
        {
            return SimpleCurveCollection.Contains(simpleCurve);
        }

        /// <summary>
        /// Add a new SimpleCurve to the measurement with the specified X and Y-Axis data types.
        /// </summary>
        /// <param name="xAxisArrayType">Data type of the x axis.</param>
        /// <param name="yAxisArrayType">Data type of the y axis.</param>
        /// <param name="title">The title of the SimpleCurve.</param>
        /// <param name="silent">if set to <c>true</c> [silent] the SimpleCurveAdded even is not raised.</param>
        /// <returns></returns>
        /// <exception cref="System.ArgumentException">
        /// This SimpleMeasurement does not contain the specified X-Axis array type
        /// or
        /// This SimpleMeasurement does not contain the specified Y-Axis array type
        /// </exception>
        public List<SimpleCurve> NewSimpleCurve(DataArrayType xAxisArrayType, DataArrayType yAxisArrayType, string title = "", bool silent = false)
        {
            if (!AvailableDataTypes.Contains(xAxisArrayType))
                throw new ArgumentException("This SimpleMeasurement does not contain the specified X-Axis array type");
            if (!AvailableDataTypes.Contains(yAxisArrayType))
                throw new ArgumentException("This SimpleMeasurement does not contain the specified Y-Axis array type");

            List<SimpleCurve> simpleCurves = new List<SimpleCurve>();
            DataArray[] xDataArrays = Measurement.DataSet.GetDataArrays().Where(a => a.ArrayType == (int)xAxisArrayType).ToArray();
            DataArray[] yDataArrays = Measurement.DataSet.GetDataArrays().Where(a => a.ArrayType == (int)yAxisArrayType).ToArray();

            if (xDataArrays.Length > 1 && xDataArrays.Length == yDataArrays.Length)
            {
                for (int i = 0; i < xDataArrays.Length; i++)
                {
                    Curve c = new Curve(xDataArrays[i], yDataArrays[i], $"{xDataArrays[i].Description}:{title}", Measurement.DataSet.IsFinished);
                    if (Measurement.DataSet.IsFinished)
                        c.Finish();
                    simpleCurves.Add(new SimpleCurve(c, this));
                }
            }
            else if (xDataArrays.Length > 1 && yDataArrays.Length == 1)
            {
                for (int i = 0; i < xDataArrays.Length; i++)
                {
                    Curve c = new Curve(xDataArrays[i], yDataArrays[0], $"{xDataArrays[i].Description}:{title}", Measurement.DataSet.IsFinished);
                    if (Measurement.DataSet.IsFinished)
                        c.Finish();
                    simpleCurves.Add(new SimpleCurve(c, this));
                }
            }
            else if (yDataArrays.Length > 1 && xDataArrays.Length == 1)
            {
                for (int i = 0; i < yDataArrays.Length; i++)
                {
                    Curve c = new Curve(xDataArrays[0], yDataArrays[i], $"{yDataArrays[i].Description}:{title}", Measurement.DataSet.IsFinished);
                    if (Measurement.DataSet.IsFinished)
                        c.Finish();
                    simpleCurves.Add(new SimpleCurve(c, this));
                }
            }
            else
            {
                Curve c = new Curve(xDataArrays[0], yDataArrays[0], title, Measurement.DataSet.IsFinished);
                if (Measurement.DataSet.IsFinished)
                    c.Finish();
                simpleCurves.Add(new SimpleCurve(c, this));
            }

            AddSimpleCurves(simpleCurves, silent);
            return simpleCurves;
        }

        /// <summary>
        /// Adds the specified SimpleCurve to the SimpleMeasurement.
        /// </summary>
        /// <param name="simpleCurve">The SimpleCurve.</param>
        /// <param name="silent">if set to <c>true</c> [silent] the SimpleCurveAdded event is not raised.</param>
        /// <exception cref="System.ArgumentNullException">The specified SimpleCurve is null.</exception>
        /// <exception cref="System.ArgumentException">This measurement allready contains the specified SimpleCurve.</exception>
        public void AddSimpleCurve(SimpleCurve simpleCurve, bool silent = false)
        {
            if (simpleCurve == null)
                throw new ArgumentNullException("The specified SimpleCurve is null.");
            if (ContainsSimpleCurve(simpleCurve))
                throw new ArgumentException("This SimpleMeasurement allready contains the specified SimpleCurve.");

            SimpleCurveCollection.Add(simpleCurve); //Add the SimpleCurve to this SimpleMeasurement.
            if (!Measurement.ContainsCurve(simpleCurve.Curve))
            {
                if (!silent)
                    Measurement.AddCurve(simpleCurve.Curve); //Add the original Curve to the orginal Measurement.
                else
                    Measurement.AddCurveSilent(simpleCurve.Curve); //Add the original Curve to the orginal Measurement without raising the curve added event.
            }

            if (!silent)
                OnSimpleCurveAdded(simpleCurve);
        }

        /// <summary>
        /// Adds the specified collection of SimpleCurves to the SimpleMeasurement.
        /// </summary>
        /// <param name="simpleCurves">A list of SimpleCurves.</param>
        /// <param name="silent">if set to <c>true</c> [silent] the SimpleCurveAdded event is not raised.</param>
        /// <exception cref="System.ArgumentNullException">The list of specified SimpleCurves is null</exception>
        public void AddSimpleCurves(List<SimpleCurve> simpleCurves, bool silent = false)
        {
            if (simpleCurves == null)
                throw new ArgumentNullException("The list of specified SimpleCurves is null");
            AddSimpleCurves(simpleCurves.ToArray(), silent);
        }

        /// <summary>
        /// Adds the specified collection of SimpleCurves to the SimpleMeasurement.
        /// </summary>
        /// <param name="simpleCurves">An array of SimpleCurves.</param>
        /// <param name="silent">if set to <c>true</c> [silent] the SimpleCurveAdded event is not raised.</param>
        /// <exception cref="System.ArgumentNullException">The array of specified SimpleCurves is null</exception>
        public void AddSimpleCurves(SimpleCurve[] simpleCurves, bool silent = false)
        {
            if (simpleCurves == null)
                throw new ArgumentNullException("The array of specified SimpleCurves is null");
            foreach (SimpleCurve simpleCurve in simpleCurves)
                AddSimpleCurve(simpleCurve, silent);
        }

        /// <summary>
        /// Removes the specified SimpleCurves from the SimpleMeasurement.
        /// </summary>
        /// <param name="simpleCurve">The simple curve.</param>
        /// <param name="silent">if set to <c>true</c> [silent] the SimpleCurveRemoved even is not raised.</param>
        /// <exception cref="System.ArgumentNullException">The specified SimpleCurve is null.</exception>
        /// <exception cref="System.ArgumentException">This SimpleMeasurement does not contain the specified SimpleCurve</exception>
        public void RemoveSimpleCurve(SimpleCurve simpleCurve, bool silent = false)
        {
            if (simpleCurve == null)
                throw new ArgumentNullException("The specified SimpleCurve is null.");
            if (!ContainsSimpleCurve(simpleCurve))
                throw new ArgumentException("This SimpleMeasurement does not contain the specified SimpleCurve");

            Measurement.RemoveCurve(simpleCurve.Curve); //Removes the original curve from the original measurement
            SimpleCurveCollection.Remove(simpleCurve); //Removes the SimpleCurve from the SimpleMeasurement

            if (!silent)
                OnSimpleCurveRemoved(simpleCurve);
        }

        /// <summary>
        /// Removes the specified collection of SimpleCurves from the SimpleMeasurement.
        /// </summary>
        /// <param name="simpleCurves">The list of SimpleCurves.</param>
        /// <param name="silent">if set to <c>true</c> [silent] the SimpleCurveRemoved even is not raised.</param>
        /// <exception cref="System.ArgumentNullException">The list of SimpleCurves cannot be null</exception>
        public void RemoveSimpleCurves(List<SimpleCurve> simpleCurves, bool silent = false)
        {
            if (simpleCurves == null)
                throw new ArgumentNullException("The list of SimpleCurves cannot be null");
            RemoveSimpleCurves(simpleCurves.ToArray(), silent);
        }

        /// <summary>
        /// Removes the specified collection of SimpleCurves from the SimpleMeasurement.
        /// </summary>
        /// <param name="simpleCurves">The array of SimpleCurves.</param>
        /// <param name="silent">if set to <c>true</c> [silent] the SimpleCurveRemoved even is not raised.</param>
        /// <exception cref="System.ArgumentNullException">The array of SimpleCurves cannot be null</exception>
        public void RemoveSimpleCurves(SimpleCurve[] simpleCurves, bool silent = false)
        {
            if (simpleCurves == null)
                throw new ArgumentNullException("The array of SimpleCurves cannot be null");
            foreach (SimpleCurve simpleCurve in simpleCurves)
                RemoveSimpleCurve(simpleCurve, silent);
        }
        #endregion
        #endregion

        #region Events
        /// <summary>
        /// The SimpleCurveEventHandler delegate
        /// </summary>
        /// <param name="sender">The object.</param>
        /// <param name="simpleCurve">The SimpleCurve.</param>
        public delegate void SimpleCurveEventHandler(object sender, SimpleCurve simpleCurve);

        /// <summary>
        /// Occurs when a [SimpleCurve] has been added.
        /// </summary>
        public event SimpleCurveEventHandler SimpleCurveAdded;

        /// <summary>
        /// Called when a [SimpleCurve] has been added.
        /// </summary>
        private void OnSimpleCurveAdded(SimpleCurve simpleCurve)
        {
            SimpleCurveAdded?.Invoke(this, simpleCurve);
        }

        /// <summary>
        /// Occurs when a [SimpleCurve] has been removed.
        /// </summary>
        public event SimpleCurveEventHandler SimpleCurveRemoved;

        /// <summary>
        /// Called when a [SimpleCurve] has been removed.
        /// </summary>
        /// <param name="simpleCurve">The simple curve.</param>
        private void OnSimpleCurveRemoved(SimpleCurve simpleCurve)
        {
            SimpleCurveRemoved?.Invoke(this, simpleCurve);
        }

        /// <summary>
        /// Occurs when the [measurement] has ended.
        /// </summary>
        public event EventHandler MeasurementEnded;

        /// <summary>
        /// Called when the [measurement] has ended.
        /// </summary>
        private void OnMeasurementEnded()
        {
            Measurement.EndMeasurement -= Measurement_EndMeasurement;
            Measurement.EndMeasurementAsync -= Measurement_EndMeasurementAsync;
            MeasurementEnded?.Invoke(this, EventArgs.Empty);
        }
        #endregion

        /// <summary>
        /// Performs application-defined tasks associated with freeing, releasing, or resetting unmanaged resources.
        /// </summary>
        public void Dispose()
        {
            SimpleCurveAdded = null;
            SimpleCurveRemoved = null;
            MeasurementEnded = null;
            Measurement.Dispose();
            if (SimpleCurveCollection != null)
                foreach (SimpleCurve c in SimpleCurveCollection)
                    c.Dispose();
        }
    }

    public enum MeasurementTypes
    {
        LinearSweepVoltammetry = 0,
        CyclicVoltammetry = 1,
        ACVoltammetry = 2,
        DifferentialPulseVoltammetry = 3,
        SquareWaveVoltammetry = 4,
        NormalPulseVoltammetry = 5,
        ChronoAmperometry = 6,
        MultiStepAmperometry = 7,
        FastAmperometry = 8,
        PulsedAmperometricDetection = 9,
        MultiplePulseAmperometry = 10,
        OpenCircuitPotentiometry = 11,
        ChronoPotentiometry = 12,
        MultiStepPotentiometry = 13,
        ChronoPotentiometricStripping = 14,
        ImpedanceSpectroscopy = 15,
        MixedMode = 16,
        NotSpecified = 17
    }
}
