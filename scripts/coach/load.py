"""Training load model: CTL, ATL, TSB, ACWR from sessions.csv rows."""

import datetime as dt
from collections import defaultdict


def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def daily_tss(rows):
    """{date: {"run": tss, "bike": tss}} from completed/modified/extra sessions."""
    out = defaultdict(lambda: {"run": 0.0, "bike": 0.0})
    for r in rows:
        if r.get("status") not in {"completed", "modified", "extra"}:
            continue
        tss = _f(r.get("tss"))
        if tss is None:
            continue
        sport = "bike" if r.get("sport") == "bike" else "run"
        out[r["date"]][sport] += tss
    return out


def fitness_series(daily, start, end, ctl0=0.0, atl0=0.0):
    """Exponential CTL (42 d) and ATL (7 d) from `start` to `end` inclusive (ISO dates).
    TSB(d) = CTL(d-1) - ATL(d-1)."""
    d0, d1 = dt.date.fromisoformat(start), dt.date.fromisoformat(end)
    ctl, atl, series = ctl0, atl0, []
    d = d0
    while d <= d1:
        tss = sum(daily.get(d.isoformat(), {}).values())
        tsb = ctl - atl
        ctl += (tss - ctl) / 42
        atl += (tss - atl) / 7
        series.append({"date": d.isoformat(), "tss": round(tss, 1), "ctl": round(ctl, 1),
                       "atl": round(atl, 1), "tsb": round(tsb, 1)})
        d += dt.timedelta(days=1)
    return series


def acwr(daily, end, first_date=None):
    """7-day TSS sum / (28-day TSS sum / 4). None if the 28-day sum is 0 or if the load history
    (from `first_date`) is shorter than 28 days: an incomplete chronic window is undefined."""
    e = dt.date.fromisoformat(end)
    if first_date and (e - dt.date.fromisoformat(first_date)).days < 27:
        return None
    days = [(e - dt.timedelta(days=i)).isoformat() for i in range(28)]
    s28 = sum(sum(daily.get(d, {}).values()) for d in days)
    s7 = sum(sum(daily.get(d, {}).values()) for d in days[:7])
    return round(s7 / (s28 / 4), 2) if s28 else None


def week_bounds(iso_week):
    """'2026-W45' -> ('2026-11-02', '2026-11-08')."""
    year, w = iso_week.split("-W")
    monday = dt.date.fromisocalendar(int(year), int(w), 1)
    return monday.isoformat(), (monday + dt.timedelta(days=6)).isoformat()


def week_summary(rows, iso_week, first_date=None):
    start, end = week_bounds(iso_week)
    wk = [r for r in rows if start <= r["date"] <= end]
    done = [r for r in wk if r.get("status") in {"completed", "modified", "extra"}]
    planned = [r for r in wk if r.get("status") != "extra"]

    def s(rs, key):
        return round(sum(_f(r.get(key)) or 0 for r in rs), 1)

    run = [r for r in done if r.get("sport") in {"run", "strength"}]
    bike = [r for r in done if r.get("sport") == "bike"]
    z = [s(done, "min_z1"), s(done, "min_z2"), s(done, "min_z3")]
    zt = sum(z) or None
    daily = daily_tss(rows)
    series = fitness_series(daily, first_date or start, end)
    last = series[-1]
    history_days = (dt.date.fromisoformat(end) - dt.date.fromisoformat(first_date or start)).days + 1
    return {
        "week": iso_week, "start_date": start,
        "sessions_planned": len(planned), "sessions_done": len(done),
        "compliance_pct": round(100 * len(done) / len(planned), 0) if planned else None,
        "run_min": s(run, "duration_min"), "run_km": s(run, "distance_km"),
        "bike_min": s(bike, "duration_min"), "bike_km": s(bike, "distance_km"),
        "pct_z1": round(100 * z[0] / zt, 1) if zt else None,
        "pct_z2": round(100 * z[1] / zt, 1) if zt else None,
        "pct_z3": round(100 * z[2] / zt, 1) if zt else None,
        "tss_run": s(run, "tss"), "tss_bike": s(bike, "tss"),
        "tss_total": round(s(run, "tss") + s(bike, "tss"), 1),
        "ctl": last["ctl"], "atl": last["atl"], "tsb": last["tsb"], "acwr": acwr(daily, end, first_date or start),
        "load_history_days": history_days,
    }
