# Communication protocol

The [pypalmsens.CommProtocol][] class provides an interface to exchange messages with your device using the communication protocol. You can use the Communication Protocol to directly query/manipulate the state of your device, e.g. setting registers, file operations, and sending scripts. The interface is of the physical connection type (e.g. serial port, USB, Bluetooth).

The Communication Protocol is supported by all MethodSCRIPT-capable instruments:

- [EmStat 4](https://dev.palmsens.com/comm_es4/latest/comm/comm_main.html)
- [EmStat Pico](https://dev.palmsens.com/comm_espico/latest/comm/comm_main.html)
- [Sensit Wearable](https://dev.palmsens.com/comm_sensitwb/latest/comm/comm_main.html)
- [Nexus](https://dev.palmsens.com/comm_nexus/latest/comm/comm_main.html)

## Connecting to the device

To communicate with a PalmSens instrument you need an active connection. [CommProtocol][pypalmsens.CommProtocol] supports the context manager protocol, so you can pass a [pypalmsens.Instrument][] instance. In this case, it opens and manages the connection:

```py
import pypalmsens as ps

instrument = ps.discover()[0]
with ps.CommProtocol(instrument) as comm:
    print(comm.query('t'))
    """
    es4_lr1500#Mar 12 2026 14:28:01
    R*
    """
```

Alternatively, you can manage the connection yourself. The repr shows the state of the connection:

```py
comm = ps.CommProtocol(instrument)

comm.open()
print(comm)
#> CommProtocol('EmStat4 LR [1]', connected=True)

comm.close()
print(comm)
#> CommProtocol('EmStat4 LR [1]', connected=False)
```

## Sending commands

The primary method for interactive communication is [`.query`][pypalmsens.CommProtocol.query]. It sends a command to the device, waits for completion, reads the full response, strips the prefix, and returns it as a string:

```py
with ps.CommProtocol(instrument) as comm:
    print(comm.query('i'))  # Serial number
    #> ES4LR20B0008

    print(comm.query('v'))  # MethodSCRIPT version
    #> 01.09.00

    print(comm.query('t'))  # Firmware version
    """
    es4_lr1500#Mar 12 2026 14:28:01
    R*
    """
```

For commands that run for a long time (e.g., scripts), this method will block until the script completes or times out. For more commands, see the Communication Protocol documentation for your device.

## Running MethodSCRIPTs

[`.run_methodscript`][pypalmsens.CommProtocol.run_methodscript] is a helper method that loads and executes a MethodSCRIPT on the instrument:

```py
script = 'send_string "Hello world!"'

with ps.CommProtocol(instrument) as comm:
    output = comm.run_methodscript(script)
    print(output)
    """
    THello world!
    """
```

This returns the string prepended by a `T`, which is the [text packet identifier](https://dev.palmsens.com/methodscript/latest/methodscript/methodscript_main.html#ch_cmd_send_string).

## Capabilities

You can query which features are available on the connected instrument through capability detection:

- [`.get_methodscript_capabilities`][pypalmsens.CommProtocol.get_methodscript_capabilities]: Returns a set of MethodSCRIPT command names that are licensed and supported by the device's hardware and firmware.
- [`.get_communication_capabilities`][pypalmsens.CommProtocol.get_communication_capabilities]: Returns a set of communication protocol commands supported by the device's firmware.

<!--
```py
comm = ps.CommProtocol(instrument)
comm.open()
```
-->


```py
print(comm.get_methodscript_capabilities())
"""
{
    'abort',
    'add_var',
    'alter_vartype',
    'array',
    'array_get',
    'array_set',
    'await_int',
    'battery_perc',
    'beep',
    'bit_and_var',
    'bit_inv_var',
    'bit_lsl_var',
    'bit_lsr_var',
    'bit_or_var',
    'bit_xor_var',
    'breakloop',
    'cell_off',
    'cell_on',
    'copy_var',
    'display_btns',
    'display_clear',
    'display_draw',
    'display_icon',
    'display_inp_num',
    'display_keyboard',
    'display_progress',
    'display_scroll_add',
    'display_scroll_get',
    'display_text',
    'div_var',
    'else',
    'elseif',
    'endif',
    'endloop',
    'file_close',
    'file_open',
    'float_to_int',
    'get_gpio',
    'get_gpio_msk',
    'get_progress',
    'get_time',
    'hibernate',
    'i2c_config',
    'i2c_read',
    'i2c_read_byte',
    'i2c_write',
    'i2c_write_byte',
    'i2c_write_read',
    'if',
    'int_to_float',
    'linear_fit',
    'load_saved_end',
    'load_saved_start',
    'load_saved_str',
    'load_saved_var',
    'log_var',
    'loop',
    'mean',
    'meas',
    'meas_fast_ca',
    'meas_fast_cv',
    'meas_loop_acv',
    'meas_loop_ca',
    'meas_loop_ca_alt_mux',
    'meas_loop_cp',
    'meas_loop_cp_alt_mux',
    'meas_loop_cv',
    'meas_loop_dpv',
    'meas_loop_eis',
    'meas_loop_geis',
    'meas_loop_lsp',
    'meas_loop_lsv',
    'meas_loop_npv',
    'meas_loop_ocp',
    'meas_loop_ocp_alt_mux',
    'meas_loop_pad',
    'meas_loop_swv',
    'meas_ms_eis',
    'mod_var',
    'mul_var',
    'mux_config',
    'mux_get_channel_count',
    'mux_set_channel',
    'notify_led',
    'pck_add',
    'pck_end',
    'pck_start',
    'peak_detect',
    'pow_var',
    'qr_scan',
    'rtc_get',
    'save_str',
    'save_var',
    'send_string',
    'set_acquisition_frac',
    'set_acquisition_frac_autoadjust',
    'set_autoranging',
    'set_channel_sync',
    'set_cr',
    'set_e',
    'set_e_aux',
    'set_gpio',
    'set_gpio_cfg',
    'set_gpio_msk',
    'set_gpio_pullup',
    'set_i',
    'set_int',
    'set_ir_comp',
    'set_max_bandwidth',
    'set_pgstat_chan',
    'set_pgstat_mode',
    'set_poly_we_mode',
    'set_pot_range',
    'set_range',
    'set_range_minmax',
    'set_scan_dir',
    'set_script_output',
    'smooth',
    'store_str',
    'store_var',
    'str',
    'sub_var',
    'subarray',
    'timer_get',
    'timer_start',
    'trim_enable',
    'var',
    'wait',
}
"""
print(comm.get_communication_capabilities())
"""
{
    'CC',
    'CM',
    'Fmscr',
    'G',
    'H',
    'Lmscr',
    'R',
    'S',
    'Y',
    'Z',
    'comm_lock',
    'comm_unlock',
    'dlfw',
    'e',
    'e_fs',
    'fs_clear',
    'fs_del',
    'fs_dir',
    'fs_format',
    'fs_get',
    'fs_info',
    'fs_mount',
    'fs_put',
    'fs_unmount',
    'h',
    'i',
    'l',
    'l_fs',
    'm',
    'r',
    'sfs_clear',
    'sfs_del',
    'sfs_format',
    'sfs_put',
    't',
    'v',
}
"""
```

These are helper functions that parse the hexadecimal bit fields returned by the underlying commands `CC` and `CM`:

```py
print(comm.query('CC'))
#> 000000000000000000000000000000000000002F0000003FFFFF98FF00000002

print(comm.query('CM'))
#> 000000000000000000000000000003FFFFBFE8FFFFFFFFFFFFFFFFFFFFBFFFFE
```

## Configuration

The interface exposes configuration attributes for controlling timeouts and read delays:

- [CommProtocol.timeout][pypalmsens.CommProtocol.timeout]: Maximum time (in seconds) to wait for a response before timing out. Defaults to 10s.
- [CommProtocol.delay][pypalmsens.CommProtocol.delay]: Pause (in seconds) between writing a command and reading subsequent responses. Adjust based on your specific hardware and connection type.

```py
comm.timeout = 30.0  # (1)!
comm.delay = 0.5  # (2)!
```

1. extend timeout for slow measurements
2. increase delay for slower connections

## Error handling

Communication errors raise [MethodScriptRuntimeError][pypalmsens.MethodScriptRuntimeError] (a subclass of `ConnectionError`) when the device returns an error response. The error includes an error code that can be looked up in [the MethodSCRIPT manual](https://dev.palmsens.com/methodscript/latest/methodscript/methodscript_main.html#app_err_error_codes):

```py test="skip"
comm.run_methodscript('invalid_command\n')
#> MethodScriptRuntimeError: The script command is unknown (Line 1, Col 16)
```

## Aborting measurements

Use [`.abort`][pypalmsens.CommProtocol.abort] to abort any currently running script or measurement and wait for completion. Note that this could take a while, depending on the measurement that was running:

```py
comm.abort()
```

## Low-level communication

For more control over individual reads and writes, use the following methods:

- [`.write`][pypalmsens.CommProtocol.write]: Write a command or data to the instrument. To submit a command for execution, append a newline character (`'\n'`) to the end of the string.
- [`.read`][pypalmsens.CommProtocol.read]: Read the next available chunk from the buffer without blocking. Returns an empty string (`''`) if no data are available.
- [`.lines`][pypalmsens.CommProtocol.lines]: Generator that yields response chunks as they arrive, stopping when a timeout occurs between responses.
- [`.wait_until`][pypalmsens.CommProtocol.wait_until]: Wait until a response line starting with a given prefix arrives (useful for waiting on command echoes).
- [`.read_until`][pypalmsens.CommProtocol.read_until]: Read lines from the device until a termination sequence is found.

## Response history

The interface maintains a history of recent responses for debugging and inspection via [CommProtocol.history][pypalmsens.CommProtocol.history]. By default, it stores the last 100 responses:

```py
comm.history.clear()
comm.query('t')
comm.query('i')
comm.query('v')
print(comm.history)
"""
deque(
    ['tes4_lr1500#Mar 12 2026 14:28:01\nR*\n', 'iES4LR20B0008\n', 'v01.09.00\n'],
    maxlen=100,
)
"""
```

<!--
```py
comm.close()
```
-->

## Async Comm protocol

For async workflows, use [pypalmsens.DeviceFileSystemAsync][]:

```py
import asyncio
import pypalmsens as ps


async def main():
    instruments = await ps.discover_async()
    comm = ps.CommProtocolAsync(instruments[0])
    await comm.open()

    print(await comm.query('i'))
    #> ES4LR20B0008

    print(await comm.query('v'))
    #> 01.09.00

    print(await comm.query('t'))
    """
    es4_lr1500#Mar 12 2026 14:28:01
    R*
    """

    script = 'send_string "Hello world!"'
    print(await comm.run_methodscript(script))
    """
    THello world!
    """


asyncio.run(main())
```
