#!/usr/bin/env python3
"""Capture IPv4 UDP headers on a Linux interface using AF_PACKET."""
import socket
import struct
import sys
import time


def main() -> int:
    iface = sys.argv[1] if len(sys.argv) > 1 else "eth2"
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    out_path = sys.argv[3] if len(sys.argv) > 3 else "/tmp/lab5-udp-capture.txt"
    sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0800))
    sock.bind((iface, 0))
    sock.settimeout(7)
    captured = 0
    with open(out_path, "w", encoding="utf-8") as out:
        out.write(f"IPv4 UDP capture on {iface} (provider-facing link)\n")
        out.flush()
        while captured < count:
            try:
                frame = sock.recv(65535)
            except TimeoutError:
                break
            if len(frame) < 42 or frame[12:14] != b"\x08\x00":
                continue
            ip_start = 14
            ihl = (frame[ip_start] & 0x0F) * 4
            if frame[ip_start + 9] != 17 or len(frame) < ip_start + ihl + 8:
                continue
            udp_start = ip_start + ihl
            src_port, dst_port = struct.unpack("!HH", frame[udp_start:udp_start + 4])
            src_ip = socket.inet_ntoa(frame[ip_start + 12:ip_start + 16])
            dst_ip = socket.inet_ntoa(frame[ip_start + 16:ip_start + 20])
            captured += 1
            out.write(f"{time.strftime('%H:%M:%S')} UDP {src_ip}:{src_port} -> {dst_ip}:{dst_port}\n")
            out.flush()
    sock.close()
    if not captured:
        print("No IPv4 UDP packets captured", file=sys.stderr)
        return 1
    print(f"Captured {captured} IPv4 UDP packets on {iface}: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
