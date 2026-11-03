# Deploying a version

The repo is the source of truth. A **deployment** copies the agent into the Claude Project where it runs and points the scheduled tasks at it. Athlete data is never deployed from the repo; it already lives in the Project under `athlete/`.

## 1. What is deployed

Every tracked file except `.gitignore`, `hooks/`, `scripts/tests/` and `templates/` is written to the Project with the `agent/` prefix, keeping its path:

| Repo | Project |
|---|---|
| `README.md`, `VERSION`, `CHANGELOG.md` | `agent/README.md`, `agent/VERSION`, `agent/CHANGELOG.md` |
| `framework/*.md` | `agent/framework/*.md` |
| `integrations/*.md` | `agent/integrations/*.md` |
| `tasks/*.md` | `agent/tasks/*.md` |
| `onboarding/first-run.md`, `docs/*.md` | `agent/onboarding/…`, `agent/docs/…` |
| `scripts/*.py`, `scripts/coach/*.py` | `agent/scripts/…` |

`python3 scripts/deploy_manifest.py` prints this list for the current tree.

## 2. Steps

1. Tests pass: `python3 -m pytest scripts/tests -q`.
2. Privacy check passes: `python3 scripts/privacy_check.py`.
3. `VERSION` bumped and `CHANGELOG.md` updated; commit and tag `vX.Y.Z`.
4. Write every manifest file to the Project (`project_write` with `local_path`).
5. If the data schema changed (MAJOR), migrate `athlete/data/` with the matching `scripts/migrate_*.py`, validate, write back.
6. Check the scheduled tasks still have their one-line prompts (below).
7. Run a smoke test: analyse the latest session with `scripts/analyze_session.py` and compare with the previous version's values.

## 3. Scheduled task prompts

Each task prompt is a single bootstrap line, so the instructions are versioned in the repo and not inside the task:

| Task | Prompt |
|---|---|
| Weekly review | `Using the Projects tool, read agent/tasks/_common.md and agent/tasks/weekly-review.md and execute them exactly. The athlete is not present.` |
| Weekly report | `Using the Projects tool, read agent/tasks/_common.md and agent/tasks/weekly-report.md and execute them exactly. The athlete is not present.` |
| Daily traffic light | `Using the Projects tool, read agent/tasks/_common.md and agent/tasks/daily-traffic-light.md and execute them exactly. Never ask the athlete anything.` |

## 4. Project instructions

Set the Claude Project instructions to:

> Before any review or answer about training, read `agent/README.md`, then apply `agent/framework/methodology.md` with the athlete's data in `athlete/`. Reply to the athlete in `athlete/settings.yaml → language`.
