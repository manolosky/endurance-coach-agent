# Methodology

The base context the agent applies in **every** review. Planning works in **weekly** cycles; a daily automated task runs the fatigue traffic light (section 8). Athlete-specific values (thresholds, race, availability, injuries) are never stored here: they live in `athlete/` (see `docs/athlete-data-spec.md`). Changes to this document follow `framework/improvement-process.md` and are logged in `CHANGELOG.md`.

---

## 1. Purpose and operating principles

The agent plans, uploads and adjusts **running** training, which is the focus, and prescribes **cycling** as complementary aerobic volume and active recovery, aiming to improve running performance sustainably.

Non-negotiable principles:

1. **Scientific method.** Every relevant adjustment starts from a hypothesis, is measured with defined variables (section 9) and is evaluated with data, not isolated impressions. Each athlete is an n=1 experiment (section 13).
2. **Source data.** Analyses use second-by-second series from the athlete's own sensors (chest strap, Stryd). Run: Strava streams (synced from COROS, 1 Hz: HR, power, speed, cadence) plus COROS laps and Stryd metrics; the COROS FIT file is used whenever it can be read. Bike: Strava streams. Platform summaries or third-party recalculations are never official metrics.
3. **Evidence hierarchy.** Meta-analyses and consensus first; then reviews and documented elite practice; coaches' experience last. The agent states the level of evidence when proposing anything non-standard.
4. **Consistency over heroics.** Sustained aerobic volume and staying injury-free come before extreme sessions.
5. **Feelings are data.** They are recorded in a structured way (sRPE, wellbeing) and modulate the plan together with objective data. Run **RPE** is taken from the perceived effort the athlete marks on the COROS watch after each activity (5 levels; mapping in `framework/data-schema.md`). The activity **note** is reserved for specific information: pain and injuries, strength confirmation or feedback on a particular session.
6. **Minimum maintenance.** Whatever can be done automatically with objective data is not asked of the athlete.
7. **Safety.** The agent never diagnoses. Lab results, persistent symptoms, pain, illness or signs of low energy availability are referred to a health professional. After an illness, load is not increased until the athlete reports being symptom-free.

---

## 2. Athlete profile

Read from `athlete/profile.md` (sports, level, reference marks, goals, availability, equipment) and `athlete/calendar.md` (goal race and phase dates). Availability constraints (training days, rest day, long-run day, maximum bike days) are hard constraints for planning.

---

## 3. Intensity model: 3 physiological zones

All planning uses the **3-zone model**, the standard in the training-intensity-distribution (TID) literature. Devices use 5 zones; equivalence:

| Physiological zone | Boundary | Device zones (approx.) | Feeling (RPE 1–10) |
|---|---|---|---|
| **Z1 – Low** | Below LT1/VT1 | Z1–Z2 | 2–4, easy conversation |
| **Z2 – Moderate ("Norwegian threshold")** | Between LT1 and LT2 | Z3–low Z4 | 5–7, short sentences |
| **Z3 – High** | Above LT2 | high Z4–Z5 | 8–10 |

- **LT1:** first threshold (end of "truly easy"). Proxy: `zones.yaml → run.z1_cap_bpm`.
- **LT2:** second threshold / maximal lactate steady state. Run: Stryd **Critical Power (CP)** and threshold pace, with `run.lthr_bpm` as the HR proxy; bike: `bike.lthr_bpm`.
- Until LT2 is measured, the provisional `lthr_bpm` is used for **both** the Z2/Z3 split and hrTSS, so all metrics share one value.

---

## 4. Training framework: Pyramidal + Norwegian method

### 4.1 Pyramidal distribution (base of the whole macrocycle)

- Pattern **Z1 > Z2 > Z3** in total time.
- The most observed distribution in elite endurance athletes for most of the season; over 60–90 % of time in Z1 in almost all documented cases.
- Recent meta-analyses show no clear superiority of polarized over pyramidal for performance (time trials). The critical variable is **high, well-controlled Z1 volume**.

**Weekly distribution target (run + bike combined, by time):**

| Phase | Z1 | Z2 | Z3 |
|---|---|---|---|
| Base / volume | 78–85 % | 12–18 % | 2–5 % |
| Build | 75–80 % | 15–20 % | 3–6 % |
| Race-specific | 75–80 % | 10–15 % (incl. race pace) | 5–10 % |
| Taper | Volume −30–50 %, intensity kept |

> These ranges are the **initial hypothesis**; the agent adjusts them with the athlete's data (section 10).

### 4.2 Norwegian method (controlled threshold within high volume)

Definition: **controlled** threshold intervals (originally lactate-guided, 2.0–4.5 mmol/L) within a high-volume, low-intensity approach. It is a pyramidal model, not polarized.

**Adaptation for amateur athletes (no lactate meter, work and family life):** the **"sub-maximal threshold in single sessions"** variant replaces elite double-threshold days. Double threshold (AM + PM) is an **advanced option**, only if recovery and schedule allow and after at least one well-absorbed 4–6-week block.

Norwegian threshold sessions are **run only**.

Rules:

1. **Always below LT2.** Each rep in upper Z2, never all-out. The most common mistake is going too fast.
2. **Intervals, not continuous.** Fractioning accumulates more threshold time with less fatigue.
3. **Control by cap, not by target.** A power/pace/HR cap that must not be exceeded; if exceeded, slow down.
4. **Closing criterion:** finish feeling able to do 1–2 more reps (RPE 6–7).
5. **Easy days are truly easy.** The method only works if Z1 is really Z1, on the bike too.

**Reference formats (run):**

| Type | Example | Intensity |
|---|---|---|
| Long intervals | 5–6 × 6 min / 1 min rec | ≈ half-marathon to 15K pace; 88–92 % CP |
| Medium intervals | 8–10 × 3 min / 1 min rec | ≈ 15K to 10K pace; 90–94 % CP |
| Short intervals | 20–25 × 400 m / 30 s rec | ≈ 10K pace; 92–96 % CP without exceeding the HR cap |

**Control caps (replace the lactate meter):**

- **Power (Stryd):** rep average ≤ ≈ 95 % CP.
- **HR:** end-of-rep HR ≤ ≈ 92–95 % LTHR.
- **Drift:** if HR rises more than ~5 bpm from first to last rep at equal power, the session was too hard.
- **Optional:** a lactate meter could calibrate the caps every 4–8 weeks. Not required.

> CP/LTHR percentages are **practice approximations**, not trial-validated values. They are recalibrated with the tests in section 9.

### 4.3 Role of cycling

- **Function:** low-impact aerobic volume and active recovery. Adds Z1 time without mechanical stress.
- **Frequency:** maximum per `athlete/profile.md` (default 2 days/week).
- **Intensity:** Z1 with an **HR cap** (`zones.yaml → bike.z1_cap_bpm`). A recovery ride that enters Z2 is flagged "failed recovery" and counted as moderate load.
- **Prescription:** each ride is **uploaded to COROS as a reference cycling workout** (duration and HR cap, instructions in the description). The athlete records it on the bike computer; nothing is written to the bike computer platform.
- **Specific intervals (exceptional):** described in the COROS workout; the athlete sets them up manually on the bike computer.
- **Placement:** active-rest days, the day after a quality session, or as volume. Never in the 24 h before a threshold session if it leaves leg fatigue.

### 4.4 Typical week (base/build)

| Day | Session | Sport |
|---|---|---|
| Mon | Z1 easy run (or long run if not done Sunday) | Run |
| Tue | **Norwegian threshold (long intervals)** | Run |
| Wed | Z1 recovery ride + strength, or Z1 run + strength | Bike / Run |
| Thu | **Norwegian threshold (medium or short intervals)** | Run |
| Fri | Z1 run + strength, or Z1 ride | Run / Bike |
| Sat | **Rest** (default; per athlete availability) | — |
| Sun | **Z1 long run** (marathon-pace blocks in the specific phase) | Run |

- **Max 3 quality sessions per week** (2 thresholds + long run), all running.
- **Long run:** ≤ 25–30 % of weekly run volume.
- **Strength:** 1–2 sessions per week (section 6).
- The template adapts to the athlete's availability in `athlete/profile.md`.

### 4.5 Macrocycle periodization

1. **Return to run** (only after injury or a long break): pain-free running, impact tolerance, aerobic volume on the bike. No quality until the injury rules in `athlete/calendar.md` allow it.
2. **Base / volume:** increase Z1 volume (run and bike), introduce Norwegian threshold progressively (1 → 3 sessions), strength.
3. **Build:** maximum sustainable volume; Norwegian threshold is the main stimulus.
4. **Specific (6–8 weeks before the race):** 1–2 Norwegian thresholds and race-pace work (marathon-pace blocks in the long run). Strength to maintenance. Bike only as recovery.
5. **Taper (10–14 days):** volume −30–50 %, intensity kept, positive TSB on race day.
6. **Transition:** 1–2 weeks of active recovery.

Phase dates live in `athlete/calendar.md`.

**Microcycles:** 3 load weeks + 1 deload week (volume −25–40 %). The agent may switch to 2+1 if the response calls for it.

---

## 5. Intensity anchors by sport and device

### 5.1 Run (COROS watch + Stryd + chest strap)

- **Primary intensity metric:** Stryd power (CP-based zones). Until CP is measured, **HR** is the target.
- **Secondary:** pace (affected by terrain and wind; power is not).
- **Internal control:** chest-strap HR.
- **Load:** power-based rTSS once CP exists; hrTSS until then.
- **Power source check:** the COROS connector does not report which sensor produced power. On installation the athlete confirms the watch uses Stryd as power source and cross-checks one session against the Stryd app (≤ 2 % difference).

### 5.2 Bike (bike computer + chest strap, no power meter)

- **Primary metric:** HR (zones from bike LTHR).
- **Control:** RPE.
- **Load:** hrTSS from the Strava HR stream.
- **Known limitation:** without power, short efforts are poorly controlled by HR. It does not affect the intended use (Z1). If a power meter is added, zones move to FTP.

### 5.3 Chest strap

- Single HR source for both sports.

---

## 6. Strength and durability

- **Durability** (resistance to physiological deterioration in long efforts) is the **fourth determinant** of performance, with VO2max, threshold and economy. Critical in the marathon.
- **Heavy strength** (near-maximal loads, 3–6 reps) improves running economy more than isolated plyometrics; combining both seems better still.
- **Adapt to available equipment** (`athlete/profile.md`): with limited loads, seek high relative load through **unilateral exercises**, isometrics and single-leg calf/soleus work; progressive plyometrics from the base phase.
- **Base prescription:** 2 sessions/week in base/build, 1 in the specific phase, never in the 24 h before a quality run.
- **Delivery:** COROS does not accept strength workouts through the connector. Strength goes in the **description** of that day's run workout; on strength-only days, a **15' warm-up** run workout (walk or very easy jog) carries the full session in its description.
- **Measuring durability (section 9):** Pa:HR decoupling and power/pace in the last third of the long run.

---

## 7. Load model

### 7.1 Metrics

| Metric | Definition | Use |
|---|---|---|
| **TSS** | rTSS (run, power) or hrTSS (run until CP, bike) | Session load |
| **CTL** | 42-day exponentially weighted average | Fitness |
| **ATL** | 7-day exponentially weighted average | Fatigue |
| **TSB** | CTL − ATL | Freshness |
| **ACWR** | 7-day load / 28-day average | Alert only |
| **Impact load** | Run minutes and km | Mechanical risk; tracked apart from the bike |

Computed **per sport** and **combined**, always by the agent from second-by-second series (section 11.3) using `scripts/`, so every run of the agent applies the same formulas. Impact load (run only) is tracked separately because it is the most injury-related.

### 7.2 Progression limits (initial hypotheses)

- **Combined CTL ramp:** ≤ 5 points/week sustained.
- **Run volume:** ≤ +10 %/week, except after a deload. During return to run, the injury rules in `athlete/calendar.md` take precedence.
- **ACWR:** usual 0.8–1.3; above 1.3 **alert**, above 1.5 **red alert**. ACWR has known methodological limitations and never decides on its own. With less than 28 days of load history it is **undefined** (left empty), and CTL/ATL are not trusted for decisions until about 6 weeks of history exist (or a seeded history).
- **TSB:** −10 to −30 in load blocks is normal; below −30 for more than 5–7 days requires review.

---

## 8. Autoregulation

Two levels:

- **Daily — automatic traffic light.** A scheduled task runs every morning with **objective data only** (cardiac and run load). It asks the athlete nothing. Without enough data that day, it **does not run** and sends nothing.
- **Weekly — agent review.** Trends, the week's lights, the athlete's feedback, and next week's plan (section 10).

### 8.1 Daily inputs (COROS, automatic)

| Data | Tool (official COROS MCP) | Reference |
|---|---|---|
| Overnight HRV | `querySleepHrv` | Device's personal normal range; 7-day trend |
| Resting HR | `queryRestingHeartRate` | 30-day average |
| Recent run load | `queryTrainingLoadAssessment` | Short/long-term load ratio |
| Today's session | `queryTrainingSchedule` | Whether it is a quality session |

> The daily load uses the COROS assessment as a **quick approximation**; official load metrics (section 7) are computed in the weekly review.
> **Requirement:** sleep with the watch, overnight HR/HRV monitoring on (or a connected ring).

**Run condition:** last night's HRV **and** today's resting HR must exist. Otherwise the traffic light does not run.

### 8.2 Fatigue traffic light

| State | Criterion | Action on today's session |
|---|---|---|
| 🟢 **Green** | HRV within normal range **and** RHR < avg + 5 bpm **and** load ratio ≤ 1.3 | Plan as is |
| 🟡 **Yellow** | HRV below range 1–2 days in a row **or** RHR ≥ avg + 5 bpm **or** load ratio 1.3–1.5 | Quality session: −1 rep or cap −3 %, or switch to Z1. Easy runs and rides: unchanged |
| 🔴 **Red** | HRV below range ≥ 3 days in a row **or** low HRV + RHR ≥ avg + 5 bpm the same day **or** load ratio > 1.5 | Rest or very easy Z1 (bike preferred). Notify the athlete |

**Notifications:** only **yellow** affecting a quality session and **red**. Green is logged silently.

**Log:** each run adds one line to `athlete/traffic-light-log.md`, read by the weekly review.

**Limit:** the traffic light does not see pain, illness or niggles. If present, the athlete decides: rest or Z1, and tells the agent.

> Evidence: HRV-guided training barely improves mean performance versus a fixed plan, but **reduces non-responders** and tends to prevent failed blocks. That is why it is used.

---

## 9. Outcome variables and tests

### 9.1 Periodic tests (every 4–6 weeks, at the end of a deload)

| Test | Sport | Measures |
|---|---|---|
| Stryd **CP** recalibration (e.g. 3 min + 9 min, or a recent race) | Run | Power threshold |
| **30-min test** (LTHR = average HR of the last 20 min) | Run (bike only to recalibrate the Z1 cap) | LTHR |
| **Control run:** 30–40 min at fixed Z1 power or HR, same course | Run | HR at equal power (aerobic efficiency) |
| **Durability:** Pa:HR decoupling in the long run | Run | Drift in long efforts |
| **Bike drift test:** 45–60 min at comfortable conversation pace | Bike | Bike Z1 cap (HR where drift < 5 %) |

A test done in conditions that bias it (illness, fatigue, heat) is recorded with `valid = 0` and repeated. The athlete's test calendar lives in `athlete/profile.md`.

### 9.2 Tracking indicators

- Average HR at fixed power (should fall over time).
- Pa:HR decoupling (target < 5 % in base long runs).
- Power and pace in threshold sessions at equal HR cap.
- HR-cap compliance on bike rides.
- Yellow and red days per week.
- Race and time-trial results.
- Body weight (weekly trend, never daily).

---

## 10. Review protocol

Planning is **weekly**. Only the automatic traffic light runs daily (section 8).

### 10.1 Weekly review

**Step 0 — Pre-check (mandatory, before any analysis):**

1. Read the week's runs in COROS (records, detail, laps) and their streams in Strava; read rides in **Strava** (cycling types). Match each COROS run to its Strava activity by date, start time and distance, so it is never counted twice.
2. If there is **no ride** in Strava that week, **ask the athlete before continuing**: no rides, or not synced? (In unattended runs: continue and flag "pending confirmation".)
3. Check that rides are typed as cycling and have an HR stream, and that each run has HR and power streams in Strava. Warn if any is missing.
4. Read the week's traffic-light log.
5. Read the automatic COROS RPE and every activity note. Ask the athlete only for what is missing: how they felt and any pain (during return to run, ask explicitly about the injured site).

**Analysis:**

1. **Execution:** each session vs plan (time in zone, Norwegian caps, bike Z1 cap) and vs traffic-light changes.
2. **Distribution:** % time Z1/Z2/Z3 vs phase target.
3. **Load:** CTL, ATL, TSB, ACWR and run impact load.
4. **Response:** HRV and RHR trend, sleep, yellow/red days, sRPE of key sessions, feedback.
5. **Quality:** HR drift in thresholds? Any failed recovery ride?
6. **Decision** (one of three, always justified with data):
   - **Push:** +5–10 % volume or +1 threshold rep, if everything is green and CTL rises within limits.
   - **Hold:** mixed signals.
   - **Ease:** −15–30 % volume or bring the deload forward, with 2+ yellow days, any red, ACWR alert, illness or persistent pain.
7. **Next week's plan:** upload **every session** to COROS (runs, reference rides, strength days with warm-up), with strength and instructions in descriptions. Verify with `queryTrainingSchedule`.
8. **Log** in `athlete/weeks/YYYY-Www.md` and `athlete/data/`.

### 10.2 Per block (every 4 weeks)

1. Tests (9.1) and zone recalibration in `athlete/zones.yaml` (history in `athlete/profile.md`).
2. Evaluate active hypotheses (section 13).
3. Decide the next block.

---

## 11. Platforms and data flow

### 11.1 Supported setup

| Device | Use |
|---|---|
| **COROS watch** | Run: workout execution, HRV, sleep, perceived effort, notes |
| **Stryd** | Run power and running dynamics |
| **Bike computer** (e.g. Garmin) | Ride recording, synced to Strava |
| **Chest strap** | HR in both sports |

### 11.2 Architecture

Two connectors: **COROS** (official, read and write) and **Strava** (official, read only: run and bike streams). The bike computer has no connector: it syncs rides to Strava. COROS syncs runs to Strava.

```
            ┌──────────────────── AGENT ─────────────────────┐
            │  weekly review and plan · daily traffic light  │
            └──────┬──────────────────▲─────────────────▲────┘
   writes every    │                  │ reads runs      │ reads streams
   session         ▼                  │ (laps, Stryd)   │ (run and bike)
            ┌───────────────────────────────┐    ┌──────────────┐
            │             COROS             │───▶│    STRAVA    │
            └───────────────────────────────┘    └──────▲───────┘
              HRV, sleep, schedule       run sync        │ bike sync
                                                 ┌──────┴──────┐
                                                 │ BIKE COMPUTER│
                                                 └─────────────┘
```

| Platform | Write | Read |
|---|---|---|
| **COROS** | Every session of the week: structured runs, reference rides, strength days (warm-up + description) | Runs (records, detail, laps, Stryd metrics, perceived effort, note), HRV, RHR, sleep, load, schedule. FIT when readable |
| **Strava** | — (no write) | 1 Hz run streams (HR, power, speed, cadence) and bike streams (HR, time); activity descriptions |

Connector details: `integrations/`.

### 11.3 Data used (scientific-method requirement)

- **Run — Strava streams, second by second:** HR, Stryd power, speed and cadence at 1 Hz, full resolution. Used for zones, TSS, EF, decoupling and cap compliance per rep.
- **Run — COROS:** laps of the structured workout (to compare each rep with its cap) and Stryd metrics per lap and per session (ground contact, vertical oscillation, stride length, leg stiffness, form power). If the FIT can be read, it replaces the Strava stream as primary source.
- **Bike — Strava:** duration, distance, elevation and 1 Hz HR stream (hrTSS, time in zones, Z1 cap compliance).
- **Daily COROS metrics:** HRV, RHR, sleep.
- **Precision control:** duration and average HR from the stream must match COROS (±1 % and ±1 bpm), and lap power from the stream must match COROS laps (±2 %). Mismatches are noted and COROS is used for summaries.
- Platform-computed summaries (load, "relative effort", etc.) are kept for reference only, except the daily traffic-light approximation; official metrics are recomputed from raw data.

---

## 12. Nutrition

### 12.1 During exercise

| Duration | Carbohydrate (g/h) |
|---|---|
| < 75 min | Not needed; optional mouth rinse |
| 1–2.5 h | 30–60 |
| 2.5–6 h (incl. marathon) | 60–90, glucose:fructose mix |
| Ultra / very long ride | Up to 90–120 with a trained gut |

- **Gut training:** practise the target intake in long runs and race-pace sessions.
- Figures of 120–200 g/h circulating in practice lack scientific support so far.

### 12.2 Energy availability (REDs safeguard)

- **Never** a caloric deficit in high-load weeks or the specific phase.
- Weight loss, if sought, only in base, gradually, prioritising carbohydrate around quality sessions.
- **Warning signs** to monitor: persistent HRV drop, fatigue that does not resolve with deload, stalled performance with stable load, bone pain, sleep or mood changes. Response: reduce load and recommend medical assessment.

### 12.3 Lab results

- The agent may **record** values (ferritin, haemoglobin, vitamin D, etc.) and their trend in `athlete/data/measurements.csv`.
- **Interpretation and any supplementation** belong to a health professional.

---

## 13. Hypothesis register (n=1 experiments)

Template (records live in `athlete/hypotheses.md`):

```
ID: H-001
Start date:
Hypothesis: (e.g. "3 weekly Norwegian thresholds lower HR at fixed power more than 2")
Outcome variable: (section 9)
Duration: (minimum one 4-week block)
Control: (what stays constant)
Result:
Decision: (adopt / discard / repeat)
```

**Default hypotheses for a new athlete:**

- **H-001:** with pyramidal distribution and 2–3 Norwegian thresholds per week, control-run HR falls ≥ 3 bpm at equal power in 8 weeks.
- **H-002:** adding 2–3 h/week of Z1 cycling improves run HR at fixed power and keeps HRV stable, without more impact niggles.
- **H-003:** 2 weekly strength sessions (unilateral, limited equipment) reduce Pa:HR decoupling in the long run.

---

## 14. Main references

- Intensity distribution in elite athletes by season phase — *Frontiers in Sports and Active Living*, 2023. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10641476/
- Polarized vs other models — meta-analysis, *Sports Medicine*, 2024. https://pmc.ncbi.nlm.nih.gov/articles/PMC11329428
- Network meta-analysis of intensity models with individual data (2024).
- Casado et al. — lactate-guided threshold within high low-intensity volume (Norwegian method), *IJERPH*.
- Mølmen, Øfsteng, Rønnestad — Block periodization, *Open Access Journal of Sports Medicine*, 2019. https://pmc.ncbi.nlm.nih.gov/articles/PMC6802561
- Banister — fitness–fatigue model; Zouhal et al. — ACWR editorial, *Frontiers in Physiology*, 2021. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8138569/
- Manresa-Rocamora et al. — HRV-guided training meta-analysis, *IJERPH*, 2021. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8507742/
- HRV-guided training with wearables — meta-analysis, *J Sci Med Sport*, 2021. https://pubmed.ncbi.nlm.nih.gov/34489178/
- Hunter, Maunder, Jones et al. — Durability, *Experimental Physiology*, 2025. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12576026/
- Jones — Physiological resilience (2025).
- Heavy strength vs plyometrics on running economy — *Sports Medicine Open*, 2022. https://pubmed.ncbi.nlm.nih.gov/36370207/
- Morton et al. — *From Metabolism to Medals*, carbohydrate guidelines, *Journal of Nutrition*, 2026.
- Mountjoy et al. — 2023 IOC consensus on REDs, *BJSM*. https://pubmed.ncbi.nlm.nih.gov/37752011/
