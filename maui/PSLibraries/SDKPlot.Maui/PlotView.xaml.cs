using OxyPlot;
using PalmSens.Core.Simplified;

namespace SDKPlot.Maui;

public partial class PlotView : ContentView, IPlotInvoker, IDisposable
{
    public PlotView()
    {
        InitializeComponent();

        CorePlot = new CorePlot(this);
        plotView1.Model = CorePlot.PlotModel;
    }

    /// <summary>
    /// The platform independent plot class that handles functionality of the plot
    /// </summary>
    public CorePlot CorePlot { get; }

    /// <summary>
    /// Reference to the OxyPlot PlotModel
    /// </summary>
    public PlotModel PlotModel { get { return CorePlot.PlotModel; } }



    /// <summary>
    /// Invokes event to UI thread if required.
    /// </summary>
    /// <param name="method">The method.</param>
    /// <param name="args">The arguments.</param>
    /// <returns></returns>
    /// <exception cref="System.NullReferenceException">Parent control not set.</exception>
    public bool InvokeIfRequired(Delegate method, params object[] args)
    {
        return InvokeIfRequired(() =>
        {
            method.DynamicInvoke(args);
        });
    }

    public bool InvokeIfRequired(Action action)
    {
        if (MainThread.IsMainThread)
        {
            return false;
        }

        MainThread.BeginInvokeOnMainThread(() => action?.Invoke());
        return true;
    }

    /// <summary>
    /// Invokes work on the UI thread that can be awaited
    /// </summary>
    /// <param name="action"></param>
    /// <returns></returns>
    public Task Invoke(Action action)
    {
        return MainThread.InvokeOnMainThreadAsync(action);
    }

    public void DoEvents() { }

    public void Dispose()
    {
        CorePlot?.Dispose();
    }
}
