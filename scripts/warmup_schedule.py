#!/usr/bin/env python3
"""Print a gradual IP/domain warmup calendar."""

from __future__ import annotations

import argparse
from datetime import date, timedelta


def curve(day: int, days: int, start: int, target: int) -> int:
    if days <= 1:
        return target
    t = day / (days - 1)
    eased = t * t * (3 - 2 * t)
    return max(start, int(round(start + (target - start) * eased)))


def main() -> int:
    parser = argparse.ArgumentParser(description="Build an IP warmup schedule")
    parser.add_argument("--days", type=int, default=28)
    parser.add_argument("--start", type=int, default=50, help="Day-1 cap")
    parser.add_argument("--target-per-day", type=int, required=True)
    parser.add_argument("--from-date", default=None, help="YYYY-MM-DD (default: today)")
    args = parser.parse_args()

    start_date = date.fromisoformat(args.from_date) if args.from_date else date.today()
    print(f"# Warmup {args.days} days  {args.start} → {args.target_per_day}/day")
    print("# Hold or cut 50% if hard bounce > 2% or complaints > 0.1%\n")
    print(f"{'Day':<6}{'Date':<14}{'Cap':>10}  Notes")
    print("-" * 52)
    for i in range(args.days):
        cap = curve(i, args.days, args.start, args.target_per_day)
        day_date = start_date + timedelta(days=i)
        note = ""
        if i < 3:
            note = "staff + seeds + most-engaged only"
        elif i < 7:
            note = "recent active users"
        elif i < 14:
            note = "broad engaged cohort"
        elif i < 21:
            note = "add a slice of marketing"
        else:
            note = "approach target if metrics stay green"
        print(f"{i + 1:<6}{day_date.isoformat():<14}{cap:>10}  {note}")

    total = sum(curve(i, args.days, args.start, args.target_per_day) for i in range(args.days))
    print("-" * 52)
    print(f"Period total (if every cap is used): {total:,}")
    print(
        f"Day-{args.days} / target ratio: "
        f"{curve(args.days - 1, args.days, args.start, args.target_per_day) / max(args.target_per_day, 1):.0%}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
