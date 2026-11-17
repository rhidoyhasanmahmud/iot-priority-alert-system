# Stage 10 FINAL — first frozen synthetic MQTT/SQLite heldout result record

**Date:** 17 November 2026. **Status:** **COMPLETE / INDEPENDENTLY REAUDITED / PREDECLARED ARTIFICIAL-MODEL GATE SUPPORTED**. This is a final experimental evidence record, **not a draft paper or permission to submit**. Professor decision is pending on Thursday 19 November 2026.

## 1. Frozen design and evidence provenance

- Frozen protocol: `STI-2026-STAGE10-BOUNDED-ROUTINE-RECOVERY-HELDOUT-V1`, **SHA-256 `c66ba9824418ba20fc08be4bcfbb71bc72bff5e04f5b03d38794ccd297fa1429`**. The protocol was committed before any heldout execution and was never changed after the result.
- Code commit that actually generated data: `be73fdcebf987bb227a9cd3dd9b721681724d72c` (Stage 10 first-frozen PR #58; subsequently merged to `main`).
- **30 untouched independent synthetic source seeds `230001..230030` × 5 workload cells × 4 matched policies = 600 fresh MQTT/SQLite trials**, 150 four-policy source-matched blocks, 60 offered alerts/trial (15 urgent, 45 routine), 36,000 alert offers total. Previously inspected development seeds `9001..9010` and Stage 8/9 holdout seeds were excluded.
- Exact input fixtures, per-offer JSONL ledgers, physical main-worker SQLite files, Stage 10 pending-spool SQLite files, source-manifest SHA-256 checks, worker outcomes, host characterization and broker/dependency versions are preserved. There was **one first heldout execution**, from 2026-11-17 11:24:23 to 11:34:17 UTC; do not rerun or retune on these seeds.
- Both GitHub CI's independent audit and a second local audit re-opened **all 600** raw runs and **agree byte-for-byte** on the final result JSON: SHA-256 **`be121e2458b7dc6e47d81c264aa386a1485c55e5b4ff783e6e45dc1383f98852`**. Complete ZIP artifact SHA-256 **`e918c6304ddd50b982744a6ffad9c991ef6842f2c26b8252196c4b310b3e18c0`**.
- First-execution GitHub Actions: [run #44073533550](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/actions/runs/44073533550); [all raw evidence artifact #14323638461](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/actions/runs/44073533550/artifacts/14323638461). The GitHub Actions copy has finite retention; retain the separate durable raw ZIP backup.
- Environment: GitHub-hosted Ubuntu 24.04, 4 logical CPUs, Python 3.12.16, SQLite 3.45.1; real loopback MQTT broker; artificial PBKDF2 simulated processing and SQLite WAL/FULL persistence; **one nonpreemptive worker**. The lab characterization passed its *artificial-only* audit. **No field tracing or measured IoT SLO was used.**

## 2. What the algorithms and metrics actually mean

Four policies ran on the **same source fixture in randomized order** for each block:

1. **FIFO + bounded deferral (`B=8`)** — chronological scheduling, extra pending capacity.
2. **Strict urgent-first + bounded deferral (`B=8`)** — class-priority scheduling, equal extra capacity.
3. **Stage 9 urgent pushout + strict dispatch (`B=0`)** — prior no-additional-spool baseline. **Not an equal-resource comparator.**
4. **Stage 10 urgent pushout + bounded deferred recovery (`B=8`)** — selected candidate. Displaced routine alerts are durably written to a pending SQLite spool before removing them from the main waiting queue, and can finish during the finite run's drain. If pending B is already full, a displaced alert can still be cancelled. Pending capacity B=8 **does not bound historical database bytes**; crash/restart replay was **not** validated.

- **U ↓** = fraction of *all offered urgent alerts* rejected, cancelled, or completed after the **artificial 50 ms** relative deadline. Lower is better.
- **R ↑** = fraction of *all offered routine alerts* whose service started by the **artificial 20 ms** threshold. Higher is better.
- **C ↑** = fraction of *all offered routine alerts* ultimately completed **after the offered workload ends and finite drain is allowed**. C is **not** deadline compliance, nor a guarantee for a sustained infinite workload.

## 3. Entire 600-run policy comparison (mean over 30 source seeds)

Each cell displays **U / R / C** in percent. K is main waiting-queue capacity, B is additional pending-spool capacity.

| Source-matched cell | FIFO B8 | Strict B8 | Stage 9 pushout B0 | **Stage 10 pushout+deferred B8** |
|---|---|---|---|---|
| **Burst K3 — PRIMARY** | 36.00 / 28.59 / 78.67 | 38.00 / 26.96 / 78.89 | 0.00 / 26.15 / 52.59 | **0.00 / 26.30 / 66.30** |
| Overload K3 | 50.22 / 5.41 / 61.19 | 53.56 / 4.67 / 62.30 | 1.11 / 2.00 / 29.19 | **1.11 / 2.07 / 46.52** |
| Smooth K3 | 0.00 / 100.00 / 100.00 | 0.00 / 99.56 / 100.00 | 0.00 / 99.56 / 100.00 | **0.00 / 99.56 / 100.00** |
| Variable-work K3 | 0.00 / 99.11 / 100.00 | 0.00 / 99.19 / 100.00 | 0.00 / 98.96 / 100.00 | **0.00 / 98.96 / 100.00** |
| Burst K0 — negative control | 66.67 / 27.41 / 71.33 | 30.89 / 25.48 / 71.48 | 50.44 / 49.78 / 49.78 | **49.33 / 54.15 / 54.15** |

The **negative K0 result matters**: when there is no waiting slot to push out, Stage 10 urgent failure **49.33%** is *worse* than equal-B8 Strict **30.89%**. This is not a universally superior algorithm. Under overload, routine timely starts are only **2.07%** for the candidate: the proposed scheme does **not solve routine SLO compliance**.

## 4. Frozen PRIMARY decision: all four components passed under the artificial model

Predeclared primary cell **burst K3**, 30 source-paired differences, deterministic **10,000-resample paired-source percentile bootstrap**. Differences and 95% CIs below are **absolute percentage points (pp)**, not relative percent change.

| Frozen component | Observed paired mean (95% CI), pp | Predeclared decision | Result |
|---|---:|---|---|
| Candidate urgent U improvement against **equal-B8 FIFO** | **+36.00** [32.22, 39.78] | Lower 95% CI > **+5 pp** | **PASS** |
| Candidate urgent U improvement against **equal-B8 Strict** | **+38.00** [34.44, 41.78] | Lower 95% CI > **+5 pp** | **PASS** |
| Candidate routine eventual C improvement against **Stage 9 B0** | **+13.70** [12.52, 14.74] | Lower 95% CI > **+5 pp**; added B8 disclosed | **PASS** |
| Candidate urgent U minus Stage 9 B0 | **0.00** [0.00, 0.00] | Upper 95% CI < **+10 pp** | **PASS** |

**Prespecified intersection gate: SUPPORTED under this single artificial system model.** This gate is not a claim of algorithmic novelty, operational safety, field calibration, journal acceptance, or equal-resource dominance over Stage 9.

### Mandatory unfavorable equal-capacity comparison

The Stage 10 candidate **loses routine eventual completion to equal-B8 Strict** by **−12.59 pp** (95% paired CI **[−14.07, −11.11] pp**), and to equal-B8 FIFO by **−12.37 pp** (95% paired CI [−13.78, −10.96] pp). Candidate R is also low: **26.30%** vs Strict **26.96%** and FIFO **28.59%**. The **+13.70 pp C recovery over Stage 9 B0 uses eight additional pending slots** and therefore cannot be attributed to scheduling alone. Burst Stage 9 already has **0% urgent U**; Stage 10 matches it but does not improve urgent failure over Stage 9 in this fresh heldout.

## 5. Publication-claim boundary and remaining professor decision

**Experiment execution and evidence audit: complete. No further algorithm tuning or resampling against this frozen holdout.**

Still **not verified**: (i) originality relative to closely related published admission/scheduling/recovery algorithms, (ii) applicability to measured IoT arrival and processing traces, (iii) externally approved actual urgent/routine SLAs, (iv) crash-and-restart recovery and sustained overload behavior, (v) multiple physical hosts/hardware, (vi) long-duration operational cost (including SQLite spool growth and disk/energy), and (vii) selection bias from investigator-chosen thresholds/margins after viewing development pilots. Secondary effects have not been corrected for multiple comparisons. Confidence intervals quantify only **variation across these synthetic source seeds**.

### Supervisor go/no-go on Thursday 19 November 2026

1. **Scientific fit:** Is the actual contribution best framed as a *measured tradeoff* between urgent protection and bounded routine salvage with additional buffer—not a universally superior or necessarily novel scheduler?
2. **Fairness:** Is it acceptable that the candidate gains urgent protection versus both **equal-B8** FIFO and Strict but sacrifices ~12.6 pp routine eventual completion relative to equal-B8 Strict, while B8 boosts C versus Stage 9 B0?
3. **External validity:** Is a tightly labelled artificial-model conference submission acceptable, or must measured IoT traces, additional resource-normalized experiments, crash recovery or proof of novelty be added first?
4. **Only upon explicit supervisor GO:** begin IEEE/STI-2026 manuscript writing in the supplied template, using frozen evidence and complete limitations; get coauthor review before any actual submission. If NO-GO, record the requested follow-up as a **new separately versioned study** without editing this first heldout.

**Current publication decision: PENDING PROFESSOR. No paper drafted or submitted.**
