# Synthesis of the nineteen core papers

This active synthesis uses the retained full-text reviews. It is a focused literature assessment, not an exhaustive SLR or full independent replication. R15-R28 were checked against supplied full texts and official publisher identities (R16/R19/R21/R23/R24 use indexed official metadata where direct HTML retrieval was blocked or rate-limited; R22 also matches institutional proceedings records and reviews a separately identified arXiv v1); the earlier five reviews retain their verification provenance. R25 also matches indexed publisher identity; R27 matches Kentucky/NSF records and R28 matches the MIT-hosted journal publication and institutional author lists. R26 includes a limited independent baseline stationary calculation, not a replication of all figures. Review numbers are navigation; internal reference keys remain stable.

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

## Historical class fairness differs from per-job routine protection

[EFS](../reviews/Priority-based%20Fair%20Scheduling%20in%20Edge%20Computing.md) combines historical class shares with least-served-client selection. In its equal-profile window, client-only fairness leaves the highest class unserved, whereas priority-only fairness leaves some clients unserved. The Hybrid combines both, but count-based allocation under similar synthetic runtimes does not establish equal CPU service, a routine waiting bound or hard urgent deadlines. Formal asymptotic fairness proofs are explicitly future work.

This paper belongs among the closest readings, alongside FTS-Hybrid. Their accounting differs: cumulative job history versus emission batches/queue lengths. EFS also measures about 2.8 seconds of Hybrid decision overhead at a million history rows on its board; the paper's minutes-between-dispatch context cannot be transferred to millisecond alerts. The printed Hybrid class/client intersection needs clarification before implementation.

## Urgency, normalized age and current load are already combined

[DPTARA](../reviews/Dynamic%20priority-based%20task%20scheduling%20and%20adaptive%20resource%20allocation%20algorithms%20for%20efficient%20edge%20computing%20in%20healthcare%20systems.md) scores original importance plus elapsed age/deadline minus assigned-resource load, alongside resource reclamation, routine splitting/offload and cloud fallback. This is close prior art against novelty based on that score combination alone.

Its author-reported gains concern a coupled resource framework, not isolated queue ordering. Score assignment/reordering, task/resource units, baseline identity and the all-overloaded path need clarification. Mean latency below a class tolerance does not certify each task's deadline or routine tail protection. Extra placement capacity and partial-task execution change the question compared with one constrained message queue.

## Radio activity control can change the work reaching a queue

[PASA](../reviews/Priority%20based%20Adaptive%20Scheduling%20Algorithm%20for%20IoT%20Sensor%20Systems.md) combines traffic-class slot scheduling and sensor sleep control. Its buffer signal is a priority/total-buffer/neighbor-density proxy, not measured current occupancy. Keep that distinction when comparing it with WTI queue-state feedback or MQTT source back-off.

The reported NS2 evidence concerns aggregate delivery, loss, energy and throughput. It does not establish class deadlines or routine maximum waiting. The two-flow throughput endpoint favors EE-CATS (0.29 versus PASA's 0.272 Mb/s), so a uniform superiority claim is unsupported. Priority, transmission opportunity and sleep control change together; population and energy accounting matter before interpreting downstream delay gains.

## Burst compensation is distinct from rate fairness and job waiting

[RBSS](../reviews/An%20Approach%20to%20Scheduling%20Bursty%20Traffic.md) already uses capped, ceiling-quantized queue-dependent weights in a fluid scheduler. It distinguishes rate-normalized service fairness from compensation for unused service when a burst appears. An infinite TCS for GPS means failure of that catch-up objective, not starvation or infinite packet delay.

Its Table 2 preserves a material contrary outcome: configuring both bursty flows in S4 reduces their mean delays from 510/1829 to 294/741 microseconds while raising the representative uniform flow from 125 to 542. Policing, traffic contracts, fluid packetization and proof conditions matter. This is strong prior art against novelty based solely on backlog-driven weight boosts, with limited numerical evidence beyond the illustrative example.

## Admission, internal overflow and offered-task success use different boundaries

[RAAC](../reviews/Reliability-Aware%20Admission%20Threshold%20Selection%20for%20IoT%20Gateway-Cloud%20Systems%20-%20Trade-Off-Driven%20and%20Constraint-Based%20Approaches.md) explicitly separates offered arrivals from admitted/completed work under finite buffering and Markovian service interruptions. Its moving-threshold congestion-regime probability is control activity, not congestion at a common physical queue level. A limited independent 84-state baseline calculation reproduces weighted threshold 15 and largest feasible threshold 18; it does not validate nonstationary bursts, deadlines or an online controller.

[Finite-buffer wireless network control](../reviews/Optimal%20Control%20of%20Wireless%20Networks%20With%20Finite%20Buffers.md) proves conditional internal no-overflow and utility/backlog results while source reservoirs remain unlimited. Source retention and immediate admission rejection are different loss/wait semantics. Internal occupancy bounds, stationary mean free space and per-job timely service are separate claims. The 2012 journal version must also be distinguished from its 2010 conference precursor.

Both studies sharpen the comparison boundary: report source-offered, admitted, retained upstream, intentionally rejected, eventually completed and timely completed work. The finite-buffer journal's underloaded results also show larger queues than its comparator in some settings; finite capacity does not guarantee every average delay improves.

## Partial-quality service changes the meaning of fewer drops

[PGUS](../reviews/QoS-Aware%20Priority-Based%20Task%20Offloading%20for%20Deep%20Learning%20Services%20at%20the%20Edge.md) performs priority-first server/model assignment, with a utility combining accuracy and preferred completion time. Its three outcomes are satisfied service, unsatisfied service and drop. GUS rejects unmet requirements whereas PGUS can serve unsatisfied tasks, so fewer drops alone do not demonstrate more deadline successes.

The small-instance ILP comparison reports roughly 80% of optimal GoS; that is an empirical observation, not an approximation theorem. Prototype feasibility does not remove the unlimited-cloud mathematical assumption, batching wait, stale metadata or acceptance-semantics differences. Compare these populations before attributing gains solely to urgency ranking.

## Questions to challenge with more core literature

| Candidate question | Why these papers motivate it | Evidence still needed |
| --- | --- | --- |
| Which methods balance urgent failures with routine tail waiting under bursts? | TRIAGE/4 fairness scope; FEF thresholds; topic feedback; FTS-Hybrid mix regressions; EFS class/client accounting; WTI tradeoff; RBSS regular-flow penalty | Close deadline/aging/fair-queue approaches, contrary results and matched objective definitions |
| How do source controls distinguish urgent bursts from rate anomalies? | R15 frequency proxy and startup-rate trust; TRIAGE/4 semantic labels and admission | Methods evaluating legitimate bursts, anomaly errors and class outcomes under matched offered load |
| Which mechanisms tolerate imperfect urgency/value classification? | PR-MQTT learned min/max and routine filtering; R15 rate proxy | Evidence on drift, initial-sample bias, false alarms, missed urgency and receiver freshness |
| Which latency improvements persist under equal transport, resources and offered populations? | PrioMQTT transport change; TRIAGE/4 admission; PR-MQTT suppression; disaster/DPTARA migration; PASA source activity | Comparable evaluations isolating the intervention and reporting loss; PGUS satisfied/unsatisfied distinctions |
| How do control location and service assumptions change routine protection? | FTS-Hybrid emission batches; non-preemptive healthcare servers; DRA divisible flows | Comparable offered-load outcomes, batch flush/downstream effects, finite buffers and preemption boundaries |
| Which guarantee survives the complete admission/storage boundary? | RAAC immediate rejection and stationary saturation; finite-buffer control with unlimited source reservoirs; PGUS partial-QoS service | Finite source storage, class-specific offered-task outcomes, transient recovery and explicit waiting/deadline definitions |
| When is model-training or adaptation cost justified? | WTI transition information; FEF ANN/history; EFS history-query cost; DPTARA forecast feedback | Workload-shift/model-error/overhead studies under comparable information budgets |

These are reading questions, not demonstrated field-wide gaps or selected contributions.

## Next step

Use the [candidate research-question decision note](research-questions.md) to compare three directions: service accounting under heterogeneous bursts, admission/dispatch interaction, and label robustness. RQ-A is the provisional first investigation, with a direct fair-queue/latency-theory overlap check still pending; no gap, algorithm or final protocol is selected.

The active set remains 19 completed reviews. The bounded [search log](../search-log.csv) records targeted novelty/identity checks; the two primary-source leads in the decision note are not counted as full-text reviews. Prioritize those closest checks and application-backed requirements before broad collection or implementation. The 20-25-paper working target is a coverage guide, not evidence of novelty or a mandatory count before synthesis.

The [previous synthesis](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/blob/938a07f828909bb2d8f31e271a0b479dd117f562/literature/synthesis/findings.md) remains accessible for historical context. Supporting/excluded material is not part of this active synthesis.

