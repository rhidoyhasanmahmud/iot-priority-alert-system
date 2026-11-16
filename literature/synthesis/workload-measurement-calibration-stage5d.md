# Stage 5D — MQTT offer-boundary reconciliation and workload-calibration gate

**Date:** 16 November 2026 · **Research track:** [RQ v1.0](research-questions.md)  
**Decision:** **LOCAL MEASUREMENT CONTRACT + FICTIONAL LEDGER AUDITOR COMPLETED; REAL MQTT INSTRUMENTATION, REPRESENTATIVE CALIBRATION AND NUMERICAL REQUIREMENTS NOT COMPLETED.**  
**Scope:** two trusted classes, one non-preemptive local application worker, `K` waiting slots plus one currently executing job. This is a measurement/evidence gate, not an algorithm, performance result, authenticated field trace or novelty claim.

**Upstream:** [Stage 5A application boundary](application-boundary-stage5a.md) · [Stage 5B archived-evidence audit](archived-evidence-audit-stage5b.md) · [Stage 5C metric oracle](two-class-metric-validation-stage5c.md) · [Stage 4B REVISE/NARROW verdict](novelty-decision-stage4b.md).  
**Auditor:** [`literature/validation/stage5d_lifecycle_audit.py`](../validation/stage5d_lifecycle_audit.py) — Python standard library only. Run `python3 literature/validation/stage5d_lifecycle_audit.py --self-test`; later use `python3 literature/validation/stage5d_lifecycle_audit.py path/to/records.jsonl` on a genuinely captured ledger.

## Step 5D.1 — Verify and repair the conceptual timestamp boundary

The [immutable archived `iot_alerts/live.py`](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/blob/7e419b7ddd1f2808203a48d91849250a85d6d4dc/iot_alerts/live.py) starts `LiveProcessor.ingest` with `arrival = self.now()` **before** `parse_payload`, deduplication and capacity admission. The [archived MQTT demo](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/blob/7e419b7ddd1f2808203a48d91849250a85d6d4dc/iot_alerts/mqtt_demo.py) calls `processor.ingest(message.payload)` in the message callback. Its worker calls `time.sleep(args.service_ms/1000)`: this is **configured synthetic delay**, not measured security-event enrichment/rule/database work. The archive's `measurement`/`deadlines` metadata explicitly reflects callback entry, which cannot be silently reused for the new post-validation offer deadline.

### Frozen accounting boundary for *future* measurements

| Lifecycle | Record and clock | In primary scheduling population? | Acceptance check |
| --- | --- | --- | --- |
| Source logical publish | `published` event ID, publisher clock metadata | No | Count separately; **never subtract publisher wall clock** from gateway `monotonic_ns`. |
| Each gateway callback | `attempt.callback_ns`, gateway `time.monotonic_ns()` | No | Preserve all MQTT delivery attempts, including retransmissions. |
| Trusted parse, class, dedup decision | `attempt.validation_end_ns` and disposition `OFFERED / DUPLICATE / INVALID` | No | Every attempt has one validated outcome; duplicate and invalid attempts do not inflate offered population. |
| Finite local application offer | `offer.offer_ns`, after validation/dedup, immediately before class-neutral capacity decision | **Yes** | Unique logical offer; same local process clock; log the attempt link even when rejected. |
| Admission | `offer.terminal = REJECTED`, or an admitted lifecycle | Yes | `waiting_at_offer ≤ K`; queue-full rejection includes a full waiting queue *and* a busy worker; policy cannot filter events before offer. |
| Handler start | `start_ns` (actual handler entry) | Yes | `start_ns ≥ offer_ns`; wait time is `start_ns - offer_ns`. |
| Handler completion | `complete_ns` (declared effect boundary) | Yes | `complete_ns ≥ start_ns`; service time is `complete_ns - start_ns`; a synthetic `sleep` must be labelled as such. |
| Incomplete observation | `UNRESOLVED` with `observation_end_ns` | Yes | Emit **metric bounds**, not a fabricated exact rate or silent exclusion. |

Use `time.monotonic_ns()` from **one gateway process** for callback, validation, offer, start, completion and run cutoff. Take the offer timestamp while holding the same admission lock that observes the waiting-capacity snapshot; use a logger whose own backlog/losses are counted and whose overhead is measured. Neither a blocked callback nor a hidden unbounded receiver staging queue is a free admission mechanism. At a same-time tie, retain the Stage 5C completion → admission → dispatch convention in the simulation; real logs need enough ordering metadata to establish an equivalent event order rather than rely on ns equality alone.

**Urgent:** each offered trusted urgent ID has a local `urgent_deadline_ns = offer_ns + justified D_u`; completion `≤` deadline is successful. Rejected/expired/cancelled and late-completed offers are failures.  
**Routine:** each offered trusted routine ID has timely access iff `start_ns ≤ offer_ns + justified tau`; rejection/never-started after the window are failures.  
Both denominators are **all unique valid local offers in that class**. An incomplete run can yield an interval rather than a point estimate. If a class has zero offers, report `N/A`.

**Checklist — 5D.1**
- [x] Pin archive source and identify its callback-entry versus desired post-validation-offer mismatch.
- [x] Separate synthetic worker sleep from actual application service time.
- [x] Declare local clock, duplicate accounting, capacity admission and inclusive time boundaries.
- [ ] Change or build a future MQTT receiver/worker to log these boundaries and prove that instrumentation does not hide or reorder arrivals.
- [ ] Reconcile captured published → callback → trusted offer counts across complete independent runs.

## Step 5D.2 — Independent event-ledger contract and self-check

Use one UTF-8 JSON object per line, one **run** per file. The future experiment must write the following rows (the source publisher may write a separate clock-domain log that is joined by logical ID, never by subtracting unsynchronized timestamps):

| `type` | Mandatory fields (in addition to common `run_id`) | Meaning |
| --- | --- | --- |
| `manifest` | `policy_id`, `scenario_id`, `trace_provenance`, `K`, `routine_tau_ns`, `observation_end_ns`, `clock_domain="single_gateway_process_monotonic_ns"`, `dedup_cache_reset=true`, `publisher_log_complete`, `receiver_capture_complete` | Declared run scope. A complete publisher log has one record per unique intended logical event; completeness is an **assertion requiring evidence**, not something the checker discovers. |
| `published` | `event_id`, `publisher_clock_note` | Distinct intended logical source events, not broker retransmissions. No local ns comparisons from this record. |
| `attempt` | unique `attempt_id`, optional `event_id` for invalid parse, `callback_ns`, `validation_end_ns`, `disposition` | Individual callback attempts. `OFFERED` means trusted validation/dedup passed; `DUPLICATE` and `INVALID` never directly become local offers. |
| `offer` | `event_id`, source `attempt_id`, `trusted_class`, `offer_ns`, `waiting_at_offer`, `running_at_offer`, `terminal`, `start_ns`, `complete_ns`; urgent only: `urgent_deadline_ns` | Exactly one row per unique valid offered logical job, including locally rejected jobs. Terminal: `COMPLETED`, `REJECTED`, `EXPIRED`, `CANCELLED` or `UNRESOLVED`. For this v1 ledger, `EXPIRED/CANCELLED` mean **before service**; in-service interrupts are outside this non-preemptive contract. |

The audit script independently rejects missing/duplicate offer links, callback→validation→offer inversions, invalid capacity snapshots, rejected-but-serviced records, completed-without-service records, service overlaps and timestamp reversals. It recomputes urgent **failure** and routine **timely start** from offered denominators. For unresolved offers whose deadline/window has not elapsed at observation cutoff, it returns a truthful **lower/upper interval**; exact is `null`. If a terminal or clock convention changes, update the schema/validator **before** using corresponding records.

### Actual verification in this stage (fictional unit fixture only)

| Check | Result |
| --- | --- |
| Hand-checked ledger: 5 intended logical publishes; 6 callbacks; 1 duplicate; 1 invalid; 4 valid local offers; 3 admitted; 1 rejected; 1 intended event never observed at callback | **PASS** (fictional IDs/time units) |
| Offered urgent failure | **1/2 = 0.5** (one timely completion; one full-queue rejection) |
| Offered routine timely start | **2/2 = 1.0** (two started within an artificial `tau=100` ns) |
| Ten deliberately malformed ledgers rejected (boundary, duplicated ID, invalid lifecycle/capacity/timing, overlap, missing offer, wrong clock and early duplicate) | **10/10 PASS** |
| Incomplete routine offer, `offer + tau > observation_end`, yields lower/upper bounds instead of exact rate | **PASS** |
| Offline validator source and execution | Python **3.12.14**, no dependencies, `py_compile` PASS; **two successful byte-identical self-test runs**, source SHA-256 `19c7379ff61e32e9e8958963b2e1266d1605ec93a00c8da880bf82b3ca39c09c` |

The above invented `ns` values are small **only for arithmetic**. No real device, MQTT replay, service distribution, deadline or p-value was measured. The script does not prove that the logger captures every callback, that trusted classification is correct, that the broker is lossless, or that the worker is the system bottleneck. Full queue-occupancy transitions and comparator correctness need additional independent runtime traces, not merely admission snapshots.

**Checklist — 5D.2**
- [x] Provide a versioned source/callback/offer/start/completion JSONL schema and executable offline contract check.
- [x] Confirm the invented ledger's four local offers, U, R(tau), rejection and pre-offer counts.
- [x] Reject ten known-invalid examples; test unresolved-rate interval handling.
- [ ] Capture complete **real MQTT/gateway** ledgers with this schema; validate them independently.
- [ ] Cross-check observed event-level U and R(tau) against Stage 5C's independent oracle under matched service/offer sequences.

## Step 5D.3 — Evidence acquisition and parameter calibration **plan** (not measured)

### Two permitted research stories — choose explicitly

1. **Measured laboratory processing / calibrated synthetic arrivals.** Define the single worker's actual operation (e.g., context lookup + deterministic rule evaluation + recording) and its precise completion/acknowledgment boundary. Profile under isolated and loaded conditions; log per-class durations and tails. Generate reproducible MQTT event streams, measure publisher/callback/offer histograms and worker utilization, and calibrate the service/arrival model from **this actual testbed**, not archived sleep settings.
2. **Explicitly synthetic-only simulation with MQTT functional demonstration.** If no real application and source trace are available, ask the professor to approve the **synthetic-only claim**; use controlled ranges, not “realistic operator limits.” MQTT smoke would validate message-to-offer accounting, **not** transfer the synthetic numbers to field security operations.

### Concrete minimum measurement/evidence packet

| Evidence gate | Collect / compute | Pass only when... |
| --- | --- | --- |
| **M01: Work semantics** | Named handler steps, side effects, sync/async completion, code revision, test machine and resource limits | The operation and timestamp at which work is complete are independently reviewable. |
| **M02: Complete local lifecycle** | Separate per-attempt and per-offer trace with queue snapshots, run cutoff, loss/error counters and clock declaration | Source/callback/validation/offered/admitted/rejected/terminal partitions reconcile; unresolved remain explicit. |
| **M03: Service time** | For **completed** admitted jobs, `complete - start` by class/handler under no-load and loaded conditions; p50/p90/p95/p99, spread, batch effects and runtime/GC/I/O notes | Repeatability and load bias quantified, measured worker performs declared work; no synthetic sleep presented as application calibration. Rejected counterfactual service is unknown. |
| **M04: Arrival and burstiness** | Intended publish ID/clock, observed callback and post-dedup-offer deltas, per-class counts, offered counts/work when known, class mix, burst window/generator/seed, trace hash | “Burst shape” experiments preserve per-seed total offered count, class sequence, total **generated** work and horizon; separately label experiments that increase rate/load. Real MQTT offered timelines may differ across policies and must be reported. |
| **M05: Operator constraints** | Urgent deadline's consequence and local origin; routine `tau` reason; absolute offered urgent `epsilon`; routine target `gamma`; K from queue-entry memory/operational bound | Values, units, provenance, sensitivity bands, approver and freeze date recorded **before tuning or held-out runs**. An application-independent synthetic scenario must label every selected number as hypothetical. |
| **M06: Reproducibility** | Code SHA, Python/runtime/broker versions, machine, handler config, seeds, trace fingerprints, logger drop counts, raw redacted logs and manifest | An independent checker can rerun the auditor, recompute all rate denominators and trace outcomes, and see whether the process was bottlenecked. |
| **M07: Supervisor decision** | Dated decision: measured-lab vs synthetic-only; approved local objective; acceptance of external-validity limits | Explicit approval is recorded; no reviewer-facing novelty clearance implied. |

**Workload construction:** compare (A) *shape-only paired* bursts, where interarrival gaps are redistributed while preserving source horizon, logical IDs, class sequence and generated service work per seed, versus (B) *intensity-change overload* bursts, where total work per unit time increases. Label these as different causal interventions. Keep exact planned source traces across policies; for actual MQTT replays, separately inspect realized **offered** timestamps and source→offer missingness, so network jitter cannot be misattributed to scheduling. Test both benign and difficult regimes; do not select only configurations where a candidate wins.

**Service-time controls:** avoid granting future actual service duration to any online scheduler. If synthetic durations are produced, keep `generated_offline_service_truth_ns` exclusively in an offline evaluator, not in the policy interface. Measured live durations exist only after jobs complete; a rejected job's counterfactual duration is **not measured**. When reporting “offered work,” distinguish generated oracle truth from observed service, and do not silently impute missing rejected work.

### Parameter decision sheet (deliberately NOT FILLED)

| Quantity | Definition / unit | Current status | Required owner-backed or synthetic justification |
| --- | --- | --- | --- |
| `D_u` | Local deadline offset for urgent `complete - offer` (ns or ms, consistently converted) | **UNSET** | Security event processing requirement or explicitly hypothetical study parameter. |
| `epsilon` | Maximum absolute offered urgent failure rate `U` (fraction) | **UNSET** | Risk/service target or hypothetical feasibility region. *Not* archived 1pp tolerance relative to strict priority. |
| `tau` | Routine allowed `start - offer` (ns or ms) | **UNSET** | Desired routine access; cannot replace with historic low-class **completion** deadline. |
| `gamma` | Minimum routine timely-start fraction `R(tau)` | **UNSET** | Stakeholder/experimental objective, frozen before observing candidate results. |
| `K` | Number of **waiting slots**, excluding one running worker | **UNSET** | Resource budget and queue-entry memory measurement; test sensitivity. Historic K=1000 not validated. |
| `lambda` / class mix | Post-dedup local offered rate and U/R fraction | **UNSET** | Source trace/testbed evidence or declared synthetic scenario; load levels must include overload. |
| `p_i` distribution | Real completed-handler service or offline-generated synthetic work | **UNSET** | Per-class variability/tails and workload dependence, with evidence type recorded. |

**Do not import:** archived three-class deadlines 100/500/2000 ms; 10 ms sleep; unbounded historical pilot; old 0.01 **relative** failure budget; or Stage 5C's synthetic 5-tick fixture. They do not validate the new two-class system.

**Checklist — 5D.3**
- [x] Specify two evidence paths and their honest claim limits.
- [x] Predefine source/service/burst/parameter evidence expectations and freeze rule.
- [x] Separate burst-shape interventions from load-increase confounds, and true synthetic demand from unobserved rejected work.
- [ ] Obtain/measure source+worker traces or receive explicit supervisor approval for synthetic-only scope.
- [ ] Fill `D_u`, absolute `epsilon`, `tau`, `gamma`, `K`, rate/class mix and service-time model with provenance, sensitivity and freeze date.

## Step 5D.4 — Research gate and exact next work

| Deliverable | Status | Blocker / follow-up |
| --- | --- | --- |
| Archived timestamp mismatch source-confirmed | **DONE** | Future implementation must change boundary, not relabel old traces. |
| Proposed gateway JSONL ledger + independent offline validator | **DONE** | Validation is only against fictional fixture and malformed examples. |
| Service/arrival calibration collection specification | **DONE (PLAN)** | No calibrated measurements supplied. |
| Complete MQTT receiver→offer lifecycle measurements | **NOT STARTED** | Instrument a new/tightly scoped test harness on the implementation branch only after reviewing this contract. |
| Actual processing/clock/logging overhead evidence | **NOT STARTED** | `sleep` does not satisfy this gate. |
| Approved `D_u/epsilon/tau/gamma/K` and measured-or-synthetic scope | **NOT STARTED** | Supervisor/application owner decision required. |
| Method novelty/closest-source sign-off | **OPEN SEPARATELY** | Stage 4B remains **REVISE/NARROW**. |
| Stage 6 full experiment preregistration | **BLOCKED ON EVIDENCE** | No novel algorithm, benchmark win or conference readiness claimed. |

**Recommended next checkpoint: Stage 5E — actual instrumentation pilot.** Capture one **two-class, finite-K** gateway run (without optimized candidate policy), audit its source/callback/offer/admission/rejection/terminal IDs and timings, profile a declared real or explicitly synthetic handler, and record every unreconciled ID or incomplete observation. Repeat with burst and overload. This is a measurement feasibility test, **not** held-out conference results. If no testbed can be run, replace the pilot with a **professor-approved synthetic-only scope decision** and label the external-validity limitation.

**Overall Stage 5D checklist**
- [x] Evidence-backed boundary reconciliation contract drafted from archived source.
- [x] Runnable ledger validator and self-tests available independently of the archived application.
- [x] Trace/calibration/parameter worksheet and falsifiable exit gates documented.
- [ ] MQTT/a real worker actually instrumented and its logs audited.
- [ ] Service/arrival source + numerical targets validated and frozen.
- [ ] Supervisor accepts scope; Stage 4 novelty decision separately signed off.

**Research decision:** **GO to collecting/verifying the missing measurements; NO-GO to treating this planning/fixture packet as empirical findings or starting the full conference experiment.**
