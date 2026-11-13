# Instance

Use [discover][pypalmsens.lablink.discover] to find Lablink instances on the network. The default address (`https://127.0.0.1`) points to the local server.

An [Instance][pypalmsens.lablink.Instance] holds the server's address and optionally its metadata. Call [get_info][pypalmsens.lablink.Instance.get_info] to fill in the name, version, and serial number.

Use [login][pypalmsens.lablink.Instance.login] to start an authenticated [Session][pypalmsens.lablink.Session].

```python
from pypalmsens import lablink

local = lablink.Instance('https://127.0.0.1/')
info = await local.get_info()
# LablinkInfo(name=..., version=...)
session = await local.login('Alice', 'hunter2')
```

::: pypalmsens.lablink.Instance
