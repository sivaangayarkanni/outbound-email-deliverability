#!/usr/bin/env python3
"""Audit SPF, DKIM selectors, and DMARC for a domain."""

from __future__ import annotations

import argparse
import sys

try:
    import dns.resolver
except ImportError:
    print("Install dependency: pip install dnspython", file=sys.stderr)
    sys.exit(2)


def txt(name: str) -> list[str]:
    try:
        answers = dns.resolver.resolve(name, "TXT")
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers):
        return []
    except Exception as exc:  # noqa: BLE001
        print(f"  ! query error for {name}: {exc}", file=sys.stderr)
        return []
    records = []
    for rdata in answers:
        records.append("".join(s.decode("utf-8") if isinstance(s, bytes) else s for s in rdata.strings))
    return records


def count_spf_lookups(record: str, depth: int = 0, seen: set[str] | None = None) -> int:
    if seen is None:
        seen = set()
    if depth > 10 or record in seen:
        return 0
    seen.add(record)
    total = 0
    for tok in record.split():
        lower = tok.lower()
        if lower.startswith("include:") or lower.startswith("redirect="):
            total += 1
            target = tok.split(":", 1)[-1] if ":" in tok else tok.split("=", 1)[-1]
            nested = [r for r in txt(target) if r.lower().startswith("v=spf1")]
            if nested:
                total += count_spf_lookups(nested[0], depth + 1, seen)
        else:
            mech = lower.split(":", 1)[0].split("/", 1)[0]
            if mech in {"a", "mx", "ptr", "exists"}:
                total += 1
    return total


def check_spf(domain: str) -> int:
    print(f"\n== SPF ({domain}) ==")
    records = [r for r in txt(domain) if r.lower().startswith("v=spf1")]
    rc = 0
    if not records:
        print("  FAIL  no SPF TXT record")
        return 1
    if len(records) > 1:
        print(f"  FAIL  {len(records)} SPF records (must be exactly one)")
        rc = 1
    for rec in records:
        print(f"  record: {rec}")
        lookups = count_spf_lookups(rec)
        print(f"  DNS lookups (approx): {lookups} / 10")
        if lookups > 10:
            print("  FAIL  exceeds 10-lookup limit (PermError)")
            rc = 1
        if rec.rstrip().endswith("+all"):
            print("  FAIL  +all authorizes the entire internet")
            rc = 1
        elif rec.rstrip().endswith("?all"):
            print("  WARN  ?all is neutral — use ~all then -all")
        elif rec.rstrip().endswith("~all"):
            print("  OK    ~all (soft fail) — tighten to -all when inventory is complete")
        elif rec.rstrip().endswith("-all"):
            print("  OK    -all (hard fail)")
        else:
            print("  WARN  no terminal all mechanism")
    return rc


def check_dmarc(domain: str) -> int:
    print(f"\n== DMARC (_dmarc.{domain}) ==")
    records = [r for r in txt(f"_dmarc.{domain}") if r.lower().startswith("v=dmarc1")]
    if not records:
        print("  FAIL  no DMARC record")
        return 1
    rec = records[0]
    print(f"  record: {rec}")
    tags = dict(part.split("=", 1) for part in rec.split(";") if "=" in part)
    tags = {k.strip().lower(): v.strip() for k, v in tags.items()}
    rc = 0
    policy = tags.get("p", "")
    print(f"  policy: {policy or '(missing)'}")
    if policy not in {"none", "quarantine", "reject"}:
        print("  FAIL  p= must be none, quarantine, or reject")
        rc = 1
    elif policy == "none":
        print("  OK    monitoring mode — plan the move to quarantine/reject")
    else:
        print("  OK    enforcing")
    if "rua" not in tags:
        print("  WARN  no rua= aggregate reporting address")
    else:
        print(f"  rua:  {tags['rua']}")
    if "ruf" in tags:
        print(f"  ruf:  {tags['ruf']}")
    return rc


def check_dkim(domain: str, selectors: list[str]) -> int:
    print(f"\n== DKIM ({domain}) ==")
    rc = 0
    found = 0
    for sel in selectors:
        name = f"{sel}._domainkey.{domain}"
        records = txt(name)
        if not records:
            continue
        found += 1
        rec = records[0]
        print(f"  HIT   {name}")
        print(f"         {rec[:120]}{'\u2026' if len(rec) > 120 else ''}")
        p = None
        for part in rec.split(";"):
            part = part.strip()
            if part.lower().startswith("p="):
                p = part[2:].strip()
        if p == "":
            print("         WARN  empty p= (revoked key)")
        elif p and len(p) < 200:
            print("         WARN  public key looks short — prefer 2048-bit RSA")
    if not found:
        print("  FAIL  no selectors resolved. Pass --selector or edit the default list.")
        rc = 1
    else:
        print(f"  OK    {found} selector(s) published")
    return rc


def main() -> int:
    parser = argparse.ArgumentParser(description="Check SPF / DKIM / DMARC DNS")
    parser.add_argument("domain")
    parser.add_argument(
        "--selector",
        action="append",
        dest="selectors",
        help="DKIM selector (repeatable). Defaults cover common ESP names.",
    )
    args = parser.parse_args()
    domain = args.domain.strip().lower().rstrip(".")
    selectors = args.selectors or [
        "s1", "s2", "default", "google", "selector1", "selector2",
        "k1", "k2", "dkim", "mail", "mta1", "ses", "cm", "pm",
    ]
    print(f"Deliverability DNS audit for {domain}")
    rc = 0
    rc |= check_spf(domain)
    rc |= check_dkim(domain, selectors)
    rc |= check_dmarc(domain)
    print("\nDone.")
    return rc


if __name__ == "__main__":
    sys.exit(main())
