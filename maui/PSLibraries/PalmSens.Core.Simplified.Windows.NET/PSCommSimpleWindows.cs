using PalmSens.Windows;

namespace PalmSens.Core.Simplified.WinForms;

public class PSCommSimpleWindows : PSCommSimple
{
    private PSCommSimpleWindows(IPlatform platform, IPlatformInvoker platformInvoker) : base(platform, platformInvoker)
    {
    }

    public static PSCommSimpleWindows Create(IPlatformInvoker platformInvoker)
    {
        CoreDependencies.Init();
        var nCores = Environment.ProcessorCount;
        SynchronizationContextRemover.Init(nCores > 1 ? nCores - 1 : 1);
        return new PSCommSimpleWindows(new DeviceHandler(), platformInvoker);
    }
}

public class PlatformInvokerStub : IPlatformInvoker
{
    public bool InvokeIfRequired(Delegate method, params object[] args)
    {
        return false;
    }
}
