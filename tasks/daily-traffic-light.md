# Task: daily traffic light

**Schedule:** daily 06:45 in `settings.yaml → timezone`. **Runs:** cloud, unattended. **Writes:** `athlete/traffic-light-log.md`, `athlete/data/daily.csv`. **Never** asks the athlete anything and never writes to COROS or Strava.

Apply `agent/tasks/_common.md` first. Criteria: `agent/framework/methodology.md`, section 8.

## 1. Data (COROS only)

- Last night's HRV: `querySleepHrv` (official value and personal normal range), plus the 3 previous days.
- Resting HR: `queryRestingHeartRate` today and last 30 days (30-day average).
- Load ratio: `queryTrainingLoadAssessment`.
- Today's session: `queryTrainingSchedule` for today.

## 2. Run condition

If COROS is unavailable, or last night's official HRV or today's RHR is missing: **stop silently** (no message, no log line).

## 3. Light

`python3 scripts/traffic_light.py --hrv ... --range ... --rhr ... --rhr-avg ... --ratio ... --low-days ...` returns green / yellow / red with the triggering criterion (methodology 8.2). Without a load ratio, evaluate HRV and RHR only.

## 4. Action on today's session

- Green: unchanged.
- Yellow: if today is a run quality session (threshold, intervals, race pace), recommend −1 rep, cap −3 %, or switching to Z1. Easy runs and rides unchanged.
- Red: recommend rest or very easy Z1 (bike preferred).

## 5. Log

Append one row to `athlete/data/daily.csv` and one line to `athlete/traffic-light-log.md` (`Date | Light | HRV | Normal range | RHR | 30d avg | Load ratio | Planned session | Action`).

## 6. Notification

Only red, or yellow with a quality session today. Max 4 lines, athlete's language: light, triggering value, recommended action. Red 3 days in a row: add that the week should be reviewed with the agent and, with symptoms, a health professional consulted.
