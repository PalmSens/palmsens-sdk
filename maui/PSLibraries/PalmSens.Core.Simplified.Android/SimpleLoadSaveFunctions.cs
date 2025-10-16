using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Android.App;
using Android.Content;
using Android.OS;
using Android.Runtime;
using Android.Views;
using Android.Widget;
using PalmSens.Core.Simplified.Data;
using PalmSens.Data;
using PalmSens.PSAndroid;
using System.IO;
using PalmSens.DataFiles;

namespace PalmSens.Core.Simplified.Android
{
    public class SimpleLoadSaveFunctions
    {
        /// <summary>
        /// Loads a collection of simplemeasurements from a *.pssession file.
        /// </summary>
        /// <param name="filepath">The filepath of the *.pssession file.</param>
        /// <returns></returns>
        /// <exception cref="System.ArgumentException">File path must be specified</exception>
        /// <exception cref="System.Exception">An error occured while loading, please make sure the file path is correct and the file is valid</exception>
        public static List<SimpleMeasurement> LoadMeasurements(string filepath)
        {
            if (string.IsNullOrEmpty(filepath))
                throw new ArgumentException("File path must be specified");

            List<SimpleMeasurement> simpleMeasurements = new List<SimpleMeasurement>();
            SessionManager session = null;

            try { session = LoadSaveHelperFunctions.LoadSessionFile(filepath); }
            catch (Exception ex)
            {
                throw new Exception("An error occured while loading, please make sure the file path is correct and the file is valid");
            }

            if (session != null)
                foreach (Measurement measurement in session)
                    simpleMeasurements.Add(new SimpleMeasurement(measurement));

            return simpleMeasurements;
        }

        /// <summary>
        /// Loads a collection of simplemeasurements from a *.pssession file from your assets folder.
        /// </summary>
        /// <param name="streamReader">The stream reader referencing the *.pssession file.</param>
        /// <returns></returns>
        /// <exception cref="System.ArgumentException">Stream reader cannot be null</exception>
        /// <exception cref="System.Exception">An error occured while loading, please make sure the file in the stream reader is valid</exception>
        public static List<SimpleMeasurement> LoadMeasurements(StreamReader streamReader)
        {
            if (streamReader == null)
                throw new ArgumentException("Stream reader cannot be null");

            List<SimpleMeasurement> simpleMeasurements = new List<SimpleMeasurement>();
            SessionManager session = new SessionManager();

            try { session.Load(streamReader.BaseStream, ""); }
            catch (Exception ex)
            {
                throw new Exception("An error occured while loading, please make sure the file in the stream reader is valid");
            }

            if (session != null)
                foreach (Measurement measurement in session)
                    simpleMeasurements.Add(new SimpleMeasurement(measurement));

            return simpleMeasurements;
        }

        /// <summary>
        /// Saves a simplemeasurement to a *.pssession file.
        /// </summary>
        /// <param name="simpleMeasurement">The simple measurement.</param>
        /// <param name="filepath">The filepath of the *.pssession file.</param>
        /// <exception cref="System.ArgumentException">File path must be specified</exception>
        /// <exception cref="System.ArgumentNullException">SimpleMeasurement cannot be null</exception>
        /// <exception cref="System.Exception">An error occured while saving, please make sure the file path is correct</exception>
        public static void SaveMeasurement(SimpleMeasurement simpleMeasurement, string filepath)
        {
            if (string.IsNullOrEmpty(filepath))
                throw new ArgumentException("File path must be specified");
            if (simpleMeasurement == null)
                throw new ArgumentNullException("SimpleMeasurement cannot be null");

            SessionManager session = new SessionManager();
            session.AddMeasurement(simpleMeasurement.Measurement);
            session.MethodForEditor = simpleMeasurement.Measurement.Method;

            try { LoadSaveHelperFunctions.SaveSessionFile(filepath, session); }
            catch (Exception ex)
            {
                throw new Exception("An error occured while saving, please make sure the file path is correct");
            }
        }

        /// <summary>
        /// Saves a collection of  simplemeasurements to a *.pssession file.
        /// </summary>
        /// <param name="simpleMeasurements">Array of simplemeasurements.</param>
        /// <param name="filepath">The filepath of the *.pssession file.</param>
        /// <exception cref="System.ArgumentException">File path must be specified</exception>
        /// <exception cref="System.ArgumentNullException">SimpleMeasurements cannot be null</exception>
        /// <exception cref="System.Exception">An error occured while saving, please make sure the file path is correct</exception>
        public static void SaveMeasurements(SimpleMeasurement[] simpleMeasurements, string filepath)
        {
            if (string.IsNullOrEmpty(filepath))
                throw new ArgumentException("File path must be specified");
            if (simpleMeasurements == null || simpleMeasurements.Where(meas => meas == null).Count() > 0)
                throw new ArgumentNullException("SimpleMeasurements cannot be null");

            SessionManager session = new SessionManager();
            foreach (SimpleMeasurement measurement in simpleMeasurements)
                if (measurement != null)
                    session.AddMeasurement(measurement.Measurement);
            session.MethodForEditor = simpleMeasurements[0].Measurement.Method;

            try { LoadSaveHelperFunctions.SaveSessionFile(filepath, session); }
            catch (Exception ex)
            {
                throw new Exception("An error occured while saving, please make sure the file path is correct");
            }
        }

        /// <summary>
        /// Saves a collection of  simplemeasurements to a *.pssession file.
        /// </summary>
        /// <param name="simpleMeasurements">Array of simplemeasurements.</param>
        /// <param name="filepath">The filepath of the *.pssession file.</param>
        /// <exception cref="System.ArgumentException">File path must be specified</exception>
        /// <exception cref="System.ArgumentNullException">SimpleMeasurements cannot be null</exception>
        public static void SaveMeasurements(List<SimpleMeasurement> simpleMeasurements, string filepath)
        {
            if (string.IsNullOrEmpty(filepath))
                throw new ArgumentException("File path must be specified");
            if (simpleMeasurements == null || simpleMeasurements.Where(meas => meas == null).Count() > 0)
                throw new ArgumentNullException("SimpleMeasurements cannot be null");

            SaveMeasurements(simpleMeasurements.ToArray(), filepath);
        }

        /// <summary>
        /// Loads a method from a *.psmethod file.
        /// </summary>
        /// <param name="filepath">The filepath of the *.psmethod file.</param>
        /// <returns>Method</returns>
        /// <exception cref="System.ArgumentException">File path must be specified</exception>
        /// <exception cref="System.Exception">An error occured while loading, please make sure the file path is correct and the file is valid</exception>
        public static Method LoadMethod(string filepath)
        {
            Method method = null;
            if (string.IsNullOrEmpty(filepath))
                throw new ArgumentException("File path must be specified");

            try { method = LoadSaveHelperFunctions.LoadMethod(filepath); }
            catch (Exception ex)
            {
                throw new Exception("An error occured while loading, please make sure the file path is correct and the file is valid");
            }

            return method;
        }

        /// <summary>
        /// Loads a method from a *.psmethod file from your assets folder.
        /// </summary>
        /// <param name="streamReader">The stream reader referencing the *.psmethod file.</param>
        /// <returns></returns>
        /// <exception cref="System.ArgumentException">Stream reader cannot be null</exception>
        /// <exception cref="System.Exception">An error occured while loading, please make sure the file path is correct and the file is valid</exception>
        public static Method LoadMethod(StreamReader streamReader)
        {
            if (streamReader == null)
                throw new ArgumentException("Stream reader cannot be null");
            Method method = null;

            try { method = MethodFile2.FromStream(streamReader); }
            catch (Exception ex)
            {
                throw new Exception("An error occured while loading, please make sure the file path is correct and the file is valid");
            }

            return method;
        }

        /// <summary>
        /// Saves a method to a *.psmethod file.
        /// </summary>
        /// <param name="method">The method .</param>
        /// <param name="filepath">The filepath of the *.psmethod file.</param>
        /// <exception cref="System.ArgumentException">File path must be specified</exception>
        /// <exception cref="System.ArgumentNullException">Method cannot be null</exception>
        /// <exception cref="System.Exception">An error occured while saving, please make sure the file path is correct</exception>
        public static void SaveMethod(Method method, string filepath)
        {
            if (string.IsNullOrEmpty(filepath))
                throw new ArgumentException("File path must be specified");
            if (method == null)
                throw new ArgumentNullException("Method cannot be null");

            try { LoadSaveHelperFunctions.SaveMethod(method, filepath); }
            catch (Exception ex)
            {
                throw new Exception("An error occured while saving, please make sure the file path is correct");
            }
        }
    }
}
