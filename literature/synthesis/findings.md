# Cross-paper synthesis

This synthesis draws on **5 core-related reviews and 3 supporting-only references**, plus 1 excluded assessment retained as a screening record. The [relevance audit](../relevance-audit.md) distinguishes these roles. Supporting AoI/industrial studies inform concepts and measurement, not a claim that they directly address urgent/routine alert scheduling. No source PDF was reread or new experiment performed for this relevance audit.

## Finding 1: Priority support is established; its marginal effect depends on comparison design

[R01](../reviews/PrioMQTT%20-%20A%20prioritized%20version%20of%20the%20MQTT%20protocol.md) and [R02](../reviews/Priority-enabled%20MQTT%20-%20a%20robust%20approach%20to%20emergency%20event%20messaging.md) establish priority messaging implementations. R01 changes transport as well as queue behavior; R02 offers a small prototype timing evaluation.

**Implication:** a new claim must identify its mechanism and isolate the intervention. A successful urgent queue alone is insufficient evidence of a distinct contribution.

## Finding 2: Fairness describes different service relationships

[R08](../reviews/Multi-Tier%20Message%20Scheduling%20for%20IoT-Based%20Urban%20Emergency%20Systems%20Through%20Semantic%20Priority%20Override.md) emphasizes within-band source/device fairness, allowing cross-band starvation. [R12](../reviews/Online%20age%20of%20information%20scheduling%20-%20The%20power%20of%20packet%20management%20and%20fairness.md) relates online fairness and safe packet management to total AoI. These results do not contradict one another: they address different fairness objects and objectives.

**Implication:** specify whether protection concerns devices, urgency classes, admission probability, waiting or delivered freshness.

## Finding 3: Congestion-aware prioritization exists, with meaningful operating costs

[R09](../reviews/Real-Time%20Priority%20Queue%20Scheduling%20for%20Bursty%20Traffic.md) uses learned queue-state indices; [R11](../reviews/Adaptive%20Priority%20Scheduling%20of%20Internet%20of%20Things%20Data%20for%20Disaster%20Management%20in%20Smart%20Cities.md) combines deadline progress with migration/routing. R09 reports conditions where SP has better no-burst endpoints, while R11 shows that saving traffic can raise delay.

**Implication:** useful findings may concern operating conditions and tradeoffs rather than universal dominance. Include model-acquisition cost and component attribution.

## Finding 4: Buffer and discard semantics change the research problem

[R10](../reviews/Scheduling%20for%20Periodic%20Multi-Source%20Systems%20with%20Peak-Age%20Violation%20Guarantees.md) and [R12](../reviews/Online%20age%20of%20information%20scheduling%20-%20The%20power%20of%20packet%20management%20and%20fairness.md) concern freshness and obsolete updates. [R08](../reviews/Multi-Tier%20Message%20Scheduling%20for%20IoT-Based%20Urban%20Emergency%20Systems%20Through%20Semantic%20Priority%20Override.md) can reject alarms at admission; [R11](../reviews/Adaptive%20Priority%20Scheduling%20of%20Internet%20of%20Things%20Data%20for%20Disaster%20Management%20in%20Smart%20Cities.md) assumes infinite buffers.

**Implication:** do not rank their headline latencies as if offered populations, buffer resources and message meanings were equivalent.

## Finding 5: Applied deployment evidence and queue-only scheduling evidence answer different questions

[Review 08: textile cloud-edge-end system](../reviews/A%20Cloud-Edge-End%20Collaborative%20Remote%20Monitoring%20and%20Scheduling%20System%20for%20Textile%20Equipment.md) adds workshop evidence from 120 looms, but combines detection, aggregation, diagnosis, routing, task migration/preemption and production optimization. Table 5 (p. 22) reports alert p99 200 vs 452 ms; Table 7 (p. 24) reports burst-task response 236 ± 48 vs 521 ± 132 ms. These are different endpoints.

Table 9 (p. 28) helps separate some components: disabling compute preemption changes burst response to 348 ± 76 ms, so the full threshold-baseline gain cannot be attributed solely to priority. Redundant filtering rises 61.5% to 87.4% (+25.9 pp; +42.1% relative), changing work forwarded to the cloud. The 6x6 classification matrix and repeated hold-out aggregation need clarification before treating the stated multi-label exact-match metric as independently verified.

**Connection:** like R01 and R11, multiple interventions complicate attribution; like R08/R12, changed traffic populations require explicit semantics. Alarm clustering, source-rate shedding and obsolete-update replacement are distinct mechanisms.

**Implication:** classify this as supporting systems/evaluation work. Ask whether distinct incidents remain observable and compare equal offered populations/resources before claiming a scheduling advantage. One paper's reporting ambiguity is not proof of a novel research gap.

## Questions to challenge with further reading

| Candidate question | Existing supporting evidence | Evidence needed before calling it a gap |
| --- | --- | --- |
| Which policies protect routine service while controlling urgent failure under bursts? | R08 separates intra-band fairness from cross-band service; R09 demonstrates priority/congestion tradeoffs | Closest deadline/aging/fair-queue methods and counterexamples |
| Which apparent latency gains persist when loss and offered workload are reconciled? | R01 transport changes; R08 shedding; R11 retained-traffic cost | Matched evaluations that already address these confounders |
| When do learned versus simple queue-state rules justify their information/overhead costs? | R09 transition training; R08 measured scheduling overhead | Methods studying workload shift, model error and overhead under comparable resources |

The new R13 evidence strengthens the need to separate alert-pipeline latency, compute-task response and production-order completion. It does not select a new algorithm or authorize implementation.

These are reading directions. None is a chosen contribution.

## Full-text screening record: review 09 excluded from the core set

[Review 09: smart waste monitoring](../reviews/IoT-based%20smart%20waste%20management%20system%20-%20real-time%20monitoring%20and%20environmental%20compensation.md) describes threshold sensing, rain-triggered suspension and periodic ThingSpeak updates. It has no priority/deadline queue policy, burst scheduling baseline or routine-service evaluation; therefore it is **not counted toward the 20-25 relevant scheduling-paper target**.

Its reported 99% correctness lacks test denominators; methodology uses feet while Table 1 uses metres; Table 2 mixes average update delay and 95%-within-2s phrasing. These reporting issues further limit its use, but scope mismatch alone justifies exclusion. Its publisher/DOI identity is verified; journal rank is not asserted.

**Transferable lesson:** sensor validity, event detection, sampled publication and queue dispatch have different timing boundaries. Pausing observation during rain is not evidence of improved scheduler reliability. Keep this record to avoid repeating selection; do not let recent publication year or a high headline accuracy substitute for relevance.

## Evidence that would change our direction

- A recent method already answering a candidate question under comparable assumptions.
- A requirement that makes update replacement or rate shedding unacceptable.
- An objective whose operational meaning differs from the convenient available metric.
- A simple baseline explaining the supposed improvement.
- A fair implementation or data requirement that exceeds available resources.

## Research decision

Continue targeted reading toward 20-25 relevant papers, updating the [comparison matrix](comparison.csv) and this synthesis after each batch. Select the conference-paper idea from supported questions. The archived prototype is reusable engineering work, not a constraint on the conclusion.
