"""Block personal data and credentials from entering the public repository.

  python3 scripts/privacy_check.py           # scan every tracked or untracked, non-ignored file
  python3 scripts/privacy_check.py --staged  # scan the staged content (pre-commit hook)

Checks: forbidden paths (athlete/, activity files, credential and connector config files),
API keys and tokens, emails, GPS coordinates, user home paths, long numeric IDs, device serials,
every term in athlete/settings.yaml -> privacy.blocklist and, with --staged, the commit identity.
"""

import os
import re
import subprocess
import sys

import _bootstrap  # noqa: F401

from coach.privacy import SECRET_PATTERNS, forbidden_path, is_noreply_email, scan_text

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HIDDEN_KINDS = {"blocklisted term", *SECRET_PATTERNS}


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, check=True).stdout


def git_paths(*args):
    return [p for p in git(*args, "-z").decode("utf-8").split("\0") if p]


def blocklist():
    path = os.path.join(ROOT, "athlete", "settings.yaml")
    if not os.path.exists(path):
        return []
    try:
        import yaml
        with open(path, encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
    except Exception as exc:
        # Failing open here would silently disable the athlete's blocklist.
        raise SystemExit(f"Privacy check FAILED: cannot read the blocklist ({exc})") from exc
    return [t for t in (data.get("privacy") or {}).get("blocklist") or [] if t]


def staged_files():
    return git_paths("diff", "--cached", "--name-only", "--diff-filter=ACMR")


def all_files():
    return git_paths("ls-files", "--cached", "--others", "--exclude-standard")


def staged_text(rel):
    # The index, not the working copy, is what gets committed.
    return git("show", f":{rel}").decode("utf-8", "replace")


def working_text(rel):
    with open(os.path.join(ROOT, rel), "rb") as fh:
        return fh.read().decode("utf-8", "replace")


def identity_problems():
    """Commit metadata is public: author and committer must use a no-reply address."""
    problems = []
    for var, role in (("GIT_AUTHOR_IDENT", "author"), ("GIT_COMMITTER_IDENT", "committer")):
        match = re.search(r"<([^>]*)>", git("var", var).decode("utf-8", "replace"))
        if not (match and is_noreply_email(match.group(1))):
            problems.append(f"commit {role} email is not a no-reply address (set user.email)")
    return problems


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    staged = "--staged" in argv
    read = staged_text if staged else working_text
    terms = blocklist()
    problems = identity_problems() if staged else []
    for rel in staged_files() if staged else all_files():
        if forbidden_path(rel):
            problems.append(f"{rel}: forbidden path (athlete data, activity file or credentials)")
            continue
        try:
            text = read(rel)
        except FileNotFoundError:
            continue
        for kind, match in scan_text(text, terms):
            shown = "<hidden>" if kind in HIDDEN_KINDS else match
            problems.append(f"{rel}: {kind}: {shown}")
    for p in problems:
        print("PRIVACY", p)
    print(f"Privacy check FAILED ({len(problems)})" if problems else "Privacy check OK")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
