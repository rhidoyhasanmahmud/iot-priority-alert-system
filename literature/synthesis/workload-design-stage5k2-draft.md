# Stage 5K.2 — Synthetic workload contract and calibration decisions (DRAFT)

**Date:** 16 November 2026  
**Track:** Researcher-selected Controlled Testbed  
**Status:** **DESIGN CANDIDATE ONLY — NOT CALIBRATED, NOT FROZEN, NO SCIENTIFIC PERFORMANCE RUN AUTHORIZED**  
**Inputs:** [Stage 5J broker lab](controlled-testbed-stage5j.md) · [Stage 5K.1 evidence audit](workload-calibration-stage5k.md) · [Stage 5I fail-closed evidence register](workload-evidence-calibration-stage5i.md) · [RQ v1.0](research-questions.md).

## 1. Actual evidence versus a proposed workload

The audited Stage 5J real-MQTT/SQLite environment has one non-preemptive FIFO worker, `K` waiting slots plus one active slot, 60 **fictional** tamper/health messages per run, fixed one-urgent-to-three-routine source mix, and debug `D_u=τ=50 ms`. In Stage 5K.1 we independently profiled **committed-only** SQLite durations. We did **not** observe the service demand rejected messages would have consumed. The 18-case CI batch is an engineering integrity test, **not** 18 independent real-world capture periods.

This document proposes a *future declared synthetic workload model*. Nothing here validates source representativeness, operational deadlines, a new scheduling algorithm, or existing-policy superiority.

## 2. Versioned workload contract — proposed fields

The future fixture must be built **once, independently of the policy**, and saved with a content SHA-256. Two distinct data channels are necessary:

| Channel | Event-level fields | When an online policy may see it |
| --- | --- | --- |
| **Offer-visible** | `fixture_id`, `event_id`, `trusted_class`, `planned_offer_offset_ns`, optional declared urgent deadline at local offer | Only upon actual post-validation local offer, not before; no future arrivals |
| **Hidden execution schedule** | `event_id`, `synthetic_required_work_units` or explicitly justified service-demand model, generator seed and model version | Execution service model / *offline* auditor only; **never** online dispatch before starting that job |
| **Measured outcome** | Actual local `offer_ns`, `start_ns`, `complete_ns`, admission disposition, SQLite commit, CPU/memory, policy decisions | Observed after execution; no retcon of rejected-service duration as observed |

**Important distinction:** A generated work requirement for every offered ID can support **synthetic experiment accounting**; it is not a measured service time for rejected events and not a real handler distribution. Any transformation from synthetic work units to time needs an explicit *tested* service model. Never insert an oracle service value into a live policy's priority/dispatch decision unless its information-access contract explicitly permits a prediction available to all comparators.

## 3. Proposed factor isolation, not committed parameters

| Axis | Proposed design rule | Why it matters | Approval |
| --- | --- | --- | --- |
| **Burst concentration** | Match **planned total source horizon and total offered IDs/work**, vary only gap concentration, then separately add high-rate overload | Prevent burst shape being confounded with average input intensity | [ ] |
| **Mean work versus variability** | Fix the declared mean offered *synthetic* work while varying dispersion. Record work for admitted **and rejected** IDs in hidden offline fixture | Needed to distinguish schedule burst effects from job-size effects | [ ] |
| **Urgent/routine mix** | Evaluate multiple predeclared class proportions, retaining one fixed mix for each seed/policy pairing | Avoid basing the conclusion on the invented 1:3 split | [ ] |
| **Buffer capacity** | Include more than one finite `K`, and explicitly preserve `K waiting + one running` semantics | Expose admission dependence without claiming resource-derived physical limits | [ ] |
| **Deadline / access targets** | Declare `D_u`, ε, τ, γ, expiry and undefined denominator handling **before** outcome analysis | Avoid target-tuning to favorable debug traces | [ ] |
| **Evaluation host** | Fix CPU/quota/power/SQLite config, warmup, background load and logging/measurement overhead for compared policies | CI process timing and queue occupancy vary even under identical source IDs | [ ] |

**Current numeric values are illustrative only:** 60 events, 3 fixture seeds, 1:3 classes, `K=0/3`, `D_u=τ=50 ms`. They must **not** be inherited as paper targets without a fresh signed decision. Candidate sensitivity grids and run counts are deliberately **TBD**, not invented here.

## 4. Pre-study calibration pathways

Two transparent routes can support the chosen Controlled Testbed:

**A. Externally anchored synthetic workload (preferred where permitted):** Derive *assumption ranges* from rights-cleared public/deployment trace characteristics or a documented actual handler microbenchmark. Keep trace identifiers, collection window, preprocessing, exclusions, class mapping, service-demand measurement and source hashes available to independent reviewers. Synthetic generated load must still be labelled synthetic.

**B. Explicitly artificial sensitivity study:** If empirical anchors are unavailable, state that arrivals, class labels, service demand and numeric constraints are **hypothetical**. Ask the professor/venue to approve that scope. Make the contribution a properly controlled explanation **inside the declared model**, without extrapolating to industrial/medical/emergency IoT or operator SLA guarantees.

The Stage 5I [16-field readiness gate](../../experiments/stage5i_evidence_gate.py) remains the authority for external-evidence packets. A self-declared DOI or source link, a passed CI run, or a fabricated signed date cannot automatically upgrade a fictional workload into deployment evidence.

## 5. Freeze checklist and rejection criteria

- [x] Separate visible arrivals, hidden ex-ante simulated work and post-hoc measured outcomes at the contract level.
- [x] Record how Stage 5K.1 committed-only service sampling can bias conclusions about offered work.
- [x] Specify burst-vs-intensity, mix-vs-size and capacity-vs-hardware confound controls in a draft.
- [x] Implement and independently test an **explicitly fictional candidate** event/work fixture with cross-axis pairing checks; [pilot and limitations](stage5k2_fixture_pilot.md). This is software-contract validation, **not** study-model approval or empirical calibration.
- [ ] Professor approves **A or B** and the exact application/generalization scope.
- [ ] Approve/freeze the *scientific* fixture generator, justified source/work ranges, and an enforceable online hidden-service information firewall. The current synthetic candidate and its hashes/tests are **not** signed research specifications.
- [ ] Select justified *numeric* factor ranges, mean and variation families; include zero-denominator, expiry and tie rules.
- [ ] Verify source count, offered work and per-event pairing across all candidate policies before any treatment run.
- [ ] Sign a dated protocol freeze with fixed seeds/training-versus-holdout, independent run-level replication and resource configuration.

**Stop condition:** If the only support for work amounts, deadline targets and class ratios is our current tiny fictional SQLite CI run, this stage **must remain UNCALIBRATED**. Even after A/B approval, the Stage 4B novelty threat and Stage 6 scientific-protocol sign-off are separate gates.
