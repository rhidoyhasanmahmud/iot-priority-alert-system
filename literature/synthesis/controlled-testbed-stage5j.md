# Stage 5J — Controlled synthetic MQTT→SQLite testbed: paired multi-run engineering pilot

**Date:** 16 November 2026  
**Direction chosen by researcher:** **Controlled Testbed**.  
**Status:** **18/18 REAL-BROKER CONTROLLED-LAB RUNS INDEPENDENTLY AUDITED; SOURCE/WORKLOAD VALIDITY, NUMERIC TARGETS AND NOVELTY STILL OPEN.**  
**Scope boundary:** This is a controlled **real MQTT broker + runnable SQLite application surrogate** driven by **fictional synthetic inputs**, NOT a real-device deployment, medically/safety-critical alert system, representative application service-time distribution, new scheduling algorithm, or published performance finding.  
**Evidence ancestry:** [Stage 5H individually verified joint pipeline](joint-mqtt-sqlite-stage5h.md) · [Stage 5I fail-closed evidence register](workload-evidence-calibration-stage5i.md) · [RQ v1.0](research-questions.md) · [Stage 4B novelty REVISE/NARROW](novelty-decision-stage4b.md).

## 5J.1 — What the controlled testbed actually contains

`stage5j_controlled_pilot.py` launches **a fresh child Python process for every run**, invoking unchanged [`stage5h_joint_gateway.py`](../../experiments/stage5h_joint_gateway.py). Each child begins with an empty dedup cache and per-run on-disk SQLite database. When `--transport mqtt` is used in CI, Stage 5H publishes the synthetic tamper/health fixture through Eclipse Paho QoS1 to a **real loopback Mosquitto broker**, waits for receiver callback capture, then one class-neutral, nonpreemptive FIFO worker performs fictional device-context lookup, deterministic rule, SQLite row insertion and `Connection.commit()`; post-run SQLite is backed up for a second independent reader.

The gateway lifecycle remains the **same 2-class offered-population** research boundary, with `K` waiting slots **plus one active/reserved slot**. No priority policy has been substituted; there is no FIFO-vs-priority comparative performance claim. The actual SQLite API work is executed, but the database schema/rules and source mix are synthetic. The code and backend are therefore **working laboratory components**, not a validated production handler.

**Checklist — 5J.1**
- [x] Respect the researcher's controlled-testbed selection without pretending data come from deployed devices.
- [x] Keep Stage 5H's validated MQTT/callback/offer/queue/worker/commit semantics unchanged.
- [x] Separate process/DB/dedup state for every run to avoid cross-run handler state contamination.
- [ ] Replace or approve the fictional SQLite rule/context workload as an application-representative stand-in.
- [ ] Validate trusted class semantics and whether a real application would commit at this boundary.

## 5J.2 — Predeclared *engineering* run matrix (NOT a preregistered paper experiment)

The [controlled runner](../../experiments/stage5j_controlled_pilot.py) uses three *distinct seeded input fixtures*, three *planned source pacing shapes*, and two *illustrative* waiting capacities:

| Factor | Values in the broker laboratory CI | Reason / limitation |
| --- | --- | --- |
| Fixture seed | `101`, `202`, `303` | Same seeded event fields across shapes and capacities within seed; different seeded values do **not** create three independent real-world sites/days |
| Shape | `base`, `burst`, `overload` | `base` and `burst` have the **same planned total source horizon**, but different gap concentration; `overload` has all zero gaps and **changes offered source intensity** |
| Waiting capacity | `K=0`, `K=3` | Illustrative **debug** levels; neither is derived from actual memory/resource limits |
| Source events | `60` per run | Exactly 1/4 tamper URGENT and 3/4 health ROUTINE by deterministic generator; NOT observed mix |
| Handler/worker | Single-worker FIFO + SQLite WAL/FULL | No new scheduling algorithm; effect is one committed fictional alert row |
| Debug timing | `D_u=50 ms`, `tau=50 ms` | **Non-approved diagnostics only**; do not infer `epsilon`, `gamma` or safe SLA from results |

The matrix is **3 seeds × 3 shapes × 2 capacities = 18 sequential child-process runs**, 60 planned unique alerts per run, **1,080 planned source→offer logical observations** (not 1,080 independent experimental units). Their execution order is shuffled with `random.Random(20261116)` and recorded in the batch manifest. Pairwise comparisons should be based on correctly matched **seed and capacity**, and no inferential test or acceptance target is run in this stage. Source horizon is `59 × 8 ms = 472 ms` for `base` and `burst`, and **0 ms planned gap horizon** for `overload`; actual callback/offered elapsed times are separately observed and may drift.

This design avoids **calling an intensified overload condition a pure burst-shape treatment**. It does not yet control filesystem cache, DB saturation, sensor physics, host throttling or broker external load. A future paper analysis must explicitly group dependent events **within runs** and consider independent capture periods/hosts rather than treating individual alerts as independent replications.

**Checklist — 5J.2**
- [x] Freeze three documented synthetic source shapes and keep base-vs-burst **planned** horizon matched.
- [x] Pair the same fixture payload and source count across shapes and both illustrative waiting capacities.
- [x] Randomize and persist child-run order, separated from monotonic time comparisons between processes.
- [x] Preserve `overload` as a different-intensity condition; do not attribute overload differences solely to burstiness.
- [ ] Obtain actual traffic/handler workload mix and additional independent capture periods before selecting experimental factors for a conference result.
- [ ] Get owner-backed capacity and deadline ranges; no paper-level primary hypotheses are preregistered yet.

## 5J.3 — Independent audit and resource provenance

Each run writes a **complete Stage 5H JSONL callback/offer/SQL timing ledger**, a separate **post-run SQLite database backup** and a per-process output log. The parent records SHA-256 of all three artifacts, OS/Python/SQLite/Paho/version metadata, elapsed child-process wall time, differences in child `user`/`system` CPU time, and samples Linux `/proc/<pid>/status` `VmRSS` about every **10 ms**. Sampled resident memory is *not* a guaranteed true peak, stable benchmark, CPU quota or proof of resource capacity. Child process wall time also includes interpreter startup, publishing, queue drain and teardown, so it is **not** handler service time.

[`stage5j_batch_audit.py`](../../experiments/stage5j_batch_audit.py) is a separate verification entry point. It does **not** import the Stage 5J runner for production auditing. It independently:

1. Recomputes randomized run order and complete factorial coverage; rejects renamed, missing or extra cases.
2. Verifies exact source SHA-256 **across source shapes and capacities** for each seed, frozen synthetic input count and planned-horizon base/burst equality; overload is zero-gap.
3. Reopens every SQLite backup and delegates to the independent Stage 5H verifier for all offered events, class/rule JSON, one-worker timing, complete callback reconciliation and exact committed row accounting.
4. Recomputes raw ledger, SQLite and per-run log hashes; checks handler p95/queue-wait p95 are direct **descriptive** values of each saved run, not pooled or compared as hypothesis tests.
5. Checks that recorded resource samples are typed and nonnegative, and the manifest **still admits** synthetic provenance and unapproved debug timing.

Python 3.12 smoke passed **two seeds × two K values × three shapes = 12 in-process lab runs**, each independently audited against its source and saved SQLite; the independent gate also passed **9/9 deliberate corruptions** (source horizon, changed ledger/log hashes, fake count/seed/CPU, missing run, fictitious operator approval, fictitious new scheduling policy). An additional 12-run in-process runner self-test passed. These are distinct from the subsequent real-broker run, which has now passed in CI.

**Checklist — 5J.3**
- [x] Record raw JSONL, SQLite backup, child log, SHA-256, runtime fingerprint, process CPU and **sampled** RSS diagnostics.
- [x] Re-audit every run's independent SQLite and lifecycle evidence, including K/source-shape equivalence checks.
- [x] Execute positive **12-run in-process** smoke and independent **9 negative** corruption tests.
- [x] Keep resource-sampling limitations and source clock boundaries explicit.
- [x] Run **18/18 real Mosquitto broker** CI pilot, download its artifact and re-audit the complete batch independently after CI; see 5J.4.
- [ ] Validate realistic handler resource envelope and backend timing with controlled warm/cold/loaded repeats on fixed hardware.

## 5J.4 — Broker-backed CI evidence gate

The [GitHub Actions Stage 5J workflow](../../.github/workflows/stage5j-controlled-testbed.yml) provisions Ubuntu/Python 3.12, local Mosquitto and Eclipse Paho 2.x, performs prior Stage 5H independent-audit regression plus Stage 5J 12-run/self-test/negative cases, then executes all **18 broker-backed synthetic lab trials** sequentially and reopens every persisted SQLite backup. It verifies exactly **18/18 valid records**, a total of **1,080 source/offered logical events**, pairing integrity, and explicit `field_calibration=NOT_AVAILABLE` and `novel_policy_evaluation=NOT_PERFORMED`. It does **not** test significance, target `U/epsilon` or claim `R/gamma` compliance.

**Observed verified runs (16 November 2026):**

- [Stage 5J controlled-testbed CI #43882411348](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/actions/runs/43882411348) — **SUCCESS**; real Mosquitto + Paho 2.2.0, Python 3.12.16, SQLite 3.45.1, 4-logical-CPU Ubuntu AWS-hosted Linux runner. The logged audit declares `technical_audit=PASS`, `transport=mqtt`, `field_calibration=NOT_AVAILABLE`, `novel_policy_evaluation=NOT_PERFORMED`.
- **18/18 independent cases audited**, **1,080 offered synthetic logical events** = **697 committed fictional SQLite alert rows + 383 full-buffer rejections** (all mutually reconciled; no inferred missing offers). Per-run raw JSONL, SQLite database backups and child output logs had hashes checked against the batch manifest.
- The **[CI artifact #14233685797](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/actions/runs/43882411348/artifacts/14233685797)** was downloaded and `stage5j_batch_audit.py` re-run **outside the CI job** against its extracted `paired/batch.json` and raw persisted files: exit code **0**. Its 14-day GitHub Actions retention is expected to end around **30 November 2026**; this is not durable external storage.
- The **[Stage 5F MQTT regression #43882411135](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/actions/runs/43882411135)** also completed **SUCCESS**; the prior [Stage 5I fail-closed gate #43880322439](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/actions/runs/43880322439) was already **SUCCESS** on its own workflow. The latter is **not** claimed as a new 5J PR-run regression.

Descriptive *accounting*, grouped across three synthetic seeds (**not** a statistically independent benchmark):

| Source shape | Waiting K | Offered | Fictional SQLite commits | Full-buffer rejects |
| --- | ---: | ---: | ---: | ---: |
| base | 0 | 180 | 165 | 15 |
| base | 3 | 180 | 174 | 6 |
| burst | 0 | 180 | 118 | 62 |
| burst | 3 | 180 | 140 | 40 |
| overload (intensity changed) | 0 | 180 | 38 | 142 |
| overload (intensity changed) | 3 | 180 | 62 | 118 |
| **Total** | — | **1,080** | **697** | **383** |

The tabulation demonstrates ledger conservation **inside this one small controlled run**; it does **not** show a new algorithm's advantage, policy superiority, valid application loss rates, urgent-deadline compliance or transferability to a different host. In particular, overload has zero planned source gaps, unlike base/burst at 472 ms planned source horizon. No statistical hypothesis or confidence interval is asserted.

The CI artifact contains raw JSONLs and SQLite files for each of 18 runs, child logs, `batch.json`, independently computed `paired_batch_audit.json`, and Mosquitto log. A repository snapshot of [the CI batch manifest](../../experiments/fixtures/stage5j_ci43882411348_batch.json) and [the audit result](../../experiments/fixtures/stage5j_ci43882411348_audit.json) preserves small metadata after artifact expiry, **but those two JSON files alone cannot re-verify the raw databases/ledgers**. Re-running the source-controlled workflow can regenerate the experiment with **different measured timing** despite identical deterministic fixtures.

**Checklist — 5J.4**
- [x] Commit a repeatable real-broker CI integration plan with full raw-evidence artifact and 18-run independent acceptance gate.
- [x] Observe Stage 5J GitHub Actions workflow **SUCCESS**, 18/18 broker cases and independent negative batch checks.
- [x] Download and independently re-audit all persisted SQLite/JSONL outputs; retain original CI run ID and full evidence hashes in the batch manifest, plus environmental fingerprint and explicit non-field status.
- [x] Confirm Stage 5F MQTT regression on this PR and previously completed Stage 5I readiness workflow **SUCCESS**.
- [ ] Retain raw MQTT/SQLite archive in durable storage if audit access is needed after GitHub's 14-day CI artifact expiry.

## 5J.5 — The academic gate remains CLOSED

Stage 5J addresses **testbed engineering repeatability**, not empirical application validity. Even if all 18 synthetic runs pass, the paper still lacks:

- Real or externally validated arrival/class/work distributions, true handler workload and reproducible deployment resource limits.
- An operator-reviewed local-offer urgent `D_u` and offered loss budget `epsilon`, plus routine waiting `tau` / access target `gamma` and memory-backed `K`.
- A faithful, competitive prior-art baseline set and independently signed Stage 4B novelty decision (currently **REVISE/NARROW**).
- A preregistered statistical unit, sufficient independent runs, held-out workload design, meaningful confidence intervals, falsification thresholds and substantive contribution.

This controlled testbed choice is compatible with a **synthetic-input, real-MQTT/SQLite-lab feasibility paper** if supervisor/venue scope is explicitly approved. It does not, by itself, establish the original RQ's novelty, a scheduling method or an application-level deadline guarantee.

**Checklist — 5J.5**
- [x] Honor user's controlled-testbed direction while retaining all 5I provenance blockers and Stage 4B novelty warning.
- [x] Avoid treating three distinct input seeds or 1,080 messages as independent scientific replicates.
- [x] Refrain from performance-improvement and safety guarantees; keep FIFO as a **baseline only**.
- [ ] Supervisor approves a narrow controlled-lab research claim or requires actual domain data.
- [ ] Collect real/approved service-work evidence and a resource-specific K budget, then freeze the future paper protocol.
- [ ] Only after theory/novelty sign-off, implement justified candidate policies and matched-control evaluation.

### Reproduce without MQTT (engineer smoke only)

```bash
# From repository root; create NEW output path for each run.
python3 experiments/stage5j_controlled_pilot.py --self-test
python3 experiments/stage5j_batch_audit.py --self-test
python3 experiments/stage5j_controlled_pilot.py \
  --transport inproc --seeds 11 22 --events 12 \
  --queue-capacities 0 1 --output-dir stage5j-local-diagnostics
python3 experiments/stage5j_batch_audit.py \
  stage5j-local-diagnostics/batch.json
```

**Stage 5J decision:** Controlled MQTT/SQLite experimental **engineering infrastructure verified, 18/18 broker cases PASS**. Legitimate scientific interpretation remains restricted to this one synthetic-input lab protocol; valid **field calibration, operator-approved thresholds, independent scientific inference, novelty and a conference contribution remain PENDING**.
