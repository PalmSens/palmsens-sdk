namespace PalmSens.Core.Simplified.MAUI;

public class MauiPlatformInvoker : IPlatformInvoker
{
    /// <summary>
    /// Invokes method/callback delegate to UI thread if required.
    /// </summary>
    /// <param name="method">The method.</param>
    /// <param name="args">The arguments.</param>
    /// <returns></returns>
    public bool InvokeIfRequired(Delegate method, params object[] args) =>
        InvokeIfRequired(() => method.DynamicInvoke(args));

    /// <summary>
    /// Invokes action to UI thread if required.
    /// </summary>
    /// <param name="action">The action.</param>
    /// <returns></returns>
    public bool InvokeIfRequired(Action action)
    {
        if (MainThread.IsMainThread)
        {
            return false;
        }

        MainThread.BeginInvokeOnMainThread(action.Invoke);
        return true;
    }
}