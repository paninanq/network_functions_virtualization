#!/bin/sh
set -eu

LAB_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$LAB_DIR"
: "${ROS_PASS:?Set ROS_PASS to the lab RouterOS password}"
mkdir -p evidence

docker exec clab-panina-l5-dc1 vtysh -c "show bgp summary" > evidence/dc1-bgp-summary.txt
docker exec clab-panina-l5-dc1 vtysh -c "show ip route bgp" > evidence/dc1-bgp-routes.txt
docker exec clab-panina-l5-srv1 curl -sS -o /dev/null -w 'HTTP %{http_code}\n' http://198.51.100.1/ > evidence/nat-http.txt
docker logs --tail 5 clab-panina-l5-isp > evidence/nat-isp-log.txt 2>&1

{
  printf '%s\n' 'Simulated WAN probe from ISP to the protected DC host.'
  printf '%s\n' 'Expected result: no replies; HQ forward-default-deny counter increases.'
} > evidence/wan-attack.txt 2>&1

docker exec clab-panina-l5-isp ip route add 10.3.0.0/16 via 100.64.1.2
docker exec clab-panina-l5-isp ping -c 2 -W 1 10.3.100.10 >> evidence/wan-attack.txt 2>&1 || true
docker exec clab-panina-l5-isp ip route del 10.3.0.0/16 via 100.64.1.2

ROS_PASS="$ROS_PASS" python3 scripts/ros-exec.py clab-panina-l5-hq "/system identity print; /routing/bgp/session print; /interface wireguard peers print detail; /ip firewall filter print stats" > evidence/hq-final.txt
ROS_PASS="$ROS_PASS" python3 scripts/ros-exec.py clab-panina-l5-br "/system identity print; /interface wireguard peers print detail" > evidence/br-final.txt
ROS_PASS="$ROS_PASS" sh scripts/rest-demo.sh > evidence/rest-api.txt
ROS_PASS="$ROS_PASS" sh scripts/final-check.sh > evidence/final-output.txt 2>&1
printf '%s\n' 'Collected evidence:'
find evidence -maxdepth 1 -type f -printf '%f\n' | sort
