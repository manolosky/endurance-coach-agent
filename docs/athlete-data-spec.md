# Athlete data specification

The agent is generic. Everything that describes a specific athlete lives in an `athlete/` directory that is **created per installation and never committed** (see `.gitignore`). This document is the contract the agent relies on: if `athlete/` follows it, the agent works for any athlete, on any machine.

## 1. Principles

1. **Never in git.** `athlete/` is ignored; `hooks/pre-commit` refuses commits that touch it or that contain terms from `settings.yaml → privacy.blocklist`.
2. **One source per fact.** Thresholds live in `zones.yaml`, the race in `calendar.md`, logs in `data/`. Other files reference, never copy.
3. **Append-only logs.** CSV rows and weekly files are only added or corrected (with a note), never deleted.
4. **Machine-readable where code reads it.** Anything a script needs (`settings.yaml`, `zones.yaml`, CSV) has a fixed format; narrative files are Markdown.
5. **Same layout everywhere.** On a laptop it is `athlete/` next to the repo; in a Claude Project the same files live under the `athlete/` path prefix.

## 2. Layout

```
athlete/
├── settings.yaml          ← language, time zone, units, connectors, vault path, privacy blocklist
├── zones.yaml             ← current thresholds used by every calculation
├── profile.md             ← background, history, equipment, baselines, test battery, recalibrations
├── calendar.md            ← goal race, macrocycle, phase dates, injury rules, milestones
├── improvement-log.md     ← register of proposals for this athlete (process in framework/improvement-process.md)
├── hypotheses.md          ← active and closed n=1 experiments
├── traffic-light-log.md   ← one line per daily traffic-light run
├── data/                  ← CSV logs, schema in framework/data-schema.md
│   ├── sessions.csv · intervals.csv · strength.csv · weeks.csv
│   └── daily.csv · tests.csv · measurements.csv · gear.csv
├── weeks/                 ← YYYY-Www.md: plan, context, daily execution, load, decision
└── reports/               ← YYYY-Www.md, only when a report could not reach the vault
```

Create it with `python3 scripts/init_athlete.py`, which copies `templates/athlete/` and never overwrites existing files.

## 3. Required files and minimum content

| File | Required before | Minimum content |
|---|---|---|
| `settings.yaml` | First run | `language`, `timezone`, `units`, `connectors` |
| `zones.yaml` | First plan | `hr_max_bpm`, `run.z1_cap_bpm`, `run.lthr_bpm`, `bike.z1_cap_bpm` (provisional values allowed, flagged) |
| `profile.md` | First plan | Sports, level, reference marks, availability (training days, rest day, long-run day, max bike days), strength equipment |
| `calendar.md` | First plan | Goal race (name, date, distance) and phase dates |
| `data/*.csv` | First review | Header row only (from templates) |
| Others | When used | Template content |

## 4. `settings.yaml`

```yaml
language: es              # athlete-facing output: es | en (asked on first run)
timezone: Europe/Madrid   # IANA name
units: metric
connectors:
  coros: true             # read + write (plan upload)
  strava: true            # read: run and bike streams
obsidian:
  vault_path: ""          # absolute path on the athlete's computer; empty = no vault
privacy:
  blocklist: []           # names, IDs, places, paths that must never appear in the repo
```

## 5. `zones.yaml`

```yaml
version: YYYY-MM-DD       # written to sessions.csv → zones_version
hr_max_bpm: 0
run:
  z1_cap_bpm: 0           # LT1 proxy: top of Z1
  lthr_bpm: 0             # LT2 proxy: used for Z2/Z3 split and hrTSS
  cp_w: null              # Stryd critical power; null until measured
  threshold_pace_s_km: null
bike:
  z1_cap_bpm: 0
  lthr_bpm: null
provisional: [run.lthr_bpm]   # values not yet confirmed by a test
```

Changing `zones.yaml` is an athlete-data change (no approval needed when it records a valid test result); changing **how** zones are derived is a methodology change (needs approval).

## 6. Where the data comes from

| Data | Source | Written by |
|---|---|---|
| Run streams (HR, power, speed, cadence, 1 Hz) | Strava `get_activity_streams` | Weekly review |
| Run laps and Stryd metrics, perceived effort, activity note | COROS `getActivityDetail`, `queryActivityLapData` | Weekly review |
| Bike streams | Strava | Weekly review |
| HRV, resting HR | COROS (or ring) | Daily traffic light |
| RPE, pain, strength done | COROS perceived effort + note; Strava description for bike | Weekly review / chat |
| Thresholds | Tests (`tests.csv`) | Agent, after a valid test |

## 7. Moving or sharing

- To move an installation: copy `athlete/` (or the Project's `athlete/` docs) to the new place. Nothing else is needed.
- To share the agent: share the repo. The other person runs `init_athlete.py` and `onboarding/first-run.md`; they never receive your `athlete/`.
- To delete all personal data: delete `athlete/` and the Project's `athlete/` docs.
