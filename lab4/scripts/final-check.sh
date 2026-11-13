#!/bin/sh
set -eu

STUDENT=panina
N=3
ODL=http://10.104.3.100:8181
export TZ=Europe/Moscow

echo '========================================'
echo "ЛР4 завершена: $(date '+%d.%m.%Y %H:%M:%S %Z')"
echo "Студент: $(whoami)@$(hostname), STUDENT=$STUDENT, N=$N"
echo '========================================'

docker exec clab-panina-l4-h1 ping -c 2 -W 1 10.3.4.3
CONNECTED=$(docker exec clab-panina-l4-s2 ovs-vsctl get Controller br0 is_connected)
[ "$CONNECTED" = true ] || { echo "ERROR: s2 controller is not connected" >&2; exit 1; }
FAIL_MODE=$(docker exec clab-panina-l4-s2 ovs-vsctl get-fail-mode br0)
[ "$FAIL_MODE" = secure ] || { echo "ERROR: s2 fail-mode is $FAIL_MODE, expected secure" >&2; exit 1; }
docker exec clab-panina-l4-s2 ovs-vsctl show | grep -E 'Bridge|Controller|is_connected|fail_mode'
INVENTORY=$(curl -fsS --max-time 10 -u admin:admin \
  "$ODL/rests/data/opendaylight-inventory:nodes?content=nonconfig&depth=3")
NODES=$(printf '%s\n' "$INVENTORY" | jq -ec '[."opendaylight-inventory:nodes".node[].id] | sort')
printf '%s\n' "$NODES"
[ "$NODES" = '["openflow:1","openflow:2"]' ] || { echo "ERROR: unexpected ODL inventory: $NODES" >&2; exit 1; }
FLOW_DUMP=$(docker exec clab-panina-l4-s2 ovs-ofctl -O OpenFlow13 dump-flows br0)
printf '%s\n' "$FLOW_DUMP"
printf '%s\n' "$FLOW_DUMP" | grep -Eq 'n_packets=[1-9][0-9]*.*priority=200' \
  || { echo "ERROR: no baseline flow has a nonzero packet counter" >&2; exit 1; }
