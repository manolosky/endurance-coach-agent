"""Privacy rules for a public repository: nothing that identifies an athlete may be committed."""

import re

PATTERNS = {
    "email address": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+\.[A-Za-z0-9.-]+"),
    "GPS coordinates": re.compile(r"-?\d{1,3}\.\d{4,}\s*,\s*-?\d{1,3}\.\d{4,}"),
    "Windows user path": re.compile(r"[A-Za-z]:\\+Users\\+[A-Za-z0-9]"),
    "macOS user path": re.compile(r"/Users/[A-Za-z0-9]"),
    "long numeric ID": re.compile(r"(?<![\d.])\d{11,}(?![\d.])"),
    "device serial": re.compile(r"\b[A-Z]\d{2}[A-Z]{2}\d{5,}\b"),
}

# Addresses allowed in tracked files (generic, non-personal).
ALLOWED = {"noreply@anthropic.com"}

FORBIDDEN_PREFIXES = ("athlete/", "athlete-")


def scan_text(text, blocklist=()):
    """Return a list of (kind, match) findings in `text`."""
    found = []
    for kind, rx in PATTERNS.items():
        for m in rx.finditer(text):
            if m.group(0) not in ALLOWED:
                found.append((kind, m.group(0)))
    for term in blocklist:
        t = str(term).strip()
        # Whole-word, case-insensitive: "Ana" must not match "analysis".
        if t and re.search(r"(?<!\w)" + re.escape(t) + r"(?!\w)", text, re.IGNORECASE):
            found.append(("blocklisted term", term))
    return found


def forbidden_path(path):
    p = path.replace("\\", "/")
    return p.startswith(FORBIDDEN_PREFIXES) or p.endswith((".fit", ".tcx", ".gpx"))
