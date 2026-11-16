# Stage 5B — Archived workload evidence audit and acquisition gate

**Date:** 16 November 2026 · **Decision:** **ARCHIVED EVIDENCE INVENTORY + LIMITED CONSISTENCY CHECK COMPLETE; Stage 5B research evidence validation NOT COMPLETE.**  
**Research question:** [RQ v1.0](research-questions.md) · **Application contract:** [Stage 5A](application-boundary-stage5a.md) · **Novelty risk:** [Stage 4B](novelty-decision-stage4b.md) · **Progress:** [checklist](research-progress-checklist.md).

**Audited immutable source:** [archived implementation commit 7e419b7ddd1f2808203a48d91849250a85d6d4dc](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/tree/7e419b7ddd1f2808203a48d91849250a85d6d4dc). The **current main remains literature-first**. This is a **read-only audit of archived source and committed summaries**, not a newly run experiment, algorithm improvement, field trace, or validation of the claimed conference effect.

> **Reviewer verdict:** There **are** trace-generator code, finite-buffer simulation, a completed *historical* unbounded baseline pilot and recorded MQTT engineering smoke tests. There is **not** adequate two-class, finite-K, variable-service, offered-population evidence to answer the current RQ or substantiate operational epsilon/tau/gamma/K. We must not equate a saved experiment plan with executed results.

## Step 5B.1 — Authentic archived artifact inventory

| Evidence ID | Actual immutable artifact / provenance | What it establishes | Does **not** establish |
| --- | --- | --- | --- |
| **A01** | [pilot README](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/blob/7e419b7ddd1f2808203a48d91849250a85d6d4dc/evidence/pilot/README.md), [config](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/blob/7e419b7ddd1f2808203a48d91849250a85d6d4dc/evidence/pilot/config.json), [run metrics](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/blob/7e419b7ddd1f2808203a48d91849250a85d6d4dc/evidence/pilot/run_metrics.csv), [aggregate](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/blob/7e419b7ddd1f2808203a48d91849250a85d6d4dc/evidence/pilot/aggregate.csv) | **90 recorded policy runs**: 3 arrival rates (50/90/120 events/s) × 10 seeds × 3 policies (FIFO, strict priority, fixed aging); 1000 events/run, 90,000 generated/completed policy-event records; independent same-seed trace matching within rate. | **Unbounded** queue, three priority classes (10/20/70 expected split), **constant 10 ms** processing, no rejections; not finite-K RQ, not offered routine R(tau). |
| **A02** | [paired intervals](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/blob/7e419b7ddd1f2808203a48d91849250a85d6d4dc/evidence/pilot/paired_intervals.csv) and [README limitations](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/blob/7e419b7ddd1f2808203a48d91849250a85d6d4dc/evidence/pilot/README.md) | Exploratory paired comparison for aging vs strict priority at rate 90, with 10 seed-pairs and reported bootstrap intervals. | Not a new-method improvement or a high-confidence claim across regimes. |
| **A03** | [live smoke README](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/blob/7e419b7ddd1f2808203a48d91849250a85d6d4dc/evidence/live-validation-smoke/README.md), [summary](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/blob/7e419b7ddd1f2808203a48d91849250a85d6d4dc/evidence/live-validation-smoke/summary.json) | **Eight** recorded planned-trace policy runs at **one** scenario and **one** seed (6101), each with 40 logical generated offers, 24 completed and 16 dropped; **one local AMQTT 0.11.3/Paho 2.1.0 engineering smoke**. | 320 independent real-device alerts, production Mosquitto results, repeated statistical evidence, real enrichment costs, R(tau) benefit or a policy ranking. |
| **A04** | [smoke summary checks](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/blob/7e419b7ddd1f2808203a48d91849250a85d6d4dc/evidence/live-validation-smoke/summary.json) | Two queue-overload functional checks (each: 32 message attempts, 2 admitted/completed, 30 queue-full rejected); a broker-restart/resubscribe/dedup check (5 attempts, 3 admitted/completed, 2 duplicates). | Exactly-once across a crash, forced broker retransmission, non-lossy network, reproducible wall-clock performance or scholarly novelty. |
| **A05** | [workload generator](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/blob/7e419b7ddd1f2808203a48d91849250a85d6d4dc/iot_alerts/workloads.py), [generator/replay guide](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/blob/7e419b7ddd1f2808203a48d91849250a85d6d4dc/docs/workload-generator.md) | Deterministic seed-controlled Poisson/interarrival-index-burst generator; explicit three-class labels, per-event service time; constant/uniform/exponential service choices; five-column saved CSV and fingerprint. | Real traffic traces, operator-backed burst profiles, two-class preregistration, service-time prediction accuracy or identical average offered rate between different traffic shapes. |
| **A06** | [simulation engine](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/blob/7e419b7ddd1f2808203a48d91849250a85d6d4dc/iot_alerts/simulator.py), [metrics](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/blob/7e419b7ddd1f2808203a48d91849250a85d6d4dc/iot_alerts/metrics.py) | One non-preemptive worker, configurable number of **waiting** slots, full-queue rejection and drain; computed drop-inclusive deadline failure for **deadline-bearing** offered jobs. | R(tau) implementation for the selected **routine offered** denominator; class-specific U as current RQ; exact online information isolation in a future work-aware scheduler. |
| **A07** | [live processor](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/blob/7e419b7ddd1f2808203a48d91849250a85d6d4dc/iot_alerts/live.py), [MQTT demo](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/blob/7e419b7ddd1f2808203a48d91849250a85d6d4dc/iot_alerts/mqtt_demo.py), [live guide](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/blob/7e419b7ddd1f2808203a48d91849250a85d6d4dc/docs/live-validation.md) | A single worker, bounded local admission, dedup/retry counters and local timestamped receipt/service lifecycle; live worker **sleeps for a configured duration**. | Actual security-event context enrichment/rule evaluation/durable storage timing; a matched post-validation-offer boundary; calibrated variable application service times. |
| **A08** | [archived research registration](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/blob/7e419b7ddd1f2808203a48d91849250a85d6d4dc/configs/research-v1.json), [live profile registration](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/blob/7e419b7ddd1f2808203a48d91849250a85d6d4dc/configs/live-validation-v1.json), [evidence audit guide](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/blob/7e419b7ddd1f2808203a48d91849250a85d6d4dc/docs/research/reproducibility.md) | Historical **plans**: 48 primary scenario combinations; 10 tuning and 30 held-out seed sets; separate 160-run live validation profile. | **Execution** of full primary research, full 160 live runs, validated acceptance thresholds or a new algorithm's contribution. |

**Status:** A01–A08 source identities and stated reading limits inspected. Archived summaries and implementation are **not promoted** to main-branch experimental results. Raw compressed event-level pilot example and compressed live trace archive were **not independently decompressed/verified in this review**, and the archived Python study was **not re-executed**.

**Checklist — 5B.1**
- [x] Locate exact, immutable archived implementation commit and the available pilot/live evidence.
- [x] Distinguish genuinely recorded pilot/smoke outputs from unexecuted primary-study and 160-run plans.
- [x] Distinguish local MQTT engineering evidence from real sensor/security-system evidence.
- [ ] Re-run the archived evidence verifier from a pinned clean checkout if the archive is to be cited as a reproducibility check.
- [ ] Obtain new data designed for the **current** two-class RQ and its outcome definitions.

## Step 5B.2 — Limited independent checks on *committed summaries*

The following are **new arithmetic/shape checks** over the GitHub text files listed above. They **do not** verify per-event ground truth, execution code hashes, broker logs, compressed raw traces or external replicability.

| Check | Recomputed from committed files | Result |
| --- | --- | --- |
| Pilot group count | 3 rates × 10 seeds × 3 policies | **90** distinct rate/seed/policy groups. |
| Pilot per-class rows | 90 groups × 3 priority classes | **270** rows in `run_metrics.csv` (plus header). |
| Pilot offered/completed records according to run-class counts | For each of 90 groups, sum of its three class `count` values | **Exactly 1000 in all 90 groups**, total **90,000 policy-event records**. This is repeated simulation input across policies, **not 90,000 distinct device observations**. |
| Pilot aggregate p95 | Recalculate mean of ten per-run `p95_latency_ms` values for each rate/policy/class | **27/27 aggregate values match** committed `aggregate.csv` within numeric tolerance (absolute 1e-8 ms). |
| Live-workload counts | Sum eight policy entries from `summary.json` | 8 × 40 planned generated offers = **320 policy-event records**; **192 completed, 128 dropped**; **40 unique planned jobs reused in each policy run** under one seed. |
| Overload functional count | Check each `received_messages` vs `admitted + rejected_queue_full + duplicates + invalid` | Both overload checks: **32 = 2 + 30 + 0 + 0**. |
| Restart/dedup functional count | Same basic attempt partition | **5 = 3 + 0 + 2 + 0**; 3 completed; code does not claim durable duplicate state after receiver crash. |

**Method:** read the immutable UTF-8 `run_metrics.csv`, `aggregate.csv` and `summary.json`; group by (rate, seed, policy) and (rate, policy, priority) as above; compare floats under tolerance. These tests are repeatable arithmetic over the published text, not a rerun of its original generator. No experiment was newly executed for this PR.

**Checklist — 5B.2**
- [x] Verify all 90 pilot groups have exactly 1000 reported events and the aggregate table matches the saved per-run p95 means.
- [x] Reconcile live smoke top-level 8-policy, drop/admission and duplicate-attempt counts.
- [x] Label **same planned trace across policies** separately from statistically independent runs.
- [ ] Verify the compressed live raw bundle, event-level rows and source hashes under authorized checked-out source.
- [ ] Confirm true measured service durations and queue lifecycle against raw local event logs before performance claims.

## Step 5B.3 — Critical compatibility gaps with the **current** RQ

| Gap | Archived implementation/evidence | Stage 5A + current RQ requirement | Required repair or decision before Stage 6 |
| --- | --- | --- | --- |
| **G01—Population** | 3 classes high(0)/medium(1)/low(2). | 2 classes: device tampering **urgent**, device health **routine**; medium parked. | Generate/replay only classes 0 and 2 (e.g., zero medium sampling weight), **then declare the recoding**. Do not compare legacy 3-class pilot as if two-class. |
| **G02—Capacity** | Completed pilot's waiting queue **unbounded**, no drops. Live smoke K=5 does have drops. | One worker, finite **K waiting slots**, class-neutral reject-on-full. | Use a controlled finite K in new simulation and MQTT run; capacity definition same; report occupancy and *offered* rejections. |
| **G03—Routine endpoint** | Historical pilot emphasizes completed-only p95 **latency/wait**; `metrics.py` does not export primary `R(tau)`. | **Routine offered jobs starting within tau**, including dropped jobs as failures. | Derive `R(tau)` from completions' start minus offer plus all rejected routine offers; implement audit on disjoint outcomes. |
| **G04—Urgent endpoint** | Generic deadline failure applies to **all deadline-bearing** classes, often 100/500/2000 ms historical. | Urgent offered **completed by its own deadline**, with local drops/late/expiry counted as failures. | Restrict urgent population explicitly; freeze deadline source and distinguish expiry/unfinished/censoring. |
| **G05—Service model** | Historical pilot **constant 10 ms**; variable-time simulator generator exists, but **live worker uses `time.sleep(service_ms)`**, not actual enrichment/rule/storage. | Unknown **unstarted** service durations; service variability and actual handler/decision cost measured. | Add service-duration workload sweeps; document generator oracle truth as **offline-only**; measure real handler if claims are about application workload. |
| **G06—Offer boundary** | `LiveProcessor.ingest()` records `arrival = self.now()` at **callback entry, before validation and dedup**. Live validation reconciles first receiver receipt for logical ID. | Stage 5A's `offer_ns` starts **after** validation/dedup at local queue offer. | **Boundary mismatch must be fixed or formally redefined consistently.** Record distinct `callback_receive_ns` and `offer_ns`; do not compare raw archived receiver-relative latency to new post-validation U/R(tau) without reprocessing. |
| **G07—Burst comparability** | `burst` compresses interarrival gaps over an **event-index window** and reduces the total arrival span, thereby **increasing overall offered rate**. | Claims should distinguish burst concentration from additional offered traffic/work and class mix. | Predeclare both burst shape and total offered-rate/work controls; do not attribute improvement to “burstiness alone” when load changes. |
| **G08—MQTT replay** | All policies share planned events; realized callback arrivals can vary with transport, OS and publisher drift; local smoke used **AMQTT**, while validation guide supports Mosquitto. | Matched **offered local** inputs for simulation; in MQTT, accurately observed received/offer population and drift. | Keep separate planned/send/ACK/receive/offer timelines; select/pin broker and host; use enough independent runs to estimate variability; don't say MQTT arrival traces identical. |
| **G09—Information fairness** | `Alert.service_time_s` contains generator-created **true future demand** for every synthetic job. Existing FIFO/priority/etc selectors do not by themselves establish an information-contract for a future work-based method. | No online algorithm may read true unstarted service duration. | Enforce/verify policy API that exposes only available metadata + past observed work; preserve oracle truth **only** in offline metrics. |
| **G10—Acceptance budget** | `configs/research-v1.json` uses `urgent_failure_budget: 0.01` for **relative difference versus strict priority** under an old 3-class objective. | Current RQ requires an **absolute offered urgent failure epsilon**, plus routine tau/gamma and K; all domain/synthetic scenario assumptions labeled. | **Do not import 0.01 as absolute epsilon** or call old 100/500/2000 ms deadlines operator-backed. Supervisor-approved/bounded scenario spec needed. |
| **G11—Execution evidence** | Archived 48-condition primary research plan, sensitivity analyses and 160 live-run profile; their own guide says full study **not executed**. | Current RQ needs matched independent repeats + held-out results under the **new** metric/protocol. | Never relabel a plan or smoke check as primary study. Register **new versioned plan** after 5B evidence gates and Stage 6 protocol review. |

**Critical reviewer observation:** the archive has an *implemented* bounded queue and variable synthetic service-time generator, which is useful engineering groundwork; **the archived pilot results do not exercise both in the main comparison.** That distinction should determine next investment, not whether a Python module exists.

**Checklist — 5B.3**
- [x] Produce source-specific mapping between archive evidence and current RQ (including local timestamp origin and old relative 1pp budget).
- [x] Flag synthetic sleep as **not** measured application processing and three-class/unbounded pilot as **not** current primary.
- [x] Identify exact required R(tau), urgent U and policy-information repairs.
- [ ] Verify a new two-class trace/metric implementation under finite K and variable service, with full per-offer accounting.
- [ ] Show that broker/callback delivery or upstream serialization does not invalidate the chosen local worker bottleneck.

## Step 5B.4 — Evidence acquisition and method-readiness order

### Path choice: synthetic+MQTT **lab-only**, subject to supervisor acceptance

The existing archive supports planning a *controlled synthetic study with an MQTT engineering validation layer*. That is a **study design**, not a new source of real sensor rates, authentic attack severity or security system requirements. Because no authentic device trace or measured enrichment service time is present, claims must be restricted to the declared synthetic generator **until empirical calibration is obtained**.

**Follow this order (do not tune a new scheduler yet):**

1. **Define the local offer population exactly** and add/log both callback receipt and post-validation queue offer. Reconcile every planned logical event through reception, dedup, local offer, admission and final outcome.
2. **Create two-class source-trace contract** with event ID, offer relative time, class, urgent local deadline, offline synthetic true service duration, generator SHA/config, event-index burst parameters and trace fingerprint. Match input traces across policies in simulation; log actual offered local trace separately in MQTT.
3. **Pilot an exact finite-K bookkeeping check**, not a performance claim: deterministic trace with simultaneous offers, local full-queue rejects and deadline misses; prove by test that `offered = admitted + rejected` and `U,R(tau)` use **offered** denominators. Verify K waiting slots and ≤1 running; distinguish queue rejection from MQTT non-delivery.
4. **Establish variability** with declared constant, uniform and exponential **synthetic** job durations, matching expected mean and tracking **realized offered work** per trace. Use separate generator seeds for repeated traces; disclose that independent synthetic noise is not a calibrated actual service model.
5. **Account for actual handler cost**: either instrument representative local enrichment/rule/record work or state service is synthetic sleep and downgrade conclusions to simulated queue/service behavior. Benchmark dispatcher/accounting time independently.
6. **Write budget provenance card** for epsilon, tau, gamma, K and urgent deadline: value/range, unit, operational vs illustrative status, source, rationale and signed approval. No retrospective tuning to a desirable result.
7. **Pre-register Stage 6 baseline protocol** including FIFO, strict priority, EDF+FIFO, aging and a matched-information work-aware comparator; defer any “new” scheduler or held-out research result until 4B novelty and 5B operational/synthetic scope are explicitly agreed.

### Recommended acceptance tests before granting Stage 5B evidence clearance

| Test | Acceptance condition | Status |
| --- | --- | --- |
| **T01** Reproduced source snapshot | Archived verifier/report matches committed input and hashes (or discrepancies recorded) | **PENDING** |
| **T02** Current RQ mapping | Only urgent/routine events in primary trace; all class and deadline metadata checked | **PENDING** |
| **T03** Offered conservation | All local offered events accounted with disjoint admitted/rejected, no silent source filtering | **PENDING** |
| **T04** Finite waiting capacity | No more than K queued and one running, overload rejection deterministic | **PENDING** |
| **T05** Outcome oracle | Separately recomputed U and R(tau) match per-event trace and include drops | **PENDING** |
| **T06** Service information | No candidate sees a future job's true `service_time_s`; measured scheduler overhead accounted | **PENDING** |
| **T07** MQTT boundary/drift | Distinct receive/offer/start/complete timestamps, logical ID dedup and publisher drift disclosure | **PENDING** |
| **T08** Requirement provenance | Numerical budgets/capacity declared as approved or explicitly scenario-only *before* experiment selection | **PENDING** |
| **T09** Research sign-off | Supervisor accepts lab-only claims and Stage 4B remaining gaps/revisions are explicitly owned | **PENDING** |

**Checkpoint — 5B.4**
- [x] Draft source-backed minimum new evidence packet, order and pass/fail criteria.
- [x] Keep archived data immutable and current main implementation-free.
- [x] Require method/metric equivalence before new experiments and avoid cherry-picking archive results.
- [ ] Execute new acceptance tests and collect actual per-offer trace/handler samples.
- [ ] Obtain professor/supervisor authorization of **synthetic-only** external-validity limits or a real-source alternative.

## Decision memo for Hasan / supervisor

- **Research feasibility:** **CONDITIONAL GO** for a *measurement-first, baseline-only lab pilot* after its accounting and source boundary are corrected.
- **Current Stage 5B evidence validity:** **NO CLEARANCE YET**. We located meaningful engineering artifacts but have **not collected** new application-calibrated evidence or approved budgets.
- **Paper strength:** An unbounded, three-class, 10-ms-constant-service pilot cannot support the new finite-K, two-class R(tau) versus urgent-U contribution. A one-seed MQTT smoke is a function check, not strong statistical evidence.
- **Novelty:** [Stage 4B REVISE/NARROW](novelty-decision-stage4b.md) and full-text/database/supervisor sign-off remain independently open; new data alone does **not** establish novelty.
- **Next repository step:** register a **new Stage 6 measurement/baseline protocol** only after the critical G01–G10 mismatches and T01–T09 gates are addressed, or explicitly mark the unresolved assumptions as a strictly synthetic case study.

**Overall Stage 5B checkpoint**
- [x] Archived pilot, live smoke and code provenance inspected at the stated levels.
- [x] Committed CSV/JSON arithmetic checks completed; no new experiments claimed.
- [x] Compatibility threats and concrete pass/fail collection protocol written.
- [ ] Raw archive verifier and current two-class offered-population traces independently executed.
- [ ] Service-time realism, epsilon/tau/gamma/K provenance and supervisor acceptance.
- [ ] Formal Stage 4B novel-contribution sign-off.
