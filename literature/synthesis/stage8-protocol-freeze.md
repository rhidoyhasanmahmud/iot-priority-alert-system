# Stage 8 — Frozen controlled-testbed experimental protocol

**Research line:** STI 2026, *Routine-Service Protection Under Bursty IoT Alerts: Deadline Trade-offs and Practical Limits*. This is **separate** from the earlier QPAIN 2027 `adaptive_guarded` protocol and neither modifies nor supersedes that plan.

**Locked configuration:** [`stage8_frozen_protocol.json`](../../experiments/stage8_frozen_protocol.json). Exact byte-level SHA-256:

`1fe656270ce5843af8b26a6a288f712bb4afbf25a05f7d1f2ea9221e93163c52`

**Status:** Researcher-directed, version-controlled **synthetic-only protocol freeze**. The user explicitly requested a Controlled Testbed and autonomous protocol freeze on 16 November 2026. No supervisor approval, production SLA, real IoT workload, or scheduling novelty has been independently established. This is an investigator-controlled *pre-outcome commitment*, **not** a registry-issued preregistration or institutional scientific approval. Publication suitability must be decided against those limits.

## Exact scientific question and predeclared decision rule

At a *single, finite, non-preemptive MQTT-to-SQLite processing bottleneck*, compare online **FIFO**, **strict urgent-first**, and **routine wait guard** under identical pre-generated synthetic offers and hidden work. The guard is an intentionally simple **non-novel candidate**: when the oldest waiting routine has age at least `τ/2`, serve it next; otherwise serve the oldest waiting urgent job (or FIFO when none). No policy sees future jobs or unstarted service requirements.

The **primary operating point** is a concentrated burst, 60 offers (15 urgent, 45 routine), 1-second planned horizon, `K=3` *waiting* plus one active worker; all other points are predeclared sensitivities. This primary point was chosen **after exploratory Stage 7 evidence but before any held-out run**. It is not presented as selection-blind discovery.

- `D_u = 50 ms` urgent **completion** deadline; `U` = rejected urgent + admitted urgent completing after local offer plus `D_u`, divided by **all offered** urgent IDs. Equality with the deadline counts as on-time.
- `τ = 20 ms` routine **start** budget; `R` = routine service starts no later than `τ` after local offer, divided by **all offered** routine IDs. Rejected IDs are failures.
- Both timings originate from the local post-validation/dedup admission offer, *not* physical sensor publication or actuator action.
- Predeclared hypothetical absolute joint operating target: `U ≤ 0.10` and `R ≥ 0.75`, evaluated **per independent seed and per tested policy**. These are illustrative target values, not owner-approved deployment SLOs.
- **Co-primary treatment gate:** compare `routine_wait_guard` against `strict_urgent_first` under primary burst `K=3`. Both are required: 95% paired-bootstrap *lower* CI for `R_guard − R_priority` **strictly exceeds 0.05**, and 95% paired-bootstrap *upper* CI for `U_guard − U_priority` is **at most 0.01** (one percentage point). Failure or inconclusiveness of either gate **precludes** the claim. Negative/null results are retained.

The guard is **not** accepted as a novel contribution. Stage 4B's adverse prior-art verdict still stands. A peer-reviewed paper may need to focus instead on a bounded empirical failure envelope—or stop altogether—if strong existing methods explain or dominate the observations.

## Factor design, replications and controls

| Factor | Frozen specification |
| --- | --- |
| Workload source | Stage 5K.2 deterministic policy-independent ex-ante work/offer fixtures; hidden work units `1/4/7` with 4-unit mean; no service oracle in dispatcher |
| Service implementation | PBKDF2 SHA-256 (10,000 iterations/work unit) **plus actual SQLite WAL/FULL commit**, with a separately audited host-local service characterization |
| Main / sensitivity scenarios | `burst`: clustered/flat/1s; `smooth`: smooth/flat/1s; `overload`: smooth/flat/0.25s; `variable`: smooth/variable/1s |
| Queue | `K=3` for all four; secondary `K=0` negative-control scenario for burst |
| Policies | FIFO; strict urgent-first; fixed routine-wait guard at half-τ. All have identical admission, no eviction or class-based drop rules |
| Independent replications | **30 fresh held-out seeds `210001`–`210030`** (source IDs, work and urgency externally fixed before policy evaluation) |
| Number of trials | **30 seeds × 5 cells × 3 policies = 450 real MQTT/SQLite trials**, 150 matched source blocks |
| Pilot exclusion | Old `71/101/202/303/917` and new reserved tuning seeds `7001`–`7005` cannot enter the held-out analysis |
| Randomization | Shuffle source scenario/capacity blocks with fixed seed `20261116`; shuffle three policy executions **within each matched block** using source-key-derived seed |
| Trial isolation | Fresh child Python process, UUID and SQLite file for each run; live Mosquitto/QoS1 broker on loopback; independent audit of every ledger and persisted row |
| Host | One GitHub `ubuntu-24.04`, Python 3.12 job, host fingerprint and service probe preserved; no field service-time generalization |

## Analysis locked before holding out data

**Independent seed = experimental unit.** Jobs inside a run share state and are never independent samples for a confidence interval. The independent analysis reopens and validates all 450 databases, checks source/work hashes, admission and scheduling decisions, observed event timing, and exact protocol/settings before computing outcomes.

- Primary paired differences and **two-sided 95% percentile bootstrap CI** with **10,000 seed-resampled replicates** and fixed analysis PRNG seed `818019`.
- Both co-primary thresholds form an intersection gate: no positive conclusion unless **both** predeclared interval bounds pass. No post-hoc superiority or noninferiority margin changes.
- Report all scenarios (including non-bursty, overload and no-waiting controls), rejected counts, class rates, and *admitted-only* routine wait p95 (with its selection bias and drop rate disclosed). Other comparisons with FIFO are **descriptive exploratory** with unadjusted intervals, not new discoveries.
- Stop and mark entire batch invalid if a missing ledger, failed broker, timed-out run, altered source, inconsistent SQLite commit, or auditor disagreement occurs. No favorable-only exclusions, replacement seeds or combining pre/post-correction batches. A changed protocol/implementation needs a new version and fresh holdout.
- Explicitly keep all negative, null and contradictory observations; treat GitHub shared runner load, small 30-seed precision, one artificial work family, unknown field transfer and prior-art limitations as threats to validity.

This design is **a reproducible, conditional synthetic model evaluation**, not proof of operational IoT deadlines, universal feasibility, optimality or algorithm originality. No manuscript writing starts as part of Stage 8.

## Auditable execution

On a machine with Python 3.12 and importable scripts in `experiments/`:

```bash
# Preflight uses only reserved tuning seeds, not scientific outcomes.
python experiments/stage8_frozen_study.py \
  --mode pilot --pilot-seeds 7001 7002 --output-dir /tmp/stage8-pilot
python experiments/stage8_independent_analysis.py \
  --study-dir /tmp/stage8-pilot --pilot

# Holdout requires the committed revision and an actual loopback Mosquitto broker.
python experiments/stage8_frozen_study.py \
  --mode holdout --git-revision COMMITTED_SHA --output-dir /tmp/stage8-heldout
python experiments/stage8_independent_analysis.py \
  --study-dir /tmp/stage8-heldout --output /tmp/stage8-independent-results.json
```

CI uses [the dedicated Stage 8 workflow](../../.github/workflows/stage8-frozen-holdout.yml) to run preflight **before** held-out experiments, gate the independent raw/SQLite analysis and retain machine-readable artifacts. The experiment JSON and analyst-written validation output are research records, **not manuscript sections**.
