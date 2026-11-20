#!/bin/sh
set -eu

VERSION=${ROUTEROS_VERSION:-7.23.8}
BUILD_DIR=$(mktemp -d /tmp/nfv-vrnetlab.XXXXXX)
trap 'rm -rf "$BUILD_DIR"' EXIT HUP INT TERM

command -v git >/dev/null
command -v curl >/dev/null
command -v unzip >/dev/null
command -v docker >/dev/null
command -v make >/dev/null

git clone --depth 1 https://github.com/srl-labs/vrnetlab.git "$BUILD_DIR/vrnetlab"
curl -fsSL --retry 3 \
  "https://download.mikrotik.com/routeros/${VERSION}/chr-${VERSION}.vmdk.zip" \
  -o "$BUILD_DIR/chr-${VERSION}.vmdk.zip"
unzip -o "$BUILD_DIR/chr-${VERSION}.vmdk.zip" -d "$BUILD_DIR/vrnetlab/mikrotik/routeros"

cd "$BUILD_DIR/vrnetlab/mikrotik/routeros"
make docker-image DOCKER_PLATFORM=
docker image inspect "vrnetlab/mikrotik_routeros:${VERSION}" >/dev/null
echo "Built vrnetlab/mikrotik_routeros:${VERSION}"
