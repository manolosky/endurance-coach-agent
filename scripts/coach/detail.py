"""Parse COROS getActivityDetail text into schema fields (COROS session values win for summaries)."""

import re

from .rpe import rpe_from_label

_NUM = r"([0-9]+(?:\.[0-9]+)?)"
FIELDS = {
    "hr_avg_bpm": rf"Average Heart Rate:\s*{_NUM}",
    "power_avg_w": rf"Average Power:\s*{_NUM}",
    "cadence_avg": rf"Average Cadence:\s*{_NUM}",
    "ground_contact_ms": rf"Average Ground Time:\s*{_NUM}",
    "vertical_osc_cm": rf"Vertical Oscillation:\s*{_NUM}",
    "stride_length_m": rf"Average Stride Length:\s*{_NUM}",
    "form_power_ratio_pct": rf"FP Ratio:\s*{_NUM}",
    "distance_km": rf"Distance:\s*{_NUM}\s*km",
    "coros_load": rf"Training Load:\s*{_NUM}",
}


def _duration_s(text, label):
    m = re.search(rf"{label}:\s*(?:(\d+):)?(\d+):(\d+)", text)
    if not m:
        return None
    h, mi, s = (int(x) if x else 0 for x in m.groups())
    return h * 3600 + mi * 60 + s


def parse_detail(text):
    out = {}
    for key, rx in FIELDS.items():
        m = re.search(rx, text or "")
        if m:
            out[key] = float(m.group(1))
    out["duration_s"] = _duration_s(text or "", "Workout Time")
    m = re.search(r"Perceived Effort:\s*([^\n]+)", text or "")
    out["perceived_effort_label"] = m.group(1).strip() if m else None
    out["rpe_0_10"] = rpe_from_label(out["perceived_effort_label"])
    m = re.search(r"Workout Note:\s*([^\n]+)", text or "")
    out["workout_note"] = m.group(1).strip() if m else None
    return out
