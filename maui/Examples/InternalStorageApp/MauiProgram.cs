using Microsoft.Extensions.Logging;
using PalmSens.Core.Simplified;
using PalmSensInternalStorage.Services;

#if WINDOWS
using PalmSens.Core.Simplified.WinForms;
#endif

namespace PalmSensInternalStorage
{
    public static class MauiProgram
    {
        public static MauiApp CreateMauiApp()
        {
            var builder = MauiApp.CreateBuilder();
            builder
                .UseMauiApp<App>()
                .ConfigureFonts(fonts =>
                {
                    fonts.AddFont("OpenSans-Regular.ttf", "OpenSansRegular");
                    fonts.AddFont("OpenSans-Semibold.ttf", "OpenSansSemibold");
                });

#if ANDROID
            //builder.Services.AddSingleton<>();
#elif IOS
            //builder.Services.AddSingleton<>();
#elif MACCATALYST
            //builder.Services.AddSingleton<>();
#elif WINDOWS
            var psCommSimple = PSCommSimpleWindows.Create(new MauiPlatformInvoker());
            builder.Services.AddSingleton<PSCommSimple>(psCommSimple);
#endif

#if DEBUG
            builder.Logging.AddDebug();
#endif

            return builder.Build();
        }
    }
}
