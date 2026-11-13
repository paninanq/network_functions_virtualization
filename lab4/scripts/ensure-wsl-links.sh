#!/bin/sh
# Repair data veths after deploy when WSL2/containerlab leaves only eth0.
set -eu

has_iface() {
  docker exec "$1" ip link show "$2" >/dev/null 2>&1
}

ensure_pair() {
  a=$1
  ai=$2
  b=$3
  bi=$4
  a_has=0
  b_has=0
  has_iface "$a" "$ai" && a_has=1
  has_iface "$b" "$bi" && b_has=1

  if [ "$a_has" -eq 0 ] && [ "$b_has" -eq 0 ]; then
    containerlab tools veth create -a "$a:$ai" -b "$b:$bi"
  elif [ "$a_has" -ne "$b_has" ]; then
    echo "Only one endpoint exists: $a:$ai <-> $b:$bi" >&2
    exit 1
  fi

  docker exec "$a" ip link set "$ai" up
  docker exec "$b" ip link set "$bi" up
}

ensure_pair clab-panina-l4-h1 eth1 clab-panina-l4-s1 eth1
ensure_pair clab-panina-l4-s1 eth2 clab-panina-l4-s2 eth2
ensure_pair clab-panina-l4-h2 eth1 clab-panina-l4-s2 eth1
ensure_pair clab-panina-l4-h3 eth1 clab-panina-l4-s2 eth3

docker exec clab-panina-l4-h1 sh -c 'ethtool -K eth1 tx off && ip addr replace 10.3.4.1/24 dev eth1'
docker exec clab-panina-l4-h2 sh -c 'ethtool -K eth1 tx off && ip addr replace 10.3.4.2/24 dev eth1'
docker exec clab-panina-l4-h3 sh -c 'ethtool -K eth1 tx off && ip addr replace 10.3.4.3/24 dev eth1'
