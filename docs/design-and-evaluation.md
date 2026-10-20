# Design and evaluation

## Research question
How does non-preemptive strict priority scheduling change high-priority IoT alert latency and low-priority waiting time compared with FIFO under increasing load?

This is an implementation and evaluation project. It does not claim a new scheduling algorithm or an attack detector. Security alerts may be represented as input events, but no detector is implemented.

## Design
The MQTT demo has a simulated publisher, local Mosquitto broker and one receiver/worker. Priority 0 is high, 1 medium, 2 low. FIFO preserves receiver arrival order. Priority selects the highest-priority waiting event; equal priorities retain arrival order. Work already in progress is never interrupted.

The separate discrete-event experiment provides reproducible comparisons without operating-system timing noise. Both policies consume the exact same seeded Poisson arrival trace, priority assignments and constant service cost. Its queue is unbounded and all events drain after arrivals stop. The demo has a bounded 10,000-event queue, logs rejection and uses MQTT QoS 1, which may duplicate delivery. Demo measurements are descriptive, not comparative research evidence.

## Experiment protocol
1. Use 10 ms service time (nominal capacity 100 events/s).
2. Compare arrival rates 50, 90, 120 and 200 events/s.
3. Use 10,000 events per run and at least 10 seeds (e.g. 1–10).
4. Save config.json, both raw CSVs and summary.csv for every run. Record the code commit and Python version with the evidence.
5. Report per-priority mean and p95 response latency, maximum waiting time and completed count. Throughput is total completions divided by time from first arrival to final completion, including queue drain.
6. Compare paired runs and report uncertainty across seeds. Do not treat individual events as independent replicate experiments.

Latency is completion minus arrival; waiting time excludes processing. p95 uses the nearest-rank definition. Throughput is system-wide and repeated in each priority summary row; do not sum those values.

## Limits and interpretation
Strict priority can delay or starve low-priority work under sustained high-priority load. A finite draining experiment cannot demonstrate indefinite starvation. Overload scenarios are finite bursts, not stable steady-state operation. No warm-up is discarded. Constant service cost and synthetic priorities simplify real deployments. Priority does not increase processing capacity or guarantee deadlines; low load may show little benefit.

The demo reports receiver-local time from enqueue to completion, excluding sensor/network latency. It trusts publisher priorities, has no authentication, deduplication or restart recovery, and is bound to localhost for laboratory use. Do not interpret it as a secure production system. Priority spoofing, aging, TLS, access control, real hardware and burst workloads are future extensions.

## Initial development milestones
Weeks 1–2: problem and proposal. Weeks 3–4: MQTT and message flow. Weeks 5–6: scheduler and tests. Weeks 7–9: experiment matrix. Weeks 10–12: analysis, limitations and report. The expanded research direction is described in [the proposal](../docx/IoT_Alert_Processing_Research_Proposal.docx).


## Evidence update

The simulator also supports fixed aging through its Python API and the pilot runner. See [pilot evidence](../evidence/pilot/README.md), [application scenario](application-scenario.md) and [related-work comparison](related-work.md). The original two-policy CLI and MQTT demo retain their existing scope.
