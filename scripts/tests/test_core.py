import csv

import analyze_session
import migrate_v1_to_v2
import traffic_light
import validate_data
from coach import laps as lapmod
from coach import load, metrics, privacy, rpe
from coach.schema import COLUMNS


def test_rpe_mapping():
    assert [rpe.rpe_from_label(x) for x in
            ["Very Easy", "easy", "Moderate", "HARD", "Max Effort"]] == [2, 4, 6, 8, 10]
    assert rpe.rpe_from_label("Unknown") is None
    assert rpe.rpe_from_label("") is None
    assert rpe.label_from_detail("x\nPerceived Effort: Very Easy\n") == "Very Easy"
    assert rpe.note_from_detail("Workout Note: tibia 2/10\n") == "tibia 2/10"


def test_zone_minutes_and_hrtss():
    time = list(range(3600))
    hr = [140] * 1800 + [160] * 1200 + [180] * 600
    assert metrics.zone_minutes(hr, time, 145, 170) == [30.0, 20.0, 10.0]
    assert metrics.hr_tss([170] * 3600, time, 170) == 100.0


def test_normalized_power_constant():
    assert metrics.normalized_power([200] * 120) == 200.0


def test_decoupling_zero_when_steady():
    assert metrics.decoupling_pct([200] * 600, [140] * 600) == 0.0


def test_over_cap_in_windows():
    time = list(range(100))
    hr = [150] * 10 + [140] * 90
    over, tot, pct = metrics.over_cap(hr, time, 145, [(0, 50)])
    assert (over, tot, pct) == (10, 50, 20.0)


def test_lap_comparison(synthetic_run):
    from coach.streams import load_streams
    s = load_streams(synthetic_run["streams"])
    laps = lapmod.load_laps(synthetic_run["laps"])
    rows, ok, worst = lapmod.compare_with_stream(laps, s)
    assert ok and worst == 0.0
    assert [r["power_stream_w"] for r in rows] == [180.0, 110.0, 180.0, 110.0]


def test_analyze_session_end_to_end(synthetic_run, capsys):
    out = analyze_session.main([
        "--streams", synthetic_run["streams"], "--zones", synthetic_run["zones"],
        "--sport", "run", "--laps", synthetic_run["laps"], "--detail", synthetic_run["detail"],
        "--plan-cap", "145", "--coros-duration-s", "600", "--coros-hr-avg", "139"])
    assert out["rpe_0_10"] == 2
    assert out["work_laps"] == [1, 3]
    assert out["seconds_over_cap"] == 80 and out["work_seconds"] == 480
    assert out["precision"]["lap_power_ok"] and out["precision"]["duration_ok"]
    assert out["cadence_avg"] == 147.6   # (156 spm x 480 s + 114 spm x 120 s) / 600 s
    assert out["power_avg_w"] == 166.0 and out["summary_source"] == "coros"   # COROS detail wins
    assert out["precision"]["power_avg_ok"]   # stream 166.0 vs COROS 166
    assert out["ground_contact_ms"] == 300.0  # work laps only (no detail value given)


def test_lap_tolerance_low_power():
    laps = [{"lapIndex": 1, "time": 10.0, "avgPower": 200, "avgHr": 140},
            {"lapIndex": 2, "time": 10.0, "avgPower": 100, "avgHr": 130}]
    stream = {"time": list(range(20)), "watts": [200] * 10 + [102.5] * 10,
              "heart_rate": [140] * 10 + [130] * 10}
    _rows, ok, worst = lapmod.compare_with_stream(laps, stream)
    assert ok and worst == 2.5   # 2.5 % but only 2.5 W: passes the 3 W floor


def test_parse_detail():
    from coach.detail import parse_detail
    d = parse_detail("Workout Time: 35:41\nAverage Heart Rate: 136 bpm\nAverage Power: 147 W\n"
                     "Average Ground Time: 394 ms\nVertical Oscillation: 8.5 cm\n"
                     "Perceived Effort: Moderate\nWorkout Note: ok\n")
    assert d["duration_s"] == 2141 and d["hr_avg_bpm"] == 136 and d["power_avg_w"] == 147
    assert d["vertical_osc_cm"] == 8.5 and d["rpe_0_10"] == 6 and d["workout_note"] == "ok"


def test_load_model():
    rows = [{"date": "2026-01-05", "status": "completed", "sport": "run", "tss": "50"},
            {"date": "2026-01-06", "status": "missed", "sport": "run", "tss": "40"}]
    d = load.daily_tss(rows)
    assert d["2026-01-05"]["run"] == 50 and "2026-01-06" not in d
    s = load.fitness_series(d, "2026-01-05", "2026-01-05")
    assert s[0]["ctl"] == round(50 / 42, 1) and s[0]["atl"] == round(50 / 7, 1)
    assert load.week_bounds("2026-W02") == ("2026-01-05", "2026-01-11")


def test_traffic_light():
    assert traffic_light.light(None, 50, 0, 48, 47)[0] == "no_data"
    assert traffic_light.light(60, 50, 0, 48, 47, 1.0)[0] == "green"
    assert traffic_light.light(45, 50, 0, 48, 47, 1.0)[0] == "yellow"
    assert traffic_light.light(45, 50, 2, 48, 47, 1.0)[0] == "red"
    assert traffic_light.light(45, 50, 0, 53, 47, 1.0)[0] == "red"
    assert traffic_light.light(60, 50, 0, 48, 47, 1.6)[0] == "red"


def test_privacy_patterns():
    # Fake values only, assembled at runtime so this file never contains a matching literal.
    at = "@"
    bad = ("mail me at nobody" + at + "example.invalid; at 12.3" + "45678, -98.7" + "65432; "
           "C:" + "\\Users\\" + "nobody\\vault; id " + "1" * 15 + "; serial " + "X99" + "ZZ" + "00000")
    kinds = {k for k, _ in privacy.scan_text(bad)}
    assert kinds == {"email address", "GPS coordinates", "Windows user path",
                     "long numeric ID", "device serial"}
    assert privacy.scan_text("Secret Name ran", ["secret name"])
    assert privacy.scan_text("analysis was patented", ["Ana", "Pat"]) == []   # whole words only
    assert privacy.scan_text("version 2.0.0, 2026-11-03, 42.195 km") == []
    assert privacy.forbidden_path("athlete/data/sessions.csv")
    assert not privacy.forbidden_path("templates/athlete/settings.yaml")


def test_migration_and_validation(tmp_path):
    v1 = tmp_path / "v1"; v1.mkdir()
    (v1 / "sesiones.csv").write_text(
        "sesion_id,fecha,semana,fase,deporte,tipo,estado,superficie,dolor_tibia_0_10,notas\n"
        "20260105-1,2026-01-05,2026-W02,readaptacion,carrera,trote_caminar,completada,cesped,2,x\n")
    (v1 / "semanas.csv").write_text("semana,decision,integracion\n2026-W02,mantener,ok\n")
    out = tmp_path / "v2"
    report = migrate_v1_to_v2.migrate(str(v1), str(out))
    assert report["sessions.csv"] == 1
    row = next(csv.DictReader(open(out / "sessions.csv")))
    assert (row["phase"], row["sport"], row["type"], row["status"], row["surface"]) == (
        "return_to_run", "run", "run_walk", "completed", "grass")
    assert (row["pain_0_10"], row["pain_site"]) == ("2", "shin")
    assert next(csv.DictReader(open(out / "weeks.csv")))["decision"] == "hold"
    assert validate_data.main([str(out)]) == 0


def test_validation_catches_errors(tmp_path):
    for name, cols in COLUMNS.items():
        (tmp_path / name).write_text(",".join(cols) + "\n")
    good = validate_data.main([str(tmp_path)])
    bad_row = ["x"] * len(COLUMNS["sessions.csv"])
    with open(tmp_path / "sessions.csv", "a") as fh:
        fh.write(",".join(bad_row) + "\n")
    assert good == 0 and validate_data.main([str(tmp_path)]) == 1


def test_acwr_needs_28_days_of_history():
    d = {"2026-01-05": {"run": 50.0, "bike": 0.0}}
    assert load.acwr(d, "2026-01-11", first_date="2026-01-05") is None
    assert load.acwr(d, "2026-02-01", first_date="2026-01-05") is not None
