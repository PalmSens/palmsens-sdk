using PalmSens.Core.Simplified.WinUi;

// To learn more about WinUI, the WinUI project structure,
// and more about our project templates, see: http://aka.ms/winui-project-info.

namespace PalmSens.Core.Simplified.WinUi
{
    public class PSCommSimpleWinUi : PSCommSimple
    {
        private PSCommSimpleWinUi(IPlatform platform, IPlatformInvoker platformInvoker) : base(platform, platformInvoker)
        {
        }

        public static PSCommSimpleWinUi Create()
        {
            DeviceHandler deviceHandler = new DeviceHandler();
            return new PSCommSimpleWinUi(deviceHandler, new WinUiMainThreadInvoker());
        }
    }
}
