#if ANDROID
using PalmSens.Core.Simplified.Android;
#endif

namespace PalmSens.Core.Simplified.MAUI
{
    public class MauiPlatformInvoker : IPlatformInvoker
    {
        public bool InvokeIfRequired(Action action)
        {
            if (MainThread.IsMainThread)
            {
                return false;
            }

            MainThread.BeginInvokeOnMainThread(() => action?.Invoke());
            return true;
        }

        public bool InvokeIfRequired(Delegate method, params object[] args)
        {
            throw new NotImplementedException();
        }
    }

    public class PSCommSimpleMaui : PSCommSimple
    {
        private PSCommSimpleMaui(IPlatform platform, IPlatformInvoker platformInvoker) : base(platform, platformInvoker) { }

        public static PSCommSimpleMaui PSCommFactory()
        {
#if ANDROID
            InitAsyncFunctionality(System.Environment.ProcessorCount); //Initiate the asynchronous functions in the SDK
            var deviceHandler = new DeviceHandler(new MauiPlatformInvoker());
            return new PSCommSimpleMaui(deviceHandler, deviceHandler);
#elif IOS
            return null;
#endif
        }

        /// <summary>
        /// It is recommended to call this before running measurements,
        /// as the platform specific wake and powermanagement functions can disrupt running measurements
        /// </summary>
        public static void InitiateWakeAndPowerManagementSettings()
        {
#if ANDROID
            PSAndroid.Utils.CoreDependencies.Init(Platform.CurrentActivity); //Initiates PSSDK threading dependencies and external library resolver
#elif IOS
#endif
        }

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
