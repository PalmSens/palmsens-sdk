using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using PalmSens.Core.Simplified.Data;
using PalmSens.Data;
using PalmSens.DataFiles;

namespace PalmSens.Core.Simplified
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

            try
            {
                using (var fileStream = new FileStream(filepath, FileMode.Open, FileAccess.Read))
                {
                    session = LoadSessionFile(fileStream, filepath);
                }
            }
            catch (Exception ex)
            {
                throw new Exception("An error occured while loading, please make sure the file path is correct and the file is valid");
            }

            if (session != null)
                foreach (Measurement measurement in session)
                    simpleMeasurements.Add(new SimpleMeasurement(measurement));

            return simpleMeasurements;
        }

        private static SessionManager LoadSessionFile(Stream stream, string filePath)
        {
            SessionManager sm = new SessionManager();
            using (StreamReader sr = new StreamReader(stream))
                sm.Load(sr.BaseStream, filePath);

            sm.MethodForEditor.MethodFilename = new FileInfo(filePath).Name;
            return sm;
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

            try
            {
                using (var fileStream = new FileStream(filepath, FileMode.OpenOrCreate, FileAccess.Write))
                {
                    SaveSessionFile(fileStream, filepath, session);
                }
            }
            catch (Exception ex)
            {
                throw new Exception("An error occured while saving, please make sure the file path is correct");
            }
        }

        private static void SaveSessionFile(Stream stream, string filePath, SessionManager sessionManager)
        {
            sessionManager.MethodForEditor.MethodFilename = new FileInfo(filePath).Name;
            using (StreamWriter sw = new StreamWriter(stream))
            {
                sessionManager.Save(sw.BaseStream, filePath);
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

            try
            {
                using (var fileStream = new FileStream(filepath, FileMode.OpenOrCreate, FileAccess.Write))
                {
                    SaveSessionFile(fileStream, filepath, session);
                }
            }
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

            try
            {
                using (var fileStream = new FileStream(filepath, FileMode.Open, FileAccess.Read))
                {
                    method = LoadMethod(fileStream, filepath);
                }
            }
            catch (Exception ex)
            {
                throw new Exception("An error occured while loading, please make sure the file path is correct and the file is valid");
            }

            return method;
        }

        private static Method LoadMethod(Stream stream, string filePath, bool isCorrosion = false)
        {
            using (StreamReader sr = new StreamReader(stream))
            {
                var method = filePath.EndsWith(MethodFile2.FileExtension) ? MethodFile2.FromStream(sr) : MethodFile.FromStream(sr, filePath, isCorrosion).Method;
                method.MethodFilename = new FileInfo(filePath).Name;
                return method;
            }
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

            try
            {
                using (var fileStream = new FileStream(filepath, FileMode.OpenOrCreate, FileAccess.Write))
                {
                    SaveMethod(method, fileStream, filepath);
                }
            }
            catch (Exception ex)
            {
                throw new Exception("An error occured while saving, please make sure the file path is correct");
            }
        }

        private static void SaveMethod(Method method, Stream stream, string filePath)
        {
            MethodFile2.Save(method, stream, filePath, true);
        }
    }
}