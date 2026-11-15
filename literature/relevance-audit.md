# Paper relevance audit - 15 November 2026

## Scope and evidence basis

**Working scope:** urgent-versus-routine service, deadlines, aging/fairness and burst/overload handling in IoT messaging. An explicit relevant dispatch/admission decision matters; merely sensing data or using MQTT/cloud does not establish relevance.

Audited main commit: `938a07f828909bb2d8f31e271a0b479dd117f562`. This is a relevance assessment of **all 14 catalog entries** using the **9 existing repository reviews** and their method/evidence pointers. It is not a fresh reading of every original PDF, new bibliographic verification, quality ranking or independent replication. The other 5 entries have no full-text review recorded.

## Decisions and counts

| Class | Count | Count toward core 20-25 target? |
| --- | ---: | --- |
| Core-related, full text reviewed | 5 | Yes |
| Supporting-only, full text reviewed | 3 | No |
| Unrelated, excluded after full-text assessment | 1 | No |
| Catalog-only, pending full-text screening | 5 | No |

Previous headline review totals mixed these roles. **Current core progress is 5, not 9.** A core label means relevant prior work; it does not imply a robust result or a ready-to-copy baseline.

## All reviewed papers

| Review no. | Paper | Decision | Why / model boundary |
| --- | --- | --- | --- |
| 01 | [PrioMQTT: A prioritized version of the MQTT protocol](reviews/PrioMQTT%20-%20A%20prioritized%20version%20of%20the%20MQTT%20protocol.md) | Core-related | Explicit broker/message priority ordering for time-critical MQTT. Direct prior art, although transport also changes. Protocol/transmission layer; UDP/TCP change prevents queue-only gain attribution. |
| 02 | [Priority-enabled MQTT: a robust approach to emergency event messaging](reviews/Priority-enabled%20MQTT%20-%20a%20robust%20approach%20to%20emergency%20event%20messaging.md) | Core-related | Explicit Urgent/Critical/FCFS message classes and emergency-priority delivery. Small architecture prototype; weak timing/statistical evidence. Relevance is not a quality endorsement. |
| 03 | [Multi-Tier Message Scheduling for IoT-Based Urban Emergency Systems Through Semantic Priority Override](reviews/Multi-Tier%20Message%20Scheduling%20for%20IoT-Based%20Urban%20Emergency%20Systems%20Through%20Semantic%20Priority%20Override.md) | Core-related; closest | Semantic alarm scheduling, strict bands, device/source fairness and overload admission protection. Within-band fairness is not routine cross-band protection; admission and metadata must be aligned. |
| 04 | [Real-Time Priority Queue Scheduling for Bursty Traffic](reviews/Real-Time%20Priority%20Queue%20Scheduling%20for%20Bursty%20Traffic.md) | Core-related; closest | Priority and instantaneous queue congestion explicitly drive burst-aware service selection. Switch queues and learned transition/index model, not directly equivalent to a single event worker. |
| 05 | [Scheduling for Periodic Multi-Source Systems with Peak-Age Violation Guarantees](reviews/Scheduling%20for%20Periodic%20Multi-Source%20Systems%20with%20Peak-Age%20Violation%20Guarantees.md) | Supporting only | Useful freshness/threshold and queue-management theory. Periodic peak-AoI objective, not urgency-class deadline or emergency-alert tradeoff. Do not treat as a direct comparator. |
| 06 | [Adaptive Priority Scheduling of Internet of Things Data for Disaster Management in Smart Cities](reviews/Adaptive%20Priority%20Scheduling%20of%20Internet%20of%20Things%20Data%20for%20Disaster%20Management%20in%20Smart%20Cities.md) | Core-related; closest | Adaptive urgency/deadline-progress scheduling explicitly protects less urgent traffic in disaster IoT. Multi-hop routing/migration, preemption and infinite buffers complicate comparison; still core conceptual prior art. |
| 07 | [Online age of information scheduling: The power of packet management and fairness](reviews/Online%20age%20of%20information%20scheduling%20-%20The%20power%20of%20packet%20management%20and%20fairness.md) | Supporting only | Useful online fairness, starvation counterexamples and packet-management theory. Total AoI and replaceable status updates differ from non-replaceable emergency alerts. |
| 08 | [A Cloud-Edge-End Collaborative Remote Monitoring and Scheduling System for Textile Equipment](reviews/A%20Cloud-Edge-End%20Collaborative%20Remote%20Monitoring%20and%20Scheduling%20System%20for%20Textile%20Equipment.md) | Supporting only | Industrial alert-pipeline architecture, compute coordination and component ablation. Composite sensing/filtering/diagnosis/routing/placement study; not a queue-only urgency/routine policy comparison. |
| 09 | [IoT-based smart waste management system: real-time monitoring and environmental compensation](reviews/IoT-based%20smart%20waste%20management%20system%20-%20real-time%20monitoring%20and%20environmental%20compensation.md) | Excluded: unrelated | Sensor threshold/rain-state monitoring with no service scheduling or class tradeoff. IoT and cloud dashboard alone do not meet this research scope. |

### Closest papers to study first

1. **Review 03 / R08 TRIAGE/4:** strongest conceptual alarm/fairness/admission overlap; compare semantic inputs and class/device fairness carefully.
2. **Review 04 / R09 bursty queue scheduling:** strongest congestion/priority overlap; learned switch queues need model/information alignment.
3. **Review 06 / R11 adaptive disaster scheduling:** closely relevant deadline/urgency protection, but queue/routing/migration effects must be separated.
4. **Review 01 / R01 PrioMQTT:** direct priority-message prior art; transport confounds numerical comparisons.
5. **Review 02 / R02 priority-enabled MQTT:** relevant emergency-class architecture; limited evaluation strength.

These are reading priorities, not publication rankings or a chosen algorithm.

### Supporting papers: limited use

- **Review 05 / R10 periodic GRR:** freshness violation theory. Retain only for explaining why peak AoI is different from distinct-event deadlines.
- **Review 07 / R12 online AoI:** fairness/worst-case reasoning and legal packet replacement. Do not transfer its total-AoI theorem to non-replaceable alarms.
- **Review 08 / R13 textile system:** industrial motivation, filtering/placement and evaluation boundaries. Composite gains do not establish a queue-only improvement.

These may support an introduction, metric definition or limitations discussion; they do not fill missing closest-method coverage.

### Excluded paper

**Review 09 / R14 smart waste monitoring:** no scheduling/admission service policy for competing event classes, no deadline/fairness or burst scheduling evaluation. Keep its existing assessment only to avoid repeated screening. Do not spend further detailed-review effort on it or include it to inflate the target.

## Catalog entries not yet confirmed by full text

| Internal key | Candidate title | Status and next check |
| --- | --- | --- |
| R03 | PR-MQTT: a novel approach for traffic reduction and message prioritisation in IoT applications | Pending full-text screening; inspect actual scheduling/model/evaluation before inclusion. |
| R04 | Towards Integrating MQTT with Time-Sensitive Networking | Pending full-text screening; inspect actual scheduling/model/evaluation before inclusion. |
| R05 | Extending MQTT with Real-Time Communication Services Based on SDN | Pending full-text screening; inspect actual scheduling/model/evaluation before inclusion. |
| R06 | Response Time Analysis for RT-MQTT Protocol Grounded on SDN | Pending full-text screening; inspect actual scheduling/model/evaluation before inclusion. |
| R07 | Modification of Mosquitto Broker for Delivery of Urgent MQTT Message | Pending full-text screening; inspect actual scheduling/model/evaluation before inclusion. |

These are not newly recommended/verified publications in this audit. Existing complete metadata and DOI identity are retained in [references.json](references.json), with their reading-status limits. A title suggesting priority or real time is only a screening lead.

## Next collection rule

Prioritize full texts on deadline-aware/aging/queue-state scheduling, urgent-versus-routine service and overload/admission tradeoffs. Do not select only papers favorable to a previous prototype. Retain adverse results and mismatched-but-close methods with explicit scope limits.

Screen first. If unrelated, explain the short exclusion reason rather than producing another long review. No implementation, source-PDF redistribution, deletion of reviews or new experiments are part of this audit.
