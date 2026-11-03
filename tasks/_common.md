# Common rules for every task

Every scheduled task starts in a fresh session with no memory. Before its own steps it does this:

## 1. Load the agent and the athlete

With the **Projects** tool (`project_info` to list docs, `project_read` to read, `project_write` with `local_path` to write) (project docs use path prefixes `agent/` and `athlete/`):

1. Read `agent/README.md`, `agent/VERSION` and the task file it was told to run.
2. Read `athlete/settings.yaml` and `athlete/zones.yaml`. If either is missing, stop and notify (in English): "athlete/ is not initialised — run onboarding/first-run.md".
3. Read whatever else the task lists.

If the Projects tool or a required connector (COROS, Strava; load them with ToolSearch) is unavailable: **do not write anything to COROS**, send a short notification saying what is missing, and stop.

## 2. Materialise the scripts

Copy every Project doc whose path starts with `agent/scripts/` into the working directory, keeping the relative path (`agent/scripts/coach/metrics.py` → `./scripts/coach/metrics.py`). Copy `athlete/settings.yaml`, `athlete/zones.yaml` and **all eight** `athlete/data/*.csv` into `./athlete/` the same way (validation needs every file). Install `pyyaml` if missing (`pip install --break-system-packages pyyaml`). All calculations go through these scripts, never ad-hoc code, so every run applies identical formulas.

## 3. Language

- Everything the athlete reads — notifications, report text, workout names and descriptions uploaded to COROS, questions — is written in `settings.yaml → language` (`es` = Spanish, `en` = English).
- Everything internal — CSV columns and enums, file names, log keys, improvement-log entries' Area/Status — stays in English. Free-text columns (`notes`, `rationale`, `issues`) are written in English.

## 4. Writing data

- Validate with `python3 scripts/validate_data.py athlete/data` before writing any CSV back to the Project; never write a file that fails validation.
- CSVs and weekly files are append-only; never overwrite what the athlete entered.
- Write back with `project_write` using `local_path`.

## 5. Safety

Never diagnose. With persistent pain, illness or signs of low energy availability: do not increase load, reduce it if needed, and recommend seeing a health professional.

## 6. Improvement

Before finishing, ask "what could be better?" and add any finding to `athlete/improvement-log.md` as `proposed`. Never apply a process change.
