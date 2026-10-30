# Instance

A reference to a Lablink instance — a server that manages one or more instruments. An `Instance` holds the server's address and optionally its metadata, fetched via `get_info()`.

The default address (`https://127.0.0.1`) points to the local server. A freshly created instance only knows its address — call `get_info()` to fill in the name, version, and serial number. Everything else hangs off `login()`, which returns a [Session][pypalmsens.lablink.Session].

```python
local = lablink.Instance('https://127.0.0.1/')
info = await local.get_info()   # LablinkInfo: name, version, serial number
session = await local.login('Alice', 'hunter2')
```

::: pypalmsens.lablink.Instance
