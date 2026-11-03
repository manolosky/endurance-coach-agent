"""Create athlete/ from templates/athlete/ (like `npm install` creates node_modules).
Never overwrites existing files. CSV headers come from coach/schema.py.

  python3 scripts/init_athlete.py [target_dir]
"""

import csv
import os
import shutil
import sys

import _bootstrap  # noqa: F401

from coach.schema import COLUMNS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES = os.path.join(ROOT, "templates", "athlete")


def init(target):
    created = []
    for base, _dirs, files in os.walk(TEMPLATES):
        rel = os.path.relpath(base, TEMPLATES)
        dest_dir = os.path.normpath(os.path.join(target, rel))
        os.makedirs(dest_dir, exist_ok=True)
        for f in files:
            if f == ".gitkeep":
                continue
            dest = os.path.join(dest_dir, f)
            if not os.path.exists(dest):
                shutil.copyfile(os.path.join(base, f), dest)
                created.append(os.path.relpath(dest, target))
    data = os.path.join(target, "data")
    os.makedirs(data, exist_ok=True)
    for name, cols in COLUMNS.items():
        dest = os.path.join(data, name)
        if not os.path.exists(dest):
            with open(dest, "w", encoding="utf-8", newline="") as fh:
                csv.writer(fh, lineterminator="\n").writerow(cols)
            created.append(os.path.join("data", name))
    return created


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "athlete")
    made = init(target)
    print(f"{len(made)} file(s) created in {target}" if made else "athlete/ already complete")
    for m in made:
        print("  +", m)
