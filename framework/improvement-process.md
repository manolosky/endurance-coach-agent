# Continuous improvement process

> **Guiding principle:** the system is never finished. In every review, automated task or conversation the agent asks **what could be done better** — training, data, connectors, tasks or documentation — and records it. No finding stays only in a conversation.
>
> **Approval rule:** the agent **proposes**, the athlete **approves**. No process change (methodology, schema, integrations, tasks, scripts or docs) is applied without explicit athlete approval. Automated tasks only record proposals; they never apply them.

## 1. When to open a proposal

Whenever an improvement point appears, for example:

- A connector fails, changes or falls short (missing data, new limit, new tool).
- Data arrives incomplete, misclassified or needs manual correction.
- An automated task does not do what was expected.
- The plan does not fit the athlete's reality (schedule, feedback, equipment, injuries, illness).
- A result (test, trend, hypothesis) contradicts what the methodology expected.
- Documentation is outdated, ambiguous or contradictory.
- The athlete proposes a change or is uncomfortable with the process.

Every 4 weeks (block end) the register is reviewed even without new proposals.

## 2. Where things live

| What | Where | In git? |
|---|---|---|
| This process | `framework/improvement-process.md` | Yes |
| The register of proposals for one athlete | `athlete/improvement-log.md` | **No** |
| Changes to the agent itself | Commits + `CHANGELOG.md` | Yes (no personal data) |

A proposal that changes the agent (methodology, schema, scripts, tasks) is written in the repo **in generic terms**: the commit and changelog describe the rule, never the athlete's data that triggered it.

## 3. Flow

1. **Record** in `athlete/improvement-log.md` with status `proposed` (finding + change, one line each).
2. **Show** it in the "Pending your approval" section of the weekly report.
3. **Discuss** it with the athlete.
4. **Approved:** apply it. Athlete-data change → edit `athlete/`. Agent change → commit, bump `VERSION`, add a `CHANGELOG.md` entry, deploy (`docs/deploy.md`). Close the proposal with date and version.
5. **Rejected:** close as `rejected` with the reason.
6. A hypothesis about training is handled with the scientific method (`framework/methodology.md`, section 13).

**Exceptions (no prior approval):** fixing a wrong CSV value (with a note); the day-of-session adjustments the methodology already defines (traffic light, injury pain rule); recording a valid test result in `athlete/zones.yaml`. Reported in the weekly report.

## 4. Register format (`athlete/improvement-log.md`)

```
| ID | Date | Area | Finding | Proposed change | Status | Resolution |
```

- **Areas:** training · data · connector · tasks · documentation · athlete.
- **Statuses:** proposed · approved · rejected · closed.
