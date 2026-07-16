# Device File System

The PalmSens devices (such as the EmStat, Sensit, Nexus) have an internal filesystem where they store measurements (`.pssession` files), methods (`.psmethod` files), and other data. PyPalmSens provides a file-system-like interface to browse, read, write, and delete files on the connected instrument.

## Overview

The [pypalmsens.DeviceFileSystem][] class exposes a familiar POSIX-style path API for interacting with device storage. It supports directory traversal, file inspection, measurement loading, and cleanup — all as if the device were a mounted drive.

An async variant, [pypalmsens.DeviceFileSystemAsync][], is available for use with asynchronous instrument managers.

## Connecting to the Device Filesystem

To access the device filesystem you need an active connection to the instrument. The simplest approach is to pass an [pypalmsens.InstrumentManager][] (or its async counterpart) directly:

```python
>>> import pypalmsens as ps

>>> with ps.connect() as manager:
...     fs = ps.DeviceFileSystem(manager)
...     print(fs.root)
/
```

You can also pass an [pypalmsens.Instrument][] instance, in which case a new internal manager is created automatically:

```python
>>> instrument = ps.discover()[0]
>>> with ps.connect(instrument) as manager:
...     fs = ps.DeviceFileSystem(manager)
```

The filesystem itself also supports the context manager protocol, so you can use it directly:

```python
>>> with ps.connect() as manager:
...     with ps.DeviceFileSystem(manager):
...         # filesystem operations
```

## Browsing Files

### Listing Directory Contents

Use [pypalmsens.DeviceFileSystem.iterdir][] to iterate over entries in a directory. It yields [pypalmsens.DevicePath][] objects:

```python
>>> import pypalmsens as ps

>>> with ps.connect() as manager:
...     fs = ps.DeviceFileSystem(manager)
...     for entry in fs.iterdir():
...         print(entry)
Measurements/
Data/
config.xml
```

### Directory Tree View

For a quick overview of the entire directory structure, use [pypalmsens.DeviceFileSystem.tree][] which returns a nested dictionary:

```python
>>> with ps.connect() as manager:
...     fs = ps.DeviceFileSystem(manager)
...     tree = fs.tree()
...     print(tree)
{
    'Measurements': {'_files': ['exp001.pssession', 'exp002.pssession']},
    'Data': {'_files': []}
}
```

The returned dict uses `'_files'` as a special key containing the list of files at each directory level. Sub-dicts represent subdirectories.

### Checking Existence

Use [pypalmsens.DeviceFileSystem.exists][] to check whether a path exists on the device:

```python
>>> fs.exists('Measurements/exp001.pssession')
True
>>> fs.exists('Measurements/missing_file.pssession')
False
```

## Inspecting Files

### File Size and Timestamps

You can query file metadata without loading the full content:

```python
>>> path = 'Measurements/exp001.pssession'
>>> fs.size_of(path)
245760  # bytes
>>> fs.timestamp_of(path)
'2025-11-15T14:32:00'  # ISO format string
```

### Free and Total Space

Check the device storage capacity:

```python
>>> fs.free()     # free space in bytes
8388608
>>> fs.size()     # total filesystem size in bytes
16777216
```

## Loading Measurements

The most common use case for the device filesystem is loading saved measurements. Use [pypalmsens.DeviceFileSystem.load_measurement][] to load a `.pssession` file from the device into a [pypalmsans.data.Measurement][] object:

```python
>>> import pypalmsens as ps

>>> with ps.connect() as manager:
...     fs = ps.DeviceFileSystem(manager)
...     path = 'Measurements/exp001.pssession'
...     measurement = fs.load_measurement(path)
...     print(measurement.curves)
[Curve(CV i vs E Scan 1, n_points=200), Curve(CV i vs E Scan 2, n_points=200)]
```

The returned [pypalmsens.data.Measurement][] object provides full access to the measurement data, curves, metadata, and EIS datasets.

## Reading Text Files

For plain-text files on the device (such as configuration or log files), use [pypalmsens.DeviceFileSystem.read_text][]:

```python
>>> content = fs.read_text('config.xml')
>>> print(content[:200])
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
  ...
</configuration>
```

## Managing Files

### Removing Individual Files

Use [pypalmsens.DeviceFileSystem.remove][] to delete a file from the device:

```python
>>> fs.remove('Measurements/exp001.pssession')
```

### Deleting All Files

To clear all files on the device, use [pypalmsens.DeviceFileSystem.delete_all_files][]:

```python
>>> fs.delete_all_files(confirm=True)  # (1)!
```

1. The `confirm` flag defaults to `False` as a safety measure in interactive environments like Jupyter notebooks or REPL sessions. Set it to `True` to actually delete files.

## Path Handling

PyPalmSens uses [pypalmsens.DevicePath][] objects for all path operations. These are subclasses of Python's `pathlib.PurePath` with POSIX-style semantics, so you can use familiar path operations:

```python
>>> fs / 'Measurements' / 'exp001.pssession'  # (1)!
DevicePath('Measurements/exp001.pssession')
```

1. The `/` operator is overloaded on the filesystem instance to join paths.

You can also use standard `pathlib` methods:

```python
>>> path = fs / 'Measurements' / 'exp001.pssession'
>>> path.name
'exp001.pssession'
>>> path.parent
DevicePath('Measurements')
>>> path.suffix
'.pssession'
```

## Async Filesystem

For async workflows, use [pypalmsens.DeviceFileSystemAsync][] with an [pypalmsens.InstrumentManagerAsync][]:

```python
>>> import asyncio
>>> import pypalmsens as ps

>>> async def main():
...     instruments = await ps.discover_async()
...     manager = ps.InstrumentManagerAsync(instruments[0])
...     await manager.connect()
...     try:
...         fs = ps.DeviceFileSystemAsync(manager)
...         for entry in fs.iterdir():  # iterdir is synchronous
...             print(entry)
...         path = 'Measurements/exp001.pssession'
...         measurement = await fs.load_measurement(path)  # load_measurement is async
...     finally:
...         await manager.disconnect()

>>> asyncio.run(main())
```

Note that while [pypalmsens.DeviceFileSystemAsync.iterdir][] and [pypalmsens.DeviceFileSystemAsync.tree][] are synchronous (they use the same underlying synchronous connection call), methods like [pypalmsens.DeviceFileSystemAsync.load_measurement][], [pypalmsens.DeviceFileSystemAsync.remove][], and [pypalmsens.DeviceFileSystemAsync.delete_all_files][] are asynchronous.

## Error Handling

Filesystem operations raise [pypalmsens.FileSystemException][] (a subclass of `OSError`) when a device operation fails:

```python
>>> try:
...     fs.read_text('nonexistent_file.txt')
... except ps.FileSystemException as e:
...     print(f'Failed to read file: {e}')
Failed to read file: File not found
```

## Complete Example

Here is a complete example that browses the device filesystem, loads measurements, and cleans up old data:

```python
>>> import pypalmsens as ps

>>> with ps.connect() as manager:
...     fs = ps.DeviceFileSystem(manager)
...
...     # Browse files
...     for entry in fs.iterdir('Measurements'):
...         print(f'{entry.name}: {fs.size_of(entry)} bytes')
...
...     # Load a measurement
...     path = 'Measurements/exp001.pssession'
...     measurement = fs.load_measurement(path)
...     print(measurement.curves)
...
...     # Clean up old files (with confirmation)
...     fs.delete_all_files(confirm=True)
```
