# Task: weekly review and plan

**Schedule:** Monday 00:00 in `settings.yaml → timezone`. **Runs:** cloud, unattended. **Writes:** COROS (plan) and Project (`athlete/`).

Apply `agent/tasks/_common.md` first. The athlete is not present and cannot answer.

## 0. Context

Read: `agent/framework/methodology.md`, `agent/framework/data-schema.md`, `agent/integrations/coros.md`, `agent/integrations/strava.md`, `athlete/profile.md`, `athlete/calendar.md`, `athlete/improvement-log.md` (apply only `approved` or `closed` items), the latest `athlete/weeks/YYYY-Www.md` and all `athlete/data/*.csv`.

## 1. Data of the closed week (Monday–Sunday)

1. **Runs (COROS):** `querySportRecords` for the range; for each run `getActivityDetail` (Stryd metrics, `Perceived Effort`, `Workout Note`) and `queryActivityLapData`. Write each lap result, exactly as returned (JSON), to `./work/<labelId>-laps.json` and each detail text to `./work/<labelId>-detail.txt` with the Write tool. Never re-type values by hand: copy the tool output verbatim.
2. **Run streams (Strava):** `list_activities` for the range; match each COROS run to its Strava `Run` (start ±2 min, distance ±2 %); `get_activity_streams` with `time, heart_rate, watts, velocity_smooth, cadence, moving`, full resolution. Large results are saved by the harness to a file whose path the tool result gives: copy that file to `./work/<labelId>-streams.json`. If the result comes back inline instead, write it verbatim to that path.
3. **FIT:** try `downloadActivityFitFiles` once; if it does not return a readable file (expected), continue. Record the outcome in the weekly file's Integrations section, not in the athlete notification.
4. **Rides (Strava):** cycling activities in the range; streams `time, heart_rate, moving`; read the description as the athlete's note.
5. **Plan:** `queryTrainingSchedule` for the range. The planned HR cap of each session is `plan_hr_cap_bpm` in `athlete/data/sessions.csv` (written when the plan was uploaded); if it is missing, read the workout with `queryScheduledWorkoutDetails` (highest HR target of its work sections) and, failing that, use `zones.yaml → <sport>.z1_cap_bpm` for easy sessions.
6. **Analyse every session** with:
   ```
   python3 scripts/analyze_session.py --streams work/<labelId>-streams.json --zones athlete/zones.yaml \
       --sport run|bike --laps work/<labelId>-laps.json --detail work/<labelId>-detail.txt \
       --plan-cap <plan_hr_cap_bpm>
   ```
   It returns JSON with zones, hrTSS, IF, EF, decoupling, over-cap time, RPE from the COROS label and a precision check against COROS. Values the athlete sees on the watch (average HR and power, Stryd metrics, RPE) always come from COROS (`summary_source = coros`); zones, load and efficiency always come from the stream. If any precision check fails, write it in the session `notes` and in the weekly file, and still use COROS for the summary values.
7. **Notes:** from each `Workout Note` (any language) extract `pain_0_10`, `pain_site`, `issues`, `strength_done`. Respect anything the athlete already entered in `sessions.csv` or `athlete/weeks/`.

## 2. Step 0 without the athlete (replaces the questions in methodology 10.1)

- No ride in Strava: assume none, flag "pending confirmation" in the log and the notification.
- No pain/feedback information: do **not** assume all went well; in return-to-run apply the minimum progression and mark the decision provisional.
- Illness or symptoms recorded that week: do not increase volume or intensity; recommend medical advice if symptoms persist.
- A session with no perceived effort marked: leave RPE empty and mention it in the notification.

## 3. Load and decision

- `python3 scripts/weekly_load.py athlete/data/sessions.csv --week <YYYY-Www>` → TSS per sport, CTL, ATL, TSB, ACWR, run km and change, distribution.
- Decide **push / hold / ease** per methodology 10.1, with data, respecting `athlete/calendar.md` (phase, injury rules) and `athlete/profile.md` (availability).

## 4. Plan of the new week

- Build every session within the athlete's availability. Upload with `createScheduledWorkout`: structured runs with HR targets (power once CP exists), reference rides, strength-only days as 15' warm-up runs with the session in the description.
- Names `S<n> · <type>` and descriptions **in the athlete's language**; include the injury pain rule when `athlete/calendar.md` defines one, and the reminder: mark perceived effort on the watch; write a COROS note only for pain, strength confirmation or specific feedback (rides: Strava description).
- Verify with `queryTrainingSchedule`. If upload fails, write each session's exact structure in the weekly file (fallback) and say so.

## 5. Log (append-only)

- Update the closed week's rows in `athlete/data/sessions.csv`; add `intervals.csv` rows for quality sessions and tests; add the `weeks.csv` row.
- Add the new week's planned rows to `sessions.csv` (with `plan_name`, `plan_duration_min`, `plan_hr_cap_bpm` and, when used, `plan_power_min_w`/`plan_power_max_w`) and its initial `weeks.csv` row.
- Complete `athlete/weeks/<closed>.md` (execution, load, decision) and create `athlete/weeks/<new>.md` with the plan.
- A valid test result → `tests.csv` and `athlete/zones.yaml` (bump `version`, history in `profile.md`). A biased test → `valid = 0`, no zone change.
- Validate, then write back.

## 6. Notification (always, max 5 lines, athlete's language)

Decision and main reason, planned run km and minutes, key sessions, pending items (ride unconfirmed, provisional decision, fallback, missing RPE), number of proposals awaiting approval.
