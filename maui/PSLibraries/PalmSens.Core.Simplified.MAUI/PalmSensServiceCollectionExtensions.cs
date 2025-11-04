namespace PalmSens.Core.Simplified.MAUI;

public static class PalmSensServiceCollectionExtensions
{
    public static void AddPalmSensSDKServices(this MauiAppBuilder builder)
    {
        builder.Services.AddSingleton<PSCommSimpleMaui>(PSCommSimpleMaui.PSCommFactory());
        builder.Services.AddSingleton<IPlatformInvoker>(new MauiPlatformInvoker());
    }
}