#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
LAB_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
SONIC_BRANCH=${SONIC_BRANCH:-202511}
SONIC_BUILD_ID=${SONIC_BUILD_ID:-1278069}
ARTIFACT_URL="https://sonic-build.azurewebsites.net/api/sonic/artifacts?branchName=${SONIC_BRANCH}&platform=vs&target=target%2Fdocker-sonic-vs.gz&buildId=${SONIC_BUILD_ID}"

command -v curl >/dev/null
command -v gunzip >/dev/null
command -v docker >/dev/null

echo "Loading upstream SONiC ${SONIC_BRANCH}, build ${SONIC_BUILD_ID}..."
curl -fsSL --retry 3 "$ARTIFACT_URL" | gunzip -c | docker load
docker tag docker-sonic-vs:latest "docker-sonic-vs:${SONIC_BRANCH}"
docker build -t "sonic-course:${SONIC_BRANCH}" "$SCRIPT_DIR/sonic-course"
docker image inspect "sonic-course:${SONIC_BRANCH}" >/dev/null
echo "Built sonic-course:${SONIC_BRANCH}"
