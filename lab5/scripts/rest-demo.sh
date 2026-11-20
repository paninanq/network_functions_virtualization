#!/bin/sh
set -eu

HQ_IP=${HQ_IP:-10.105.3.12}
ROS_USER=${ROS_USER:-admin}
: "${ROS_PASS:?Set ROS_PASS to the lab RouterOS password}"
BASE="http://${HQ_IP}/rest"
AUTH="${ROS_USER}:${ROS_PASS}"

printf '%s\n' '--- GET identity ---'
curl -fsS -u "$AUTH" "$BASE/system/identity" | jq .
printf '%s\n' '--- GET addresses ---'
curl -fsS -u "$AUTH" "$BASE/ip/address" | jq -r '.[] | "\(.address)\t\(.interface)"'
printf '%s\n' '--- GET BGP sessions ---'
curl -fsS -u "$AUTH" "$BASE/routing/bgp/session" | jq .

printf '%s\n' '--- PUT address-list record ---'
curl -fsS -u "$AUTH" -X PUT "$BASE/ip/firewall/address-list" \
  -H 'content-type: application/json' \
  -d '{"list":"lab","address":"192.0.2.3","comment":"panina"}' | jq .

ID=$(curl -fsS -u "$AUTH" "$BASE/ip/firewall/address-list?list=lab" | jq -r '.[0][".id"]')
test -n "$ID" && test "$ID" != null

printf '%s\n' '--- PATCH address-list record ---'
curl -fsS -u "$AUTH" -X PATCH "$BASE/ip/firewall/address-list/$ID" \
  -H 'content-type: application/json' \
  -d '{"comment":"patched by REST"}'
printf '\n%s\n' '--- DELETE address-list record ---'
curl -sS -u "$AUTH" -X DELETE "$BASE/ip/firewall/address-list/$ID" -o /dev/null -w 'HTTP %{http_code}\n'
