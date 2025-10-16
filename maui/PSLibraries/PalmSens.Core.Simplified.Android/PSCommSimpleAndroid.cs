using Android.App;
using Android.OS;
using System;

namespace PalmSens.Core.Simplified.Android
{
    public class PSCommSimpleAndroid : PSCommSimple
    {
        public static PSCommSimpleAndroid PSCommFactory()
        {
            PalmSens.PSAndroid.Utils.CoreDependencies.Init(Application.Context); //Initiates PSSDK threading dependencies and external library resolver
            InitAsyncFunctionality(System.Environment.ProcessorCount); //Initiate the asynchronous functions in the SDK
            return new PSCommSimpleAndroid(new DeviceHandler(null));
        }

        /// <summary>
        /// Do not use this constructor, use the Factory method to create a new instance
        /// </summary>
        /// <param name="platform"></param>
        protected PSCommSimpleAndroid(DeviceHandler platform) : base(platform, platform) { }

        /// <summary>
        /// Required initialization for using the async functionalities of the PalmSens SDK.
        /// The amount of simultaneous operations will be limited to prevent performance issues.
        /// When possible it will leave one core free for the UI.
        /// </summary>
        /// <param name="nCores">The number of CPU cores.</param>
        public static void InitAsyncFunctionality(int nCores)
        {
            SynchronizationContextRemover.Init(nCores > 1 ? nCores - 1 : 1);
        }
    }
}
