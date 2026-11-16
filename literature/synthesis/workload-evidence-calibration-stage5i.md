# Stage 5I — Field-workload evidence acquisition and fail-closed calibration readiness

**Date:** 16 November 2026  
**Decision:** **EVIDENCE INTAKE CONTRACT + NEGATIVE RESEARCH-READINESS GATE IMPLEMENTED; REAL APPLICATION CALIBRATION / OPERATOR NUMBERS NOT AVAILABLE.**  
**Context:** [Stage 5H joint MQTT→SQLite engineering evidence](joint-mqtt-sqlite-stage5h.md) · [Stage 5D offered-population semantics](workload-measurement-calibration-stage5d.md) · [RQ v1.0](research-questions.md) · [Stage 4B REVISE/NARROW](novelty-decision-stage4b.md).

## 5I.1 — Freeze what the working claim requires

**Do not confuse three levels of evidence:**

1. **Executable lifecycle integrity:** Stage 5H synthetic gateway has a valid published→callback→validated local offer→admission→handler→SQLite commit ledger; the database backup can be independently reopened. That contract is **engineering-verified**.
2. **Representative input and service demand:** Evidence must cover **actual** source bursts, the real handler's request mix/service work, negative/failure cases and host/resource constraints. Stage 5H's seeded 16 fictional devices, fixed rules, independent SQLite file, 1:3 urgent/routine fixture and short GitHub runner samples do **not** meet this standard.
3. **Application-backed success requirements:** The application owner must specify where the deadline clock begins, what counts as an effect, and acceptable urgent/routine outcomes. The authors cannot choose `D_u`, `epsilon`, `tau`, `gamma` or `K` from observed pilot results to manufacture a successful experiment.

Our primary local model is **one nonpreemptive application worker, `K` waiting slots plus one reserved/running place, two trusted classes and post-validation/post-dedup local offering**. Urgent failure `U` is evaluated on **all offered urgent jobs**: rejected, expired, cancelled and late-completed count as failure (unresolved cases need conservative bounds). Routine timely-start `R(tau)` uses **all offered routine jobs** in its denominator, with rejected/never-started jobs counted as not timely. An event sent by a device but lost before the local offer is **not** silently recast as an offered event. Such upstream loss must be separately reported, and any end-to-end device deadline requires a *different* clock/correlation contract.

**Checklist — 5I.1**
- [x] Keep the offered-population scope and nonpreemptive one-worker finite-`K` boundary from Stage 5D/5H.
- [x] Distinguish synthetic engineering integrity from operational representativeness and research approval.
- [x] Reject fabricated SLA constants or arbitrary benchmark pass criteria.
- [ ] Obtain application-owner agreement that post-validation **local offer** is the right safety/service boundary.
- [ ] Verify whether actual deadlines are per-alert/per-site rather than one fixed `D_u`; if so, revise the experiment schema first.

## 5I.2 — Minimum external evidence request to take to the owner

Collect **redacted**, rights-cleared data and a separate immutable collection manifest. Do not commit live device identifiers, site identities, exact geolocation, IPs, credentials or sensitive security payloads to this open repository. An evidence URI may refer to an access-controlled internal artifact; its existence and SHA-256 alone do not confer reuse rights or independent authenticity.

| Packet section | Required evidence | Invalid shortcut |
| --- | --- | --- |
| Application authority | Owner/supervisor acceptance of scenario, urgent/routine meaning, successful effect, privacy/data-use approval | Equating fictional Stage 5G flags with a real alarm policy |
| Event source | Population, capture sites, UTC observation window, collector/software version, source clock, sampling/drop policy, input class mix, arrivals and time-varying burst windows | Replaying Stage 5H's deterministic 8 ms/zero-gap synthetic schedule |
| Gateway capture | Separate source publisher list, MQTT broker ingress/drop/retry/backpressure metrics, receiver callbacks, invalid/duplicate attempts, post-validation offers, capacity decisions and unknown/missing IDs | Calling QoS1 publisher ACK a proof of subscriber/local-offer delivery |
| Handler and effect | Real processing method/code version, database/backend, context lookup, rule/side effect, transaction/ack boundary, independent effect record, error and retry policy | Treating the tiny SQLite lab rule as measured production work |
| Timing | Gateway `monotonic` clock domain, timestamp instrumentation overhead, callback/offer/start/commit relation, host and service-clock drift, source→gateway caveats | Subtracting different host clocks without a verified synchronization/error model |
| Resource and stability | CPU/memory/disk/broker/DB utilization, waiting-capacity/memory justification, warm/cold repeats, independent capture intervals and outages | One GitHub-hosted run as a service distribution or confidence interval |
| Operational decision | Owner-backed `D_u`, `epsilon`, `tau`, `gamma`, `K`, boundary and rationale, dated approval artifact | Selecting constants after inspecting success rates |
| Research integrity | Complete closest-paper methods, novelty/go/no-go memo, preregistered matched-policy protocol | Calling FIFO queueing or offered-loss accounting a new scheduling algorithm |

**Data owner questions to send, not assume answered:**

1. Which deployment or testbed can supply **rights-approved** gateway measurements? What does a tamper/urgent alert mean operationally, and is its requirement local processing or an end-to-end physical action?
2. What constitutes *completion* (transaction persisted, alert displayed, notification acknowledged, actuator action)? Are duplicate/late outcomes unsafe or merely delayed?
3. Can one collect **complete** source and receiver/offer logs, broker drops/backpressure and actual resource utilization across busy and quiet periods, with privacy controls?
4. Are deadline and routine objectives formal operator policies, customer-facing SLAs, or still design proposals? Who can sign them off, and are they per class or per message?
5. Is a **synthetic-only, explicitly bounded** conference paper acceptable if no production/testbed traces can be released? This choice requires venue/supervisor confirmation and a correspondingly narrow contribution claim.

**Checklist — 5I.2**
- [x] Specify the complete 16-item evidence register and avoid storing sensitive source material.
- [x] Define provenance, representative handler, sampling, failures, clocks, resource and ownership controls.
- [ ] Obtain an actual rights-approved, independently attributable field/testbed evidence packet.
- [ ] Characterize missing source events and **upstream** censoring outside offered-population metrics.
- [ ] Record reviewer names, dates, stable private URIs and genuine artifact hashes only after inspection.

## 5I.3 — Parameter decision worksheet (deliberately blank)

The checked-in [`stage5i_evidence_register.json`](../validation/fixtures/stage5i_evidence_register.json) keeps these unknowns explicitly `null`; filling them is **not** a coding task and is **not** justified by any Stage 5F/H 50 ms demo configuration.

| Symbol | Required semantics | Decision source | Current |
| --- | --- | --- | --- |
| `D_u` | Urgent per-offer deadline to successful completion, **ms**; confirm whether fixed or per message | Application-owner operational requirement, not observed p95 | **UNKNOWN** |
| `ε` | Maximum acceptable **absolute** urgent failure fraction among all urgent offers; reject/drop/late included | Owner risk tolerance plus explicit consequences | **UNKNOWN** |
| `τ` | Routine maximum acceptable offer→worker-start wait, **ms** | Owner routine accessibility objective | **UNKNOWN** |
| `γ` | Minimum share of all **offered** routine jobs started by `offer + τ` | Owner policy; not observed FIFO's achieved rate | **UNKNOWN** |
| `K` | Integer waiting-slot cap **excluding** the reserved/active job; constrain by memory and hardware budget | Measured deployment gateway resource capacity and failure envelope | **UNKNOWN** |

Research protocol should later predeclare parameter ranges/sensitivity **before** comparison results. The resulting lab outcomes are descriptive, not a source from which to retroactively tune `ε` or `γ` for a flattering claim. Absolute errors should use correct denominators and report confidence/uncertainty in a preregistered way; repeated messages from one deployment/day are not automatically independent observations.

**Checklist — 5I.3**
- [x] Publish blank, typed operational decision fields and exact urgent/routine offered denominators.
- [x] Require an external reviewed evidence reference before accepting any numerical proposal in the readiness validator.
- [ ] Obtain dated owner-backed operational criteria, with baseline-agnostic justification.
- [ ] Obtain resource constraints for `K`, and workload sensitivity/independent-day replication plan.
- [ ] Resolve single versus per-event deadlines and measurement-clock agreement before setting threshold values.

## 5I.4 — Executable negative evidence gate

[`stage5i_evidence_gate.py`](../validation/stage5i_evidence_gate.py) has no dependency on a new scheduler. Given a declared packet, a Stage 5D-compatible ledger and (for Stage 5H) a **separately inspectable SQLite backup**, it:

1. Re-runs the existing independent lifecycle verification and, for a Stage 5H run, the stronger independent fixture/class/rule/SQLite row-equality gate.
2. Checks the packet has exactly the required controls and well-formed reviewer/URI/SHA/UTC evidence references **without pretending their substantive authenticity was proved**.
3. Rejects malformed `D_u`/`tau` (`> 0` if set), `ε`/`γ` (fractions `[0,1]`), Boolean/negative `K`, and any `D_u`/`ε`/`τ`/`γ`/`K` number without a recorded operator-decision reference.
4. Treats **any Stage 5H deterministic fixture as non-representative**, even if someone relabels its accompanying metadata `observed_deployment` and supplies plausible-looking citation strings.
5. Issues `NOT_READY` with an explicit blocker list. Even if every formal field is later filled, it can only issue `READY_FOR_INDEPENDENT_HUMAN_REVIEW_ONLY`, **never automatic Stage 6 approval**.

The built-in local Python 3.12 self-test passed one positive **technical** SQLite trace audit and nine defensive cases (false deployment label, seven invalid packet/parameter mutations and missing independently inspectable SQLite backup). No external sources, real devices or actual authorized documents were supplied. The archived Stage 5H `base` broker trace is still technically sound, but under the provisional packet its diagnosis is:

- `technical_audit_passed = true`; `STAGE5H_SQLITE_SOURCE_AND_LIFECYCLE_VERIFIED`.
- `published_unique = offered_unique = 60`; `independently_matched_db_rows = 58`.
- `verdict = NOT_READY`; **23 explicit blockers**: synthetic origin, Stage 5H deterministic fixture, 16 missing external evidence controls and five unset numeric operational parameters.
- `stage6_permission = NEVER_AUTOMATIC_HUMAN_SIGNOFF_REQUIRED`.

The actual checked-in [`stage5i_synthetic_readiness.json`](../validation/fixtures/stage5i_synthetic_readiness.json) stores this **blocked diagnostic**, rather than a misleading certification. An accompanying [Stage 5I CI workflow](../../.github/workflows/stage5i-evidence-gate.yml) replays all three archived real-broker Stage 5H cases through the readiness gate and **requires** `NOT_READY`. This is a regression to catch an accidental upgrade of synthetic measurements into field evidence.

**Checklist — 5I.4**
- [x] Implement fail-closed evidence register, parameter typing and independent stage-specific trace verification.
- [x] Run a positive technical verification and nine safety cases, including forged source metadata, and keep research-ready status false.
- [x] Record a reproducible 23-blocker diagnosis for a valid Stage 5H synthetic MQTT+SQLite trace.
- [x] Add CI regression of **all three archived** broker-backed Stage 5H traces, asserting technical PASS and research `NOT_READY`.
- [ ] Confirm new CI workflow actually completes successfully on the Stage 5I PR; inspect job logs and links.
- [ ] Independently review real external document contents before marking any evidence reference complete.

## 5I.5 — What must happen before Stage 6

**Route A: representative application paper.** Secure the rights-cleared packet and owner review; instrument the *real* handler; repeat measured source/service trials across stable independent capture windows and resource/failure conditions; approve exactly defined deadlines and capacity before a frozen protocol. Then reconcile closer scheduling prior art and register truthful, matched baselines for the actual experiment.

**Route B: explicitly synthetic conference study.** If no representative data can be used, keep the study framed as a **synthetic operating-region/metric-methodology analysis**. Require supervisor and venue-fit agreement; do not claim field safety requirements, a new queueing theorem or statistically generalizable deployment improvements. Specify synthetic arrival/service models, sensitivity ranges and how limitations change external validity.

Neither route authorizes claiming novel scheduling behavior without resolving the [Stage 4B REVISE/NARROW prior-art decision](novelty-decision-stage4b.md). The existing Stage 5H FIFO is a **reference baseline**, not the study's original method.

**Checklist — 5I.5**
- [x] Provide both explicitly conditional research routes and exact human decision gates.
- [x] Keep Stage 6 preregistration and new scheduler implementation blocked until domain and novelty review.
- [ ] Professor/application owner chooses representative-testbed route versus synthetic-only route and records a dated decision.
- [ ] Source real trace/handler/failure evidence and operator parameters **or** approve a correctly narrowed synthetic-only study.
- [ ] Close Stage 4B original-paper/database/novelty checks and specify a non-trivial proposed contribution.
- [ ] After all gates, freeze matched baselines, statistical unit, held-out workload split and analysis plan before comparative runs.

### Reproduce the blocked diagnosis

```bash
# Repository root: self-tests need no broker, paho or third-party dependencies.
python3 literature/validation/stage5i_evidence_gate.py --self-test

# Decode one archived verified SQLite file into a NEW local path.
base64 --decode literature/validation/fixtures/stage5h_mqtt_base_ci43877369913.sqlite.b64 \
  > stage5i-base.sqlite
python3 literature/validation/stage5i_evidence_gate.py \
  --packet literature/validation/fixtures/stage5i_evidence_register.json \
  --ledger literature/validation/fixtures/stage5h_mqtt_base_ci43877369913.jsonl \
  --sqlite stage5i-base.sqlite --output stage5i-diagnostic.json

# Read the blocked evidence controls; this output is NOT an SLA/performance result.
```

**Stage 5I verdict:** An actionable evidence-acquisition and defensible negative calibration gate exists. **No real-workload or real-handler calibration is completed; no operational deadlines or research contribution is approved.** The next blocker is chiefly **external coordination with the application owner and supervisor**, not implementing another lab scheduling algorithm.
