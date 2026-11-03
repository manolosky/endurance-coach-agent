"""COROS perceived effort (5 levels) -> RPE 0-10. See framework/data-schema.md 3.1."""

import re

COROS_TO_RPE = {
    "very easy": 2,
    "easy": 4,
    "moderate": 6,
    "hard": 8,
    "very hard": 10,
    "max effort": 10,
    "maximum effort": 10,
    "max": 10,
}


def rpe_from_label(label):
    """Return the RPE for a COROS label, or None if unknown/empty."""
    if not label:
        return None
    return COROS_TO_RPE.get(" ".join(label.strip().lower().split()))


def label_from_detail(text):
    """Extract the 'Perceived Effort' label from getActivityDetail text output."""
    m = re.search(r"Perceived Effort:\s*([^\n]+)", text or "")
    return m.group(1).strip() if m else None


def note_from_detail(text):
    """Extract the 'Workout Note' from getActivityDetail text output."""
    m = re.search(r"Workout Note:\s*([^\n]+)", text or "")
    return m.group(1).strip() if m else None
