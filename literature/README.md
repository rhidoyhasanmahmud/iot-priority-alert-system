# Core literature review

**19 completed, core-related reviews.** Target: approximately 20-25 relevant papers, with deep reading of the closest 5-8 methods. The number is a planning target, not proof of completeness.

## Review register

| No. | Paper | Year | Research use | Main comparison limit |
| --- | --- | ---: | --- | --- |
| 01 | [PrioMQTT: A prioritized version of the MQTT protocol](reviews/PrioMQTT%20-%20A%20prioritized%20version%20of%20the%20MQTT%20protocol.md) | 2024 | Time-critical MQTT priority | Transport changes alongside priority |
| 02 | [Priority-enabled MQTT: a robust approach to emergency event messaging](reviews/Priority-enabled%20MQTT%20-%20a%20robust%20approach%20to%20emergency%20event%20messaging.md) | 2024 | Emergency-message class handling | Small prototype and unclear timing endpoints |
| 03 | [Multi-Tier Message Scheduling for IoT-Based Urban Emergency Systems Through Semantic Priority Override](reviews/Multi-Tier%20Message%20Scheduling%20for%20IoT-Based%20Urban%20Emergency%20Systems%20Through%20Semantic%20Priority%20Override.md) | 2026 | Closest alarm/fairness/admission work | Within-band fairness and admission shaping differ from routine-class protection |
| 04 | [Real-Time Priority Queue Scheduling for Bursty Traffic](reviews/Real-Time%20Priority%20Queue%20Scheduling%20for%20Bursty%20Traffic.md) | 2025 | Closest burst/congestion-aware priority work | Switch queues require transition training/model alignment |
| 05 | [Adaptive Priority Scheduling of Internet of Things Data for Disaster Management in Smart Cities](reviews/Adaptive%20Priority%20Scheduling%20of%20Internet%20of%20Things%20Data%20for%20Disaster%20Management%20in%20Smart%20Cities.md) | 2024 | Closest adaptive urgency/deadline work | Multi-hop routing/migration and infinite buffers |
| 06 | [A New Back-off Algorithm with Priority Scheduling for MQTT Protocol and IoT Protocols](reviews/A%20New%20Back-off%20Algorithm%20with%20Priority%20Scheduling%20for%20MQTT%20Protocol%20and%20IoT%20Protocols.md) | 2021 | Broker-assigned frequency priority and source back-off | Weak measurements; frequency is not urgency; combined intervention |
| 07 | [An Adaptive Emergency First Intelligent Scheduling Algorithm for Efficient Task Management and Scheduling in Hybrid of Hard Real-Time and Soft Real-Time Embedded IoT Systems](reviews/An%20Adaptive%20Emergency%20First%20Intelligent%20Scheduling%20Algorithm%20for%20Efficient%20Task%20Management%20and%20Scheduling%20in%20Hybrid%20of%20Hard%20Real-Time%20and%20Soft%20Real-Time%20Embedded%20IoT%20Systems.md) | 2019 | Close urgency/deadline/starvation method | Preemptive CPU model; ANN detail and result-table inconsistencies |
| 08 | [PR-MQTT: a novel approach for traffic reduction and message prioritisation in IoT applications](reviews/PR-MQTT%20-%20a%20novel%20approach%20for%20traffic%20reduction%20and%20message%20prioritisation%20in%20IoT%20applications.md) | 2024 | Broker value-based priority and selective forwarding | Filtering changes delivered work; equation/example ambiguity |
| 09 | [Design of topic priority based on industrial publish-subscribe system](reviews/Design%20of%20topic%20priority%20based%20on%20industrial%20publish-subscribe%20system.md) | 2022 | Topic priority, emergency override and routine feedback | Underspecified feedback control; no formal waiting bound |
| 10 | [Data-Priority Aware Fair Task Scheduling for Stream Processing at the Edge](reviews/Data-Priority%20Aware%20Fair%20Task%20Scheduling%20for%20Stream%20Processing%20at%20the%20Edge.md) | 2024 | Closest stream-priority/fairness batching method | Mix-sensitive gains; batch/pipeline and pseudocode limits |
| 11 | [Delay and size-dependent priority-aware scheduling for IoT-based healthcare traffic using heterogeneous multi-server priority queueing system](reviews/Delay%20and%20size-dependent%20priority-aware%20scheduling%20for%20IoT-based%20healthcare%20traffic%20using%20heterogeneous%20multi-server%20priority%20queueing%20system.md) | 2023 | Delay/size priority with heterogeneous servers | Analytical evidence; infinite queues; simulation/quota future work |
| 12 | [Deadline-aware rate allocation for IoT services in data center network](reviews/Deadline-aware%20rate%20allocation%20for%20IoT%20services%20in%20data%20center%20network.md) | 2018 | Deadline plus historical-deprivation service feedback | Preemptible flows; link fairness; successful-only latency |
| 13 | [Priority-based Fair Scheduling in Edge Computing](reviews/Priority-based%20Fair%20Scheduling%20in%20Edge%20Computing.md) | 2020 | Closest historical class/client fairness method | Job-count shares; similar runtimes; Hybrid class/client intersection needs clarification |
| 14 | [Dynamic priority-based task scheduling and adaptive resource allocation algorithms for efficient edge computing in healthcare systems](reviews/Dynamic%20priority-based%20task%20scheduling%20and%20adaptive%20resource%20allocation%20algorithms%20for%20efficient%20edge%20computing%20in%20healthcare%20systems.md) | 2025 | Urgency, age/deadline and load with routine offloading | Coupled placement/resources; score ordering, units and overload path unclear |
| 15 | [Priority based Adaptive Scheduling Algorithm for IoT Sensor Systems](reviews/Priority%20based%20Adaptive%20Scheduling%20Algorithm%20for%20IoT%20Sensor%20Systems.md) | 2019 | Traffic-class slot scheduling and adaptive sensor sleep | MAC/source-control model; buffer proxy; no class deadline/tail evidence |
| 16 | [An Approach to Scheduling Bursty Traffic](reviews/An%20Approach%20to%20Scheduling%20Bursty%20Traffic.md) | 2014 | Foundational backlog-weighted burst/rate fairness | Fluid/policed flows; burst gains raise regular-flow delay; conditional proofs |
| 17 | [Reliability-Aware Admission Threshold Selection for IoT Gateway–Cloud Systems: Trade-Off-Driven and Constraint-Based Approaches](reviews/Reliability-Aware%20Admission%20Threshold%20Selection%20for%20IoT%20Gateway-Cloud%20Systems%20-%20Trade-Off-Driven%20and%20Constraint-Based%20Approaches.md) | 2026 | Finite-buffer admission under service interruptions | Stationary class-neutral model; moving congestion metric; no task deadlines |
| 18 | [QoS-Aware Priority-Based Task Offloading for Deep Learning Services at the Edge](reviews/QoS-Aware%20Priority-Based%20Task%20Offloading%20for%20Deep%20Learning%20Services%20at%20the%20Edge.md) | 2022 | Priority-aware assignment and partial-QoS admission | Unlimited cloud model; served-not-satisfied differs from successful timely service |
| 19 | [Optimal Control of Wireless Networks With Finite Buffers](reviews/Optimal%20Control%20of%20Wireless%20Networks%20With%20Finite%20Buffers.md) | 2012 | Foundational finite-buffer admission/routing control | Finite internal queues with unlimited source reservoirs; conditional utility/backlog bounds |

## Reading workflow

1. [Search and screen for scope relevance](search.md).
2. Read each paper's problem, method, assumptions and evaluation.
3. Write a [critical review](review-template.md) with source locations and limitations.
4. Update the [comparison matrix](synthesis/comparison.csv) and [synthesis](synthesis/findings.md).
5. Use the [finalized main question and three sub-questions](synthesis/research-questions.md), check overlap through [logged searches](search-log.csv), and establish the contribution before selecting a method.

[Reference metadata](references.json) contains exactly these nineteen active papers. Prior supporting/excluded notes and unreviewed catalog items are preserved in the [earlier Git snapshot](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/tree/938a07f828909bb2d8f31e271a0b479dd117f562/literature), outside the active list.

## File naming and order

Use the full paper title plus `.md`; replace unsafe punctuation such as a colon with a readable hyphen. Numbers belong in this register and metadata, not filenames. Use encoded destinations for Markdown links containing spaces. Retain internal reference keys/DOIs for identity; current visible serials are consecutive 01-19.

## Research boundary

The current research frame selects routine-service protection under an urgent deadline-failure budget, with one main question and three sub-questions. Novelty and application-backed requirements remain unresolved. No algorithm, comparator implementation or simulation matrix is selected. Core relevance is separate from evidence quality or baseline fidelity. Include contrary findings and close methods even when their resource model differs. Do not fill the target with generic IoT applications or loosely related theory.

