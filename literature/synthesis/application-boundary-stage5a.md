# Stage 5A — Application boundary and evidence contract

**Date:** 16 November 2026 · **Status:** **PROVISIONAL PROTOTYPE CONTRACT COMPLETE; domain validity, traces and numeric budgets PENDING.**  
**Track:** [conference RQ v1.0](research-questions.md) · [Stage 4B novelty decision](novelty-decision-stage4b.md) · [live checklist](research-progress-checklist.md).

> **Research positioning:** A *synthetic + MQTT-replayed application-processing experiment* is currently defensible as a controlled **laboratory prototype**, **not** as evidence of an actual deployment's urgent safety or security requirements. This step writes down what is measured and what must still be justified. It neither validates numerical targets nor selects a new algorithm.

## Step 5A.1 — Select one concrete, reproducible demonstrator (PROVISIONAL)

The [archived prototype's application-scenario document](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/blob/archive/implementation-before-literature-reset-2026-11-11/docs/application-scenario.md) described a **gateway-side security-event enrichment service** for a building/small industrial site. We reuse it as an **illustrative processing workload only**, because it explains the actual processing bottleneck better than a generic “IoT priority queue” story. This is continuity with historical code, **not** an assertion that an operator chose or deployed the system.

A device sends a previously classified event through MQTT. A gateway receiver validates the message and deduplicates its logical event ID. One local application worker subsequently enriches the event with context, evaluates a rule and records the outcome. We **do not** claim intrusion detection, real incident reduction, command/control of equipment, network-QoS scheduling, or guaranteed source-to-action latency.

**Primary study mapping (two classes, consistent with RQ v1.0):**

| RQ class | Archived illustrative event | Study meaning | Current status |
| --- | --- | --- | --- |
| **Urgent** | Device tampering alert (previously “high”) | Must **complete local worker processing** by its locally defined deadline to count as urgent success | Scenario/example chosen; operator deadline **not validated** |
| **Routine** | Periodic device-health event (previously “low”) | Must **start local worker service** within the waiting budget to count as timely routine access | Scenario/example chosen; wait threshold **not validated** |
| **Excluded from primary study** | Repeated authentication failures (previously “medium”) | A third-class policy would change the RQ/model and confound the primary two-class comparison | Archived for possible later external-validity experiment; **not silently merged** into urgent |

**Why this boundary can be studied:** a finite local application queue can become backlogged if enrichment/rule-recording takes longer than the event ingress interval. That is a **hypothesis to measure**. We have not demonstrated that the worker, rather than broker delivery, receiver work, storage I/O or upstream source limitation, is the actual bottleneck.

**Checklist — 5A.1**
- [x] Select and cite a specific **archived illustrative** MQTT application scenario.
- [x] Map exactly two classes to RQ v1.0; explicitly park the original medium class.
- [x] Limit the claim to one local non-preemptive event-processing worker.
- [ ] Obtain named domain/deployment owner or professor acceptance that this prototype is an appropriate *conference application case*.
- [ ] Identify an authentic trace or justify a calibration method; **none is presently verified**.

## Step 5A.2 — Freeze a measurement *contract*, not unverified measurements

### Local lifecycle and time origin

| Stage | Timestamp/event | In/out of measured scheduling problem | Notes |
| --- | --- | --- | --- |
| Device creates/publishes logical event | `source_publish` | **Out**, observability only | Wall clocks across devices cannot directly establish local nanosecond delay without synchronization. |
| Broker forwards and subscriber callback receives | `gateway_receive` | **Out**, separately instrumented | Distinguish MQTT delivery latency and redeliveries from application worker scheduling. |
| Receiver validates + deduplicates + obtains trusted class/deadline metadata | `validated_event` | **Out**, separately timed | No policy-specific filtering; log the rejected-invalid/duplicate rate outside the offered population. |
| Event is handed to the finite **application admission boundary** | **`offer_ns = a_i`** | **Start of study's offered population** | Every valid, unique event actually offered must be logged even if the local waiting queue is full. |
| Admission decision | `admit/reject`, queue occupancy | **In** | Same class-neutral full-queue rejection rule for compared policies; **K waiting slots**, plus ≤1 currently executing job. |
| Scheduler chooses job; worker begins its handler | **`start_ns = s_i`** | **In** | Start is at the actual beginning of the sole non-preemptive handler, not MQTT receipt, callback entry or dispatch-decision call. |
| Handler fully finishes defined local enrichment/rule/record operation | **`complete_ns = c_i`** | **End of urgent deadline objective** | Declare the exact local effect/recording completion point; if asynchronous durability is outside it, **do not** claim durable end-to-end completion. |
| Queue removes an expired/cancelled job or run stops | `terminal_reason` | **In** | Expiry/cancellation policy must be identical across comparison candidates and fixed in Stage 6. Report any unsettled job rather than silently counting success/failure. |

**Time measurement rules**
1. For `offer_ns/start_ns/complete_ns`, use a **single local monotonic time base** in the application process. For source-to-gateway timing, separately specify device/broker clock synchronization or report only same-clock intervals.
2. Relative urgent deadline `D_u` maps to an absolute local deadline `d_i = offer_ns_i + D_{u,i}` (if class-specific, document every variant). This excludes network and sensor latency by design.
3. Routine access budget `tau` uses `start_ns_i - offer_ns_i <= tau`; **routine completion is a secondary outcome**, not a substitute.
4. Actual service time for a completed non-preemptive job is `complete_ns - start_ns` for the declared handler. **No unstarted job can use its future measured duration** as a scheduler input.
5. Avoid a blocked callback or hidden unbounded receiver queue acting as an upstream reservoir. Record source-published, gateway-received, locally-offered and rejected counts separately; disclose losses and rate throttling before `offer_ns`.
6. Deduplicate MQTT retransmissions consistently using the logical event ID **before** the offered boundary, retaining a separate counter of delivery attempts and suppressed duplicates. The RQ population is *unique offered logical processing jobs*, not wire packets.
7. Run duration alone must not censor urgent jobs whose deadline is still in the future or routine jobs whose `tau` has not elapsed. Follow each offered job to its relevant endpoint, or explicitly classify it as **right-censored** in an incomplete run.

### Primary and supporting outcome definitions

| Outcome | Counting/denominator | Handling of exclusions |
| --- | --- | --- |
| **Urgent failure `U`** | `1 - urgent_on_time_completed / urgent_offered` | Local rejected, expired, cancelled before successful completion and late completed urgent offers are failures. Unresolved jobs must be followed or marked separately censored; never quietly excluded. |
| **Routine timely access `R(tau)`** | `routine_started_by_offer_plus_tau / routine_offered` | Local rejection and not-started-by-`tau` are not successes; whether late-started jobs subsequently finish is a separate measure. |
| **Queue and capacity** | Occupancy before/after admission, queue-full rejections, max waiting jobs | Explicitly check waiting count ≤ K and active jobs ≤ 1. |
| **Offered work** | `sum(p_i)` over **known completed** jobs; demand model for rejected jobs only if generator truth is separately recorded | Live MQTT-rejected events have **unobserved counterfactual service duration**; do not infer it from payload bytes or omit the missingness. For synthetic generator truth, label `generated_p_i` as offline oracle truth and prevent scheduler access. |
| **Policy cost** | Dispatcher/accounting wall-time and state/memory footprint on fixed hardware | Actual worker processing time and scheduler overhead are different; avoid mixing or free-charging either. |
| **Zero denominator** | No urgent/routine offered in a cell → `N/A` rate | Predeclare aggregation rules; never report empty class as 0% failure or 100% access. |

**Minimum invariant checks (later implementation):**
- Each valid logical local offer receives **exactly one** admission result (`admitted` or `rejected`).
- Every admitted job is either completed, explicitly expired/cancelled, or still outstanding at observation end. Terminal sets must be disjoint.
- `start_ns >= offer_ns`, `complete_ns >= start_ns` where known.
- Only one job occupies the processing worker at any instant; no implicit preemption.
- Deadline comparisons and inclusive/exclusive tie handling must be identical across policies.
- Source-published vs local-offered discrepancy is reported, not silently interpreted as local policy success.

**Checklist — 5A.2**
- [x] Specify provisional offered, service-start, completion and separate MQTT transport boundaries.
- [x] Specify two-class offered-denominator, duplicate, expiry/censoring and timestamp conventions.
- [x] Define observable invariants and counterfactual-duration missingness.
- [ ] Instrument the receiver, scheduler, processor and source publisher to **verify** these boundaries in code/traces.
- [ ] Demonstrate the assumed worker bottleneck under normal, burst and overload conditions.

## Step 5A.3 — Evidence register: *what is known, what is not*

| ID | Parameter / operational claim | Current evidence | Decision today | Required evidence to validate |
| --- | --- | --- | --- | --- |
| **E01** | MQTT receiver → local gateway enrichment worker | [Archived scenario/prototype](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/blob/archive/implementation-before-literature-reset-2026-11-11/docs/application-scenario.md), **historical design** | **Provisional demonstrator accepted for planning**, not real deployment | Reinspect existing code or implement new measured handler; state task semantics and side-effect boundary. |
| **E02** | Worker actually dominates latency | No controlled profiling in current literature-only branch | **UNVERIFIED** | Separately measure broker-to-callback, receiver, queue wait, dispatch and handler duration. |
| **E03** | Urgent completion deadline(s) `D_u` | Archived illustrative high/medium/low: **100/500/2000 ms** | **UNVALIDATED**; these three values are not the current two-class service standard | Operator/process owner justification or explicitly *synthetic scenario-only* label and sensitivity. |
| **E04** | Routine waiting budget `tau` and desired fraction `gamma` | No operationally grounded values | **UNSET** | Application requirement and consequences of misses; predeclare both before tuning. A historical “2000 ms low-priority deadline” was not a validated *start* deadline. |
| **E05** | Absolute offered urgent failure budget `epsilon` | No authorized application requirement | **UNSET** | Owner-backed risk/SLI threshold. Historical “≤1 percentage point worse than strict priority” is a **relative comparator tolerance**, not `U <= epsilon`. |
| **E06** | Waiting capacity K | Historical experimental capacity **K=1000**, not a measured memory/latency bound | **UNVALIDATED candidate**, no current committed K | Memory cap, queue entry size, broker/receiver resource isolation and K sensitivity. |
| **E07** | Service-demand variability | Archived pilot sometimes used synthetic **constant 10 ms** processing | **UNVERIFIED for variable-service-demand RQ** | Instrument actual handler; record empirical distribution, per-class variation, temporal dependence and tails; use independent seeds only where generation is involved. |
| **E08** | Bursty arrival and class mix | Historical synthetic normal/burst load generator; no authenticated production trace | **SYNTHETIC ONLY** | Publish seed/config and per-class offered-time trace; if claiming realism, justify burst structure with published/authorized device data, measured lab data or explicitly limit claim to synthetic stress tests. |
| **E09** | End-to-end real-world security/safety effectiveness | None | **OUT OF SCOPE** | Do not imply an alarm actuated or a security breach prevented. |
| **E10** | Historical evaluation counts and algorithms | Archive described FIFO, priority, aging, EDF and experimental adaptive policy; previous **10 tuning / 30 evaluation seeds** plan | **ARCHIVED PLAN ONLY** | Stage 6 will preregister fair baselines and seeds; do not assume experimental results or grandfather the archived candidate as novel. |

**Non-negotiable distinction:** a configured number, an author's synthetic scenario, a measured lab observation and an operator-authorized requirement are **four different evidence levels**. None can be silently promoted to another.

### Minimum evidence packet for Stage 5B

1. **Scenario card**: application owner or explicitly lab-only research status; handler side effects; reason for urgent deadline and routine wait.
2. **Local timing sample**: timestamped event lifecycle on the same process clock, separated from MQTT forwarding.
3. **Workload provenance**: trace generator code/version, configuration, seeds, device count, ingress rates, burst durations, class proportion; preserve **offered** events per policy.
4. **Service demand**: repeated timing distribution of the actual worker function or clear **synthetic service-time model**; record calibration and any unavailable p for rejected jobs.
5. **Numerical budget sheet**: epsilon, tau, gamma, K with explicit units, source, approval status, sensitivity ranges and frozen-before-held-out date.
6. **Ethics/privacy**: synthetic or anonymized trace by default, with identifiers detached from people/devices; no real sensitive security event disclosure.

**Checklist — 5A.3**
- [x] Recover **historical** scenario values while rejecting them as validated requirements.
- [x] Explicitly separate relative 1 percentage-point tolerance from absolute `epsilon`.
- [x] Record service- and arrival-trace provenance gaps and a concrete minimum evidence packet.
- [ ] Obtain authentic timing/trace evidence or document that paper scope is **synthetic-only**.
- [ ] Validate and freeze numerical epsilon, tau, gamma, K and sensitivity ranges.

## Step 5A.4 — Stage 6 handoff: trace schema and first controlled test

### Event-level record (schema proposal; **not implemented**)

| Field | Unit/type | Required purpose |
| --- | --- | --- |
| `run_id, scenario_id, policy_id, seed` | strings / integer | Reproduce matched offered traces and identify independent runs |
| `logical_event_id, mqtt_delivery_attempts` | stable string / integer | Disclose and deduplicate broker redeliveries |
| `trusted_class` | `URGENT` or `ROUTINE` | Current two-class boundary |
| `source_published_count_ref, gateway_receive_ns` | counter/reference, local ns where feasible | Audit upstream offered-population distortion |
| `offer_ns, admit_ns, rejected_ns` | monotonic local ns / null | Count all local offers and capacity losses |
| `queue_waiting_at_offer, K` | integer | Verify finite waiting capacity |
| `start_ns, complete_ns, urgent_deadline_ns` | monotonic local ns / null | Compute U and R(tau) on correct populations |
| `terminal_status, terminal_reason` | enum / string | Partition completed, rejected, expired, cancelled, unresolved |
| `handler_duration_ns, dispatch_decision_ns` | ns / null | Separate observed service and scheduler/accounting cost |
| `generated_offline_service_truth_ns` | ns / null, synthetic only | Offline demand accounting **never revealed to policy** |
| `payload_bytes, handler_type, scenario_load_label` | size, categorical | Diagnose burden without pretending bytes equal CPU time |

**First pilot question (not a novelty claim):** can a fixed worker and locally bounded waiting queue reproduce both *routine timely-start loss* and *offered urgent deadline failure* under a synthetic urgent burst, without hidden upstream censoring? This tests measurement correctness **before** optimizing a candidate scheduler.

**Stage 6 pre-registration constraints:**
- Keep the same offered event IDs/times, classification, demand generator, worker capacity, K and class-neutral admission rule across FIFO, strict priority, EDF+FIFO, aging and a faithful work-aware comparator.
- Use no future arrivals or hidden actual unstarted durations in online policy decisions.
- If a source policy requires actual job size, either declare it oracle/reference-only or define and label an information-matched adaptation; do not claim identical implementation.
- Fix tie rules, expiry, whether active service includes simulated handler vs actual local action, and scheduler overhead billing.
- Choose and justify tuning vs held-out splits, independent run seeds, interval/statistical reporting and negative regimes **before** the final experiments.
- Compare application-level metrics only; separate broker delivery results and do not transfer findings to a safety/security system without deployment evidence.

**Checklist — 5A.4**
- [x] Provide a trace schema suitable for reproducible U, R(tau), capacity and overhead reporting.
- [x] Define a baseline-only measurement/feasibility pilot and prohibit oracle-information contamination.
- [ ] Implement schema and validate event conservation, timing clocks and duplicate accounting.
- [ ] Freeze and review the exact evaluation protocol with the professor.
- [ ] Run a *pilot* only after traces and requirements have been checked.

## Stage 5A decision and outstanding gate

**GO** to building the **measurement/evidence packet**, **NOT** to claims of deployed-system deadline assurances, optimized scheduling, proved novelty or a full conference experiment.

**Go/No-Go for Stage 5B:** We may proceed with a **synthetic-only experimental paper** if the professor accepts its limited external validity; otherwise obtain a defensible representative trace/calibration from a named application. Without a budget source, epsilon/tau/gamma/K can be scenario variables, **not** “requirements satisfied”.

**Overall Stage 5A checklist**
- [x] Historical scenario chosen **provisionally** and mapped to the RQ's two classes.
- [x] Application offered/start/completion boundary and observable lifecycle defined.
- [x] Evidence provenance, missing requirements and first-pilot schema documented.
- [ ] Operator/professor accepts scope and application-level relevance.
- [ ] Actual trace/handler timing obtained or synthetic-only limitation approved.
- [ ] Numerical budgets and queue capacity justified/frozen.
- [ ] Stage 4B full-theory/database/supervisor novelty sign-off remains **separately open**.

**Research invariant:** [RQ v1.0](research-questions.md) is intentionally unchanged. The [Stage 4B novelty verdict](novelty-decision-stage4b.md) remains **REVISE/NARROW**, not novelty-certified.
