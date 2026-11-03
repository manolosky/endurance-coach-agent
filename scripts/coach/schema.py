"""Machine-readable data schema (v2). Human documentation: framework/data-schema.md."""

SCHEMA_VERSION = 2

COLUMNS = {
    "sessions.csv": [
        "session_id", "date", "week", "phase", "sport", "type", "status", "change_reason",
        "plan_name", "plan_duration_min", "plan_hr_cap_bpm", "plan_power_min_w", "plan_power_max_w",
        "source", "activity_id", "start_time", "surface", "gear_id", "temperature_c",
        "duration_min", "elapsed_min", "distance_km", "elevation_gain_m",
        "hr_avg_bpm", "hr_max_bpm", "power_avg_w", "power_np_w", "pace_avg_s_km", "speed_avg_kmh",
        "cadence_avg", "ground_contact_ms", "vertical_osc_cm", "stride_length_m",
        "leg_stiffness_kn_m", "form_power_ratio_pct",
        "min_z1", "min_z2", "min_z3", "tss", "tss_type", "if", "decoupling_pct", "ef",
        "pct_time_over_cap", "cap_respected", "failed_recovery", "coros_load",
        "strava_relative_effort", "rpe_0_10", "srpe", "pain_0_10", "pain_site", "issues",
        "carbs_g_h", "strength_done", "zones_version", "notes",
    ],
    "intervals.csv": [
        "session_id", "n", "type", "duration_s", "distance_m", "power_avg_w", "pace_avg_s_km",
        "hr_avg_bpm", "hr_end_bpm", "pct_cp", "pct_lthr", "cap_exceeded",
    ],
    "strength.csv": [
        "session_id", "date", "block", "exercise", "sets", "reps", "seconds", "load_kg", "band",
        "rpe_0_10", "notes",
    ],
    "weeks.csv": [
        "week", "start_date", "phase", "phase_week", "is_deload", "sessions_planned",
        "sessions_done", "compliance_pct", "run_min", "run_km", "bike_min", "bike_km",
        "strength_sessions", "pct_z1", "pct_z2", "pct_z3", "tss_run", "tss_bike", "tss_total",
        "ctl", "atl", "tsb", "acwr", "run_km_change_pct", "ef_control_run",
        "long_run_decoupling_pct", "hrv_avg_ms", "rhr_avg_bpm", "sleep_avg_h", "days_green",
        "days_yellow", "days_red", "pain_max", "weight_kg", "feeling_1_5", "decision",
        "rationale", "integration",
    ],
    "daily.csv": [
        "date", "source", "hrv_ms", "hrv_range_min_ms", "hrv_range_max_ms", "hrv_7d_avg_ms",
        "rhr_bpm", "rhr_30d_avg_bpm", "sleep_h", "sleep_score", "temp_dev_c", "load_ratio",
        "light", "planned_session", "action",
    ],
    "tests.csv": [
        "test_id", "date", "session_id", "test", "parameter", "value", "unit", "previous_value",
        "conditions", "valid", "notes",
    ],
    "measurements.csv": ["date", "type", "value", "unit", "source", "reference_range", "notes"],
    "gear.csv": [
        "gear_id", "type", "model", "use", "start_date", "initial_km", "limit_km",
        "retired_date", "notes",
    ],
}

ENUMS = {
    ("sessions.csv", "phase"): {"return_to_run", "base", "build", "specific", "taper", "transition"},
    ("sessions.csv", "sport"): {"run", "bike", "strength"},
    ("sessions.csv", "type"): {
        "easy_z1", "run_walk", "norwegian_threshold", "long_run", "marathon_pace", "x_factor",
        "recovery", "test", "strength", "race",
    },
    ("sessions.csv", "status"): {"completed", "modified", "missed", "extra"},
    ("sessions.csv", "surface"): {"grass", "dirt", "track", "asphalt", "mixed", "road"},
    ("sessions.csv", "source"): {"coros", "strava", "manual"},
    ("sessions.csv", "tss_type"): {"rTSS", "hrTSS", "sRPE"},
    ("weeks.csv", "phase"): {"return_to_run", "base", "build", "specific", "taper", "transition"},
    ("weeks.csv", "decision"): {"push", "hold", "ease"},
    ("weeks.csv", "integration"): {"ok", "partial", "fallback"},
    ("intervals.csv", "type"): {"warmup", "work", "recovery", "cooldown"},
    ("daily.csv", "light"): {"green", "yellow", "red", "no_data"},
    ("tests.csv", "test"): {
        "bike_drift", "control_run", "threshold_30min", "cp_3_9", "race", "estimate", "declared",
    },
    ("tests.csv", "parameter"): {
        "lthr", "threshold_pace", "threshold_power", "cp", "z1_cap", "ef", "hr_max",
    },
    ("gear.csv", "type"): {"shoe", "bike"},
}

BOOLEANS = {
    ("sessions.csv", "cap_respected"), ("sessions.csv", "failed_recovery"),
    ("sessions.csv", "strength_done"), ("weeks.csv", "is_deload"),
    ("intervals.csv", "cap_exceeded"), ("tests.csv", "valid"),
}

TEXT_COLUMNS = {
    "session_id", "date", "week", "change_reason", "plan_name", "activity_id", "start_time",
    "gear_id", "pain_site", "issues", "zones_version", "notes", "start_date", "rationale",
    "exercise", "block", "band", "source", "planned_session", "action", "test_id", "unit",
    "conditions", "model", "use", "retired_date", "reference_range", "type", "parameter",
    "phase", "sport", "status", "surface", "tss_type", "decision", "integration", "light",
}
