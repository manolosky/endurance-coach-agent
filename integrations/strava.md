# Strava — read-only connector (run and bike streams)

Official Strava MCP from the Claude directory. Requires an active Strava subscription. No write access.

## Activities

- `list_activities` for a date range. Bike: `sport_type` Ride, GravelRide, MountainBikeRide, VirtualRide… Run: `Run`, synced from COROS.
- **Run matching:** each COROS run is matched to its Strava `Run` by start date/time (±2 min) and distance (±2 %). A run is never counted twice.
- The activity **description** is returned: it is the feedback channel for **rides** (RPE, pain). COROS notes are not synced to Strava.

## Streams

`get_activity_streams`:

| Sport | Streams | Resolution |
|---|---|---|
| Run | `time`, `heart_rate`, `watts`, `velocity_smooth`, `cadence`, `moving` | Full (omit `resolution`): 1 Hz |
| Bike | `time`, `heart_rate`, `moving` | Full |

- The result is large and is saved to a file by the tool: process it with `scripts/analyze_session.py`, never print series into the conversation.
- **Run cadence is per leg:** steps/min = value × 2.
- **Precision control** (`analyze_session.py` does it): duration and average HR vs COROS (±1 % and ±1 bpm); power per COROS lap vs stream (±2 %). Mismatch → note it and use COROS for summaries.
- Power in Strava comes from the file COROS syncs, so it is the same data the watch recorded. Validation on first use: lap differences ≤ 2.5 W except the first lap, where a few seconds of pre-start recording shift the window.

## Other

- `get_athlete_zones`: reference only; official zones are in `athlete/zones.yaml`.
