# Research design review — checkpoint 1

Reviewed 20 October 2026. Decision: proceed with an experimental implementation of the [candidate specification](candidate-spec.md). Algorithmic novelty and publication suitability remain unresolved. This checkpoint supersedes the proposal's occupancy-only candidate rule, not the historical pilot evidence.

## What the literature establishes

| Source | Established overlap | Consequence for this project |
| --- | --- | --- |
| R1, R2, R3, R7 in [related work](../related-work.md) | MQTT priority support and urgent delivery already exist. | Priority queues or an MQTT demo alone are insufficient contributions. |
| R5, R6 | Real-time MQTT architectures and response-time analysis already exist. | Receiver-local measurements cannot establish network-wide or hard real-time guarantees. |
| R8 | Semantic urgency and device fairness are studied together. | Obtain and compare the full method before asserting a distinct scheduling contribution. Current review uses abstract/metadata only. |
| R9 | Instantaneous queue length and priority guide burst-aware scheduling. | Occupancy-dependent scheduling and the urgency/congestion tradeoff are existing ideas. |

R9 uses switch output queues and a Whittle-index formulation; our candidate uses one application worker and per-event deadlines. This model distinction motivates a separate experiment, but does not establish novelty. R8 full text was unavailable during review. Absence of a feature from an abstract is not evidence that the paper lacks it. This is a focused review, not a systematic or exhaustive literature search.

## Why revise the candidate

The proposed aging interval decreases as occupancy rises. Faster promotion can move routine work ahead of urgent alerts precisely when the queue is congested. Once all effective priorities reach zero, ordering is determined by the tie-breaker, rather than original urgency.

The existing [pilot](../../evidence/pilot/README.md) is a diagnostic warning, not candidate evidence: at 120 arrivals/s, fixed aging and FIFO both have approximately 1,568 ms high-priority mean-of-run-p95 latency, versus approximately 23 ms for strict priority. These are finite unbounded runs with 10 ms service, 1,000 events and ten seeds. They neither test adaptive aging nor establish sustained starvation.

Revision: test occupancy-dependent aging with an estimated deadline guard. The guard can still fail under overload, inaccurate service estimates or future arrivals. Its benefit must be separated from the occupancy component using matched ablations.

## Testable research question

In a bounded, non-preemptive IoT application worker, does occupancy-dependent aging improve routine waiting compared with tuned fixed aging using the same deadline guard and tie-breaker, while respecting a prespecified urgent deadline-failure budget?

- H1: the candidate reduces low-priority per-run p95 waiting relative to the matched fixed-aging baseline.
- H2: its high-priority deadline-failure increase relative to strict priority remains within 0.01 absolute probability (one percentage point).
- H3: disabling the guard worsens urgent deadline failure in at least some congested scenarios; this is a mechanism hypothesis, not a required positive result.

The 0.01 budget is a study design choice, not a domain safety standard. Also report budgets 0, 0.005 and 0.02 as sensitivity analyses. Report mean paired differences with 95% paired bootstrap intervals across seeds, using 10,000 resamples. Resample whole seeds, never individual alerts. For H1, an interval entirely below zero supports improvement. For H2, the upper confidence limit must be at most 0.01. Correct for multiple comparisons when making joint confirmatory claims; otherwise label scenario-level intervals exploratory.

A tradeoff claim additionally requires reporting low-priority drop fraction and deadline failure: faster completed events can merely reflect selective loss. A strong positive claim requires no increase in these loss measures (upper paired confidence limit at most zero), or an explicit narrower statement describing the cost. Undefined metrics cannot pass a criterion. Report every registered scenario, including failures. Success in selected scenarios does not support a universal improvement claim.

## Frozen evaluation inputs, version 1

These version 1 inputs are serialized in [the registered plan](../../configs/research-v1.json) and implemented by the [Task 7 runner](experiment-runner.md). Primary experiments have not yet been run.

| Dimension | Primary plan |
| --- | --- |
| Policies | FIFO, strict priority, EDF, existing fixed aging; candidate and matched controls in the specification |
| Traffic | Poisson and event-index burst; burst interval [0.4, 0.6), multiplier 5 |
| Base arrival rate | 50, 90, 120, 200 events/s; burst compression increases overall offered load |
| Service | Constant, uniform ±50%, exponential; mean parameter 10 ms |
| Waiting capacity | 100 and 1,000; no eviction, reject arriving event when full |
| Events and priority weights | 10,000; high:medium:low = 1:2:7 |
| Relative deadlines | High 100 ms, medium 500 ms, low 2,000 ms |
| Tuning seeds | 1001–1010; diagnostic seeds 1–10 excluded |
| Evaluation seeds | 2001–2030, untouched until parameters and analysis manifest are recorded |

Tune one global parameter setting per method, not a setting per evaluation scenario. Pool tuning scenarios with equal scenario weight. Select feasible settings satisfying the H2 budget, then minimize average low-priority per-run p95 waiting; ties use lower urgent failure, then lexicographic parameter order. If none is feasible, record that outcome rather than relax the budget. Preserve raw traces, exact parameters, software version and hashes. Task 7 must serialize this plan before evaluation; amendments require a dated rationale before inspecting held-out outcomes.

Primary conclusions concern finite generated workloads with full drain. Extra checks should cover high-priority-heavy traffic, service-estimate error, capacity zero, no deadlines and large queues. These are stress/compatibility checks, not new primary scenarios chosen after seeing results.

## Claim boundary and next gate

Task 6 may implement the heuristic and deterministic selection tests. Before a paper claims novelty, obtain R8 full text, assess applicable recent methods and either implement a justified closest-method comparator or explain model incompatibility. If the candidate fails against matched fixed aging, report that negative result and reconsider the method; do not claim the combination is novel by default. Device fairness, attack detection, authenticated priority, hard deadlines and end-to-end latency are outside the present evidence.

## Task 7 protocol clarification — 21 October 2026 (Malaysia time)

Before inspecting any held-out primary outcomes: tuning feasibility uses the upper 95% paired percentile-bootstrap limit for the equally weighted, scenario-averaged urgent failure difference versus strict priority. A pooled tuning pass does not establish per-scenario H2 success. Each seed is resampled as a whole across scenarios. Tuning selects one global setting independently for adaptive guarded and matched fixed guarded methods. Existing arrival-tie fixed aging stays at its historical 100 ms as an explicitly untuned reference; the matched fixed guarded method is the tuned fixed-aging comparator. Unguarded controls inherit their corresponding guarded method's selected parameters. Loss-based claim checks remain required in Task 8; they are not additional tuning filters.

The executable primary plan has 48 scenarios, 7,680 tuning runs and 11,520 held-out evaluation runs. A separate reduced smoke profile tests orchestration and is labelled as engineering evidence only. Registration writes the plan, analysis rules, source snapshot and hashes before tuning. Evaluation is a separate command that requires complete, checksum-verified tuning artifacts and feasible frozen selections. If tuning is infeasible, preserve the negative result; a redesigned protocol requires a new registration and independent evaluation seeds after any held-out outcomes have been examined.

## Closest-method checkpoint — 21 October 2026

The [focused comparator review](closest-method-comparison.md) verifies R8 publisher abstract evidence and reviews R9 author-postprint method sections. R8 publisher full text remains inaccessible; exact reproduction and novelty assessment remain open. Existing matched controls support a mechanism study, not state-of-the-art superiority. Review the comparator acceptance criteria before committing the primary experiment budget. The v1 executable protocol is unchanged.
