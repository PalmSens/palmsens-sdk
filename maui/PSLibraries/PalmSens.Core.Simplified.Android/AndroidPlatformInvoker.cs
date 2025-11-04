using Android.OS;
using AndroidX.Annotations;

namespace PalmSens.Core.Simplified.Android;

public class AndroidPlatformInvoker : IPlatformInvoker
{
    Handler mainHandler = new Handler(Looper.MainLooper);

    public bool InvokeIfRequired(Delegate method, params object[] args) =>
        InvokeIfRequired(() => method.DynamicInvoke(args));

    /// <summary>
    /// Invokes action to UI thread if required.
    /// </summary>
    /// <param name="action">The action.</param>
    /// <returns></returns>
    public bool InvokeIfRequired(Action action)
    {
        if (Looper.MyLooper() != Looper.MainLooper)//Check if event needs to be cast to the UI thread
        {
            mainHandler.Post(action.Invoke); //Recast event to UI thread                
            return true;
        }
        return false;
    }
}