#if ANDROID
using PalmSens.Core.Simplified.Android;
#elif WINDOWS
using PalmSens.Core.Simplified.WinUi;
#endif

namespace PalmSens.Core.Simplified.MAUI
{
    public class PSCommSimpleMaui : PSCommSimple
    {
        private bool _initialized;

        private PSCommSimpleMaui(IPlatform platform, IPlatformInvoker platformInvoker) : base(platform, platformInvoker) { }

        public static PSCommSimpleMaui PSCommFactory()
        {
#if ANDROID
            return new PSCommSimpleMaui(new DeviceHandler(), new MauiPlatformInvoker());
#elif IOS
            return null;
#elif WINDOWS
            return new PSCommSimpleMaui(new DeviceHandler(), new MauiPlatformInvoker());
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

        /// <summary>
        /// Initialize the PalmSens SDK for MAUI. This method must be called before using any other functionality of the SDK.
        /// This method requires the MainPage to be have been initialized first.
        /// </summary>
        public async void Initialize()
        {
            if (_initialized)
            {
                return;
            }

            _initialized = true;

            InitAsyncFunctionality(System.Environment.ProcessorCount); //Initiate the asynchronous functions in the SDK

#if ANDROID
            PalmSens.Core.Android.Utils.CoreDependencies.Init(Platform.CurrentActivity);
#elif IOS
            PowerManagement.Init(() => { }, () => { }); //TODO implement power management sleep prevention during measurement on iOS
#elif WINDOWS
            //TODO implement power management sleep prevention during measurement for WinUi?
            PalmSens.Windows.CoreDependencies.Init();
#endif

#if ANDROID || IOS
            await RequestBluetoothPermissions();
#endif
        }

        private async Task RequestBluetoothPermissions()
        {
            PermissionStatus status = await Permissions.CheckStatusAsync<Permissions.Bluetooth>();

            if (status == PermissionStatus.Granted)
                return;

            if (status == PermissionStatus.Denied && DeviceInfo.Platform == DevicePlatform.iOS)
            {
                // Prompt the user to turn on in settings
                // On iOS once a permission has been denied it may not be requested again from the application
                throw new NotImplementedException();
            }

            if (Permissions.ShouldShowRationale<Permissions.Bluetooth>())
            {
                // Prompt the user with additional information as to why the permission is needed
                throw new NotImplementedException();
            }

            await Permissions.RequestAsync<Permissions.Bluetooth>();
        }
    }
}
