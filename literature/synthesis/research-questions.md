# Research questions for the conference study

**Decision:** version 1.0, 16 November 2026. Finalize **one main question and three supporting sub-questions** within the former RQ-A direction. Admission/outage control and label robustness are parked. This freezes the question and initial system boundary; it does not certify novelty, select a new algorithm, or make the project submission-ready.

**Evidence base:** the 19 retained review notes, their [comparison matrix](comparison.csv), [synthesis](findings.md), and targeted primary-source checks. This session cross-checks existing reviews; it is not a fresh full-PDF review or independent replication of all 19 papers. Newly screened leads are not counted as completed reviews.

**বাংলা সারকথা:** জরুরি alert-এর deadline failure গ্রহণযোগ্য সীমার মধ্যে রেখে routine কাজকে কতটা সময়মতো service দেওয়া সম্ভব—কখন সম্ভব, কোন mechanism ফল বদলায়, আর বাস্তব তথ্য ও overhead ধরলে ফল কতটা টেকে। এটি একটি conference study; তিনটি আলাদা project নয়।

## 1. Main research question

> At a finite-capacity, non-preemptive IoT processing bottleneck, under what burst and service-demand conditions can an online scheduler improve routine access within a declared waiting budget while keeping the offered urgent-job deadline-failure rate within a predeclared acceptable budget?

**Routine access** means starting service within a waiting budget, not completing by that time. **Urgent failure** includes urgent work rejected at the declared bottleneck. “Improve” requires comparison with explicit conventional policies under matched resources and information; it is not a promised result.

**Working title:** *Routine-Service Protection Under Bursty IoT Alerts: Deadline Trade-offs and Practical Limits*.

This is an explanatory performance study first. A new method is justified only if an important limitation remains after checking established methods and theory.

## 2. Three sub-questions

### RQ1 — Operating conditions and limits

> How do burst structure and service-demand variability change the routine-access versus urgent-deadline-failure trade-off, and which capacity or non-preemptive blocking conditions explain failure to meet both declared service targets?

**Purpose:** identify when routine protection is useful, costly or infeasible under explicit assumptions.

**Evidence needed later:** controlled workload comparisons, a trade-off frontier for the evaluated policy family, and an explanation tied to offered service work, burst timing and blocking.

**Falsification and limits:** revise an explanation that fails outside its calibration cases. Failure of every tested policy does not prove that no possible policy could succeed. A frontier obtained from tested policies is empirical; universal impossibility or delay guarantees require applicable proofs. A familiar capacity/blocking observation alone is not an original contribution.

### RQ2 — Mechanism and comparison

> Under matched admission rules, resources and runtime information, how do count-based and consumed-work-based routine protection compare with established urgency-, deadline- and fair-service policies, and what explains any difference?

**Purpose:** determine whether a result comes from service accounting or another changed control.

**Evidence needed later:** a controlled count/work comparison, strong conventional comparators, comparable tuning effort and complete offered-population outcomes.

**Falsification and limits:** count/work comparison is diagnostic, not the novelty claim. Reject a useful-new-mechanism claim if a conventional comparator matches or dominates it at the same urgent-failure budget and comparable cost. Matching admission rules does not force identical admitted populations: dispatch changes occupancy and which arrivals encounter a full queue. Label adaptations honestly.

### RQ3 — Available information and cost

> How much of any observed benefit survives when exact service times of unstarted jobs and future arrivals are unavailable, after accounting for service-time estimation error where estimates are used and for measured scheduling/accounting overhead?

**Purpose:** determine whether the answer is usable with information the queue can obtain.

**Evidence needed later:** declare each policy's observations; distinguish measured past service from predicted future service; examine estimation error when relevant; measure decision cost in a reproducible execution environment.

**Falsification and limits:** restrict or withdraw a practical claim that needs oracle durations, favorable-only error cases, extra capacity or uncharged overhead. Completed-job accounting does not reveal unstarted-job duration; bytes are not automatically processing time. Prediction is optional and no learning model is selected. Synthetic independent noise alone is not realistic prediction evidence.

The three sub-questions answer **when**, **why**, and **whether the result survives practical constraints**. They share one model and outcome definition; they do not require three new algorithms.

## 3. Initial scope

| Dimension | Decision |
| --- | --- |
| Location | One local IoT application-processing bottleneck; distinguish broker transmission, radio access and downstream pipelines |
| Server | One fixed-capacity worker; jobs run to completion once started, without preemption |
| Population | Two trusted classes: urgent alerts and routine work; label generation is external |
| Capacity | A finite number of waiting jobs, plus the one job in service; fix the capacity before evaluation and report workload/memory separately |
| Offered boundary | Every job presented for admission to this bottleneck, including rejected jobs; local arrival-to-completion is not source-to-actuator latency |
| Admission | Same class-neutral full-queue rejection rule across primary dispatch comparisons; no suppression, push-out, upstream reservoir or cloud service |
| Workload | Bursts and variable service demand; measure offered work as well as counts; isolate size variability at fixed mean offered work where appropriate |
| Information | Class, arrival/deadline metadata, current queues and measured past service; estimates only when declared and equally available |
| Scheduling | Online decisions; no future-arrival oracle. Specify within-class order, ties and expiry before implementation |
| Parked extensions | Outages, wrong urgency labels, adversarial floods, routing, migration, task splitting and multi-worker placement |

The application must justify a processing bottleneck and its service requirements. Changing the layer does not establish novelty. Application choice, workload provenance, deadline values and routine requirements still need evidence.

## 4. Outcomes and decision rule

Let `a_i` denote arrival at the stated admission boundary, `s_i` service start, `c_i` completion, and `d_i` an urgent job's absolute deadline.

| Quantity | Definition | Interpretation |
| --- | --- | --- |
| `U`: urgent offered-job failure | `1 - N_urgent_completed_by_deadline / N_urgent_offered` | Rejection, expiry and late completion cannot disappear from the denominator |
| `R(tau)`: routine timely access | `N_routine_started_by_(arrival+tau) / N_routine_offered` | Rejected and not-yet-started work do not count as timely access |
| Routine wait and completion | Arrival-to-start distribution, completed fraction, and arrival-to-completion where observable | Disclose conditional denominators and unresolved work; starting is not completing |
| Count/work allocation | Starts/completions and measured consumed service by class | Equal counts, busy time and waiting are different objectives |
| Lifecycle | `offered = rejected + admitted`; `admitted = completed + expired/cancelled + unfinished` | Use disjoint categories; split urgent completions into on-time and late |
| Cost | Decision/accounting time, memory and any estimation/training cost | Measure actual cost; simulator execution time is not deployment scheduling overhead |

The application must justify an urgent-failure budget `epsilon`, routine waiting budget `tau`, and target routine-access fraction `gamma`. No values are invented here. Set these before held-out evaluation; sensitivity sweeps cannot retrospectively define acceptability.

A primary success claim requires `U <= epsilon` and `R(tau) >= gamma` under declared conditions. An improvement claim also needs comparison at the same urgent-failure budget, uncertainty and a practically meaningful effect. `epsilon` is an absolute requirement, not merely “a little worse than strict priority.”

Follow urgent arrivals through their deadlines and routine arrivals through their waiting budgets, or mark unresolved outcomes as censored. Ending a run is not a failure event. Report rejected/unfinished work alongside conditional quantiles.

Use matched offered traces across policies and independent run/trace repetitions for uncertainty. Requests or windows within one run are not independent repetitions. Separate tuning and held-out evaluation; report adverse/no-benefit regimes. Finite-run maxima or zero observed failures are not universal guarantees.

## 5. Literature cross-check and novelty boundary

Section 8 gives complete retained citations. These rows cover all 19 active reviews; source locations and qualifications remain in their review notes.

| Retained sources | Existing coverage | Consequence |
| --- | --- | --- |
| R01, R02 | MQTT/emergency priority and prototype messaging | Priority alone is insufficient; align transport and timing |
| R08, R09, R11 | Semantic alarms, burst/congestion-aware priority, adaptive deadline/routing controls | Recognize urgency in comparators; separate training, admission and migration |
| R15, R17, R24 | Source back-off, selective forwarding and radio activity | Lower offered work can explain delay; align populations/resources |
| R16, R18, R19, R22 | Routine opportunities, timeout feedback, batching and historical fairness | Routine protection already exists; clarify accounting, preemption and downstream effects |
| R20, R21, R23 | Size-sensitive service, deadline/miss-history feedback and placement/resource control | Size, age, deadlines or load in a score are insufficient novelty |
| R25, R26, R27, R28 | Burst/rate trade-offs, finite admission, partial-quality service and internal-buffer guarantees | Report routine costs, offered failures and storage/acceptance boundaries; retain theorem assumptions |

### Additional primary-source checks

| Lead | Evidence and reading level | Consequence |
| --- | --- | --- |
| G01: Lenzini et al., 2004 | Official IEEE identity/abstract and Pisa author record checked; full-text review pending | DRR latency/fairness trade-offs already exist; a count-to-work change is insufficient |
| G03: Tabatabaee and Le Boudec, RTAS 2021 | EPFL proceedings PDF, pp. 171-172: introduction, assumptions, Algorithm 1 and packet-to-job mapping inspected; complete proof review pending | Variable-size service and real-time jobs are explicitly covered. Compare size eligibility and arrival/service envelopes rather than dismissing this as packet-only theory |
| G04: Dell'Amico et al., 2016 | EURECOM journal identity and author-hosted submission, Sections 1, 3 and 4 inspected; complete review pending | Estimated sizes, fairness and error sensitivity already have prior art. Preemption is a comparison boundary, not proof of a gap |

**Assessment:** this direction is relevant and testable; field-wide novelty is **not established**. G03 is especially close. G04 prevents replacing a weak count/work claim with generic prediction-error sensitivity. These are bounded checks, not exhaustive searches or independent proof validation. G01/G03/G04 remain outside the 19 completed active reviews.

The earlier TSN admission lead for B remains in the [search log](../search-log.csv). B is parked; C is deferred because credible label ground truth/error mechanisms are unresolved. Neither is an additional conference question.

### Contribution objective and stop rule

Seek **one original explanatory result**: a useful characterization of when routine service can be protected at an explicit urgent-failure budget, beyond applicable existing theory and faithful conventional policies. A justified mechanism may follow if needed.

Reject or reframe the intended novelty claim if existing theory supplies the same result under matching assumptions; if the result merely restates count/work differences, familiar blocking limits or generic estimate sensitivity; or if a gain disappears with strong conventional comparators, equal information/resources or complete rejection accounting. Do not choose workloads or acceptability targets after seeing winners.

An honest negative result guides the project; it is not automatically a conference contribution. Archived code is not a reason to preserve an unsupported method.

## 6. What is finalized and what remains

| Item | Status |
| --- | --- |
| Main question and RQ1-RQ3 | Finalized for this research stage |
| Direction and initial boundary | Former RQ-A; scoped above |
| Application and numeric service budgets | Pending evidence |
| Exact original contribution | Pending closest-theory comparison |
| Algorithm/comparator specifications | Not selected |
| Full analytical/evaluation protocol | Pending requirements and novelty decision |
| Target conference and venue fit | Not selected |
| Best Paper outcome | An ambition, not a predicted or guaranteed outcome |

The reviewer judgment is that this direction permits clearer causal comparisons with fewer unsupported models than adding outage control or a new classifier now. It is not an estimated award probability.

## 7. Next action before implementation

1. Complete G01/G03's closest-theory review, and G04 where estimates matter; trace relevant deadline/fair-queue successors. State precisely when existing results do or do not answer the question.
2. Choose one credible processing application and obtain measurements or a justified trace source. Explain its deadlines, `epsilon`, `tau` and `gamma`.
3. If a meaningful contribution survives, specify the smallest fair protocol answering RQ1-RQ3, including comparator fidelity, lifecycle, tuning and uncertainty.
4. Begin implementation after those decisions. Additional papers should resolve a concrete coverage gap; reaching 20-25 is not itself readiness.

Revise this decision if contrary evidence requires it. “Finalized” means the current question and scope, not immunity to evidence.

## 8. References and provenance

Retained records inherit the identity, version and verification qualifications in their reviews and [metadata](../references.json). This session does not newly verify every old publication record. No indexing, quartile or ranking is inferred.

- **R01.** Gaetano Patti; Luca Leonardi; Giuseppe Testa; Lucia Lo Bello. 2024. **PrioMQTT: A prioritized version of the MQTT protocol**. *Computer Communications, 220, 43-51*. Elsevier. DOI: [10.1016/j.comcom.2024.03.018](https://doi.org/10.1016/j.comcom.2024.03.018). [Review](../reviews/PrioMQTT%20-%20A%20prioritized%20version%20of%20the%20MQTT%20protocol.md).

- **R02.** P S Akshatha; S Divyashree; S M Dilip Kumar. 2024. **Priority-enabled MQTT: a robust approach to emergency event messaging**. *Journal of Engineering and Applied Science, 71, article 67*. Springer Nature. DOI: [10.1186/s44147-024-00400-2](https://doi.org/10.1186/s44147-024-00400-2). [Review](../reviews/Priority-enabled%20MQTT%20-%20a%20robust%20approach%20to%20emergency%20event%20messaging.md).

- **R08.** João Carlos N. Bittencourt; Paulo Portugal; Francisco Vasques; Daniel G. Costa. 2026. **Multi-Tier Message Scheduling for IoT-Based Urban Emergency Systems Through Semantic Priority Override**. *IEEE Access, 14, 140988-141015*. IEEE. DOI: [10.1109/ACCESS.2026.3732592](https://doi.org/10.1109/ACCESS.2026.3732592). [Review](../reviews/Multi-Tier%20Message%20Scheduling%20for%20IoT-Based%20Urban%20Emergency%20Systems%20Through%20Semantic%20Priority%20Override.md).

- **R09.** Rongping Lin; Jinpeng Zhang; Shan Luo; Jing Fu; Xiong Wang; Hui Li; Moshe Zukerman. 2025. **Real-Time Priority Queue Scheduling for Bursty Traffic**. *IEEE Internet of Things Journal, 12(24), 55883-55892*. IEEE. DOI: [10.1109/JIOT.2025.3627212](https://doi.org/10.1109/JIOT.2025.3627212). [Review](../reviews/Real-Time%20Priority%20Queue%20Scheduling%20for%20Bursty%20Traffic.md).

- **R11.** Marie C. Pognon; Alejandro Quintero; Samuel Pierre. 2024. **Adaptive Priority Scheduling of Internet of Things Data for Disaster Management in Smart Cities**. *IEEE Access, 12, beginning p. 83285 (end pagination not established in retained review)*. IEEE. DOI: [10.1109/ACCESS.2024.3407672](https://doi.org/10.1109/ACCESS.2024.3407672). [Review](../reviews/Adaptive%20Priority%20Scheduling%20of%20Internet%20of%20Things%20Data%20for%20Disaster%20Management%20in%20Smart%20Cities.md).

- **R15.** Marwa O Al Enany; Hany M. Harb; Gamal Attiya. 2021. **A New Back-off Algorithm with Priority Scheduling for MQTT Protocol and IoT Protocols**. *International Journal of Advanced Computer Science and Applications (IJACSA), 12(11), 349-357*. The Science and Information Organization. DOI: [10.14569/IJACSA.2021.0121140](https://doi.org/10.14569/IJACSA.2021.0121140). [Review](../reviews/A%20New%20Back-off%20Algorithm%20with%20Priority%20Scheduling%20for%20MQTT%20Protocol%20and%20IoT%20Protocols.md).

- **R16.** Sehrish Malik; Shabir Ahmad; Israr Ullah; Dong Hwan Park; DoHyeun Kim. 2019. **An Adaptive Emergency First Intelligent Scheduling Algorithm for Efficient Task Management and Scheduling in Hybrid of Hard Real-Time and Soft Real-Time Embedded IoT Systems**. *Sustainability, 11(8), article 2192*. MDPI. DOI: [10.3390/su11082192](https://doi.org/10.3390/su11082192). [Review](../reviews/An%20Adaptive%20Emergency%20First%20Intelligent%20Scheduling%20Algorithm%20for%20Efficient%20Task%20Management%20and%20Scheduling%20in%20Hybrid%20of%20Hard%20Real-Time%20and%20Soft%20Real-Time%20Embedded%20IoT%20Systems.md).

- **R17.** Jiby J. Puthiyidam; Shelbi Joseph. 2024. **PR-MQTT: a novel approach for traffic reduction and message prioritisation in IoT applications**. *International Journal of Web Engineering and Technology, 19(1), 44-66*. Inderscience Enterprises Ltd. DOI: [10.1504/IJWET.2024.138096](https://doi.org/10.1504/IJWET.2024.138096). [Review](../reviews/PR-MQTT%20-%20a%20novel%20approach%20for%20traffic%20reduction%20and%20message%20prioritisation%20in%20IoT%20applications.md).

- **R18.** Dejian Chen; Dong Li; Renchun Guo. 2022. **Design of topic priority based on industrial publish-subscribe system**. *Frontiers in Energy Research, 10, article 979174*. Frontiers Media SA. DOI: [10.3389/fenrg.2022.979174](https://doi.org/10.3389/fenrg.2022.979174). [Review](../reviews/Design%20of%20topic%20priority%20based%20on%20industrial%20publish-subscribe%20system.md).

- **R19.** Faiza Akram; Peng Kang; Palden Lama; Samee U. Khan. 2024. **Data-Priority Aware Fair Task Scheduling for Stream Processing at the Edge**. *2024 IEEE Cloud Summit, 117-122*. IEEE. DOI: [10.1109/Cloud-Summit61220.2024.00026](https://doi.org/10.1109/Cloud-Summit61220.2024.00026). [Review](../reviews/Data-Priority%20Aware%20Fair%20Task%20Scheduling%20for%20Stream%20Processing%20at%20the%20Edge.md).

- **R20.** Barbara Kabwiga Asingwire; Louis Sibomana; Alexander Ngenzi; Charles Kabiri. 2023. **Delay and size-dependent priority-aware scheduling for IoT-based healthcare traffic using heterogeneous multi-server priority queueing system**. *IET Communications, 17(16), 1877-1887*. John Wiley & Sons Ltd on behalf of The Institution of Engineering and Technology. DOI: [10.1049/cmu2.12675](https://doi.org/10.1049/cmu2.12675). [Review](../reviews/Delay%20and%20size-dependent%20priority-aware%20scheduling%20for%20IoT-based%20healthcare%20traffic%20using%20heterogeneous%20multi-server%20priority%20queueing%20system.md).

- **R21.** Bo Shen; Naveen Chilamkurti; Ru Wang; Xingshe Zhou; Shiwei Wang; Wen Ji. 2018. **Deadline-aware rate allocation for IoT services in data center network**. *Journal of Parallel and Distributed Computing, 118, 296-306*. Elsevier Inc. DOI: [10.1016/j.jpdc.2017.09.012](https://doi.org/10.1016/j.jpdc.2017.09.012). [Review](../reviews/Deadline-aware%20rate%20allocation%20for%20IoT%20services%20in%20data%20center%20network.md).

- **R22.** Arkadiusz Madej; Nan Wang; Nikolaos Athanasopoulos; Rajiv Ranjan; Blesson Varghese. 2020. **Priority-based Fair Scheduling in Edge Computing**. *2020 IEEE 4th International Conference on Fog and Edge Computing (ICFEC), 39-48*. IEEE. DOI: [10.1109/ICFEC50348.2020.00012](https://doi.org/10.1109/ICFEC50348.2020.00012). [Review](../reviews/Priority-based%20Fair%20Scheduling%20in%20Edge%20Computing.md).

- **R23.** J. Anand; B. Karthikeyan. 2025. **Dynamic priority-based task scheduling and adaptive resource allocation algorithms for efficient edge computing in healthcare systems**. *Results in Engineering, 25, 104342*. Elsevier B.V. DOI: [10.1016/j.rineng.2025.104342](https://doi.org/10.1016/j.rineng.2025.104342). [Review](../reviews/Dynamic%20priority-based%20task%20scheduling%20and%20adaptive%20resource%20allocation%20algorithms%20for%20efficient%20edge%20computing%20in%20healthcare%20systems.md).

- **R24.** K. Kavitha; G. Suseendran. 2019. **Priority based Adaptive Scheduling Algorithm for IoT Sensor Systems**. *2019 International Conference on Automation, Computational and Technology Management (ICACTM), 361-366*. IEEE. DOI: [10.1109/ICACTM.2019.8776691](https://doi.org/10.1109/ICACTM.2019.8776691). [Review](../reviews/Priority%20based%20Adaptive%20Scheduling%20Algorithm%20for%20IoT%20Sensor%20Systems.md).

- **R25.** Mahmoud Daneshvar Farzanegan; Hossein Saidi; Mehdi Mahdavi. 2014. **An Approach to Scheduling Bursty Traffic**. *ETRI Journal, 36(1), 69-79*. Electronics and Telecommunications Research Institute (ETRI). DOI: [10.4218/etrij.14.0112.0524](https://doi.org/10.4218/etrij.14.0112.0524). [Review](../reviews/An%20Approach%20to%20Scheduling%20Bursty%20Traffic.md).

- **R26.** Shensheng Tang. 2026. **Reliability-Aware Admission Threshold Selection for IoT Gateway–Cloud Systems: Trade-Off-Driven and Constraint-Based Approaches**. *IoT, 7(3), 60*. MDPI. DOI: [10.3390/iot7030060](https://doi.org/10.3390/iot7030060). [Review](../reviews/Reliability-Aware%20Admission%20Threshold%20Selection%20for%20IoT%20Gateway-Cloud%20Systems%20-%20Trade-Off-Driven%20and%20Constraint-Based%20Approaches.md).

- **R27.** Minoo Hosseinzadeh; Andrew Wachal; Hana Khamfroush; Daniel E. Lucani. 2022. **QoS-Aware Priority-Based Task Offloading for Deep Learning Services at the Edge**. *2022 IEEE 19th Annual Consumer Communications & Networking Conference (CCNC), 319-325*. IEEE. DOI: [10.1109/CCNC49033.2022.9700676](https://doi.org/10.1109/CCNC49033.2022.9700676). [Review](../reviews/QoS-Aware%20Priority-Based%20Task%20Offloading%20for%20Deep%20Learning%20Services%20at%20the%20Edge.md).

- **R28.** Long Bao Le; Eytan Modiano; Ness B. Shroff. 2012. **Optimal Control of Wireless Networks With Finite Buffers**. *IEEE/ACM Transactions on Networking, 20(4), 1316-1329*. IEEE/ACM (published by IEEE). DOI: [10.1109/TNET.2011.2176140](https://doi.org/10.1109/TNET.2011.2176140). [Review](../reviews/Optimal%20Control%20of%20Wireless%20Networks%20With%20Finite%20Buffers.md).

### Targeted leads, not completed active reviews

- **G01.** Luciano Lenzini; Enzo Mingozzi; Giovanni Stea. 2004. **Tradeoffs between low complexity, low latency, and fairness with deficit round-robin schedulers**. *IEEE/ACM Transactions on Networking, 12(4), 681-693*. IEEE. DOI: [10.1109/TNET.2004.833131](https://doi.org/10.1109/TNET.2004.833131). [Official IEEE record](https://ieeexplore.ieee.org/document/1331430/) · [Pisa author record](https://arpi.unipi.it/handle/11568/202043). Identity/abstract checked; full-text review pending.

- **G03.** Seyed Mohammadhossein Tabatabaee; Jean-Yves Le Boudec. 2021. **Deficit Round-Robin: A Second Network Calculus Analysis**. *2021 IEEE 27th Real-Time and Embedded Technology and Applications Symposium (RTAS), 171-183*. IEEE. DOI: [10.1109/RTAS52030.2021.00022](https://doi.org/10.1109/RTAS52030.2021.00022). [EPFL-hosted proceedings PDF](https://infoscience.epfl.ch/bitstreams/e0172e0b-b99c-43cc-9488-31afda35f1fa/download) · [Official conference program](https://2021.rtas.org/program/index.html). The DOI appears on p. 171. Reading locations above refer to this conference version, not a later journal version or revised preprint. Complete proof review pending.

- **G04.** Matteo Dell'Amico; Damiano Carra; Pietro Michiardi. 2016. **PSBS: Practical Size-Based Scheduling**. *IEEE Transactions on Computers, 65(7), 2199-2212*. IEEE. DOI: [10.1109/TC.2015.2468225](https://doi.org/10.1109/TC.2015.2468225). [EURECOM journal record](https://www.eurecom.edu/en/publication/4449) · [Author-hosted submission](https://profs.sci.univr.it/~carra/downloads/carra_psbs.pdf). The author file is marked “under submission”; its sections are not journal pagination. EURECOM's DOI link resolves to IEEE article 7194777, whose direct retrieval was blocked. Complete review pending.

**Search provenance:** [executed queries and screening records](../search-log.csv). This is a focused review using a web search service, not a claimed Google Scholar/Scopus systematic search. Earlier three-candidate wording remains in [version 0.1 at the reviewed main snapshot](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/blob/5fe80d23c949cbe5fe0ef6d1691715aad93386a5/literature/synthesis/research-questions.md).

[Review register](../README.md) · [Comparison](comparison.csv) · [Synthesis](findings.md)
