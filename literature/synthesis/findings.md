# Synthesis of the five core papers

This active synthesis uses the retained full-text reviews. It is a focused literature assessment, not an exhaustive SLR, new source verification or independent replication. Review numbers are navigation; internal reference keys remain stable.

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

## Questions to challenge with more core literature

| Candidate question | Why these papers motivate it | Evidence still needed |
| --- | --- | --- |
| Which methods balance urgent failures with routine tail waiting under bursts? | TRIAGE/4 fairness scope; WTI congestion/priority tradeoff | Close deadline/aging/fair-queue approaches, contrary results and matched objective definitions |
| Which latency improvements persist under equal transport, resources and offered populations? | PrioMQTT transport change; TRIAGE/4 admission; disaster routing/migration | Comparable evaluations isolating the intervention and reporting loss |
| When is model-training or adaptation cost justified? | WTI transition information; adaptive controls and measured overhead | Workload-shift/model-error/overhead studies under comparable information budgets |

These are reading questions, not demonstrated field-wide gaps or selected contributions.

## Next step

Screen new papers for an explicit scheduling/admission mechanism relevant to urgency, deadlines, routine protection or overload. Review only those that materially inform this question. Continue toward 20-25 core-relevant reviews before choosing the idea and designing experiments.

The [previous synthesis](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/blob/938a07f828909bb2d8f31e271a0b479dd117f562/literature/synthesis/findings.md) remains accessible for historical context. Supporting/excluded material is not part of this active synthesis.
