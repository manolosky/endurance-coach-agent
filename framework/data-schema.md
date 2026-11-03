# Data schema (v2)

Derived metrics and athlete-declared data. Raw data lives in COROS and Strava; the agent stores what it computes and what the athlete reports. Files live in `athlete/data/` (never in git). The machine-readable column list is `scripts/coach/schema.py`; this document explains it.

## 1. Conventions

- **Format:** CSV, UTF-8, `,` separator, `.` decimal, quoted text when it contains commas.
- **Dates:** ISO `YYYY-MM-DD`; times `HH:MM` in `settings.yaml → timezone`; ISO weeks `2026-W45`.
- **Empty = not available.** Never `0` for "not measured".
- **Units in the column name** (`_min`, `_km`, `_bpm`, `_w`, `_s_km`…). Pace in **seconds per km** (4:30/km = 270).
- **Booleans:** `1` / `0`.
- **Append-only.** Corrections edit the row and say so in `notes`; rows are never deleted.
- **Enums in English, lowercase, snake_case** (section 12). Free text (`notes`, `issues`, `plan_name`) is kept as written.
- **Zones version:** each session stores the `zones.yaml → version` used (`zones_version`).
- **Validation:** `python3 scripts/validate_data.py athlete/data` before every write.

## 2. Files

| File | One row per | Key | Links to |
|---|---|---|---|
| `sessions.csv` | Session (planned and/or done) | `session_id` | weeks, intervals, strength, gear |
| `intervals.csv` | Rep or lap of a quality session or test | `session_id` + `n` | sessions |
| `strength.csv` | Exercise done | `session_id` + `exercise` | sessions |
| `weeks.csv` | ISO week | `week` | sessions, daily |
| `daily.csv` | Day | `date` | weeks |
| `tests.csv` | Test result | `test_id` | sessions |
| `measurements.csv` | Body measure or lab value | `date` + `type` | — |
| `gear.csv` | Shoe pair or bike | `gear_id` | sessions |

## 3. `sessions.csv`

Joins **planned** and **done**. Planned and not done: `status = missed`; done but not planned: `status = extra`.

| Column | Type | Description | Source |
|---|---|---|---|
| `session_id` | text | `YYYYMMDD-n` (n = order in the day) | Agent |
| `date` | date | | — |
| `week` | text | ISO week | Computed |
| `phase` | enum | phase | Calendar |
| `sport` | enum | run / bike / strength | — |
| `type` | enum | session type | Plan |
| `status` | enum | completed / modified / missed / extra | Computed |
| `change_reason` | text | If modified/missed: traffic light, pain, schedule, illness… | Athlete |
| `plan_name` | text | Workout name in COROS | Plan |
| `plan_duration_min` | number | | Plan |
| `plan_hr_cap_bpm` | number | | Plan |
| `plan_power_min_w` / `plan_power_max_w` | number | If power-based | Plan |
| `source` | enum | coros / strava / manual | — |
| `activity_id` | text | COROS labelId or Strava id | Platform |
| `start_time` | time | | Platform |
| `surface` | enum | surface | Athlete / plan |
| `gear_id` | text | Shoe or bike used | Athlete |
| `temperature_c` | number | | Strava / COROS |
| `duration_min` | number | Moving time | Platform |
| `elapsed_min` | number | Total time incl. stops | Platform |
| `distance_km` | number | | Platform |
| `elevation_gain_m` | number | | Platform |
| `hr_avg_bpm` / `hr_max_bpm` | number | | Stream |
| `power_avg_w` | number | Stryd (run) | Stream / COROS |
| `power_np_w` | number | Normalized power | Computed |
| `pace_avg_s_km` | number | Run, moving | COROS |
| `speed_avg_kmh` | number | Bike | Stream |
| `cadence_avg` | number | Steps/min (run) or rpm (bike) | Stream |
| `ground_contact_ms` | number | Stryd | COROS |
| `vertical_osc_cm` | number | Stryd | COROS |
| `stride_length_m` | number | Stryd | COROS |
| `leg_stiffness_kn_m` | number | Stryd | COROS |
| `form_power_ratio_pct` | number | Stryd | COROS |
| `min_z1` / `min_z2` / `min_z3` | number | Minutes in physiological zones | Computed |
| `tss` | number | Session load | Computed |
| `tss_type` | enum | rTSS / hrTSS / sRPE | Computed |
| `if` | number | Intensity factor | Computed |
| `decoupling_pct` | number | Pa:HR (run) or HR drift (bike), 1st vs 2nd half | Computed |
| `ef` | number | Efficiency: power (or speed) / HR | Computed |
| `pct_time_over_cap` | number | % of work time above the cap | Computed |
| `cap_respected` | 1/0 | `1` if `pct_time_over_cap` < 5 % | Computed |
| `failed_recovery` | 1/0 | Recovery ride/run that entered Z2 | Computed |
| `coros_load` | number | COROS Training Load (reference only) | COROS |
| `strava_relative_effort` | number | Reference only | Strava |
| `rpe_0_10` | number | Perceived effort (run: automatic from COROS, 3.1) | COROS / athlete |
| `srpe` | number | `rpe_0_10 × duration_min` | Computed |
| `pain_0_10` | number | Max pain during, after or next morning | Note / athlete |
| `pain_site` | text | e.g. `shin`, `knee_left` | Note / athlete |
| `issues` | text | Other niggles, short | Note / athlete |
| `carbs_g_h` | number | Carbohydrate per hour (sessions > 75 min) | Athlete |
| `strength_done` | 1/0 | If the session included strength | Note / athlete |
| `zones_version` | text | `zones.yaml → version` | Agent |
| `notes` | text | | — |

### 3.1 RPE from COROS

The athlete marks perceived effort on the watch after each activity (5 levels). `getActivityDetail` returns it as `Perceived Effort`:

| COROS label | Meaning | `rpe_0_10` |
|---|---|---|
| Very Easy | Very easy | 2 |
| Easy | Easy | 4 |
| Moderate | Moderate | 6 |
| Hard | Hard | 8 |
| Max Effort / Very Hard | Maximal | 10 |

- Unknown label → `rpe_0_10` empty and a note, so the table can be extended (`scripts/coach/rpe.py`).
- If the activity note gives a different RPE, COROS wins and the note goes to `notes`.
- Bike (not recorded on COROS): RPE from the Strava description if present; otherwise empty.

## 4. `intervals.csv`

Quality sessions and tests only. Checks each rep against its cap.

| Column | Type | Description |
|---|---|---|
| `session_id` | text | |
| `n` | number | Rep or lap number |
| `type` | enum | warmup / work / recovery / cooldown |
| `duration_s` | number | |
| `distance_m` | number | |
| `power_avg_w` | number | |
| `pace_avg_s_km` | number | |
| `hr_avg_bpm` | number | |
| `hr_end_bpm` | number | HR at the end of the rep (cap control) |
| `pct_cp` | number | Power / current CP |
| `pct_lthr` | number | End HR / current LTHR |
| `cap_exceeded` | 1/0 | |

## 5. `strength.csv`

`session_id, date, block (a / b / prevention / plyometrics), exercise (snake_case, e.g. bulgarian_split_squat), sets, reps (per leg if unilateral), seconds (isometrics), load_kg (empty if bodyweight or band), band, rpe_0_10, notes`.

## 6. `weeks.csv`

| Column | Description |
|---|---|
| `week`, `start_date` (Monday), `phase`, `phase_week`, `is_deload` | |
| `sessions_planned`, `sessions_done`, `compliance_pct` | done / planned |
| `run_min`, `run_km` (impact load), `bike_min`, `bike_km`, `strength_sessions` | |
| `pct_z1`, `pct_z2`, `pct_z3` | Run + bike distribution |
| `tss_run`, `tss_bike`, `tss_total`, `ctl`, `atl`, `tsb`, `acwr` | At week close |
| `run_km_change_pct` | vs previous week |
| `ef_control_run`, `long_run_decoupling_pct` | |
| `hrv_avg_ms`, `rhr_avg_bpm`, `sleep_avg_h` | When available |
| `days_green`, `days_yellow`, `days_red` | Traffic light |
| `pain_max`, `weight_kg`, `feeling_1_5` | |
| `decision` | push / hold / ease |
| `rationale` | Data-based justification |
| `integration` | ok / partial / fallback |

## 7. `daily.csv`

`date (wake-up day), source (coros / ring), hrv_ms, hrv_range_min_ms, hrv_range_max_ms, hrv_7d_avg_ms, rhr_bpm, rhr_30d_avg_bpm, sleep_h, sleep_score, temp_dev_c, load_ratio, light (green / yellow / red / no_data), planned_session, action`.

## 8. `tests.csv`

`test_id (e.g. T3-20261121), date, session_id, test (bike_drift / control_run / threshold_30min / cp_3_9 / race / estimate / declared), parameter (lthr / threshold_pace / threshold_power / cp / z1_cap / ef / hr_max), value, unit (bpm / s_km / w / ratio), previous_value, conditions, valid (1/0), notes`.

## 9. `measurements.csv`

Long format: `date, type (weight / height / body_fat_pct / ferritin / haemoglobin / vitamin_d / …), value, unit, source (scale / lab / coros / athlete), reference_range, notes`. Interpretation belongs to a health professional.

## 10. `gear.csv`

`gear_id (S1, S2… shoes; B1 bike), type (shoe / bike), model, use (easy / quality / race / trail), start_date, initial_km, limit_km, retired_date, notes`. Accumulated km = `sum(sessions.distance_km by gear_id) + initial_km`.

## 11. Reference calculations (implemented in `scripts/coach/metrics.py`)

| Metric | Formula |
|---|---|
| Zone minutes | Per 1 Hz sample: Z1 if HR < `z1_cap_bpm`; Z2 if < `lthr_bpm`; else Z3 |
| hrTSS | `Σ (dt/3600) × (HR/LTHR)² × 100` over all samples (IF² form with HR) |
| IF (HR) | `mean HR / LTHR` |
| rTSS | `duration_h × IF² × 100`, IF = NP / CP |
| NP | 4th root of mean of 30 s rolling average power⁴ |
| CTL / ATL | Exponential average of daily TSS, constants 42 and 7 days |
| TSB | CTL(yesterday) − ATL(yesterday) |
| ACWR | 7-day TSS sum / (28-day TSS sum / 4) |
| EF | Run: NP / mean HR; bike: speed / mean HR |
| Decoupling | `(EF 1st half − EF 2nd half) / EF 1st half × 100` |
| Over-cap time | Seconds with HR > cap within work laps / work seconds |
| Lap alignment | COROS laps (workout sections) laid over the stream by cumulative duration; stream vs lap power must agree within 2 % |

> Until CP is measured, run load is **hrTSS** (`tss_type`). After the CP test, history is recomputed as rTSS and noted.

## 12. Enums

| Field | Values |
|---|---|
| `phase` | return_to_run, base, build, specific, taper, transition |
| `sport` | run, bike, strength |
| `type` | easy_z1, run_walk, norwegian_threshold, long_run, marathon_pace, x_factor, recovery, test, strength, race |
| `status` | completed, modified, missed, extra |
| `surface` | grass, dirt, track, asphalt, mixed, road |
| `source` | coros, strava, manual |
| `tss_type` | rTSS, hrTSS, sRPE |
| `decision` | push, hold, ease |
| `integration` | ok, partial, fallback |
| `light` | green, yellow, red, no_data |

## 13. Migration from v1

v1 used Spanish column names and values. `scripts/migrate_v1_to_v2.py` converts a v1 data folder to v2 (same rows, English columns and enums; `dolor_tibia_0_10` → `pain_0_10` + `pain_site = shin`).
