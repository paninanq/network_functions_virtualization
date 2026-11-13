#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

docker build -t lab-tools:1.0 "$SCRIPT_DIR/lab-tools"
docker build -t ovs-lab:latest "$SCRIPT_DIR/ovs-lab"
docker build -t odl:chromium "$SCRIPT_DIR/odl"
