# Stage 5K — Controlled workload and handler calibration: evidence before parameters

**Date:** 16 November 2026  
**Chosen direction:** Controlled Testbed; **not** a field-sensor deployment.  
**Status:** **5K.1 descriptive raw-evidence audit COMPLETE; application/workload calibration and scientific protocol NOT APPROVED.**  
**Inputs:** [Stage 5J broker-backed controlled testbed](controlled-testbed-stage5j.md), [Stage 5I external-evidence gate](workload-evidence-calibration-stage5i.md), [Stage 4B novelty decision](novelty-decision-stage4b.md), and [RQ v1.0](research-questions.md).

> **What this stage contributes so far:** a reproducible, fail-closed description of what our synthetic MQTT/SQLite testbed actually measured, including class-wise admission, observed handler durations **of committed offers only**, source-shape controls and environment provenance. It does **not** calibrate the generator to actual traffic or validate an operational threshold.

## 5K.1 — Audited descriptive profile, not inferred service demand

The [Stage 5K profile implementation](../validation/stage5k_workload_profile.py) first calls the **independent Stage 5J batch gate**. That gate reopens **every** raw JSONL, SQLite backup and child log and checks their hashes and source design; only then does the profiler compute class-wise descriptive counts and committed-service timing distributions. The profiler does **not** import or depend on the source gateway/handler for normal operation. A missing or tampered raw artifact fails the analysis rather than relying on the tiny archived manifest alone.

For [the original 18-case real-broker Stage 5J CI run #43882411348](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/actions/runs/43882411348), independent re-analysis of the downloaded raw artifact returned:

| Shape | K waiting | Offered synthetic | SQLite committed | Buffer rejected |
| --- | ---: | ---: | ---: | ---: |
| base | 0 | 180 | 165 | 15 |
| base | 3 | 180 | 174 | 6 |
| burst | 0 | 180 | 118 | 62 |
| burst | 3 | 180 | 140 | 40 |
| overload (different intensity) | 0 | 180 | 38 | 142 |
| overload (different intensity) | 3 | 180 | 62 | 118 |
| **Total** | — | **1,080** | **697** | **383** |

The 18 separate per-run 95th-percentile **SQLite fictional handler spans among *completed* jobs** ranged from approximately **0.621 to 2.054 ms** on the recorded CI host; see [machine-readable profile](../validation/fixtures/stage5k_stage5j_ci43882411348_profile.json) for all exact integers and each host/source/ledger hash. These figures are **not** performance targets or calibrated processing demands. The saved profile records only per-run descriptive p95s; no pooled pseudo-replication, group significance, or urgency policy improvement is inferred.

**Selection bias is decisive:** The full queue rejects many offers before their handler starts. We do not know the counterfactual service time those rejected events would have required. Their missing processing demand **cannot be assumed to be missing at random**: admission depends on arrival timing, queue state and preceding service, potentially interacting with event type or work. Therefore neither the 697 observed service durations nor their class-wise quantiles can be assumed representative of the offered-work distribution. A different policy could admit different alerts even under exactly the same source.

The source is **deterministic fictional tamper/health input**: 1 urgent tamper in every 4 source events and 3 routine health in 4, with seeded device contexts/rules. `base` and `burst` have a matching **planned** 472 ms source horizon per 60 events, while `overload` has zero planned gaps and thus **higher intensity**, not a pure alternative burst shape. Actual measured local offer spans differ from planned source gaps. `K=0/3` and `D_u=τ=50 ms` are **debug settings only**.

The [CI raw artifact #14233685797](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/actions/runs/43882411348/artifacts/14233685797) has 14-day GitHub retention (expected expiry around **30 November 2026**). The [archived run manifest](../validation/fixtures/stage5j_ci43882411348_batch.json), [Stage 5J audit summary](../validation/fixtures/stage5j_ci43882411348_audit.json) and this new profile preserve summaries/hashes but **cannot independently reconstruct or re-audit missing raw SQLite files after expiry**. Save the ZIP to a durable research store before then if historical raw access is required.

**5K.1 technical checklist**

- [x] Separate observed post-commit service times from unobserved offered-work demands and explicitly disclose selection bias.
- [x] Re-audit complete 18-case MQTT raw evidence before computing class-wise and per-run descriptive service diagnostics.
- [x] Preserve paired design distinctions: base/burst matched planned horizon; overload a different-intensity scenario.
- [x] Record selected run hashes, source provenance, class admission and host diagnostics without falsely marking calibration.
- [x] Run a **12-case in-process self-test**, plus **3 negative cases** (forged source provenance, forged completion count and tampered raw JSONL).
- [ ] Add approved/independently sourced workload or defensible controlled-sensitivity parameters.
- [ ] Reproduce controlled-resource diagnostics on pinned and sufficiently characterized hardware, with warm/cold and backend-load repeats.

## 5K.2 — Calibration decision card (UNAPPROVED)

The researcher selected *Controlled Testbed*. This permits **scientific claims about the declared lab conditions**, not claims about a deployed alert service. All scientific assumptions below must be fixed before result-oriented policy comparisons, with review sign-off. A reliable experiment may keep synthetic workloads if assumptions and limits are defensible and the paper's contribution survives strong comparators.

| Decision | Present evidence | Decision required before Stage 6 | Current status |
| --- | --- | --- | --- |
| Application boundary | MQTT callback → validated local offer → finite K → one fictional SQLite worker | Is the selected IoT context a *fictional exemplar* or a justified representative application? Name the observed effect and who can approve it. | **OPEN** |
| Arrival and class mix | 60 seeded offers, fixed 1:3 urgent:routine, planned base/burst horizon | Justify a multi-level class mix and burstiness grid using primary external trace, source characterization or clearly synthetic hypothesis; never call it observed. | **OPEN** |
| Offered service demands | SQLite span measured **only on committed jobs** | Choose independently measured full-application per-type work, or predeclare a controlled service-demand model with fixed mean and varied dispersion; cannot impute rejected jobs from these data. | **OPEN** |
| K waiting positions | K 0 and 3, plus one active service position | Declare actual queue memory/item footprint for production claims, or predeclare nonoperational synthetic K sensitivity without physical-capacity claims. | **OPEN** |
| Urgent U and routine R(τ) | Exact offered-population metric contract; fake 50 ms debug timing | Set source and origin of `D_u`, ε, τ, γ. For synthetic-only studies, state *experimental* target values and sensitivity limits without inventing operator SLAs. | **OPEN** |
| Hardware and environment | CI host/runtime fingerprint, 10ms RSS sampling, child CPU | Fix evaluation host/quota/DB configuration, warmup, repeat count, backup/IO interference and resource measurement methodology. | **OPEN** |
| Novelty and comparator scope | Stage 4B **REVISE/NARROW** | Authorized N01/N03/N06/N09 full-theory review, scientific claim, and supervisor Go/Revise/No-Go. | **OPEN** |

**Proposed factors to discuss, NOT frozen parameter values:**

1. Hold an explicitly synthetic total offered-work *model* fixed where comparing burst concentration; vary burst concentration separately from total arrival intensity.
2. For service-variability sensitivity, choose a disclosed distribution family and at least three variability levels while fixing a disclosed mean. Treat the entire service demand of **all offered IDs** as generated ex ante and save it **even when rejected**; no algorithm may inspect the unknown duration of an unstarted job.
3. Evaluate at least two finite waiting capacities and clearly distinct workload intensity levels with matched seeded source realizations. Define independent experimental units at the **run/capture-period** level, not the alert level.
4. Predefine urgent failure among **all locally offered urgent IDs**, routine timely-start among **all locally offered routine IDs**, and what a zero offered-class denominator means. Keep class-neutral full-queue admission, one non-preemptive worker and a clear expiry rule for fair baseline comparisons.
5. Use a held-out workload set, resource/clock controls, honest measured scheduling overhead, and confidence intervals across independent experimental runs. Avoid estimating uncertainty from the 1,080 correlated per-message events as if independent.

These are study-design requirements, **not** new simulated results and **not** a proposed novel policy. The current FIFO engine is only a testbed baseline; additional algorithms belong **after** Stage 4B/6 decisions.

## 5K.3 — What must be signed off next

- [ ] **Professor:** Is an explicitly declared synthetic-only real-MQTT/SQLite *empirical operating-region study* a suitable conference contribution, given Stage 4B novelty risk?
- [ ] **Researcher + professor:** Approve application scenario, synthetic sensitivity plan or ethically usable trace, and the claim boundary.
- [ ] **Researcher:** Freeze data generation, service-demand source *for every offered ID*, and parameter/sensitivity values **before** held-out experiments.
- [ ] **Supervisor:** Approve a fair and feasible comparator family (FIFO, strict priority, deadline-based, aging, appropriate work-fair/closest prior-work adaptations), information availability and falsification rule.
- [ ] **Research team:** Freeze Stage 6 protocol including run-level independent replication, resource envelopes and statistics.

**Research gate decision — NOT READY FOR STAGE 6 SCIENTIFIC RESULTS.** Stage 5K.1 **engineering/descriptive audit is complete**; scientific workload and service-demand calibration remain **blocked**. Do not write a measured performance advantage or operational reliability result from Stage 5J/5K data.

### Reproduce

From the repository root, with **the complete raw** `stage5j` artifact (not only archived `batch.json`):

```bash
python3 literature/validation/stage5k_workload_profile.py --self-test
python3 literature/validation/stage5k_workload_profile.py \
  --batch path/to/downloaded/paired/batch.json \
  --output new-descriptive-profile.json
```

The script refuses to overwrite an existing output and always emits `stage6_research_ready=false`, `field_representativeness=NOT_ESTABLISHED` for the frozen Stage 5J synthetic source, regardless of how favorable its descriptive numbers look.
