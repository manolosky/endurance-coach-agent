# COROS — official MCP connector

**URL:** `https://mcpeu.coros.com/mcp` (EU region; read and write; OAuth).

## Read

| Tool | Use | Notes |
|---|---|---|
| `querySportRecords` | Activity list with `labelId`, `sportType`, start/end timestamps | Run codes 100–103, bike 200–205 |
| `getActivityDetail` | Session summary, Stryd metrics, **`Perceived Effort`** (RPE), **`Workout Note`** (athlete note) | Verified |
| `queryActivityLapData` | Two lap groups: workout sections (type 10) and per km (type 2), with Stryd metrics per lap | `groundTime` ms, `strideHeight` mm, `avgStrideLength` cm, `legStiffness` in tenths of kN/m |
| `queryCustomActivityLapData` | Arbitrary time window | E.g. last N minutes |
| `querySleepHrv` | Official nightly HRV, normal range | Max 7 days per call; date = wake-up day |
| `queryRestingHeartRate` | Daily RHR | |
| `queryTrainingLoadAssessment` | Short/long-term load and ratio | Daily traffic light only |
| `queryTrainingSchedule` | Scheduled workouts for a range | Verification after upload |
| `queryDevices` | Bound watch | Does **not** list paired sensors (Stryd) |
| `downloadActivityFitFiles` / `queryActivityFitFileDownloadUrls` | FIT files | **Not usable from cloud sessions**: binary not accepted and the URL host is blocked. Try once; fall back to Strava streams silently |

## Write

- `createScheduledWorkout`: one new workout on a date (today to +90 days). **Main path for the weekly plan.**
- `queryScheduledWorkoutDetails` + `updateScheduledWorkout`: change a scheduled workout.
- `createSingleWorkout` / `scheduleWorkout`: reusable library workouts.
- `createTrainingPlan` / `updateTrainingPlan`: 4–16-week plans (not used; the cycle is weekly).

**Capabilities and limits:**

- Sports: run (1), bike (2), trail (5). **No strength.**
- Intensity per section: HR (bpm or % LTHR), pace (s/km), power in watts (run: absolute range only). Repeats 1–20, not nested.
- `courseDescription`: free text shown as is on the app and watch. Used for strength, rules (e.g. injury pain rule) and instructions, **in the athlete's language**.
- **Moving or deleting** a scheduled workout is not supported: done in the COROS app.

## Conventions

- **Strength:** on run days, in that workout's description; strength-only days are a **15' warm-up** run workout (very easy HR cap) with the full session in its description.
- **Names:** `S<n> · <session type>` (n = macrocycle week), in the athlete's language.
- **Feedback:** the athlete marks perceived effort on the watch after each activity (→ RPE) and writes a note in the COROS app only for pain, strength confirmation or specific feedback.
