using System;
using System.Threading.Tasks;
using PalmSens.Comm;

namespace PalmSens.Core.Simplified
{
    public interface ICommSimpleCommandAsync<TResult>
    {
        Task<TResult> ExecuteAsync();
    }

    public class CommSimpleAsyncCommand<TResult> : ICommSimpleCommandAsync<TResult>
    {
        private readonly ClientConnection _connection;
        private readonly Func<ClientConnection, Task<TResult>> _funcToRun;

        public CommSimpleAsyncCommand(ClientConnection connection, Func<ClientConnection, Task<TResult>> funcToRun)
        {
            _connection = connection ?? throw new ArgumentNullException(nameof(connection));
            _funcToRun = funcToRun ?? throw new ArgumentNullException(nameof(funcToRun));
        }

        #region ICommSimpleCommandAsync<TResult> Members

        public async Task<TResult> ExecuteAsync()
        {
            if (_connection.State != CommManager.DeviceState.Idle)
                throw new InvalidOperationException("Device is not idle at the moment. This could indicate it's busy or not connected.");

            await new SynchronizationContextRemover();

            return await _connection.RunAsync(() => _funcToRun(_connection));
        }

        #endregion
    }
}