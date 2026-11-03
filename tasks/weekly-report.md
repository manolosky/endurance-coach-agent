# Task: weekly report (Obsidian)

**Schedule:** Monday 15:00 in `settings.yaml → timezone`. **Runs:** on the athlete's computer (desktop app open). **Writes:** the vault; the Project only if the closed week's `weeks.csv` row is missing.

Apply `agent/tasks/_common.md` first. This task never changes COROS, Strava, the plan or any process document.

**Golden rule:** readable in **5 minutes** (≈ 400–500 words besides short tables). Short sentences, no filler, never repeat what the charts show. Max 4 charts.

## 1. Data

Read `agent/framework/methodology.md`, `agent/framework/data-schema.md`, `agent/integrations/obsidian.md`, `athlete/calendar.md`, `athlete/improvement-log.md`, all `athlete/data/*.csv` and `athlete/weeks/` for the closed and the new week (written at 00:00). If the closed week's `weeks.csv` row is incomplete, complete it following `tasks/weekly-review.md` sections 1 and 3 and write it back.

## 2. Charts

`python3 scripts/charts.py athlete/data --week <YYYY-Www> --lang <language> --out work/charts` (matplotlib, PNG 1600×900, history since the first week). Only charts with data, max 4, by priority:

1. `weekly-volume` — run km and minutes (done vs plan) and bike minutes.
2. `fitness-fatigue` — CTL, ATL, TSB.
3. `efficiency` — EF of Z1 runs at similar HR + long-run decoupling.
4. `zones` — % Z1/Z2/Z3 vs phase target.

During return to run, if pain was logged, replace 4 with `pain`. After a test, replace the least relevant with `tests`.

## 3. Report `Reports/YYYY-Www.md`

Frontmatter (English keys): `week, phase, decision, compliance_pct, run_km, ctl, tsb`. Body **in the athlete's language**, only these sections:

1. **In one line:** decision and why.
2. **Key numbers:** compliance %, run km and minutes (done/plan), bike minutes, % Z1, fitness trend (CTL/TSB).
3. **Charts:** `![[charts/YYYY-Www-<name>.png]]`, one reading sentence each.
4. **Good** (max 3) and **To improve** (max 3), each with a number.
5. **This week:** 2–3 key sessions and the week's goal.
6. **Pending your approval:** `proposed` items from `athlete/improvement-log.md` and approved ones in progress (ID, finding, change, one line each). New finding while writing → add it as `proposed`. None → "None".
7. **I need from you** (max 3): missing data, confirmations.

End with a link to `athlete/weeks/YYYY-Www.md` in the Project.

## 4. Write to the vault

Vault path: `settings.yaml → obsidian.vault_path` (remote-device tools; apart from the task's working directory, write only inside the vault; create folders; delete nothing):

- `Reports/YYYY-Www.md`, `Reports/charts/YYYY-Www-<name>.png`
- `Data/*.csv`: mirror of `athlete/data/` (overwrite)
- `Home.md`: list of reports newest first (`[[Reports/YYYY-Www]]`) and 3 key figures of the latest week.

## 5. Notification (max 3 lines, athlete's language)

Report ready, decision, number of proposals awaiting approval. If the computer is unreachable: save to `athlete/reports/YYYY-Www.md`, say it will be copied next run; on every run, also copy pending reports from `athlete/reports/`.
