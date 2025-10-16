using PalmSens.Core.Simplified;

namespace PalmSensBasicExample.Services
{
    public class MauiPlatformInvoker : IPlatformInvoker
    {
        public static bool InvokeIfRequired(Action action)
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
            return InvokeIfRequired(() =>
            {
                method.DynamicInvoke(args);
            });
        }
    }
}
