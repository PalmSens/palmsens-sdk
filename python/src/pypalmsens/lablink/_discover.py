"""mDNS discovery service for LabLink devices.

This module discovers LabLink devices on the local network by browsing
for the `_lablink._tcp.local.` mDNS service type. Each discovered device
is resolved to its host name, addresses, and TXT record properties and
returned as a dictionary.

Run as a script for discovering lablinks using the command-line:

    python -m pypalmsens.lablink._discover [--timeout SECONDS] [--v6-only] [--debug]
"""

from __future__ import annotations

import argparse
import asyncio
import contextlib
import logging
from typing import Any

from zeroconf import IPVersion, ServiceStateChange, Zeroconf
from zeroconf.asyncio import AsyncServiceBrowser, AsyncServiceInfo, AsyncZeroconf

logger = logging.getLogger(__name__)


async def _resolve_service_info(
    zeroconf: Zeroconf,
    service_type: str,
    name: str,
    discovered: list[dict[str, Any]],
) -> None:
    """
    Resolve a newly found LabLink device and append its info to the results.

    Parameters
    ----------
    zeroconf : Zeroconf
        The zeroconf instance used for async service requests.
    service_type : str
        mDNS service type being browsed (e.g. '_lablink._tcp.local.').
    name : str
        Name of the discovered service.
    discovered : list[dict]
        List to append device info dictionaries into.

    Notes
    -----
    Appends a dictionary with keys:
      - server: hostname (e.g. 'lablink-01.local.')
      - addresses: parsed scoped IPs
      - Other TXT record fields verbatim.
    """
    info = AsyncServiceInfo(service_type, name)
    if await info.async_request(zeroconf, 1200):
        props: dict[str, Any] = {
            'server': info.server,
            'addresses': info.parsed_scoped_addresses(),
        }
        for key, value in info.decoded_properties.items():
            if key:
                props[key] = value

        logger.debug('Found %s', props)
        discovered.append(props)


async def discover(
    ip_version: IPVersion = IPVersion.All,
    timeout: float = 10,
) -> list[dict[str, Any]]:
    """
    Browse the local network for LabLink devices for a fixed duration.

    Uses zeroconf to browse for the `_lablink._tcp.local.` service type.
    Each discovered device is resolved into a dictionary of properties
    (hostname, addresses, TXT record fields) and appended to the results list.

    Parameters
    ----------
    ip_version : IPVersion
        IP protocol version for browsing/name resolution.
        Defaults to `zeroconf.IPVersion.All`.
    timeout : float
        How many seconds to browse before stopping. Default is 10.

    Returns
    -------
    list[dict]
        One dictionary per discovered LabLink device. Each dict contains:

        * server: fully qualified host name (e.g. "lablink-01.local.")
        * addresses: parsed scoped IP address strings
        * other TXT record fields as-is, e.g. name, serial, version

        The list is empty if no devices are discovered within the timeout.

    Examples
    --------
    >>> import asyncio
    >>> devices = asyncio.run(discover(timeout=10))
    >>> device, _* = devices
    >>> devices["name"]
    'lablink-01'
    >>> devices["addresses"]
    ['192.168.1.42', ...]
    """
    discovered: list[dict[str, Any]] = []
    tasks: set[asyncio.Task] = set()

    def on_service_state_change(
        zeroconf: Zeroconf, service_type: str, name: str, state_change: ServiceStateChange
    ) -> None:
        logger.info('%s: %s', state_change.name, name)
        if state_change is ServiceStateChange.Added:
            task = asyncio.create_task(
                _resolve_service_info(zeroconf, service_type, name, discovered)
            )
            tasks.add(task)
            task.add_done_callback(tasks.discard)

    aiozc = AsyncZeroconf(ip_version=ip_version)
    browser = AsyncServiceBrowser(
        aiozc.zeroconf, '_lablink._tcp.local.', handlers=[on_service_state_change]
    )
    logger.info('browsing for _lablink._tcp.local (timeout=%s s).', timeout)

    try:
        await asyncio.sleep(timeout)
        _ = await asyncio.gather(*tasks, return_exceptions=True)
    finally:
        await browser.async_cancel()
        await aiozc.async_close()

    return discovered


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--debug', action='store_true', help='enable debug logging')
    parser.add_argument('--v6-only', action='store_true', help='use IPv6 only')
    parser.add_argument(
        '--timeout', action='store', type=int, help='timeout in seconds', default=10
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)
    ip_version = IPVersion.V6Only if args.v6_only else IPVersion.All

    with contextlib.suppress(KeyboardInterrupt):
        lablinks = asyncio.run(discover(ip_version, timeout=args.timeout))

    print(f'\nDiscovered {len(lablinks)} lablinks:')
    for lablink in lablinks:
        print(lablink['name'], lablink['addresses'])
