"""Daily fatigue traffic light (framework/methodology.md 8.2).

  python3 scripts/traffic_light.py --hrv 52 --range-min 48 --range-max 66 --low-days 0 \
      --rhr 50 --rhr-avg 48 --ratio 1.1
"""

import argparse
import json


def light(hrv, range_min, low_days, rhr, rhr_avg, ratio=None):
    """Return (light, reasons). `low_days` = consecutive previous days with HRV below range."""
    if hrv is None or rhr is None:
        return "no_data", ["missing overnight HRV or resting HR"]
    hrv_low = range_min is not None and hrv < range_min
    streak = (low_days + 1) if hrv_low else 0
    rhr_high = rhr_avg is not None and rhr >= rhr_avg + 5
    reasons = []
    if streak >= 3:
        reasons.append(f"HRV below range {streak} days in a row")
    if hrv_low and rhr_high:
        reasons.append("low HRV and resting HR >= average + 5 bpm")
    if ratio is not None and ratio > 1.5:
        reasons.append(f"load ratio {ratio} > 1.5")
    if reasons:
        return "red", reasons
    if hrv_low:
        reasons.append(f"HRV below range ({streak} day(s))")
    if rhr_high:
        reasons.append("resting HR >= average + 5 bpm")
    if ratio is not None and ratio > 1.3:
        reasons.append(f"load ratio {ratio} in 1.3-1.5")
    return ("yellow", reasons) if reasons else ("green", [])


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--hrv", type=float)
    ap.add_argument("--range-min", type=float)
    ap.add_argument("--range-max", type=float)
    ap.add_argument("--low-days", type=int, default=0)
    ap.add_argument("--rhr", type=float)
    ap.add_argument("--rhr-avg", type=float)
    ap.add_argument("--ratio", type=float)
    a = ap.parse_args(argv)
    state, why = light(a.hrv, a.range_min, a.low_days, a.rhr, a.rhr_avg, a.ratio)
    print(json.dumps({"light": state, "reasons": why}))
    return state


if __name__ == "__main__":
    main()
