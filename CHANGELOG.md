# Changelog

All notable changes to the agent. Versioning: [SemVer](https://semver.org) — MAJOR breaks the data schema or methodology, MINOR adds a capability, PATCH fixes. Entries describe rules, never athlete data.

## [2.0.2] — 2026-11-03

### Fixed
- Pre-commit hook finds Python on Windows (`python3`, `python` or `py`) and blocks the commit if no Python 3 is available, instead of failing open.

## [2.0.1] — 2026-11-03

### Fixed
- Weekly review: tool outputs (laps, detail, streams) are written verbatim to `work/` files; inline stream results handled.
- Weekly review: the planned HR cap has a defined source (`sessions.csv → plan_hr_cap_bpm`, then the scheduled workout, then `zones.yaml`), and planned rows store it on upload.
- Weekly review: summary values follow one rule (COROS for watch-visible values, stream for zones/load/efficiency); failed precision checks are noted, not used to switch sources.
- FIT attempt is logged in the weekly file instead of being silently dropped.
- Common rules: all eight CSVs are materialised so validation can run; Projects tool calls named explicitly.

## [2.0.0] — 2026-11-03

First public version. Earlier iterations (v1.x) ran privately, mixed agent and athlete data, and are not part of this repository.

### Added
- Repository structure separating the **agent** (this repo, English) from the **athlete** (`athlete/`, git-ignored, spec in `docs/athlete-data-spec.md`).
- Selectable athlete-facing language (`athlete/settings.yaml → language`, asked on first run).
- `scripts/` package with tests: session analysis from 1 Hz streams, COROS lap alignment and precision check, zone minutes, hrTSS, NP, EF, decoupling, CTL/ATL/TSB/ACWR, RPE mapping, CSV validation, v1→v2 migration, `init_athlete.py`, weekly charts, daily traffic light.
- Privacy guard (`scripts/privacy_check.py`, `hooks/pre-commit`): blocks `athlete/`, activity files, emails, GPS coordinates, user home paths, long numeric IDs, device serials and the athlete's private blocklist.
- Task instructions versioned in `tasks/`; scheduled tasks run a one-line bootstrap prompt (`docs/deploy.md`).
- Onboarding (`onboarding/first-run.md`) and deployment procedure (`docs/deploy.md`).

### Changed
- Data schema v2: English column names and enums; generic `pain_0_10` + `pain_site` instead of a site-specific pain column.
- Run analysis reads Strava 1 Hz streams plus COROS laps and session values; COROS FIT is used only when readable.
- Run RPE comes from the COROS perceived-effort scale (5 levels → 2/4/6/8/10); activity notes carry pain, strength confirmation and specific feedback.
- Summary values the athlete sees on the watch (average HR and power, Stryd metrics, RPE) are taken from COROS; zones, load and efficiency from the stream.
- One provisional LTHR value is used for both the Z2/Z3 split and hrTSS until LT2 is tested.
- Over-cap time and decoupling use work laps only (walk breaks excluded).
- Lap power precision tolerance: ±2 % or ±3 W.
- ACWR is undefined with less than 28 days of load history.
- Safety: no load increase after illness until symptom-free.
