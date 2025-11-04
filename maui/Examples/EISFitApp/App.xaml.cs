namespace PalmSensEISFIt
{
    public partial class App : Application
    {
        public App()
        {
            this.UserAppTheme = AppTheme.Light;
            InitializeComponent();
        }

        protected override Window CreateWindow(IActivationState? activationState)
        {
            return new Window(new AppShell());
        }
    }
}
