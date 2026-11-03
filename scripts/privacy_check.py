"""Block anything personal from entering the public repository.

  python3 scripts/privacy_check.py           # scan every tracked/untracked file of the repo
  python3 scripts/privacy_check.py --staged  # scan only staged files (pre-commit hook)

Checks: forbidden paths (athlete/, FIT/TCX/GPX), emails, GPS coordinates, user home paths,
long numeric IDs, device serials, and every term in athlete/settings.yaml -> privacy.blocklist.
"""

import os
import subprocess
import sys

import _bootstrap  # noqa: F401

from coach.privacy import forbidden_path, scan_text

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {".git", "athlete", "__pycache__", ".pytest_cache", ".venv"}


def blocklist():
    path = os.path.join(ROOT, "athlete", "settings.yaml")
    if not os.path.exists(path):
        return []
    try:
        import yaml
        data = yaml.safe_load(open(path, encoding="utf-8")) or {}
    except Exception:
        return []
    return [t for t in (data.get("privacy") or {}).get("blocklist") or [] if t]


def staged_files():
    out = subprocess.run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
                         cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return [p for p in out.splitlines() if p]


def all_files():
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            yield os.path.relpath(os.path.join(base, f), ROOT)


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    files = staged_files() if "--staged" in argv else list(all_files())
    terms = blocklist()
    problems = []
    for rel in files:
        if forbidden_path(rel):
            problems.append(f"{rel}: forbidden path (athlete data or activity file)")
            continue
        try:
            text = open(os.path.join(ROOT, rel), encoding="utf-8").read()
        except (UnicodeDecodeError, FileNotFoundError):
            continue
        for kind, match in scan_text(text, terms):
            shown = match if kind != "blocklisted term" else "<blocklisted>"
            problems.append(f"{rel}: {kind}: {shown}")
    for p in problems:
        print("PRIVACY", p)
    print("Privacy check OK" if not problems else f"Privacy check FAILED ({len(problems)})")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
