# Stage 10 — Final experimental protocol freeze (NO paper)

**Protocol ID:** `STI-2026-STAGE10-BOUNDED-ROUTINE-RECOVERY-HELDOUT-V1`  
**Pinned SHA-256:** `c66ba9824418ba20fc08be4bcfbb71bc72bff5e04f5b03d38794ccd297fa1429`  
**Frozen JSON:** `literature/validation/stage10_frozen_protocol.json`  
**Freeze:** 17 November 2026, before opening any Stage 10 `230001..230030` holdout fixture.  
**Prior pilot disclosure:** The `B=8` candidate was selected **after** inspecting reserved synthetic development seeds `9001..9010`; these are never used for holdout inference.

## Research question, defined without outcome flexibility

Can an urgent pushout policy that **adds** a bounded durable deferred routine buffer (8 extra *pending* slots) simultaneously (i) protect urgent completion deadlines relative to **both** FIFO+B8 and Strict+B8, (ii) recover more routine completions than the original Stage9 urgent pushout+B0, and (iii) avoid a practically excessive urgent regression relative to Stage9+B0 **under this artificial model**?

This study is **not** a claim of equal-resource dominance: B8 vs Stage9+B0 changes available admission capacity. The candidate's `C` can be lower than matched B8 FIFO/Strict, and **that loss must be reported**. Persisting a victim in SQLite before main-queue removal is real per-run I/O but process crash/restart recovery is not implemented/tested. The spool bounds pending jobs, **not cumulative SQLite history bytes**. Priority queueing and pushout admission are established ideas; algorithm novelty is **not verified**.

## Frozen setup

- 30 **previously unseen** synthetic source seeds `230001..230030`; excluded Stage8 `210001..210030`, Stage9 `220001..220030`, and Stage10 dev `9001..9010`.
- Exactly 60 offers per source fixture (15 urgent, 45 routine), one original nonpreemptive worker, local real Mosquitto MQTT broker and Python paho client, actual PBKDF2 work + SQLite WAL/FULL commit.
- Primary: clustered burst/K3. Secondary: smooth/K3, overload/K3, variable-work/K3, burst/K0 negative control. `K` counts main *waiting* slots, not the active worker. `B` counts extra currently pending deferred slots.
- Each paired block runs **four policies**: FIFO+B8, Strict Urgent-First+B8, Stage9 Pushout+B0, and Stage10 Pushout+Deferred Recovery+B8. A new process, source-matched offer fixture and physical SQLite database are used per policy. Random block and policy order are deterministic and pinned.
- 30 seeds × 5 cells × 4 policies = **600 real-MQTT/SQLite trials**, first execution only. Every raw ledger, fixture, worker SQLite database, and spool SQLite backup must independently pass SHA-256, source, capacity, queue, dispatch, and physical service reconstruction.
- Synthetic urgent deadline **50ms** after local validated offer; synthetic routine timely-start threshold **20ms**. These are investigator choices, **not measured IoT SLAs**.

## All-offered metrics

| Metric | Definition | Desired direction |
|---|---|---|
| **U** | All offered urgent rejected, cancelled or SQLite-completed after 50ms, divided by all offered urgent | Lower |
| **R** | All offered routine starting worker service within 20ms, divided by all offered routine | Higher |
| **C** | All offered routine eventually completed after the **finite-source end-of-run drain**, divided by all offered routine | Higher |

`C` does **not** test a routine completion SLA; it counts completed accepted work after draining. C must never be marketed as timely completion or a sustained-overload guarantee. Per-class rejected and cancelled counts stay in denominators; nothing is excluded for a favorable rate.

## Predeclared primary decision — ALL four components

On 30 source-matched seeds for primary burst/K3, calculate a **95% paired-seed percentile bootstrap CI with exactly 10,000 resamples**. The four-way gate is considered supported **only if all**:

1. Lower 95% CI of `U_FIFO+B8 − U_Stage10+B8` **> 0.05**.
2. Lower 95% CI of `U_Strict+B8 − U_Stage10+B8` **> 0.05**.
3. Lower 95% CI of `C_Stage10+B8 − C_Stage9+B0` **> 0.05** (**added capacity explicitly disclosed**).
4. Upper 95% CI of `U_Stage10+B8 − U_Stage9+B0` **< 0.10** (artificial investigator-chosen urgent noninferiority tolerance).

Mandatory descriptive comparison: `C_Stage10+B8 − C_Strict+B8` and `C_Stage10+B8 − C_FIFO+B8`, both with paired CIs, along with **R**, source jitter, capacity use, urgent late completions and cancellations. Secondary cells are exploratory; no positive secondary result can overwrite a failed primary gate. Margins were selected after examining development data and have no field-owner approval.

## Immutable execution and decision handoff

1. CI first runs protocol-hash/seed-isolation/adversarial tests and an independent auditor on a reserved in-process preflight. **No heldout seed is opened during preflight.**
2. The first frozen heldout GitHub CI job pins the PR head commit SHA, real broker/Python versions, host characterization and all 600 source-matched trials. Any failed/incomplete run invalidates the full study; **do not selectively retry or substitute favorable runs**.
3. A separate analysis code path reopens **all 600** ledgers and physical main/spool SQLite databases before producing paired seed CIs and the four-component gate. It must emit the result even if the gate fails.
4. Preserve raw evidence, version hashes, full negative findings and CI job record for supervisor review.
5. **Do not write or submit a manuscript before Professor go/no-go.** Even a positive artificial-model gate cannot establish empirical field reliability, originality, energy efficiency, safety, hard real-time guarantees or paper acceptance.

## Reproduction

```bash
python -m unittest discover -s literature/validation -p 'test_stage10_frozen_protocol.py' -v
python literature/validation/stage10_frozen_study.py --mode pilot --pilot-seeds 9008 --output-dir stage10-reserved
python literature/validation/stage10_independent_analysis.py --pilot --study-dir stage10-reserved
# The unique frozen real-MQTT heldout run is performed by the pinned GitHub Actions PR workflow.
```
