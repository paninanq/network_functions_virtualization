#!/bin/sh
# Usage: STUDENT=panina N=3 ./scripts/push-flows.sh [all|baseline|acl]
set -eu

STUDENT=${STUDENT:-panina}
N=${N:-3}
ODL=${ODL:-http://10.104.${N}.100:8181}
MODE=${1:-all}
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
FLOW_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/../flows" && pwd)

if [ "$STUDENT" != panina ] || [ "$N" != 3 ]; then
  echo "These flow JSON files are for STUDENT=panina and N=3." >&2
  exit 2
fi

case "$MODE" in
  all|baseline|acl) ;;
  *) echo "Usage: $0 [all|baseline|acl]" >&2; exit 2 ;;
esac

failed=0
for file in "$FLOW_DIR"/*.json; do
  [ -f "$file" ] || continue
  stem=$(basename "$file" .json)
  case "$stem" in
    s1-*|acl-*) switch=1 ;;
    s2-*) switch=2 ;;
    *) echo "Cannot determine switch for $file" >&2; exit 2 ;;
  esac

  case "$MODE:$stem" in
    baseline:acl-icmp-h3) continue ;;
    acl:s1-*|acl:s2-*) continue ;;
  esac

  flow_id="${STUDENT}-${stem}"
  code=$(curl -sS -u admin:admin -X PUT \
    -H 'Content-Type: application/json' \
    --data-binary "@$file" \
    -o /dev/null -w '%{http_code}' \
    "$ODL/rests/data/opendaylight-inventory:nodes/node=openflow%3A${switch}/flow-node-inventory:table=0/flow=${flow_id}") || {
      echo "PUT $flow_id: curl failed" >&2
      failed=1
      continue
    }
  printf 'PUT %s: %s\n' "$flow_id" "$code"
  case "$code" in
    200|201|204) ;;
    *) failed=1 ;;
  esac
done

exit "$failed"
