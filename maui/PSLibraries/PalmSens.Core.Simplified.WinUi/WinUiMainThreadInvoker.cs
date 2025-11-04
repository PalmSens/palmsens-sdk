using System;

namespace PalmSens.Core.Simplified.WinUi;

public class WinUiMainThreadInvoker : IPlatformInvoker
{
    public bool InvokeIfRequired(Delegate method, params object[] args) =>
        InvokeIfRequired(() => method.DynamicInvoke(args));

    public bool InvokeIfRequired(Action action)
    {
        throw new NotImplementedException();
    }
}