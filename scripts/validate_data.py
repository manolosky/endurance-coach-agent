"""Validate athlete/data/*.csv against the v2 schema. Exit code 1 on any error.

  python3 scripts/validate_data.py athlete/data
"""

import csv
import os
import sys

import _bootstrap  # noqa: F401

from coach.schema import BOOLEANS, COLUMNS, ENUMS, TEXT_COLUMNS


def validate_file(path, name):
    errors = []
    with open(path, encoding="utf-8", newline="") as fh:
        reader = csv.reader(fh)
        try:
            header = next(reader)
        except StopIteration:
            return [f"{name}: empty file (header required)"]
        if header != COLUMNS[name]:
            missing = [c for c in COLUMNS[name] if c not in header]
            extra = [c for c in header if c not in COLUMNS[name]]
            errors.append(f"{name}: header mismatch (missing {missing}, unexpected {extra})")
            return errors
        for i, row in enumerate(reader, start=2):
            if len(row) != len(header):
                errors.append(f"{name}:{i}: {len(row)} fields, expected {len(header)}")
                continue
            for col, val in zip(header, row):
                if val == "":
                    continue
                if (name, col) in ENUMS and val not in ENUMS[(name, col)]:
                    errors.append(f"{name}:{i}: {col}={val!r} not in {sorted(ENUMS[(name, col)])}")
                elif (name, col) in BOOLEANS and val not in {"0", "1"}:
                    errors.append(f"{name}:{i}: {col}={val!r} must be 0 or 1")
                elif col not in TEXT_COLUMNS and (name, col) not in ENUMS:
                    try:
                        float(val)
                    except ValueError:
                        errors.append(f"{name}:{i}: {col}={val!r} is not a number")
    return errors


def main(argv=None):
    folder = (argv or sys.argv[1:] or ["athlete/data"])[0]
    errors = []
    for name in COLUMNS:
        path = os.path.join(folder, name)
        if not os.path.exists(path):
            errors.append(f"{name}: missing")
            continue
        errors += validate_file(path, name)
    for e in errors:
        print("ERROR", e)
    print("OK" if not errors else f"{len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
