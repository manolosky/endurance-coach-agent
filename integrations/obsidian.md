# Obsidian vault (weekly reports)

The weekly report is written to a folder on the athlete's computer, reached through the Claude desktop app (the scheduled task requires that computer to be on with the app open). The vault path is `athlete/settings.yaml → obsidian.vault_path`; it is personal and never written in this repo.

```
<vault>/
├── Home.md                       ← index of reports and key figures
├── Reports/
│   ├── YYYY-Www.md               ← one report per week (YAML frontmatter)
│   └── charts/
│       └── YYYY-Www-<name>.png   ← weekly-volume, fitness-fatigue, efficiency, zones, tests, pain
└── Data/
    └── *.csv                     ← mirror of athlete/data/ (read-only)
```

- **Source of truth:** `athlete/data/`. The vault is a read-only copy; manual edits in the vault are not read back.
- Report frontmatter (`week`, `phase`, `decision`, `compliance_pct`, `run_km`, `ctl`, `tsb`) enables Dataview queries.
- Report and chart text are in the athlete's language (`settings.yaml → language`); file names and frontmatter keys stay in English.
- **Fallback:** if the computer is unreachable, the report is saved as `athlete/reports/YYYY-Www.md` and copied to the vault on the next run.
