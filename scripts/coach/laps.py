"""COROS lap data (queryActivityLapData JSON) laid over a 1 Hz stream."""

import json

SECTION_GROUP = 10   # laps by workout section
KM_GROUP = 2         # laps by km
SESSION_GROUP = -1   # one lap = whole session (values COROS shows)


def load_laps(path, group=SECTION_GROUP):
    """Return the laps of one group as dicts with seconds, power, HR, Stryd metrics."""
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    for g in data.get("lapGroups", []):
        if g.get("type") == group:
            return g["laps"]
    return []


def windows(laps):
    """Cumulative [start, end) seconds of each lap."""
    out, t = [], 0.0
    for lap in laps:
        dur = float(lap["time"])
        out.append((t, t + dur))
        t += dur
    return out


def compare_with_stream(laps, stream, tol_pct=2.0, tol_w=3.0):
    """Per-lap power and HR: COROS lap value vs stream mean over the same window.
    A lap passes if it is within `tol_pct` OR `tol_w` (low-power laps such as walks)."""
    t, w, hr = stream["time"], stream.get("watts"), stream.get("heart_rate")
    rows = []
    for lap, (a, b) in zip(laps, windows(laps)):
        idx = [i for i, ti in enumerate(t) if a <= ti < b]
        if not idx:
            continue
        sw = sum(w[i] or 0 for i in idx) / len(idx) if w else None
        sh = sum(hr[i] or 0 for i in idx) / len(idx) if hr else None
        cw = lap.get("avgPower")
        diff = (sw - cw) if (sw is not None and cw) else None
        rows.append({
            "lap": lap.get("lapIndex"), "start_s": a, "duration_s": b - a,
            "power_coros_w": cw, "power_stream_w": round(sw, 1) if sw is not None else None,
            "power_diff_w": round(diff, 1) if diff is not None else None,
            "power_diff_pct": round(100 * diff / cw, 1) if diff is not None else None,
            "hr_coros_bpm": lap.get("avgHr"), "hr_stream_bpm": round(sh, 1) if sh else None,
            "hr_max_bpm": lap.get("maxHr"),
        })
    checked = [r for r in rows[1:] if r["power_diff_pct"] is not None]   # lap 1 has start offset
    failing = [r for r in checked
               if abs(r["power_diff_pct"]) > tol_pct and abs(r["power_diff_w"]) > tol_w]
    worst = max((abs(r["power_diff_pct"]) for r in checked), default=0.0)
    return rows, not failing, worst


def stryd_session_metrics(laps):
    """Duration-weighted Stryd metrics over section laps, in schema units.
    Fallback only: session values from COROS getActivityDetail take precedence, because
    walking laps distort lap averages and COROS is the reference the athlete sees."""
    tot = sum(float(l["time"]) for l in laps) or 1.0

    def wavg(key, scale=1.0):
        vals = [(float(l[key]), float(l["time"])) for l in laps if l.get(key)]
        s = sum(d for _, d in vals)
        return round(sum(v * d for v, d in vals) / s * scale, 2) if s else None

    return {
        "ground_contact_ms": wavg("groundTime"),
        "vertical_osc_cm": wavg("strideHeight", 0.1),
        "stride_length_m": wavg("avgStrideLength", 0.01),
        "leg_stiffness_kn_m": wavg("legStiffness", 0.1),
        "laps_seconds": tot,
    }


def session_values(path):
    """Whole-session Stryd values from the COROS session lap (group -1), in schema units."""
    tot = load_laps(path, SESSION_GROUP)
    if not tot:
        return {}
    lap = tot[0]
    out = {}
    if lap.get("legStiffness"):
        out["leg_stiffness_kn_m"] = round(float(lap["legStiffness"]) / 10, 2)
    if lap.get("groundTime"):
        out["ground_contact_ms"] = float(lap["groundTime"])
    return out
