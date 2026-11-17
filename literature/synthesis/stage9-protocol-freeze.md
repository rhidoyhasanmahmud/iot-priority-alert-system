# Stage 9 — Experimental protocol freeze (NO manuscript)

**Status:** Pre-registered before accessing any Stage 9 held-out source seeds. Stage 8 is permanently separate; its negative primary finding is not overturned by exploratory pilot observations.

**Frozen identity:** `STI-2026-STAGE9-URGENT-PUSHOUT-HELDOUT-V1`  
**Frozen file:** `literature/validation/stage9_frozen_protocol.json`  
**SHA-256:** `ece4f64d62e668eafe5d3518219155ca76c3d017c00fb029fafa3d18b1f29b89`

## Honest research question

Within a **single-worker, finite-waiting-queue, synthetic IoT MQTT-to-SQLite testbed**, can **joint class-aware admission plus strict urgent-first dispatch** reduce the offered-population urgent deadline-failure rate relative to **both FIFO and Strict Urgent-First**, without reducing the routine timely-start fraction by more than an investigator-defined tolerance?

This is *not* a scheduling-only intervention: the new candidate evicts an already waiting routine alert when a new urgent alert arrives to a full queue. Therefore a lower urgent-failure rate may be due to the **different admission rule**, not a smarter ordering algorithm. No active job is preempted. Push-out admission itself is established queueing prior art, and no novelty or production fitness is claimed.

## Policies and fair comparison

| Label | Admission when K full | Dispatch of waiting jobs |
|---|---|---|
| FIFO | Reject new offer | FIFO |
| Strict Urgent-First | Reject new offer | Urgent first, FIFO within class |
| Routine Wait Guard (Stage 8 incumbent) | Reject new offer | Guarded routine selection |
| Urgent Push-out + Strict Priority (Stage 9) | Urgent offer replaces newest *waiting routine*, if any; otherwise reject | Urgent first, FIFO within class |

All four receive the same **source fixture** within each seed/scenario/K block, use the same one nonpreemptive worker, real PBKDF2+SQLite WAL FULL service, deadline definitions, capacity K and loopback MQTT transport. Per-policy local MQTT arrival timestamps/order are observed and reported, not assumed identical. Each run uses an independent process and SQLite database. An evicted routine is counted as **routine failure** in the complete offered-population denominator; the candidate cannot inflate its apparent success by ignoring displaced alerts.

## Experimental factors — exactly frozen

- 30 **fresh** independent held-out seeds `220001`–`220030`, with no overlap with Stage 8 `210001`–`210030`; reserved pilot/tuning seeds `8001`–`8010` are disjoint and excluded from primary inference.
- 60 offered events per fixture (15 urgent, 45 routine). 10,000 PBKDF2 iterations per synthetic work unit, work-unit family 1/4/7.
- K=3 waiting slots for the primary **burst** scenario; secondaries: smooth K3, overload K3, variable-work K3, and burst K0 **negative control** (no waiting positions exist for pushout).
- `D_urgent=50 ms` from locally validated offer to committed SQLite completion. `tau_routine=20 ms` from locally validated offer to first service start. **Both are investigator-chosen artificial thresholds, not measured device SLAs.**
- 30 source seeds × 5 cells × 4 policies = **600 held-out trials**, organized as 150 source-matched four-policy blocks, with fixed preregistered random block and policy orders.
- Independent per-trial auditors reconstruct queue/admission/dispatch, all offers, cancellations, physical SQLite rows and raw evidence. Separate batch analysis reopens all 600 raw ledgers and DBs.

## Freeze rule and primary decision (do not alter after observing heldout)

Let `U` be the fraction of all offered urgent events that are rejected, cancelled or completed **after** the artificial 50ms deadline (lower is better), and `R` the fraction of all offered routine events that start by 20ms (higher is better). Primary **burst/K3** intersection gate requires **all three**:

1. Lower bound of 95% paired-seed bootstrap CI for `U_FIFO − U_new` is greater than **0.05** (5 percentage points).
2. Lower bound for `U_Strict − U_new` is greater than **0.05**.
3. Lower bound for `R_new − R_Strict` is greater than **−0.10** (routine noninferiority margin, 10pp).

Bootstrap resamples **30 source seeds** rather than thousands of correlated jobs: 10,000 percentile resamples and fixed PRNG seeds, with CIs on *absolute rate differences*. The thresholds and 10pp margin are investigator choices without stakeholder validation. Multiple secondary comparisons are descriptive/exploratory, **not independently validated discoveries**. No failed/incomplete trial is removed or replaced; a partial run is invalid, not an invitation to retry only favorable subsets.

## Status and interpretation

- **Stage 8 (immutable):** guard hypothesis failed its preregistered 450-run primary test; see `stage8-heldout-result-record.md`.
- **Reserved in-process engineering pilot:** showed a promising large urgent-rate reduction on synthetic burst/K3 with the new admission policy. These observations **are not** real-MQTT 30-seed held-out evidence and must not be reported as a publication-grade finding.
- **Stage 9 holdout:** [initially not run; outcome must be appended only after the first frozen pipeline finishes and is independently audited].
- **Professor meeting:** demonstrate how a queue-full urgent can displace waiting routine, explain the urgent/routine tradeoff, and request a go/no-go decision for subsequent paper **writing**, which has not started.

**Scope restrictions:** Synthetic arrivals and artificial CPU workload; no real trace/workload calibration, multi-worker generalization, end-to-end device/network deadlines, formal hard-real-time guarantees, production deployment study, novel-algorithm claim, or manuscript/submission authorization.

## Reproduction

```bash
python literature/validation/test_stage9_frozen_protocol.py
python literature/validation/stage9_frozen_study.py --mode pilot --pilot-seeds 8008 --output-dir stage9-pilot
python literature/validation/stage9_independent_analysis.py --pilot --study-dir stage9-pilot
# The *first* held-out execution is controlled by the Stage 9 GitHub Actions workflow,
# with fresh pinned source revision and real Mosquitto. No opportunistic re-runs.
```
