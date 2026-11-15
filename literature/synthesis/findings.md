# Synthesis of the twelve core papers

This active synthesis uses the retained full-text reviews. It is a focused literature assessment, not an exhaustive SLR or independent replication. R15-R21 were checked against supplied full texts and official publisher identities (R16/R19/R21 use indexed official metadata where direct HTML retrieval was blocked or rate-limited); the earlier five reviews retain their verification provenance. Review numbers are navigation; internal reference keys remain stable.

## Priority messaging already exists

[PrioMQTT: A prioritized version of the MQTT protocol](../reviews/PrioMQTT%20-%20A%20prioritized%20version%20of%20the%20MQTT%20protocol.md) and [Priority-enabled MQTT: a robust approach to emergency event messaging](../reviews/Priority-enabled%20MQTT%20-%20a%20robust%20approach%20to%20emergency%20event%20messaging.md) establish time-critical/emergency message prioritization. Priority support alone is not a distinct contribution.

The first changes transport alongside scheduling; the second is a small prototype with limited timing/statistical evidence. Relevance does not remove those limitations.

## Alarm responsiveness and fairness overlap with existing work

[Multi-Tier Message Scheduling for IoT-Based Urban Emergency Systems Through Semantic Priority Override](../reviews/Multi-Tier%20Message%20Scheduling%20for%20IoT-Based%20Urban%20Emergency%20Systems%20Through%20Semantic%20Priority%20Override.md) combines semantic alarm override, source/device fairness and admission protection. Its fairness is principally within bands; routine traffic can still wait under sustained alarms.

A comparison must align urgency semantics, available metadata and admission populations. Different decision locations do not establish novelty.

## Priority and current congestion are already combined

[Real-Time Priority Queue Scheduling for Bursty Traffic](../reviews/Real-Time%20Priority%20Queue%20Scheduling%20for%20Bursty%20Traffic.md) uses learned Whittle indices and queue states to balance priority service with burst loss. Its no-burst endpoints also show conditions favoring strict priority.

Do not claim occupancy-aware priority is unstudied. Transition training, separate queues and service/slot assumptions matter for any later comparator decision.

## Deadline adaptation may interact with routing and retained work

[Adaptive Priority Scheduling of Internet of Things Data for Disaster Management in Smart Cities](../reviews/Adaptive%20Priority%20Scheduling%20of%20Internet%20of%20Things%20Data%20for%20Disaster%20Management%20in%20Smart%20Cities.md) combines deadline-progress reordering, fallback migration and next-hop selection. Infinite queues and composite interventions limit direct transfer. Saving packets can increase average delay because retained traffic consumes resources.

## Frequency-based source control can conflict with urgent bursts

[A New Back-off Algorithm with Priority Scheduling for MQTT Protocol and IoT Protocols](../reviews/A%20New%20Back-off%20Algorithm%20with%20Priority%20Scheduling%20for%20MQTT%20Protocol%20and%20IoT%20Protocols.md) already combines broker-assigned priority and rate-dependent back-off in 2021. It favors low-frequency publishers, while above-baseline traffic is treated as suspicious. Frequency is not an urgency label; a legitimate emergency may itself increase traffic.

Its latency comparison changes source control and scheduling together. The selected-publisher trace also does not support the strongest prose claim about non-overlapping latency ranges. Retain it as close prior art with limited evidence, rather than a validated deadline/fairness baseline. Further reading should examine legitimate-burst discrimination and how initial-rate assumptions affect delivered work.

## Urgency plus starvation protection is established prior art

[Fair Emergency First (FEF)](../reviews/An%20Adaptive%20Emergency%20First%20Intelligent%20Scheduling%20Algorithm%20for%20Efficient%20Task%20Management%20and%20Scheduling%20in%20Hybrid%20of%20Hard%20Real-Time%20and%20Soft%20Real-Time%20Embedded%20IoT%20Systems.md) combines slack/learned safety checks, reserved capacity and a threshold-triggered preemption option for periodic work. Its model grants CPU preemption and execution-time knowledge; its Table 7 has inconsistent count/percentage entries, and the empirical results do not certify hard-deadline safety.

[Topic-hotness priority with low-priority feedback](../reviews/Design%20of%20topic%20priority%20based%20on%20industrial%20publish-subscribe%20system.md) already combines ordinary topic ranking, an emergency override and delayed routine-service opportunities. Its feedback controller is underspecified and average-delay figures do not prove a waiting bound. This still prevents a claim that existing MQTT work ignores low-priority protection.

The remaining reading task is to compare the mechanisms and urgent-service costs under explicit assumptions. Moving to another queue location, adding an age threshold or combining urgency with routine protection is not enough to establish novelty.

## Selective forwarding changes the comparison population

[PR-MQTT](../reviews/PR-MQTT%20-%20a%20novel%20approach%20for%20traffic%20reduction%20and%20message%20prioritisation%20in%20IoT%20applications.md) learns value ranges, forwards abnormal values first and suppresses similar routine updates. It differs from PrioMQTT. Reduced forwarded work can explain part of latency/resource gains; the published signed-difference formula also conflicts with the absolute-change example.

Count source-offered, intentionally suppressed, admitted, delivered and failed work separately. A skip-count limit alone does not bound elapsed routine waiting; learned ranges and publication frequency are proxies whose errors need study.

## Batch fairness has priority-mix and downstream limits

[FTS-Hybrid](../reviews/Data-Priority%20Aware%20Fair%20Task%20Scheduling%20for%20Stream%20Processing%20at%20the%20Edge.md) is close stream-processing prior art: it combines class queues, queue-length-dependent batching and priority order. Its Table III includes medium/low regressions against PS for an equal priority mix, and its batch-size experiments show large sensitivity. One-minute p95 observations must not be reported as independent trial confidence intervals or pooled request tails.

The control changes spout emission, so downstream operators and batch-fill/flush behavior matter. This is a stronger conceptual comparison than simply asserting that conventional strict priority ignores routine traffic.

## Size and heterogeneous service already inform urgency scheduling

[Delay/size-aware healthcare scheduling](../reviews/Delay%20and%20size-dependent%20priority-aware%20scheduling%20for%20IoT-based%20healthcare%20traffic%20using%20heterogeneous%20multi-server%20priority%20queueing%20system.md) combines delay class, size class and fastest-idle-server allocation. The reported results are analytical/numerical, with infinite queues and nominal stable loads; independent simulation and a consecutive-urgent-service threshold are future work.

A model's average slowdown improvement is not a validated deadline or starvation bound. Unit/load definitions and server-state aggregation need scrutiny before faithful baseline use.

## Deadline history feedback predates a new priority score

[DRA](../reviews/Deadline-aware%20rate%20allocation%20for%20IoT%20services%20in%20data%20center%20network.md) uses remaining lifetime and recent head-of-line miss ratio for flow prices. It reports link fairness and successful-flow completion delay with deadline throughput close to EDF. Its printed residual-allocation branch also needs reconciliation.

Historical missing ratio, cumulative service deficit and per-job age are different signals. Link-throughput fairness is distinct from routine maximum waiting, and conditioning latency on successful flows omits expiry failures. A new deadline/history combination alone is insufficient novelty.

## Questions to challenge with more core literature

| Candidate question | Why these papers motivate it | Evidence still needed |
| --- | --- | --- |
| Which methods balance urgent failures with routine tail waiting under bursts? | TRIAGE/4 fairness scope; FEF thresholds; topic feedback; FTS-Hybrid mix regressions; WTI tradeoff | Close deadline/aging/fair-queue approaches, contrary results and matched objective definitions |
| How do source controls distinguish urgent bursts from rate anomalies? | R15 frequency proxy and startup-rate trust; TRIAGE/4 semantic labels and admission | Methods evaluating legitimate bursts, anomaly errors and class outcomes under matched offered load |
| Which mechanisms tolerate imperfect urgency/value classification? | PR-MQTT learned min/max and routine filtering; R15 rate proxy | Evidence on drift, initial-sample bias, false alarms, missed urgency and receiver freshness |
| Which latency improvements persist under equal transport, resources and offered populations? | PrioMQTT transport change; TRIAGE/4 admission; PR-MQTT suppression; disaster routing/migration | Comparable evaluations isolating the intervention and reporting loss |
| How do control location and service assumptions change routine protection? | FTS-Hybrid emission batches; non-preemptive healthcare servers; DRA divisible flows | Comparable offered-load outcomes, batch flush/downstream effects, finite buffers and preemption boundaries |
| When is model-training or adaptation cost justified? | WTI transition information; FEF ANN/history requirements; adaptive-control overhead | Workload-shift/model-error/overhead studies under comparable information budgets |

These are reading questions, not demonstrated field-wide gaps or selected contributions.

## Next step

Screen new papers for an explicit scheduling/admission mechanism relevant to urgency, deadlines, routine protection or overload. Review only those that materially inform this question. Continue toward 20-25 core-relevant reviews before choosing the idea and designing experiments.

The [previous synthesis](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/blob/938a07f828909bb2d8f31e271a0b479dd117f562/literature/synthesis/findings.md) remains accessible for historical context. Supporting/excluded material is not part of this active synthesis.
