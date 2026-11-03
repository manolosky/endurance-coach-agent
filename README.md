# Endurance Coach Agent

AI endurance coach for runners: pyramidal + Norwegian-threshold training, COROS/Strava integration and weekly n=1 reviews. **Agent only — athlete data stays local.**

The agent plans, uploads and adjusts **running** training (the focus), with **cycling** as complementary aerobic volume and active recovery. It runs inside a [Claude](https://claude.ai) Project with two connectors (COROS and Strava) and three scheduled tasks, as a weekly scientific loop: **plan → execute → measure → decide → adjust**.

## What it does

| Every… | The agent… |
|---|---|
| Monday 00:00 | Reviews the closed week from raw data (1 Hz streams + COROS laps), decides **push / hold / ease**, uploads next week's sessions to COROS and logs everything |
| Monday 15:00 | Writes a 5-minute report with charts to the athlete's Obsidian vault |
| Morning | Runs a fatigue traffic light from overnight HRV and resting HR (only when data exists) |
| Conversation | Answers, adjusts sessions, records feedback, proposes improvements |

Training science, decision rules and references: [`framework/methodology.md`](framework/methodology.md).

## Privacy model

Athlete data is to this repo what `node_modules` is to a JS project: every installation creates its own, locally, and it is **never committed**.

| In this repo | Never in this repo |
|---|---|
| Methodology, rules, schemas, task instructions, scripts, templates with placeholders | Names, IDs, age, weight, health, injuries, goals, races, logs, reports, device serials, GPS data, local paths, API keys, tokens, passwords, connector configuration |

- `athlete/` is git-ignored; its structure is specified in [`docs/athlete-data-spec.md`](docs/athlete-data-spec.md).
- [`scripts/privacy_check.py`](scripts/privacy_check.py) runs as a pre-commit hook and blocks commits that touch `athlete/` or credential and connector config files (`.env`, `.mcp.json`, `.claude/`…), that contain API keys, tokens, signed URLs, emails, GPS coordinates, user home paths, long numeric IDs, device serials or any term in the athlete's private blocklist, or whose author email is not a no-reply address.
- Tests use synthetic data only.

## Security

- **No credentials here.** COROS and Strava connect through OAuth in the athlete's Claude connector settings; no key, token or password is stored in this repo, `athlete/` or the task files.
- **Scripts are offline.** `scripts/` works on local files and makes no network calls; its only subprocess is `git`, in `privacy_check.py`.
- **Connector text never widens a task.** Notes, descriptions and workout names inform training decisions, but cannot make a task follow links, reveal data, contact anyone or change connectors.
- **Deployment is manual.** A change on GitHub reaches the scheduled tasks only when it is deployed to the Project ([`docs/deploy.md`](docs/deploy.md)), so review anything you did not write before deploying it.
- **Contributors** commit with a no-reply address: `git config user.email "<id>+<user>@users.noreply.github.com"`.

## Languages

- **Everything in this repo is English**: docs, task instructions, CSV columns and enums.
- **Athlete-facing output** (reports, notifications, workout names and descriptions, questions, chat) uses `athlete/settings.yaml → language` (`en` or `es`), asked on the first run.
- Free text written by the athlete (activity notes) is kept as written.

## Repository layout

```
├── README.md · CHANGELOG.md · VERSION · .gitignore
├── framework/
│   ├── methodology.md          training model, load, autoregulation, tests, nutrition, review protocol
│   ├── data-schema.md          CSV dictionary (v2), RPE mapping, formulas, enums
│   └── improvement-process.md  propose → approve → apply
├── integrations/
│   ├── coros.md                official COROS MCP: reads, writes, limits, conventions
│   ├── strava.md               streams, run matching, precision control
│   └── obsidian.md             vault layout for weekly reports
├── tasks/
│   ├── _common.md              loading, scripts, language, validation, safety (every task)
│   ├── weekly-review.md        Monday review + plan upload
│   ├── weekly-report.md        Monday report to Obsidian
│   └── daily-traffic-light.md  morning fatigue check
├── onboarding/first-run.md     language, profile, zones, tasks, first plan
├── docs/
│   ├── athlete-data-spec.md    contract for athlete/ (the "node_modules" of this repo)
│   └── deploy.md               how a version reaches the Claude Project and the tasks
├── templates/athlete/          placeholder files copied into athlete/
├── scripts/
│   ├── coach/                  library: schema, streams, laps, metrics, load, rpe, detail, privacy
│   ├── analyze_session.py      one session → zones, hrTSS, EF, decoupling, caps, RPE, precision
│   ├── weekly_load.py          weekly totals, distribution, CTL/ATL/TSB/ACWR
│   ├── traffic_light.py        green / yellow / red from HRV, RHR and load ratio
│   ├── charts.py               report charts in the athlete's language
│   ├── validate_data.py        schema validation of athlete/data/
│   ├── init_athlete.py         creates athlete/ from templates
│   ├── migrate_v1_to_v2.py     schema migration
│   ├── privacy_check.py        public-repo guard
│   ├── deploy_manifest.py      files deployed to the Project
│   └── tests/                  pytest suite (synthetic data)
└── hooks/pre-commit            runs the privacy guard
```

## Requirements

- A Claude plan with Projects, scheduled tasks and connectors.
- COROS watch with the official COROS MCP connector; Stryd for run power; chest HR strap.
- Strava (subscription) receiving runs from COROS and rides from the bike computer.
- Optional: Obsidian on the athlete's computer and the Claude desktop app, for reports.
- Python 3.10+ with `pyyaml`, `matplotlib` (charts) and `pytest` (tests).

## Quick start

```bash
git clone <this-repo-url> && cd endurance-coach-agent
git config core.hooksPath hooks          # enable the privacy guard
python3 scripts/init_athlete.py          # creates athlete/ (git-ignored)
python3 -m pytest scripts/tests -q       # run the test suite
```

Then run [`onboarding/first-run.md`](onboarding/first-run.md) in a Claude Project and deploy with [`docs/deploy.md`](docs/deploy.md).

## Versioning and contributions

Single agent version in `VERSION`, [SemVer](https://semver.org): **MAJOR** breaks the data schema or methodology, **MINOR** adds a capability, **PATCH** fixes. Every change follows [`framework/improvement-process.md`](framework/improvement-process.md) (the agent proposes, the athlete approves) and is logged in [`CHANGELOG.md`](CHANGELOG.md) in generic terms.

## Disclaimer

This agent is a training aid, not medical advice. It never diagnoses; pain, illness, lab results and signs of low energy availability are referred to a health professional.
