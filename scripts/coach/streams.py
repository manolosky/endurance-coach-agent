"""Load activity streams (Strava get_activity_streams output) into aligned lists."""

import json


def load_streams(path):
    """Read a streams JSON file. Accepts {"time": [...], "heart_rate": [...]} or a list of
    {"type": ..., "data": [...]} objects. Returns a dict of equal-length lists."""
    with open(path, encoding="utf-8") as fh:
        raw = json.load(fh)
    if isinstance(raw, list):
        raw = {item["type"]: item["data"] for item in raw}
    if "time" not in raw:
        raise ValueError("streams file has no 'time' series")
    n = len(raw["time"])
    out = {}
    for key, values in raw.items():
        if isinstance(values, list) and len(values) == n:
            out[key] = values
    return out


def sample_weights(time):
    """Seconds represented by each sample (forward difference; last sample = 1 s).
    Gaps longer than 10 s are capped at 1 s so pauses do not inflate zone time."""
    w = []
    for i in range(len(time)):
        dt = (time[i + 1] - time[i]) if i < len(time) - 1 else 1
        w.append(dt if 0 < dt <= 10 else 1)
    return w


def run_cadence_spm(cadence):
    """Strava run cadence is per leg: steps/min = value x 2."""
    return [c * 2 if c is not None else None for c in cadence]
