# First run

Run this conversation once per athlete, in the Claude Project where the agent will live. The agent asks; the athlete answers. Nothing from this conversation goes into the repo.

## 1. Language (always first)

Ask, in both languages:

> Which language do you want for reports, notifications and our conversations? / ¿En qué idioma quieres los reportes, avisos y nuestras conversaciones? **English / Español**

Write the answer to `athlete/settings.yaml → language` (`en` / `es`). From here on, talk to the athlete in that language. Internal files stay in English.

## 2. Initialise `athlete/`

Create the Project docs from `templates/athlete/` with the `athlete/` prefix (laptop: `python3 scripts/init_athlete.py`). Never overwrite existing files.

## 3. Settings

Ask and record in `settings.yaml`: time zone, whether COROS and Strava are connected (verify with one read call each), the Obsidian vault path if they want reports there, and a **privacy blocklist** (their name, nicknames, town, club, any ID) that must never appear in the public repo.

## 4. Profile and calendar

Ask in a few short rounds (use multiple-choice questions where possible):

- Sports, level, reference marks, current weekly volume, recent break or injury.
- Availability: training days per week, rest day, long-run day, maximum bike days.
- Strength equipment and usual surfaces.
- Devices: watch, Stryd (confirm the watch uses Stryd as power source), bike computer, chest strap.
- Goal race (name, date, distance) and target, if any.

Write `profile.md` and `calendar.md` (phases from `framework/methodology.md` 4.5 counted back from the race; add a return-to-run phase and injury rules if there was an injury or a long break).

## 5. Zones

Fill `zones.yaml` with declared or estimated values, listing every estimate under `provisional`, and schedule the test battery (`methodology.md` 9.1) in `profile.md`.

## 6. Scheduled tasks

Create the three tasks with a one-line prompt each (see `docs/deploy.md`): weekly review (Monday 00:00), weekly report (Monday 15:00, on the athlete's computer, only if a vault is set), daily traffic light (06:45, paused until overnight HRV and RHR are available).

## 7. First plan

Run `tasks/weekly-review.md` interactively for the first week (the athlete is present, so ask instead of assuming), upload it to COROS and verify.
