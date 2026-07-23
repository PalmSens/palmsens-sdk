# Communication protocol

The [pypalmsens.CommunicationInterface][] class provides an interface to exchange messages with your device using the communication protocol. You can use the Communication Protocol to directly query/manipulate the state of your device, e.g. setting registers, file operations, and sending scripts. The interface is of the physical connection type (e.g. serial port, USB, Bluetooth).

The Communication Protocol is supported by all MethodSCRIPT-capable instruments:

- [EmStat 4](https://dev.palmsens.com/comm_es4/latest/comm/comm_main.html)
- [EmStat Pico](https://dev.palmsens.com/comm_espico/latest/comm/comm_main.html)
- [Sensit Wearable](https://dev.palmsens.com/comm_sensitwb/latest/comm/comm_main.html)
- [Nexus](https://dev.palmsens.com/comm_nexus/latest/comm/comm_main.html)

## Connecting to the device

To communicate with a PalmSens instrument you need an active connection. [CommunicationInterface][pypalmsens.CommunicationInterface] supports the context manager protocol, so you can pass a [pypalmsens.Instrument][] instance. In this case, it opens and manages the connection:

```python
>>> import pypalmsens as ps
>>> instrument = ps.discover()[0]
>>> with ps.CommunicationInterface(instrument) as comm:
...     print(comm.query('t')
'es4_lr1500#Mar 12 2026 14:28:01\nR*'
```

Alternatively, you can manage the connection yourself. The repr shows the state of the connection:

```python
>>> comm = ps.CommunicationInterface(instrument)
>>> comm.open()
>>> comm
CommunicationInterface('/dev/ttyACM0', connected=True)
comm.close()
CommunicationInterface('/dev/ttyACM0', connected=False)
```

## Configuration

The interface exposes configuration attributes for controlling timeouts and read delays:

- [CommunicationInterface.timeout][pypalmsens.CommunicationInterface.timeout]: Maximum time (in seconds) to wait for a response before timing out. Defaults to 10s.
- [CommunicationInterface.delay][pypalmsens.CommunicationInterface.delay]: Pause (in seconds) between writing a command and reading subsequent responses. Adjust based on your specific hardware and connection type.

```python
>>> comm.timeout = 30.0  #(1)!
>>> comm.delay = 0.5     #(2)!
```

1. extend timeout for slow measurements
2. increase delay for slower connections

## Sending commands

The primary method for interactive communication is [`.query`][pypalmsens.CommunicationInterface.query]. It sends a command to the device, waits for completion, reads the full response, strips the prefix, and returns it as a string:

```python
>>> comm = ps.CommunicationInterface(manager)
>>> comm.query('i')  # Serial number
'ES4LR20B0008'
>>> comm.query('v')  # MethodSCRIPT version
'01.09.00'
>>> comm.query('t')  # Firmware version
'es4_lr1500#Mar 12 2026 14:28:01\nR*'
```

For commands that run for a long time (e.g., scripts), this method will block until the script completes or times out.

## Running MethodSCRIPTs

[`.run_methodscript`][pypalmsens.CommunicationInterface.run_methodscript] is a helper method that loads and executes a MethodSCRIPT on the instrument:

```python
>>> script = 'send_string "Hello world!"'
>>> output = comm.run_methodscript(script)
>>> output
'THello world!\n'
```

This returns the string prepended by a `T`, which is the [text packet identifier](https://dev.palmsens.com/methodscript/latest/methodscript/methodscript_main.html#ch_cmd_send_string).

## Capabilities

You can query which features are available on the connected instrument through capability detection:

- [`.get_methodscript_capabilities`][pypalmsens.CommunicationInterface.get_methodscript_capabilities]: Returns a set of MethodSCRIPT command names that are licensed and supported by the device's hardware and firmware.
- [`.get_communication_capabilities`][pypalmsens.CommunicationInterface.get_communication_capabilities]: Returns a set of communication protocol commands supported by the device's firmware.

```python
>>> comm.get_methodscript_capabilities()
{'abort', 'add_var', ..., 'var', 'wait'}
>>> comm.get_communication_capabilities()
{'CC', 'CM', ..., 't', 'v'}
```

These are helper functions that parse the hexadecimal bit fields returned by the underlying commands `CC` and `CM`:

```python
>>> comm.query('CC')
... 000000000000000000000000000000000000002F0000003FFFFF98FF00000002
>>> comm.query('CM')
... 000000000000000000000000000003FFFFBFE8FFFFFFFFFFFFFFFFFFFFBFFFFE
```

## Error handling

Communication errors raise [MethodScriptRuntimeError][pypalmsens.MethodScriptRuntimeError] (a subclass of `ConnectionError`) when the device returns an error response. The error includes an error code that can be looked up in [the MethodSCRIPT manual](https://dev.palmsens.com/methodscript/latest/methodscript/methodscript_main.html#app_err_error_codes):

```python
>>> comm.run_methodscript('invalid_command\n')
MethodScriptRuntimeError: The script command is unknown (Line 1, Col 16)
```

## Aborting measurements

Use [`.abort`][pypalmsens.CommunicationInterface.abort] to abort any currently running script or measurement and wait for completion. Note that this could take a while, depending on the measurement that was running:

```python
>>> comm.abort()
```

## Low-level communication

For more control over individual reads and writes, use the following methods:

- [`.write`][pypalmsens.CommunicationInterface.write]: Write a command or data to the instrument. To submit a command for execution, append a newline character (`'\n'`) to the end of the string.
- [`.read`][pypalmsens.CommunicationInterface.read]: Read the next available chunk from the buffer without blocking. Returns an empty string (`''`) if no data are available.
- [`.lines`][pypalmsens.CommunicationInterface.lines]: Generator that yields response chunks as they arrive, stopping when a timeout occurs between responses.
- [`.wait_until`][pypalmsens.CommunicationInterface.wait_until]: Wait until a response line starting with a given prefix arrives (useful for waiting on command echoes).
- [`.read_until`][pypalmsens.CommunicationInterface.read_until]: Read lines from the device until a termination sequence is found.

## Response history

The interface maintains a history of recent responses for debugging and inspection via [CommunicationInterface.history][pypalmsens.CommunicationInterface.history]. By default, it stores the last 100 responses:

```python
>>> comm.history
deque(['iES4LR20B0008\n', 'v01.09.00\n', ...], maxlen=100)
```
