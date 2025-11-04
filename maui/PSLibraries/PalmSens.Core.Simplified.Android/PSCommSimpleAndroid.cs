using Android.Content;
using Android.OS;
using Android.Util;
using Android.Views;
using PalmSens.Comm;
using PalmSens.Devices;
using PalmSens.Core.Simplified.Data;
using PalmSens.Core.Simplified.InternalStorage;

namespace PalmSens.Core.Simplified.Android
{
    public class PSCommSimpleAndroid : View
    {
        public PSCommSimpleAndroid(Context context, IAttributeSet attrs) :
            base(context, attrs)
        {
            Initialize();
        }

        public PSCommSimpleAndroid(Context context, IAttributeSet attrs, int defStyle) :
            base(context, attrs, defStyle)
        {
            Initialize();
        }

        private void Initialize()
        {
            this.Visibility = ViewStates.Gone;
            PalmSens.Core.Android.Utils.CoreDependencies.Init(Context);
            InitAsyncFunctionality(System.Environment.ProcessorCount); //Initiate the asynchronous functions in the SDK
            _psCommSimple = new PSCommSimple(new DeviceHandler(), new AndroidPlatformInvoker());
        }

        /// <summary>
        /// Instance of the platform independent PSCommSimple class that manages measurements and manual control
        /// </summary>
        private PSCommSimple _psCommSimple;

        public PSCommSimple PSCommSimple => _psCommSimple; 

        /// <summary>
        /// Required initialization for using the async functionalities of the PalmSens SDK.
        /// The amount of simultaneous operations will be limited to prevent performance issues.
        /// When possible it will leave one core free for the UI.
        /// </summary>
        /// <param name="nCores">The number of CPU cores.</param>
        private void InitAsyncFunctionality(int nCores)
        {
            SynchronizationContextRemover.Init(nCores > 1 ? nCores - 1 : 1);
        }
    }
}