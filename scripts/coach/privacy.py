"""Privacy rules for a public repository: nothing that identifies an athlete or grants access
to an account may be committed."""

import re

PATTERNS = {
    "email address": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+\.[A-Za-z0-9.-]+"),
    "GPS coordinates": re.compile(r"-?\d{1,3}\.\d{4,}\s*,\s*-?\d{1,3}\.\d{4,}"),
    "Windows user path": re.compile(r"[A-Za-z]:\\+Users\\+[A-Za-z0-9]"),
    "macOS user path": re.compile(r"/Users/[A-Za-z0-9]"),
    "Linux user path": re.compile(r"(?<![\w.])/home/[A-Za-z0-9._-]+"),
    "long numeric ID": re.compile(r"(?<![\d.])\d{11,}(?![\d.])"),
    "device serial": re.compile(r"\b[A-Z]\d{2}[A-Z]{2}\d{5,}\b"),
}

# These grant access to an account, so a match is never echoed to a terminal or a log.
SECRET_PATTERNS = {
    "GitHub token": re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})"),
    "API key": re.compile(
        r"\b(?:sk-[A-Za-z0-9_-]{16,}|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{30,}"
        r"|xox[abprs]-[A-Za-z0-9-]{10,}|hf_[A-Za-z0-9]{20,}|npm_[A-Za-z0-9]{20,})"),
    "private key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "JSON web token": re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}"),
    "bearer token": re.compile(r"\bbearer\s+[A-Za-z0-9._~+/-]{16,}", re.IGNORECASE),
    "credential assignment": re.compile(
        r"\b(?:api[_-]?key|access[_-]?token|refresh[_-]?token|auth[_-]?token|client[_-]?secret"
        r"|password|passwd)\b[\"']?\s*[:=]\s*[\"']?[^\s\"']{8,}", re.IGNORECASE),
    "URL with credentials": re.compile(r"\b[a-z][a-z0-9+.-]*://[^/\s:@]+:[^/\s@]+@", re.IGNORECASE),
    "signed or tokenised URL": re.compile(
        r"https?://\S+[?&](?:x-amz-signature|signature|sig|token|access_token|api_key|apikey|code)"
        r"=[^&\s]{8,}", re.IGNORECASE),
}

# Addresses allowed in tracked files (generic, non-personal).
ALLOWED = {"noreply@anthropic.com"}

# Commit metadata is public: only GitHub's no-reply addresses keep a real email out of it.
NOREPLY_SUFFIX = "@users.noreply.github.com"

FORBIDDEN_PREFIXES = ("athlete/", "athlete-", "work/", "smoke/", "exports/", "reports/")
FORBIDDEN_SUFFIXES = (".fit", ".tcx", ".gpx", ".fit.gz", ".tcx.gz", ".gpx.gz",
                      ".pem", ".key", ".p12", ".pfx")
# Credential stores and connector configuration, which can embed tokens (any directory).
FORBIDDEN_NAMES = re.compile(
    r"^(?:\.env(?:\..+)?|\.mcp\.json|claude_desktop_config\.json|credentials.*\.json"
    r"|token.*\.json|id_(?:rsa|ed25519|ecdsa)(?:\.pub)?|\.netrc|\.npmrc|\.pypirc)$")


def scan_text(text, blocklist=()):
    """Return a list of (kind, match) findings in `text`."""
    found = []
    for kind, rx in {**PATTERNS, **SECRET_PATTERNS}.items():
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
    p = path.replace("\\", "/").lower()
    parts = p.split("/")
    return (p.startswith(FORBIDDEN_PREFIXES) or p.endswith(FORBIDDEN_SUFFIXES)
            or ".claude" in parts or bool(FORBIDDEN_NAMES.match(parts[-1])))


def is_noreply_email(email):
    return email.lower().endswith(NOREPLY_SUFFIX)
