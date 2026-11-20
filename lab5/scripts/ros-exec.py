#!/usr/bin/env python3
"""Run a RouterOS SSH command through its vrnetlab management bridge."""
import getpass
import os
import subprocess
import sys


def main() -> int:
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <containerlab-node> <routeros-command>", file=sys.stderr)
        return 2

    container = sys.argv[1]
    command = " ".join(sys.argv[2:])
    password = os.environ.get("ROS_PASS") or getpass.getpass("RouterOS password: ")
    result = subprocess.run(
        [
            "docker", "exec", "-e", f"SSHPASS={password}", container,
            "sshpass", "-e", "ssh",
            "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            "-o", "LogLevel=ERROR",
            "-o", "ConnectTimeout=10",
            "admin@172.31.255.30",
            command,
        ],
        text=True,
        capture_output=True,
        timeout=90,
    )
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
