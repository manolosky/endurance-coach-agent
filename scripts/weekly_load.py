"""Weekly load summary (weeks.csv fields) from sessions.csv.

  python3 scripts/weekly_load.py athlete/data/sessions.csv --week 2026-W45
"""

import argparse
import csv
import json

import _bootstrap  # noqa: F401

from coach.load import week_summary


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("sessions")
    ap.add_argument("--week", required=True)
    ap.add_argument("--since", help="first date of the load history (default: first session)")
    a = ap.parse_args(argv)
    rows = list(csv.DictReader(open(a.sessions, encoding="utf-8")))
    first = a.since or min((r["date"] for r in rows), default=None)
    out = week_summary(rows, a.week, first)
    print(json.dumps(out, indent=2))
    return out


if __name__ == "__main__":
    main()
