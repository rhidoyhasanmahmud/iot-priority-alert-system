# Cross-paper synthesis

This is a synthesis of seven retained critical reviews, not a comprehensive proof of a literature gap. Supporting references link to the source-located individual notes. No new experiment was run.

## Finding 1: Priority support is established; its marginal effect depends on comparison design

[R01](../reviews/01-priomqtt-2024.md) and [R02](../reviews/02-priority-enabled-mqtt-2024.md) establish priority messaging implementations. R01 changes transport as well as queue behavior; R02 offers a small prototype timing evaluation.

**Implication:** a new claim must identify its mechanism and isolate the intervention. A successful urgent queue alone is insufficient evidence of a distinct contribution.

## Finding 2: Fairness describes different service relationships

[R08](../reviews/03-multi-tier-message-scheduling-2026.md) emphasizes within-band source/device fairness, allowing cross-band starvation. [R12](../reviews/07-online-aoi-packet-management-fairness-2026.md) relates online fairness and safe packet management to total AoI. These results do not contradict one another: they address different fairness objects and objectives.

**Implication:** specify whether protection concerns devices, urgency classes, admission probability, waiting or delivered freshness.

## Finding 3: Congestion-aware prioritization exists, with meaningful operating costs

[R09](../reviews/04-priority-queue-scheduling-bursty-traffic-2025.md) uses learned queue-state indices; [R11](../reviews/06-adaptive-priority-disaster-management-2024.md) combines deadline progress with migration/routing. R09 reports conditions where SP has better no-burst endpoints, while R11 shows that saving traffic can raise delay.

**Implication:** useful findings may concern operating conditions and tradeoffs rather than universal dominance. Include model-acquisition cost and component attribution.

## Finding 4: Buffer and discard semantics change the research problem

[R10](../reviews/05-periodic-multi-source-peak-age-2023.md) and [R12](../reviews/07-online-aoi-packet-management-fairness-2026.md) concern freshness and obsolete updates. [R08](../reviews/03-multi-tier-message-scheduling-2026.md) can reject alarms at admission; [R11](../reviews/06-adaptive-priority-disaster-management-2024.md) assumes infinite buffers.

**Implication:** do not rank their headline latencies as if offered populations, buffer resources and message meanings were equivalent.

## Questions to challenge with further reading

| Candidate question | Existing supporting evidence | Evidence needed before calling it a gap |
| --- | --- | --- |
| Which policies protect routine service while controlling urgent failure under bursts? | R08 separates intra-band fairness from cross-band service; R09 demonstrates priority/congestion tradeoffs | Closest deadline/aging/fair-queue methods and counterexamples |
| Which apparent latency gains persist when loss and offered workload are reconciled? | R01 transport changes; R08 shedding; R11 retained-traffic cost | Matched evaluations that already address these confounders |
| When do learned versus simple queue-state rules justify their information/overhead costs? | R09 transition training; R08 measured scheduling overhead | Methods studying workload shift, model error and overhead under comparable resources |

These are reading directions. None is a chosen contribution.

## Evidence that would change our direction

- A recent method already answering a candidate question under comparable assumptions.
- A requirement that makes update replacement or rate shedding unacceptable.
- An objective whose operational meaning differs from the convenient available metric.
- A simple baseline explaining the supposed improvement.
- A fair implementation or data requirement that exceeds available resources.

## Research decision

Continue targeted reading toward 20-25 relevant papers, updating the [comparison matrix](comparison.csv) and this synthesis after each batch. Select the conference-paper idea from supported questions. The archived prototype is reusable engineering work, not a constraint on the conclusion.
