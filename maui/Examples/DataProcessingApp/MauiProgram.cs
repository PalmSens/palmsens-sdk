using Microsoft.Extensions.Logging;
using OxyPlot.Maui.Skia;
using SkiaSharp.Views.Maui.Controls.Hosting;

#if WINDOWS
using PalmSens.Core.Simplified.WinForms;
#endif

namespace DataProcessingExample
{
    public static class MauiProgram
    {
        public static MauiApp CreateMauiApp()
        {
            var builder = MauiApp.CreateBuilder();
            builder
                .UseMauiApp<App>()
                .UseSkiaSharp()
                .UseOxyPlotSkia()
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
            //builder.Services.AddSingleton<>();
#endif

#if DEBUG
            builder.Logging.AddDebug();
#endif

            return builder.Build();
        }
    }
}
