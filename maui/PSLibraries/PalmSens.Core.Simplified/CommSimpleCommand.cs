using System;
using System.Threading.Tasks;
using PalmSens.Comm;

namespace PalmSens.Core.Simplified
{
    public interface ICommSimpleCommand<out TResult>
    {
        TResult Execute();
    }

    public class CommSimpleCommand<TResult> : ICommSimpleCommand<TResult>
    {
        private readonly ClientConnection _connection;
        private readonly Func<ClientConnection, TResult> _funcToRun;

        public CommSimpleCommand(ClientConnection connection, Func<ClientConnection, TResult> funcToRun)
        {
            _connection = connection ?? throw new ArgumentNullException(nameof(connection));
            _funcToRun = funcToRun ?? throw new ArgumentNullException(nameof(funcToRun));
        }

        #region ICommSimpleCommand<TResult> Members

        public TResult Execute()
        {
            if (_connection.State != CommManager.DeviceState.Idle)
                throw new InvalidOperationException("Device is not idle at the moment. This could indicate it's busy or not connected.");

            if (TaskScheduler.Current == _connection.TaskScheduler)
                throw new InvalidOperationException("The device can only execute one command at a time. Dead lock detected!");

            _connection.Semaphore.Wait();
            try
            {
                return _funcToRun(_connection);
            }
            finally
            {
                _connection.Semaphore.Release();
            }
        }

        #endregion
    }
}