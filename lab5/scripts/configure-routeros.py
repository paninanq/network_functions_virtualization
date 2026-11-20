#!/usr/bin/env python3
"""Configure HQ and BR over the vrnetlab management bridge."""
from __future__ import annotations

import getpass
import os
import re
import subprocess
import sys
import time
from pathlib import Path


LAB_DIR = Path(__file__).resolve().parents[1]
ROS_EXEC = LAB_DIR / "scripts" / "ros-exec.py"
PASSWORD = os.environ.get("ROS_PASS") or getpass.getpass("RouterOS password: ")
ERROR_MARKERS = ("failure:", "expected end of command", "bad command name")


def ros(node: str, commands: str | list[str]) -> str:
    command = commands if isinstance(commands, str) else "; ".join(commands)
    env = os.environ.copy()
    env["ROS_PASS"] = PASSWORD
    result = None
    for attempt in range(4):
        result = subprocess.run(
            [sys.executable, str(ROS_EXEC), f"clab-panina-l5-{node}", command],
            text=True,
            capture_output=True,
            env=env,
            timeout=120,
        )
        if "Permission denied" not in result.stderr or attempt == 3:
            break
        time.sleep(1 + attempt)
    output = result.stdout.strip()
    if result.stderr.strip():
        print(result.stderr.strip(), file=sys.stderr)
    if result.returncode != 0 or any(marker in output.lower() for marker in ERROR_MARKERS):
        raise RuntimeError(f"RouterOS command failed on {node}: {command}\n{output}")
    print(f"[{node}] {command}")
    if output:
        print(output)
    return output


def public_key(node: str, interface: str) -> str:
    output = ros(node, f":put [/interface wireguard get {interface} public-key]")
    keys = re.findall(r"(?<![A-Za-z0-9+/=])([A-Za-z0-9+/]{42,43}={0,2})(?![A-Za-z0-9+/=])", output)
    if len(keys) != 1:
        raise RuntimeError(f"Could not extract WireGuard public key for {node}/{interface}: {output}")
    return keys[0]


def main() -> int:
    hq_cleanup = [
        "/ip firewall filter remove [find comment=input-established]",
        "/ip firewall filter remove [find comment=input-invalid]",
        "/ip firewall filter remove [find comment=input-icmp]",
        "/ip firewall filter remove [find comment=input-mgmt]",
        "/ip firewall filter remove [find comment=input-bgp]",
        "/ip firewall filter remove [find comment=input-wireguard]",
        "/ip firewall filter remove [find comment=input-wan-deny]",
        "/ip firewall filter remove [find comment=input-default-deny]",
        "/ip firewall filter remove [find comment=forward-established]",
        "/ip firewall filter remove [find comment=forward-invalid]",
        "/ip firewall filter remove [find comment=dc-to-internet]",
        "/ip firewall filter remove [find comment=branch-to-dc]",
        "/ip firewall filter remove [find comment=dc-to-branch]",
        "/ip firewall filter remove [find comment=forward-default-deny]",
        "/ip firewall nat remove [find comment=inside-to-internet]",
        "/ip firewall address-list remove [find comment=branch-prefix]",
        "/ip route remove [find comment=branch-through-wg]",
        "/ip route remove [find comment=clab-mgmt]",
        "/ip route remove [find comment=isp]",
        "/ip address remove [find comment=wg-hq]",
        "/interface wireguard peers remove [find interface=wg-br]",
        "/interface wireguard remove [find name=wg-br]",
        "/ip address remove [find comment=to-dc]",
        "/ip address remove [find comment=wan]",
        "/routing/bgp/connection remove [find name=to-dc]",
        "/routing/bgp/instance remove [find name=hq]",
    ]
    br_cleanup = [
        "/ip firewall nat remove [find comment=branch-to-internet]",
        "/ip route remove [find comment=dc-through-wg]",
        "/ip route remove [find comment=clab-mgmt]",
        "/ip route remove [find comment=isp]",
        "/ip address remove [find comment=wg-branch]",
        "/interface wireguard peers remove [find interface=wg-hq]",
        "/interface wireguard remove [find name=wg-hq]",
        "/ip address remove [find comment=wan]",
        "/ip address remove [find comment=branch-lan]",
    ]

    # Addresses and management routes come before WAN defaults so SSH replies
    # keep returning through RouterOS ether1 after the Internet default is added.
    hq_base = [
        "/system identity set name=hq-panina",
        "/ip address add address=10.3.1.2/30 interface=ether2 comment=to-dc",
        "/ip address add address=100.64.1.2/30 interface=ether3 comment=wan",
        "/ip route add dst-address=10.105.3.0/24 gateway=172.31.255.29 comment=clab-mgmt",
        "/ip route add dst-address=0.0.0.0/0 gateway=100.64.1.1 comment=isp",
        "/routing/bgp/instance add name=hq as=65103",
        "/routing/bgp/connection add name=to-dc instance=hq remote.address=10.3.1.1 remote.as=65003 local.role=ebgp output.default-originate=if-installed",
        "/ip firewall nat add chain=srcnat out-interface=ether3 action=masquerade comment=inside-to-internet",
        "/interface wireguard add name=wg-br listen-port=13003",
        "/ip address add address=10.3.254.1/30 interface=wg-br comment=wg-hq",
        "/ip service set www disabled=no",
    ]
    br_base = [
        "/system identity set name=br-panina",
        "/ip address add address=100.64.2.2/30 interface=ether2 comment=wan",
        "/ip address add address=10.3.200.1/24 interface=ether3 comment=branch-lan",
        "/ip route add dst-address=10.105.3.0/24 gateway=172.31.255.29 comment=clab-mgmt",
        "/ip route add dst-address=0.0.0.0/0 gateway=100.64.2.1 comment=isp",
        "/interface wireguard add name=wg-hq listen-port=13003",
        "/ip address add address=10.3.254.2/30 interface=wg-hq comment=wg-branch",
        "/ip firewall nat add chain=srcnat out-interface=ether2 action=masquerade comment=branch-to-internet",
    ]

    # Keep the SSH session count low: RouterOS occasionally throttles rapid
    # reconnects from the vrnetlab wrapper. Each command remains independently
    # visible in the transcript and RouterOS processes the semicolon batch in
    # order.
    ros("hq", hq_cleanup + hq_base)
    ros("br", br_cleanup + br_base)

    hq_key = public_key("hq", "wg-br")
    br_key = public_key("br", "wg-hq")

    ros("hq", [
        f'/interface wireguard peers add interface=wg-br public-key="{br_key}" endpoint-address=100.64.2.2 endpoint-port=13003 allowed-address=10.3.254.2/32,10.3.200.0/24 persistent-keepalive=25s',
        "/ip route add dst-address=10.3.200.0/24 gateway=wg-br comment=branch-through-wg",
        "/ip firewall address-list add list=to-dc address=10.3.200.0/24 comment=branch-prefix",
        "/routing/bgp/connection set to-dc output.network=to-dc",
    ])
    ros("br", [
        f'/interface wireguard peers add interface=wg-hq public-key="{hq_key}" endpoint-address=100.64.1.2 endpoint-port=13003 allowed-address=10.3.254.1/32,10.3.100.0/24 persistent-keepalive=25s',
        "/ip route add dst-address=10.3.100.0/24 gateway=wg-hq comment=dc-through-wg",
    ])

    input_rules = [
        "/ip firewall filter add chain=input action=accept connection-state=established,related comment=input-established",
        "/ip firewall filter add chain=input action=drop connection-state=invalid comment=input-invalid",
        "/ip firewall filter add chain=input action=accept protocol=icmp comment=input-icmp",
        "/ip firewall filter add chain=input action=accept in-interface=ether1 comment=input-mgmt",
        "/ip firewall filter add chain=input action=accept in-interface=ether2 protocol=tcp dst-port=179 comment=input-bgp",
        "/ip firewall filter add chain=input action=accept protocol=udp dst-port=13003 comment=input-wireguard",
        "/ip firewall filter add chain=input action=drop in-interface=ether3 comment=input-wan-deny",
        "/ip firewall filter add chain=input action=drop comment=input-default-deny",
    ]
    forward_rules = [
        "/ip firewall filter add chain=forward action=accept connection-state=established,related comment=forward-established",
        "/ip firewall filter add chain=forward action=drop connection-state=invalid comment=forward-invalid",
        "/ip firewall filter add chain=forward action=accept in-interface=ether2 out-interface=ether3 comment=dc-to-internet",
        "/ip firewall filter add chain=forward action=accept in-interface=wg-br out-interface=ether2 comment=branch-to-dc",
        "/ip firewall filter add chain=forward action=accept in-interface=ether2 out-interface=wg-br comment=dc-to-branch",
        "/ip firewall filter add chain=forward action=drop comment=forward-default-deny",
    ]
    ros("hq", input_rules + forward_rules)

    # Save only the public key text in console output; the private key remains
    # in RouterOS and is intentionally absent from this script and Git.
    print(f"WireGuard peers configured. HQ public key: {hq_key}; BR public key: {br_key}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(exc, file=sys.stderr)
        raise SystemExit(1)
