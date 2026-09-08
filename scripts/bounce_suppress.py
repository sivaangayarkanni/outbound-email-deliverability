#!/usr/bin/env python3
"""Append hard-bounce and complaint events to a local suppression list.

This is a starter. Swap the CSV backend for your ESP suppression API
or a shared database before production volume.

Input JSON (stdin or --file), one event or a list:

  {"email": "user@example.com", "reason": "hard_bounce", "code": "5.1.1", "source": "postfix"}
  {"email": "user@example.com", "reason": "complaint", "source": "yahoo-fbl"}
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

VALID_REASONS = {
    "hard_bounce",
    "soft_bounce_exhausted",
    "complaint",
    "unsubscribe",
    "manual",
    "role_account",
}

FIELDS = ["email", "reason", "code", "source", "timestamp"]


def normalize(addr: str) -> str:
    addr = addr.strip().lower()
    if "@" not in addr:
        raise ValueError(f"not an email: {addr}")
    local, domain = addr.rsplit("@", 1)
    return f"{local}@{domain}"


def load_events(raw: str) -> list[dict]:
    data = json.loads(raw)
    if isinstance(data, dict):
        return [data]
    if isinstance(data, list):
        return data
    raise ValueError("JSON must be an object or array")


def existing_emails(path: Path) -> set[str]:
    if not path.exists():
        return set()
    with path.open(newline="", encoding="utf-8") as fh:
        return {row["email"] for row in csv.DictReader(fh) if row.get("email")}


def main() -> int:
    parser = argparse.ArgumentParser(description="Update a suppression CSV")
    parser.add_argument("--list", default="inventory/suppression-list.csv")
    parser.add_argument("--file", help="JSON file (default: stdin)")
    args = parser.parse_args()

    raw = Path(args.file).read_text(encoding="utf-8") if args.file else sys.stdin.read()
    if not raw.strip():
        print("No input.", file=sys.stderr)
        return 2

    events = load_events(raw)
    path = Path(args.list)
    path.parent.mkdir(parents=True, exist_ok=True)
    known = existing_emails(path)
    new_rows = []

    for ev in events:
        try:
            email = normalize(ev["email"])
            reason = ev.get("reason", "hard_bounce")
            if reason not in VALID_REASONS:
                print(f"skip unknown reason {reason} for {email}", file=sys.stderr)
                continue
            if email in known:
                print(f"exists {email}")
                continue
            row = {
                "email": email,
                "reason": reason,
                "code": str(ev.get("code", "")),
                "source": str(ev.get("source", "")),
                "timestamp": ev.get("timestamp")
                or datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }
            new_rows.append(row)
            known.add(email)
        except (KeyError, ValueError) as exc:
            print(f"skip bad event {ev!r}: {exc}", file=sys.stderr)

    write_header = not path.exists() or path.stat().st_size == 0
    with path.open("a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        if write_header:
            writer.writeheader()
        for row in new_rows:
            writer.writerow(row)
            print(f"added {row['email']} ({row['reason']})")

    print(f"{len(new_rows)} added, list size ~{len(known)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
