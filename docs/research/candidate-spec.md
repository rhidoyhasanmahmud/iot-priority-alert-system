# Candidate scheduler specification — version 1

Status: implemented in Task 6; experimental and not yet performance-evaluated. See [usage and implementation](candidate-implementation.md). Read the [design review](design-review.md) for hypotheses and limits. Working description: guarded occupancy-based aging. This is an experimental heuristic, with no optimality or starvation guarantee.

## Selection at an idle worker

Use the existing engine's admission, completion ordering, bounded waiting capacity and non-preemptive service. Do not change admission by policy. All times below are seconds. Candidate mode requires finite positive waiting capacity C; reject unbounded/zero-capacity configuration explicitly. Existing baseline policies continue supporting those configurations.

1. After completion and same-time admissions, let S be pending events, n its size, and t the dispatch time. If S is empty, do nothing. Compute u = min(1, max(0, n − 1) / C). Subtract one because one pending event can immediately occupy the idle worker; C counts waiting slots only.
2. Compute A = A_max − u × (A_max − A_min). Require finite 0 < A_min ≤ A_max. For each event, w = max(0, t − arrival), and p_eff = max(0, priority − floor(w / A)). Saturate promotions at the original priority before division where needed to avoid floating-point overflow.
3. Choose base event b by ascending (p_eff, absolute_deadline_or_infinity, arrival, id). A relative deadline is measured from arrival. Deadline equality is on time.
4. Among original-priority-0 events with known deadlines, find h by ascending (absolute_deadline, arrival, id). If none exists, dispatch b.
5. Let s_hat be a configured finite positive service estimate shared by all events. If b differs from h and t + 2 × s_hat > deadline(h), dispatch h; otherwise dispatch b. If h is already late, the same rule still applies. Do not discard late events. Equality does not activate the guard.

The estimate is configured from the workload's nominal mean or independent calibration. The primary scheduler must not inspect actual per-event service times, future arrivals or future outcomes. The simulator may use actual service times only after selection to advance time. A single-step guard neither prevents all deadline misses nor considers every endangered alert. Repeated urgent dispatch can severely delay routine work.

## Parameters and controls

Initial development defaults: A_min = 0.1, A_max = 1.0, s_hat = 0.01. These are implementation defaults, not tuned performance claims.

Tuning grid: A_min in {0.05, 0.1, 0.2}; A_max in {0.5, 1.0, 2.0}. Use s_hat = 0.01 throughout primary comparisons. Service-estimate sensitivity uses {0.005, 0.02}; keep the same actual input traces. Follow the global selection rule in the review.

| Control | Exact change | What it isolates |
| --- | --- | --- |
| Matched fixed aging with guard | Set A_min = A_max = A; same guard and deadline tie-break. Tune A in {0.05, 0.1, 0.2, 0.5, 1.0, 2.0}. | Added value of occupancy adjustment |
| Adaptive without guard | Steps 1–3 only; same selected adaptive parameters | Guard contribution |
| Fixed aging without guard, deadline tie-break | Constant A, steps 2–3; same selected matched fixed parameter | Interaction of occupancy and guard |
| Existing fixed aging | Preserve existing arrival/id tie-break and API behavior | Historical baseline; not a substitute for matched controls |

Log all resolved parameters, policy variant and guard activation count. Keep the existing historical pilot unchanged. Algorithm implementation should use a clear linear scan first; measure selection overhead before making efficiency claims.

## Required Task 6 validation

Deterministic cases must cover empty/single queues; occupancy endpoints and intermediate interval; promotion saturation; all tie-break fields; absent/equal/overdue deadlines; guard activation and no activation at exact equality; known-deadline high priority selection; variable actual service independent of s_hat; invalid parameters; and identical selection between adaptive and matched fixed variants when A_min = A_max. Integration checks must preserve accounting, timestamp order and bounded admission for every existing policy, with shared replay input. Implementing these checks is part of Task 6.
