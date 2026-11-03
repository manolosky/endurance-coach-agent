"""Analyse one session from its Strava streams (+ optional COROS laps and detail).

  python3 scripts/analyze_session.py --streams streams.json --zones athlete/zones.yaml \
      --sport run --laps laps.json --detail detail.txt --plan-cap 145

Prints JSON with the sessions.csv fields it can compute and a precision report.
Rules (framework/data-schema.md 11, framework/methodology.md 11.3):
- Zones, TSS, EF, decoupling and over-cap time come from the 1 Hz stream.
- Session summaries the athlete sees on COROS (avg HR/power, Stryd metrics, RPE) come from
  the COROS detail when given, so stored values match the watch.
- Work laps = COROS section laps with running cadence (>= 140 spm) unless --work-laps is given.
  Over-cap time and decoupling use work laps only (walk breaks would distort them).
"""

import argparse
import json

import _bootstrap  # noqa: F401
import yaml

from coach import laps as lapmod
from coach import metrics
from coach.detail import parse_detail
from coach.streams import load_streams, run_cadence_spm, sample_weights

RUNNING_CADENCE_SPM = 140


def in_windows(time, windows):
    return [any(a <= t < b for a, b in windows) for t in time]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--streams", required=True)
    ap.add_argument("--zones", required=True)
    ap.add_argument("--sport", choices=["run", "bike"], required=True)
    ap.add_argument("--laps", help="COROS queryActivityLapData JSON")
    ap.add_argument("--detail", help="COROS getActivityDetail text")
    ap.add_argument("--plan-cap", type=float, help="planned HR cap (bpm)")
    ap.add_argument("--work-laps", help="comma-separated lap indexes counted as work")
    ap.add_argument("--coros-duration-s", type=float, help="override the COROS duration")
    ap.add_argument("--coros-hr-avg", type=float, help="override the COROS average HR")
    a = ap.parse_args(argv)

    zones = yaml.safe_load(open(a.zones, encoding="utf-8"))
    sz = zones[a.sport]
    z1_cap = sz.get("z1_cap_bpm")
    lthr = sz.get("lthr_bpm") or zones["run"].get("lthr_bpm")
    if not z1_cap or not lthr:
        raise SystemExit("zones.yaml needs z1_cap_bpm and lthr_bpm for this sport")

    s = load_streams(a.streams)
    t, hr = s["time"], s["heart_rate"]
    w = sample_weights(t)
    z = metrics.zone_minutes(hr, t, z1_cap, lthr)
    out = {
        "zones_version": str(zones.get("version")), "provisional": zones.get("provisional", []),
        "duration_s": t[-1] - t[0] + 1,
        "hr_avg_bpm": round(metrics.mean(hr, w), 1), "hr_max_bpm": max(h for h in hr if h),
        "min_z1": z[0], "min_z2": z[1], "min_z3": z[2],
        "tss": metrics.hr_tss(hr, t, lthr), "tss_type": "hrTSS", "if": metrics.if_hr(hr, t, lthr),
    }

    # Work windows from COROS section laps
    windows, laps = None, []
    if a.laps:
        laps = lapmod.load_laps(a.laps)
        if a.work_laps:
            sel = {int(x) for x in a.work_laps.split(",")}
        else:
            sel = {l["lapIndex"] for l in laps if (l.get("avgCadence") or 0) >= RUNNING_CADENCE_SPM}
        windows = [win for l, win in zip(laps, lapmod.windows(laps)) if l["lapIndex"] in sel]
        out["work_laps"] = sorted(sel)
    work_mask = in_windows(t, windows) if windows else s.get("moving")

    output = None
    if a.sport == "run" and s.get("watts"):
        output = s["watts"]
        out["power_avg_w"] = round(metrics.mean(output, w), 1)
        out["power_np_w"] = metrics.normalized_power(output)
        if s.get("cadence"):
            out["cadence_avg"] = round(metrics.mean(run_cadence_spm(s["cadence"]), w), 1)
    elif s.get("velocity_smooth"):
        output = [x * 3.6 if x is not None else None for x in s["velocity_smooth"]]
    if output is not None:
        sel_o = [o for o, m in zip(output, work_mask or [True] * len(t)) if m]
        sel_h = [h for h, m in zip(hr, work_mask or [True] * len(t)) if m]
        ef = metrics.efficiency(sel_o, sel_h)
        out["ef"] = round(ef, 3) if ef else None
        out["decoupling_pct"] = metrics.decoupling_pct(output, hr, work_mask)

    if a.plan_cap:
        over, tot, pct = metrics.over_cap(hr, t, a.plan_cap, windows)
        out.update({"seconds_over_cap": over, "work_seconds": tot, "pct_time_over_cap": pct,
                    "cap_respected": int(pct is not None and pct < 5)})

    prec = {}
    if laps:
        rows, ok, worst = lapmod.compare_with_stream(laps, s)
        out["laps"] = rows
        prec.update({"lap_power_ok": ok, "worst_lap_power_diff_pct_excl_first": worst})
        work_laps = [l for l in laps if l["lapIndex"] in set(out["work_laps"])] or laps
        out.update({k: v for k, v in lapmod.stryd_session_metrics(work_laps).items()
                    if k != "laps_seconds"})
        out.update(lapmod.session_values(a.laps))

    coros = parse_detail(open(a.detail, encoding="utf-8").read()) if a.detail else {}
    if a.coros_duration_s:
        coros["duration_s"] = a.coros_duration_s
    if a.coros_hr_avg:
        coros["hr_avg_bpm"] = a.coros_hr_avg
    if coros.get("duration_s"):
        d = round(100 * (out["duration_s"] - coros["duration_s"]) / coros["duration_s"], 2)
        prec.update({"duration_diff_pct": d, "duration_ok": abs(d) <= 1})
    if coros.get("hr_avg_bpm"):
        d = round(out["hr_avg_bpm"] - coros["hr_avg_bpm"], 1)
        prec.update({"hr_avg_diff_bpm": d, "hr_avg_ok": abs(d) <= 1})
    if coros.get("power_avg_w") and out.get("power_avg_w"):
        d = round(out["power_avg_w"] - coros["power_avg_w"], 1)
        prec.update({"power_avg_diff_w": d, "power_avg_ok": abs(d) <= max(3, 0.02 * coros["power_avg_w"])})
    out["precision"] = prec

    # COROS session values win for what the athlete sees on the watch
    for key in ("hr_avg_bpm", "power_avg_w", "cadence_avg", "ground_contact_ms", "vertical_osc_cm",
                "stride_length_m", "form_power_ratio_pct", "distance_km", "coros_load",
                "perceived_effort_label", "rpe_0_10", "workout_note"):
        if coros.get(key) is not None:
            out[key] = coros[key]
    out["summary_source"] = "coros" if coros else "stream"

    print(json.dumps(out, indent=2, ensure_ascii=False))
    return out


if __name__ == "__main__":
    main()
