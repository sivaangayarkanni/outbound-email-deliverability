#!/usr/bin/env python3
"""Verify PTR and forward-confirmed reverse DNS for a sending IP."""

from __future__ import annotations

import argparse
import socket
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description="Check PTR / FCrDNS")
    parser.add_argument("ip")
    parser.add_argument("--expect-host", help="Hostname that should match the PTR")
    args = parser.parse_args()
    ip = args.ip.strip()
    print(f"rDNS audit for {ip}")

    try:
        ptr_host, _, _ = socket.gethostbyaddr(ip)
    except socket.herror as exc:
        print(f"  FAIL  no PTR: {exc}")
        return 1

    print(f"  PTR   {ip} -> {ptr_host}")
    if args.expect_host and ptr_host.rstrip(".").lower() != args.expect_host.rstrip(".").lower():
        print(f"  FAIL  expected PTR {args.expect_host}")
        return 1

    rc = 0
    try:
        infos = socket.getaddrinfo(ptr_host, None)
        forwards = sorted({item[4][0] for item in infos})
    except socket.gaierror as exc:
        print(f"  FAIL  PTR host does not resolve: {exc}")
        return 1

    print(f"  A/AAAA {ptr_host} -> {', '.join(forwards)}")
    if ip not in forwards:
        print("  FAIL  FCrDNS mismatch — PTR host does not resolve back to this IP")
        rc = 1
    else:
        print("  OK    FCrDNS matches")

    host_l = ptr_host.lower()
    if host_l.startswith("ip-") or "compute" in host_l or "amazonaws" in host_l:
        print("  WARN  PTR looks like a cloud default hostname — request a mail.example.com PTR")
    return rc


if __name__ == "__main__":
    sys.exit(main())
