# Design of topic priority based on industrial publish-subscribe system

## 1. Bibliographic record and source

**Review number:** 09 · **Internal reference key:** R18

Dejian Chen; Dong Li; Renchun Guo. 2022. **Design of topic priority based on industrial publish-subscribe system**. *Frontiers in Energy Research, 10, article 979174*. Frontiers Media SA. DOI: [10.3389/fenrg.2022.979174](https://doi.org/10.3389/fenrg.2022.979174).

- **Identity verification:** supplied title page and the [official publisher article](https://www.frontiersin.org/journals/energy-research/articles/10.3389/fenrg.2022.979174/full) checked on 15 November 2026.
- **Reviewed version:** supplied published PDF, 10 pages; PDF pages equal printed 01-10.
- **Source fingerprint (SHA-256):** `fbfcdc6fb20af85420e0e874179c3cd27a2d09fc7a801ec6686b1310f41dec00`.
- **Reading status:** full text reviewed; method/plots on pp. 5-8 visually checked; no independent replication or verification of claimed guarantees.
- **Selection:** core-related MQTT topic scheduling, emergency override and low-priority feedback. Microgrid framing does not make this unrelated: the actual intervention acts on messaging. Quartile/indexing status is not independently verified here.

## 2. Research problem

How can an MQTT server distribute important/popular topics under port congestion without leaving low-priority subscribers waiting indefinitely?

The proposed policy gives more highly subscribed topics precedence, allows emergency messages to override ordinary ranking and periodically adjusts service for delayed low-priority topics. This directly overlaps our urgent/routine overload and starvation questions.

## 3. Authors' claimed contribution

The authors combine topic-hotness ranking with time-period feedback and adjustable low-priority distribution frequency. They claim lower priority-topic delay, improved low-priority delivery and stable microgrid data communication.

The experiments show selected priority/delay trends. Statements about guaranteed delivery, minimal effect on urgent traffic or system stability are not equivalent to formal bounds established under an explicit arrival/service model.

## 4. Model and assumptions

- MQTT over TCP/IP, QoS 0, with publishers/subscribers exchanging topics through a central server (pp. 3-4).
- Hotness is described through subscription counts and, in places, topic exchange frequency. The prioritization algorithm counts subscriptions and sorts topic counts (p. 6). It is not simply publisher-rate ranking.
- Emergency indicator U is available for an override above the ordinary maximum priority (p. 5). The emergency classifier/authentication procedure is not fully specified.
- Topic hierarchy depth breaks equal priority in favor of shallower topics, according to prose (p. 5).
- Subscribers supply timeout/service needs and can request service after a prolonged lack of data. The server adjusts feedback period/distribution frequency (pp. 6-7).
- The experimental setup says Windows and an “IEDA compiler” but does not identify a reproducible full hardware/broker/version/workload configuration (p. 7).
- Queue limits, per-message service requirements, exact resource budgets, drop rules and the extent of execution/transmission preemption remain unclear. Do not infer CPU-task preemption from the word “preempt.”
- Broad claims about packet loss and industrial grid benefits are not accompanied by a grid-control/energy outcome evaluation in the reported figures.

## 5. Method and decision mechanism

**Collect subscriptions -> count and rank topics -> urgent override / depth tie-break -> distribute -> feedback for delayed low-priority topics.**

The process on p. 4 prioritizes topics under congestion and introduces periodic low-priority opportunities. On p. 5 the server distributes larger numeric priorities first. A message marked U is assigned above the ordinary maximum without counting. A stated congestion indicator is waiting time divided by unblocked receive delay > 0.5; it should not be confused with the normalized delay metric in the later plots.

The prioritization pseudocode on p. 6 counts topic subscriptions, sorts counts and restarts a collection period when additional subscriptions arrive. Repeated restart behavior needs clarification under a continuous stream of subscriptions.

The low-priority feedback pseudocode tests WT == DT, while its comment says waiting is approaching timeout. It adjusts a time period and sends low-priority data. Remaining low-priority work runs after high-priority work ends. Section text on p. 7 increases a delayed topic's distribution frequency without changing its base priority sequence.

**Reproduction questions:** exact period scheduling/budget, timeout trigger, equality versus threshold crossing, frequency update rule, tie-breaking among delayed topics and conflicts between emergency and feedback service are underspecified. The topic-depth equation on p. 5 literally compares d_i with itself; the prose suggests d_i versus d_j. Record that as a specification error, rather than silently fixing it and claiming a faithful implementation.

## 6. Evidence ledger

All observations are author-reported. Figures were visually checked; no precise values are digitized here.

| Claim examined | Source location | Actual evidence | Interpretation boundary |
| --- | --- | --- | --- |
| Priority reduces congestion delay | Experiment 1, Fig. 2, p. 7 | High-priority completion-time curve is below no-priority and attribute-taxonomy curves over the displayed 100/500/1,000 interaction points. | High-priority/interaction completion view, not urgent per-message p99, deadline failure or all-class service quality. Axis does not establish a portable per-message latency unit. |
| Feedback-period tradeoff | Experiment 2, Fig. 3, p. 8 | Feedback periods of 1, 2 and 3 seconds produce different completion-time curves; text favors longer periods for high-priority service but warns about low-priority timeout. | Parameter sensitivity in the pictured setup. It does not establish that feedback has no urgent-traffic cost. |
| Low-priority frequency adjustment | Experiment 3, Figs. 4-5, p. 8 | Average-delay/normal-delay curves for subscription intervals of 0.5 s and 1 s remain above the unblocked ratio of 1 across the shown server periods. | Selected average normalized delays, not a worst-case waiting bound, proven stability result or starvation-free guarantee. “frequency1/2” are not sufficiently specified for replication. |
| Emergency override | Priority description, p. 5 | U is assigned above ordinary maximum priority. | Explicit overlap with emergency semantics exists, but no separately controlled emergency-burst experiment is provided in Figs. 2-5. |
| Evidence availability | Data availability statement, p. 9 | Authors state raw data will be made available on request. | This review did not obtain those data or reconstruct experiments from the plots. |

## 7. Critical appraisal

**Contribution and relevance.** This is close prior art for protecting delayed low-priority messages alongside priority/urgency scheduling. A claim that existing IoT messaging work ignores starvation protection would contradict this paper's explicit feedback mechanism.

**Clarity and reproducibility.** The intended mechanism is understandable at architecture level; important update rules are not executable as written. The d_i < d_i typo, WT == DT trigger and inconsistent use of hotness terms require resolution. Popularity weighting may reward fan-out while urgency is a separate override; these objectives should not be conflated.

**Internal validity.** Baseline “attribute taxonomy” and matched offered traffic, payloads, resource capacity and timer costs are not specified sufficiently. Feedback changes distribution opportunities/frequency as well as priority outcomes. Short completion/ratio plots do not identify an isolated scheduling-order effect under equal resources.

**Construct and statistical validity.** Average normalized delay, timeout prevention and starvation are different outcomes. An assertion that one topic's higher priority implies strictly lower delay for every pair is not a general theorem without arrival/service conditions. No seed-level uncertainty, long-run maximum waiting analysis or tail/deadline distributions are provided.

**External validity.** The microgrid motivation is strong, but experiments do not establish closed-loop power-system safety or a deployed industrial effect. A single Windows development environment cannot support unrestricted scale/reliability claims.

**What would strengthen confidence:** a fully specified scheduler and control budgets; raw workloads/configurations; matched baseline controls; repeated long-run overload and urgent-burst tests; separate urgent and routine waiting/failure outcomes; and a proof or scoped bound if starvation freedom is claimed.

## 8. Synthesis contribution and open question

Compare with [semantic alarm scheduling](Multi-Tier%20Message%20Scheduling%20for%20IoT-Based%20Urban%20Emergency%20Systems%20Through%20Semantic%20Priority%20Override.md): both recognize urgency beyond the ordinary base rank, but this paper explicitly adds low-priority timeout/frequency feedback rather than principally within-band source fairness.

[PR-MQTT](PR-MQTT%20-%20a%20novel%20approach%20for%20traffic%20reduction%20and%20message%20prioritisation%20in%20IoT%20applications.md) discusses this topic-priority work in its related literature. That citation is context, not independent validation of this mechanism's performance.

**Question for further reading:** Under a fixed service budget, how do periodic routine-service opportunities and timeout/frequency feedback trade urgent failures against maximum routine waiting during sustained overload?

A field-wide answer requires more close literature. No algorithm, baseline implementation or simulation protocol is selected.

<details>
<summary>বাংলা reading note</summary>

Energy journal হলেও paperটি সরাসরি message scheduling নিয়ে। বেশি subscribed topic আগে চলে, emergency override আছে, আর low-priority message অনেকক্ষণ অপেক্ষা করলে feedback দিয়ে service দেয়। তাই priority + low-priority protection নতুন ধারণা নয়। তবে feedback-এর exact rule ও waiting guarantee যথেষ্ট স্পষ্ট নয়।

</details>

Return to the [review register](../README.md) or [cross-paper comparison](../synthesis/comparison.csv).
