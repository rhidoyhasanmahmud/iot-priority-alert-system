# Stage 9 — Frozen synthetic held-out result (NOT a manuscript)

**Date:** 17 November 2026 (UTC). **Project:** STI 2026, controlled priority IoT-alert MQTT-to-SQLite testbed.  
**Precommitted protocol:** `STI-2026-STAGE9-URGENT-PUSHOUT-HELDOUT-V1`, SHA-256 `ece4f64d62e668eafe5d3518219155ca76c3d017c00fb029fafa3d18b1f29b89`.  
**Source commit before opening holdout:** `109d69299f0e9f45a95e0c1db8f9c086d0ed1749`.  
**First frozen workflow:** [GitHub Actions 43991794944](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/actions/runs/43991794944), two jobs **successful**.  
**Raw artifact:** `stage9-frozen-heldout-raw-not-field-evidence` (ID `14288956385`), compressed SHA-256 `fc02eb8bdb1f82fd33a4a7e37c61010b9cb4df369678efecee362b48d7b35a53`; [download via Actions run](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/actions/runs/43991794944). Scheduled expiry **15 February 2027, 00:57:31 UTC**.  
**Independent-results JSON:** SHA-256 `a1cb6e47eb0fe9f5b11d468c26f336df4ce50d24d15eaf4f42a80f793e4fda0b`.

## Verification

Exactly **600/600 real-Mosquitto MQTT + SQLite WAL FULL synthetic trials** completed; 30 fresh held-out source seeds × five predeclared workload/capacity cells × four policies = **150/150 complete source-matched policy blocks**. Each trial's raw offer ledger, trusted class, admission and dispatch lifecycle, cancellation/rejection, CPU-work identity, persisted SQLite content and artificial timing endpoints passed its **separate independent raw auditor**. The entire downloaded ZIP was independently re-audited on a second environment; the recalculated batch JSON was **byte-identical** to the workflow output (SHA-256 above). All observed source-order inversion counts were zero.

The experiment compares policies on the **same synthetic source fixtures**, but per-run local MQTT arrival timing and host scheduling can differ. The new candidate changes **admission as well as dispatch**; this is not an isolated scheduling comparison. Push-out admission is known prior art, and no algorithm-novelty or field-calibration claim is made.

## Primary burst scenario (K=3; all 30 held-out source seeds)

The *offered-population* metrics were frozen before testing:

- **Urgent failure U (lower is better):** share of all 15 offered urgent alerts per run rejected, cancelled, or committed after the artificial **50 ms** local deadline.
- **Routine timely-start R (higher is better):** share of all 45 offered routine alerts per run starting service within artificial **20 ms** of locally validated offer.
- `K=3` counts waiting positions **in addition to** one nonpreemptive active worker.

| Policy | Urgent deadline failure U ↓ | Routine timely-start R ↑ | Routine rejected / run | Routine evicted / run | Routine eventually completed* |
| --- | ---: | ---: | ---: | ---: | ---: |
| FIFO | **36.44%** | **28.15%** | 15.90 | 0 | 64.67% |
| Strict Urgent-First | **38.00%** | **26.30%** | 15.87 | 0 | 64.74% |
| Routine Wait Guard (prior, not selected) | **50.00%** | **57.33%** | 16.20 | 0 | 64.00% |
| Urgent Push-out + Strict Priority | **0.00%** | **25.70%** | 16.07 | **5.53** | **52.00%** |

*Routine eventual completion is an additional **descriptive, post-hoc fairness diagnostic**, not part of the frozen primary decision. It is computed from the independently checked terminal counts: `(45 − routine_rejected − routine_evicted) / 45`. It highlights a cost the timely-start metric alone does not capture.*

**Statistical decision** (30 source-seed paired, 10,000 percentile bootstrap replicates; all differences are absolute percentage points):

| Precommitted criterion | Mean paired effect | 95% CI | Decision |
| --- | ---: | ---: | --- |
| `U_FIFO − U_new` must have CI lower bound > +5 pp | **+36.44 pp** | **[+32.67, +40.44] pp** | PASS |
| `U_Strict − U_new` must have CI lower bound > +5 pp | **+38.00 pp** | **[+33.78, +42.44] pp** | PASS |
| `R_new − R_Strict` CI lower bound must exceed −10 pp | **−0.59 pp** | **[−1.04, −0.22] pp** | PASS |

**PREDECLARED PRIMARY RELATIVE INTERSECTION GATE: SUPPORTED UNDER THIS ARTIFICIAL MODEL.** It does **not** mean the new policy dominates every metric. The experimental candidate displaced on average **5.53 waiting routine jobs/run** and cut routine **eventual completion by ~12.74 pp** relative to Strict Urgent-First, an important fairness/displacement cost that is **not captured by R**. In addition, the exploratory absolute joint target (`U ≤ 10%` **and** `R ≥ 75%`) **was not met**: the candidate reached `U=0%` but only `R=25.70%`. These are not true field SLAs.

## Secondary synthetic conditions (descriptive, not confirmatory)

| Cell | FIFO U / R | Strict Urgent-First U / R | Old Guard U / R | New Push-out U / R |
| --- | ---: | ---: | ---: | ---: |
| Burst K3 (primary) | 36.44 / 28.15 | 38.00 / 26.30 | 50.00 / 57.33 | **0.00 / 25.70** |
| Smooth K3 | 0.00 / 100.00 | 0.00 / 99.04 | 0.00 / 100.00 | 0.00 / 99.04 |
| Overload K3 | 51.78 / 5.26 | 52.00 / 4.00 | 72.67 / 38.96 | **3.56 / 1.93** |
| Variable work K3 | 0.00 / 99.26 | 0.00 / 98.07 | 0.22 / 99.33 | 0.00 / 98.22 |
| Burst K0 (no waiting, negative control) | 52.89 / 49.41 | 52.22 / 49.19 | 53.11 / 49.70 | **52.00 / 48.89** |

Numbers are percentages `U / R` (lower / higher respectively). As expected, **K0 has no queue slot to push out**, so the candidate's large urgent improvement disappears. Under smooth/variable workloads urgent failure is already at the floor, leaving almost no potential improvement. Overload urgent benefit again comes at the cost of very poor routine timely-start and **~7.53 routine evictions/run**. Secondary differences/intervals are not multiplicity-adjusted.

## Reviewer's bounded interpretation and professor decision

1. **Engineering and frozen-model hypothesis succeeded:** first-run, source-matched, 600-trial synthetic real-MQTT experiment and independent audit passed; artificial urgent failures were substantially lower than *both FIFO and Strict Urgent-First* in the primary burst/K3 cell.
2. **Global fairness and operational suitability are not established:** this is a priority-aware *drop/displace* strategy. It saved urgent offers by shifting loss toward routine offers, reducing their eventual completion by ~12.74 pp. The frozen `R` criterion alone is insufficient to assert broad fairness or service reliability.
3. **Novelty is unproven:** the central push-out mechanism is established prior art. Do not present these results as a novel algorithm or a publishable contribution without a sharper verified research gap, stronger comparable admission baselines, theoretical/empirical fairness analysis and a credible application-specific workload.
4. **External validity is absent:** synthetic source/workload, no real-device trace calibration, one Ubuntu runner/worker, artificially chosen 50/20ms timing objectives, single broker/process context, no deployment/end-to-end delay claims or hard real-time guarantees.
5. **Stage 8's negative guard result stands unchanged.** This is a new Stage 9 pre-registered experiment with different seeds and changed admission logic, not a post-hoc rewrite of Stage 8.
6. **No manuscript drafted or submitted.** Thursday **19 November 2026** professor meeting should seek a go/no-go decision on research positioning and whether to *begin* scientific paper writing. A passed relative gate is not itself a submission recommendation.

**Freeze contract:** Do not retune frozen Stage 9 algorithm, seeds, deadlines, margins, workload or primary inference after the observed heldout results; any scientifically new variant needs a new versioned protocol and independent holdout. Archive raw ZIP and independent JSON before 15 February 2027; a summary table is not a substitute.
