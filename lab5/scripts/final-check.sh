#!/bin/sh
set -eu

LAB_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$LAB_DIR"
: "${ROS_PASS:?Set ROS_PASS to the lab RouterOS password}"

printf '%s\n' '========================================'
printf 'ЛР5 завершена: %s\n' "$(date '+%d.%m.%Y %H:%M:%S %Z')"
printf 'Студент: %s@%s, STUDENT=panina, N=3\n' "$(whoami)" "$(hostname)"
printf '%s\n' '========================================'
printf '%s\n' '--- HQ identity, eBGP, WireGuard ---'
python3 scripts/ros-exec.py clab-panina-l5-hq "/system identity print; /routing/bgp/session print; /interface wireguard peers print detail"
printf '%s\n' '--- dc1 BGP summary and routes ---'
docker exec clab-panina-l5-dc1 vtysh -c "show bgp summary"
docker exec clab-panina-l5-dc1 vtysh -c "show ip route bgp"
printf '%s\n' '--- Branch to DC ping ---'
docker exec clab-panina-l5-pcb ping -c 2 -W 2 10.3.100.10
printf '%s\n' '--- DC to Internet HTTP ---'
docker exec clab-panina-l5-srv1 curl -sS -o /dev/null -w 'Internet HTTP: %{http_code}\n' http://198.51.100.1/
