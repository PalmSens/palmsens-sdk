# Communication Protocol

The [pypalmsens.CommProtocol][] and [pypalmsens.CommProtocolAsync][] classes provide an interface to exchange messages with your device using the Communication Protocol. You can use the Communication Protocol to directly query/manipulate the state of your device, e.g. setting registers, file operations, and sending scripts. The interface is of the physical connection type (e.g. serial port, USB, Bluetooth).

The Communication Protocol is supported by all MethodSCRIPT-capable instruments:

- [EmStat 4](https://dev.palmsens.com/comm_es4/latest/comm/comm_main.html)
- [EmStat Pico](https://dev.palmsens.com/comm_espico/latest/comm/comm_main.html)
- [Sensit Wearable](https://dev.palmsens.com/comm_sensitwb/latest/comm/comm_main.html)
- [Nexus](https://dev.palmsens.com/comm_nexus/latest/comm/comm_main.html)

For more information how to use these classes, see [the documentation here](../comm_protocol.md).

**Classes:**

- [`pypalmsens.CommProtocol`][pypalmsens.CommProtocol]
- [`pypalmsens.CommProtocolAsync`][pypalmsens.CommProtocolAsync]

::: pypalmsens.CommProtocol
::: pypalmsens.CommProtocolAsync
