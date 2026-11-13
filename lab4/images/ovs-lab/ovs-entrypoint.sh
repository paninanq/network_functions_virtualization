#!/bin/sh
set -eu

mkdir -p /var/run/openvswitch /var/log/openvswitch

if [ ! -s /etc/openvswitch/conf.db ]; then
  ovsdb-tool create /etc/openvswitch/conf.db /usr/share/openvswitch/vswitch.ovsschema
fi

ovsdb-server /etc/openvswitch/conf.db \
  --remote=punix:/var/run/openvswitch/db.sock \
  --remote=db:Open_vSwitch,Open_vSwitch,manager_options \
  --pidfile=/var/run/openvswitch/ovsdb-server.pid \
  --detach --no-chdir --log-file=/var/log/openvswitch/ovsdb-server.log

attempt=0
until ovs-vsctl --timeout=1 --db=unix:/var/run/openvswitch/db.sock show >/dev/null 2>&1; do
  attempt=$((attempt + 1))
  if [ "$attempt" -ge 20 ]; then
    echo "Open vSwitch database did not become ready" >&2
    exit 1
  fi
  sleep 0.25
done

ovs-vsctl --no-wait --db=unix:/var/run/openvswitch/db.sock init
ovs-vswitchd unix:/var/run/openvswitch/db.sock \
  --pidfile=/var/run/openvswitch/ovs-vswitchd.pid \
  --detach --no-chdir --log-file=/var/log/openvswitch/ovs-vswitchd.log

trap 'ovs-appctl -t /var/run/openvswitch/ovs-vswitchd.ctl exit >/dev/null 2>&1 || true; ovs-appctl -t /var/run/openvswitch/ovsdb-server.ctl exit >/dev/null 2>&1 || true' TERM INT
tail -F /var/log/openvswitch/ovsdb-server.log /var/log/openvswitch/ovs-vswitchd.log
