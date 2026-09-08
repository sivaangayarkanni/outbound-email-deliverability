#!/usr/bin/env python3
"""Query common DNSBLs for an IP and domain."""

from __future__ import annotations

import argparse
import sys

try:
    import dns.resolver
except ImportError:
    print("Install dependency: pip install dnspython", file=sys.stderr)
    sys.exit(2)


IP_ZONES = [
    "zen.spamhaus.org",
    "bl.spamcop.net",
    "b.barracudacentral.org",
    "dnsbl.sorbs.net",
    "cbl.abuseat.org",
    "psbl.surriel.com",
    "dnsbl-1.uceprotect.net",
]

DOMAIN_ZONES = [
    "dbl.spamhaus.org",
    "multi.surbl.org",
    "uribl.uribl.com",
]


def reverse_octets(ip: str) -> str:
    return ".".join(reversed(ip.split(".")))


def listed(query: str) -> tuple[bool, str]:
    try:
        answers = dns.resolver.resolve(query, "A")
        return True, ", ".join(rdata.address for rdata in answers)
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
        return False, ""
    except Exception as exc:  # noqa: BLE001
        return False, f"error: {exc}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Check IP/domain against DNSBLs")
    parser.add_argument("targets", nargs="+", help="IPv4 address and/or domain")
    args = parser.parse_args()

    rc = 0
    for target in args.targets:
        if target.replace(".", "").isdigit() and target.count(".") == 3:
            print(f"\n== IP {target} ==")
            rev = reverse_octets(target)
            for zone in IP_ZONES:
                hit, detail = listed(f"{rev}.{zone}")
                if hit and not detail.startswith("error"):
                    print(f"  LISTED  {zone} ({detail})")
                    rc = 1
                elif detail.startswith("error"):
                    print(f"  SKIP    {zone} ({detail})")
                else:
                    print(f"  clean   {zone}")
        else:
            print(f"\n== domain {target} ==")
            for zone in DOMAIN_ZONES:
                hit, detail = listed(f"{target}.{zone}")
                if hit and not detail.startswith("error"):
                    print(f"  LISTED  {zone} ({detail})")
                    rc = 1
                elif detail.startswith("error"):
                    print(f"  SKIP    {zone} ({detail})")
                else:
                    print(f"  clean   {zone}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
