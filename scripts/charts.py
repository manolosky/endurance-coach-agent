"""Weekly report charts (tasks/weekly-report.md), labels in the athlete's language.

  python3 scripts/charts.py athlete/data --week 2026-W45 --lang es --out work/charts
"""

import argparse
import csv
import os

import _bootstrap  # noqa: F401
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from coach.load import daily_tss, fitness_series, week_bounds  # noqa: E402

LABELS = {
    "en": {"volume": "Weekly volume", "run_km": "Run km", "run_min": "Run min",
           "bike_min": "Bike min", "ff": "Fitness and fatigue", "zones": "Zone distribution",
           "eff": "Aerobic efficiency (Z1 runs)", "pain": "Pain (0-10)"},
    "es": {"volume": "Volumen semanal", "run_km": "Km carrera", "run_min": "Min carrera",
           "bike_min": "Min bici", "ff": "Forma y fatiga", "zones": "Distribución por zonas",
           "eff": "Eficiencia aeróbica (rodajes Z1)", "pain": "Dolor (0-10)"},
}


def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0


def _save(fig, out, week, name):
    path = os.path.join(out, f"{week}-{name}.png")
    fig.set_size_inches(16, 9)
    fig.tight_layout()
    fig.savefig(path, dpi=100)
    plt.close(fig)
    return path


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("data")
    ap.add_argument("--week", required=True)
    ap.add_argument("--lang", default="en", choices=sorted(LABELS))
    ap.add_argument("--out", default="work/charts")
    a = ap.parse_args(argv)
    L = LABELS[a.lang]
    os.makedirs(a.out, exist_ok=True)
    rows = list(csv.DictReader(open(os.path.join(a.data, "sessions.csv"), encoding="utf-8")))
    done = [r for r in rows if r.get("status") in {"completed", "modified", "extra"}]
    made = []
    if not done:
        print("no completed sessions: no charts")
        return made

    weeks = sorted({r["week"] for r in done})
    run = {w: [r for r in done if r["week"] == w and r["sport"] != "bike"] for w in weeks}
    bike = {w: [r for r in done if r["week"] == w and r["sport"] == "bike"] for w in weeks}
    fig, ax = plt.subplots()
    x = range(len(weeks))
    ax.bar([i - 0.2 for i in x], [sum(_f(r["distance_km"]) for r in run[w]) for w in weeks],
           0.4, label=L["run_km"])
    ax2 = ax.twinx()
    ax2.plot(list(x), [sum(_f(r["duration_min"]) for r in run[w]) for w in weeks], "o-",
             label=L["run_min"])
    ax2.plot(list(x), [sum(_f(r["duration_min"]) for r in bike[w]) for w in weeks], "s--",
             label=L["bike_min"])
    ax.set_xticks(list(x), weeks)
    ax.set_xlim(-0.8, len(weeks) - 0.2)
    ax.set_ylabel(L["run_km"])
    ax2.set_ylabel("min")
    ax2.set_ylim(bottom=0)
    ax.set_title(L["volume"])
    fig.legend(loc="upper right", bbox_to_anchor=(0.98, 0.95))
    made.append(_save(fig, a.out, a.week, "weekly-volume"))

    _, end = week_bounds(a.week)
    series = fitness_series(daily_tss(rows), min(r["date"] for r in done), end)
    fig, ax = plt.subplots()
    d = [s["date"] for s in series]
    for k in ("ctl", "atl", "tsb"):
        ax.plot(d, [s[k] for s in series], label=k.upper())
    ax.set_title(L["ff"])
    ax.legend()
    ax.tick_params(axis="x", rotation=45)
    made.append(_save(fig, a.out, a.week, "fitness-fatigue"))

    z = [sum(_f(r[k]) for r in done if r["week"] == a.week) for k in ("min_z1", "min_z2", "min_z3")]
    if sum(z):
        fig, ax = plt.subplots()
        ax.bar(["Z1", "Z2", "Z3"], [100 * v / sum(z) for v in z])
        ax.set_ylabel("%")
        ax.set_title(L["zones"])
        made.append(_save(fig, a.out, a.week, "zones"))

    pain = [(r["date"], _f(r["pain_0_10"])) for r in done if r.get("pain_0_10")]
    if pain:
        fig, ax = plt.subplots()
        ax.plot([p[0] for p in pain], [p[1] for p in pain], "o-")
        ax.set_ylim(0, 10)
        ax.set_title(L["pain"])
        made.append(_save(fig, a.out, a.week, "pain"))

    for m in made:
        print(m)
    return made


if __name__ == "__main__":
    main()
