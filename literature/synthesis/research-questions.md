# Research questions and selected direction

**Status:** decision note, version 0.2, 15 November 2026. **RQ-A is selected as the research direction**, based on the 19 retained reviews and synthesis at main commit `5fe80d23c949cbe5fe0ef6d1691715aad93386a5`. B/C remain documented alternatives. The selection does not establish a literature gap, a new algorithm or a finalized experiment matrix.

**Selection:** pursue **RQ-A**; park **RQ-B** and defer **RQ-C**. This is a reviewer judgment about the clearest route to an important, testable contribution with the available project scope, not an estimated probability of winning an award. RQ-A offers a controlled urgent/routine trade-off question and a manageable first model. Its originality remains unresolved: classical fair queueing already handles variable work sizes, and the targeted search below found directly relevant fairness/latency theory. A useful contribution must go beyond comparing message counts with work counts or renaming an existing scheduler.

**বাংলা reading guide:** প্রথমে A/B/C-এর comparison ও recommendation পড়ুন। তারপর closest-paper table এবং প্রতিটি question-এর falsification condition দেখুন। এখানে কোনো algorithm-কে নতুন বা কোনো gap-কে confirmed বলা হয়নি।

## Selected question and contribution objective

> Under what burst and service-demand conditions can routine-service protection improve routine access within a declared waiting budget while keeping offered urgent-task deadline failures within a predeclared acceptable budget at a finite-capacity, non-preemptive IoT processing queue?

This refines RQ-A around the application outcome. Count-based versus consumed-work-based protection remains the first mechanism comparison, not the claimed novelty. The acceptable urgent-failure budget and routine waiting budget require application evidence and must be fixed before held-out evaluation; no numerical target is chosen here.

**Working descriptive title:** *Routine-Service Protection Under Bursty IoT Alerts: Deadline Trade-offs with Variable Service Times*. This describes the direction without claiming a new or superior algorithm.

### Why this direction is selected

| Consideration | Rationale for RQ-A | What must still be earned |
| --- | --- | --- |
| Problem significance | Urgent completion and routine observability compete for the same finite service resource | A credible alert application and justified timing/service requirements |
| Scientific depth | Can expose feasibility limits and explain how service-size/burst structure changes the outcome frontier | A new, defensible insight beyond existing fair-queue/DRR bounds |
| Causal clarity | One stage, trusted labels and equal resources allow the service-accounting effect to be isolated | Matched admission, information, tuning and overhead; no favorable-only workload selection |
| Feasibility | Does not initially require outage modeling or an independently validated urgency classifier | Reproducible relevant comparators and a tractable analytical/evaluation scope |

B remains scientifically plausible, but adds admission-by-dispatch interactions and a failure model while overlapping TRIAGE/4 and TSN admission work. C needs credible ground truth and label-error mechanisms, and risks becoming a different classification/security project. These are scope/readiness reasons for parking them, not evidence that they could not produce stronger results elsewhere.

### Evidence ambition and stop rule

Aim for one explanatory result that survives strong conventional comparators: a conditional feasibility/trade-off characterization, or a reproducible failure regime with a justified remedy. A later evaluation should connect that result to offered urgent deadline failures, routine access/waiting, rejected/unfinished work and decision cost. An implementation artifact or small prototype can strengthen deployment evidence if needed after the novelty check; neither is started by this decision.

A new scheduler is justified only if the identified limitation requires one and the evidence supports it. If existing packetized fair-queue/deadline theory or a faithful conventional comparator already answers the selected question, revise the contribution or stop that claim. Do not rescue it with an arbitrary weighted score, extra capacity, oracle metadata or post-hoc workload selection.

**Award ambition:** develop an important, original and convincing paper. No target conference, competing submission set or calibrated award-probability model is available, so neither this selection nor any numerical improvement can promise a Best Paper award. RQ selection is a commitment to a question; novelty, correctness and useful evidence remain requirements to demonstrate.

## 1. What the existing evidence rules out

The register contains 19 completed, core-related reviews. This note prioritizes eight anchors for the main scheduling/admission decision; supporting retained evidence for classification and system boundaries is cited separately. Review numbers are navigation, while R-keys identify sources. Complete citations appear in Section 9; linked reviews carry version/page mappings and evidence ledgers.

| Closest anchor | Identifiable mechanism | What our review can use | Boundary that changes the comparison |
| --- | --- | --- | --- |
| R08, TRIAGE/4 | Semantic alarm override, within-band device/zone fairness, admission protection | Emergency priority plus fairness/admission is existing work; admitted-alarm delay has conditional protection | Routine traffic can starve across bands; an alarm-aware comparator is needed. Review Sections 4-7; source p. 5, Eqs. 11-18. |
| R09, WTI | Learned queue-state indices select service under bursts | Priority and instantaneous congestion are already combined; no-burst endpoints can favor strict priority | Slotted switch queues and learned transitions differ from non-preemptive application jobs. Review Sections 4-7; source Table IV. |
| R16, FEF | Slack/prediction-based routine opportunities, reserves and threshold preemption | Urgency plus starvation relief is existing work | Preemptive CPU control and execution-time prediction are not freely available to a message worker. Review Sections 4-7; source Sections 3.3-3.4. |
| R18, topic feedback | Emergency override plus periodic low-priority timeout/frequency feedback | Messaging work already protects delayed low-priority traffic | Exact feedback budget/trigger and waiting guarantee are underspecified. Review Sections 5-7; source pp. 5-8. |
| R19, FTS-Hybrid | Priority queues, queue-length-sensitive batches and high/medium/low emission | Priority mix and batch size change class outcomes; some medium/low results regress | Spout emission and downstream processing are not one online worker queue. Review Sections 4-7; source Table III. |
| R22, EFS | Historical class job-count shares plus least-served-client selection | Client fairness and class fairness are distinct; job counts are not consumed service | Similar runtimes/equal resources, a class/client intersection ambiguity and database cost matter. Review Sections 4-7; Algorithms 2-4. |
| R25, RBSS | Capped backlog-dependent rate weights and burst-service compensation | Burst gain can increase regular-flow delay; rate fairness differs from waiting fairness | Fluid, policed flows and conditional analysis; TCS is not a packet waiting bound. Review Sections 4-7; source Table 2. |
| R26, RAAC | Finite-buffer probabilistic admission with stationary reliability-aware threshold selection | Offered versus admitted/completed work must be separated | Single aggregate class; eventual completion is not deadline success; parameter sweeps are not online control. Review Sections 4-7. |

R21's deadline/miss-history feedback and R28's finite-internal-buffer control further prevent novelty claims based on history scores or finite buffering alone. R15/R17 motivate label/proxy questions, but their weak or ambiguous evidence cannot establish that all existing methods fail.

Consequently, none of the following is sufficient novelty: adding priority to MQTT; adding an age threshold; mixing priority/deadline/load in a score; giving routine work occasional service; adding finite queues; or moving a known rule to a different layer.

## 2. Candidate comparison

These are qualitative reviewer judgments from the retained evidence and bounded search, not measured scores or acceptance probabilities.

| Candidate | Main scientific question | Potential value if supported | Largest overlap/novelty risk | Feasibility and decision |
| --- | --- | --- | --- | --- |
| **RQ-A: service accounting** | How does count-based versus work-based routine protection change the urgent-deadline/routine-waiting trade-off under heterogeneous bursts? | Explain a reproducible failure region or derive a scoped trade-off/bound that guides policy choice | DRR/fair-queue latency theory, RBSS, EFS, FEF, FTS-Hybrid and DRA already cover substantial parts | **Selected direction.** A constrained single-stage model is manageable; read the closest missing theory before selecting a method. |
| **RQ-B: admission and dispatch** | When does urgency-aware admission add value over class-neutral admission during service interruption, after holding dispatch fixed? | Explain whether benefits come from rejection, dispatch, or their interaction on the full offered population | TRIAGE/4 already couples alarms and admission; TSN deadline-aware admission has strong prior art | **Parked alternative.** More policy interactions and calibration; justify the outage model and check feasibility before any promotion. |
| **RQ-C: label robustness** | How do wrong urgency labels and legitimate rate surges change the effectiveness of priority/routine-protection policies? | Identify sensitivity and observable limits; test a mitigation without oracle urgency | Security/classification work and robust scheduling need broader coverage; a synthetic noise sweep alone is weak | **Defer.** Ground-truth labels, realistic error mechanisms and system observability are unresolved. |

### RQ-A: the unit of routine protection under variable service demand

> At a finite-capacity, non-preemptive IoT processing queue, how does the unit of routine-service protection - message count versus consumed service time - change the attainable trade-off between urgent deadline failures and routine waiting under heterogeneous, bursty workloads?

**Motivation and overlap.** EFS accounts for job counts under similar runtimes; RBSS accounts for rate-normalized work; FTS-Hybrid accounts for emission batches; FEF and DRA already incorporate deadline/slack or deprivation feedback. The reviewed mechanisms and fairness units differ. They do not, by themselves, settle this exact controlled comparison, but that observation is not proof that nobody else has studied it.

**Provisional scope.** One processing bottleneck, declared finite queue capacity, two classes, trusted labels, no preemption, migration, cloud fallback, suppression or extra service capacity. Service demand varies independently of class in the first comparison; class/size correlation is a separate sensitivity. Known message bytes must not be treated as known CPU service time without a justified model. If a rule needs demand estimates, compare equal information and account for estimation error separately.

**Testable hypothesis, not a finding.** A fixed job-count share can allocate highly variable fractions of busy time as the service-size mix changes. Work accounting may make that share less sensitive, but does not necessarily improve urgent deadlines or routine waiting: long non-preemptive jobs can block urgent work. The hypothesis of a useful QoS advantage is rejected if size-aware/deficit comparators match or dominate it after accounting for tuning, information and overhead.

**Minimum evidence needed to choose the idea.** Locate and read the closest packetized fair-queue/deadline and DRR latency results, define the protection unit precisely, and show why the question is not answered by those results under the same assumptions. A later study would need matched offered workload, controlled service-size variation at fixed mean offered work, a load/burst sanity check, and an urgent-versus-routine outcome frontier rather than one favorable weight setting.

**Possible contribution and stop condition.** A conditional analytical result or reproducible boundary explaining when a protection rule helps, hurts or cannot meet both goals. Stop or reframe if existing theory already supplies that boundary, if the apparent gain comes only from new information/rejection, or if the result is merely the known fact that packet counts differ from byte/time shares. No new score or algorithm name is proposed here.

### RQ-B: separating admission effects from dispatch effects

> Under finite buffering and intermittent service unavailability, when does urgency-aware admission improve offered urgent-task deadline success relative to class-neutral admission, and what routine access/waiting cost remains after the dispatch policy is held fixed?

**Motivation and overlap.** RAAC configures aggregate admission under Markovian outages; TRIAGE/4 already combines semantic alarm priority with protective admission; R28 bounds internal queues while retaining traffic upstream. Deadline-aware online admission in TSN is another direct overlap warning. Adding classes to RAAC or coupling a token bucket with priority is therefore not sufficient contribution.

**Provisional scope.** A single finite gateway queue, explicit service-up/down semantics, retained admitted work, immediate rejection of non-admitted work, and trusted class/deadline metadata. If arrivals during an outage cannot reach the gateway, count them at the declared source/system boundary instead of silently removing them. Keep worker capacity, offered trace, expiry rules and source storage identical across comparisons.

**Testable hypothesis, not a finding.** Class-aware admission may reduce offered urgent deadline failures relative to occupancy-only throttling, but can penalize routine access or fail during predominantly urgent floods. Evidence must separate that trade-off from the effect of dispatch: hold dispatch fixed when comparing admission, then check the admission-by-dispatch interaction. A coupled-only comparison cannot identify the cause.

**Minimum evidence needed to choose the idea.** Read the closest class-aware admission/deadline guarantees; justify an application-relevant outage model and what the controller can observe. A later controlled design must count rejection, admitted expiry, lateness and unfinished work by true class, include reliable-service and interruption conditions, and compare policies under equal parameter-estimation/tuning access. RAAC's offline stationary optimum must not be presented as an online adaptive controller.

**Possible contribution and stop condition.** A scoped characterization of when joint control offers more than either component and where routine-access constraints become infeasible. Reframe if rejection accounts for the entire latency gain, if an established class-aware gate matches the results, or if the outage assumptions exist only to make the preferred rule win. A complete optimizer is not selected.

### RQ-C: urgency labels, rate proxies and service feedback

> How do false-positive/false-negative urgency labels and legitimate sensor-rate surges affect priority scheduling with routine protection, and which observable feedback, if any, mitigates the resulting service harm without access to true urgency?

**Motivation and overlap.** R15 uses a source-rate proxy that can conflict with genuine bursts; PR-MQTT learns value ranges and suppresses similar updates; TRIAGE/4 relies on alarm labels and protects against floods. These establish that classification/admission decisions affect the offered workload. They do not establish a verified label-robustness gap.

**Provisional scope.** Treat label generation as an external process initially. Keep ground-truth urgency only for evaluation; the scheduler receives observed labels and explicitly declared telemetry. Distinguish wrong labels from adversarial flooding, delayed labels and ordinary workload drift. A false-negative urgent job must remain an urgent job in the evaluation denominator.

**Testable hypothesis, not a finding.** False positives can consume protected urgent capacity; false negatives can delay true emergencies. History/age feedback might restore opportunities for some mislabeled work, but a scheduler cannot identify unobserved true urgency from identical observable states. Any oracle-informed rule is a diagnostic upper-bound comparison, not a deployable baseline.

**Minimum evidence needed to choose the idea.** Obtain an application-grounded labeling/error process, document class prevalence and error direction/correlation, and search robust scheduling/classification-linked control beyond MQTT keywords. Independent random label flips may be a diagnostic test, but cannot stand alone as realistic deployment evidence. No classifier training or dataset is selected.

**Possible contribution and stop condition.** A reproducible sensitivity/observability result or a justified feedback mechanism whose benefit persists without oracle labels. Defer if errors are arbitrary, the only result is that incorrect priorities hurt, or credible ground truth cannot be obtained. Do not turn this into a security-classifier project by accident.

## 3. Outcome definitions required before any experiment

The table is a validity specification, not a finalized protocol or set of numeric targets. Thresholds, deadlines and operational budgets must be justified and fixed before held-out evaluation.

| Outcome | Proposed definition | Bias it prevents |
| --- | --- | --- |
| Urgent offered-task deadline failure | `1 - (true urgent tasks completed by their deadline / true urgent tasks offered)` for a fully observed cohort | Rejecting/suppressing urgent work cannot make the score look successful. Wrong labels do not alter ground truth. |
| Routine access within a waiting budget | Fraction of offered routine tasks that start service within a predeclared tau after arrival | Dropped or still-waiting work does not disappear from a completed-only waiting statistic. This is a budget-based outcome, not a proof of starvation freedom. |
| Routine waiting distribution | Arrival-to-start distribution, plus conditional quantiles with their admission/completion denominator disclosed | A finite run's largest observed wait is not a universal maximum-wait bound; short-job/drop selection cannot be hidden. |
| Work and count fairness | Report service starts/completions and consumed busy time separately, with the policy's fairness unit stated | Equal counts do not imply equal consumed work, and equal work shares do not imply equal deadlines or per-job waits. |
| Admission/lifecycle accounting | By class: offered, intentionally suppressed if allowed, rejected, admitted, on-time completed, late completed, expired/cancelled, and unfinished at observation end | Avoid overlapping terminal categories or treating upstream retained traffic as delivered/loss-free. |
| Decision/control cost | Observed decision cost and required telemetry/model-training cost, separate from modeled execution time | A simulated free decision or unavailable metadata must not masquerade as deployable low latency. |

A deadline failure cannot be finalized merely because a simulation ended. Observe each offered task through its deadline or mark it right-censored; specify a post-arrival drain/observation policy before measuring outcomes. Report routine unfinished/rejected mass alongside quantiles. Apply an identical lifecycle/expiry rule when isolating scheduler effects; vary it only as an explicit intervention.

Unbounded urgent offered demand, finite buffers and finite service cannot guarantee every urgent deadline and every routine wait simultaneously. Any formal guarantee needs feasible arrival/service envelopes, bounded non-preemptive blocking and a precisely declared admitted population. Queue occupancy alone is not a delay theorem.

## 4. Comparison rules and faithful-baseline boundaries

- Hold source-offered traces, actual service demands, queue-capacity units, transport, resource budget and metadata access constant when isolating a mechanism. Compare load in required service work per unit time, not only messages/second. Report message count and workload/memory occupancy distinctly.
- Choose a small set of relevant, reproducible comparators after the novelty check. FIFO, semantic strict priority and an appropriate fair-queue/deadline rule are possible reference families, not a selected baseline list. Parameterized policies need comparable tuning budgets and separate tuning/evaluation workloads.
- Reuse the same offered trace per run across policies; uncertainty comes from independent trace/seed runs. Time bins or many requests within one run are not independent trial repetitions. Report adverse regimes and sensitivity rather than selecting only a winning burst mix.
- Evaluate a family of urgent/routine trade-offs. A higher routine share with a larger urgent-failure cost is a trade-off, not universal dominance. Any acceptable-cost limit must be justified before test-set inspection.
- EFS needs its class/client intersection clarified; FTS-Hybrid needs batching/downstream alignment. FEF requires preemption/prediction, DRA divisible flows, RBSS fluid/traffic-contract assumptions, and WTI trained transition information. Adapted variants must be named as adaptations with changed assumptions; do not attribute the originals' guarantees to them.
- A learned or estimated-state method must not receive the held-out workload law, exact future arrivals or service demand unavailable to other policies. Separate a diagnostic oracle from a usable policy.

## 5. Targeted novelty check performed in this session

The accompanying [search log](../search-log.csv) records actual discovery/verification queries dated 15 November 2026. These were web-search-service queries, **not searches claimed to have run in Google Scholar, Scopus or IEEE Xplore's own search interface**. Search-engine coverage and results are incomplete; pooled batches do not expose reliable per-query hit attribution. Only the salient primary-source checks below support this note. No citation counts, PRISMA totals or exhaustive-coverage claims are inferred.

| Candidate | Result of bounded checking | Consequence for selection |
| --- | --- | --- |
| RQ-A | G01 below explicitly concerns DRR variable-packet fairness, exact latency/fairness bounds and implementation trade-offs. TRIAGE/4 also lists WFQ/DRR among its comparisons. | **Substantial overlap exists.** Read G01 and its closest deadline/fair-queue references before claiming a new service-accounting trade-off. This session did not establish the proposed question's novelty. |
| RQ-B | G02 below explicitly studies deadline-aware online admission and bandwidth reallocation for event-triggered traffic using ATS/CBS and network calculus. | **Substantial overlap exists.** The research would need a defensible distinction in the actual guarantee, objective or failure model; a gateway-versus-TSN location change alone is inadequate. |
| RQ-C | Broad MQTT/priority/error queries produced security/inference and architecture results, without a verified direct answer to this scheduling question in the salient screened hits. | **Unresolved, not evidence of absence.** Broaden terms to robust/misclassified-priority scheduling and inspect application label-generation studies before promotion. |

**G01 - identity and abstract checked, full text not reviewed in this session.** Luciano Lenzini; Enzo Mingozzi; Giovanni Stea. 2004. *Tradeoffs between low complexity, low latency, and fairness with deficit round-robin schedulers.* IEEE/ACM Transactions on Networking, 12(4), 681-693. IEEE. DOI: [10.1109/TNET.2004.833131](https://doi.org/10.1109/TNET.2004.833131). [Official IEEE record](https://ieeexplore.ieee.org/document/1331430/) and [University of Pisa author record](https://arpi.unipi.it/handle/11568/202043). The checked abstract establishes direct fairness/latency overlap; its particular bounds have not been adopted or independently verified here.

**G02 - identity and abstract checked, full text not reviewed in this session.** Sifan Yu; Feng He; Anlan Xie; Luxi Zhao. 2025. *Efficient adaptive bandwidth allocation for deadline-aware online admission control in centralized time-sensitive networking.* Journal of Systems Architecture, 168, 103539. Elsevier. DOI: [10.1016/j.sysarc.2025.103539](https://doi.org/10.1016/j.sysarc.2025.103539). [Official article](https://www.sciencedirect.com/science/article/pii/S1383762125002115) and [indexed official authorship statement](https://www.sciencedirect.com/science/article/abs/pii/S1383762125002115). Direct HTML retrieval returned 403; verification uses indexed official title/venue/abstract/authorship. Do not substitute the different arXiv title/author list or its numerical results for this journal article.

G01/G02 are targeted novelty-check leads, not completed active reviews. They are not added to the register, reference catalog or 19-review count. A discovery hit for the original DRR paper was not independently checked against its primary publication in this session and is not used as an additional verified citation here.

## 6. Checks still required before selecting a contribution

| Check | Required decision/evidence | Current status |
| --- | --- | --- |
| Closest-theory coverage | Read G01 and trace its nearest fair-queue/deadline predecessors/successors; compare assumptions and guarantees to RQ-A | Pending; blocks a new-method novelty claim |
| Admission overlap | Read G02 and compare with TRIAGE/4/RAAC if RQ-B is promoted | Pending; RQ-B remains an alternative |
| Exact novelty statement | State what an existing method/theorem does not already answer under the same information and resource assumptions | Not established |
| Application importance | Identify a credible alert workload, service-demand range, deadline rationale and routine service requirement | Not established; do not invent operational budgets |
| Comparator fidelity | Resolve necessary ambiguity or use a fully specified comparator with an honest adaptation label | Not selected |
| Falsifiability | Specify which outcome would reject the hypothesis, including no advantage over a strong conventional comparator | Drafted above; operational limits not fixed |
| Scope and venue fit | Choose analytical, measurement or algorithmic contribution and match it to the eventual conference | Venue and contribution type not selected |

Suggested follow-up query families are **not yet executed searches**: `non-preemptive deadline fair queueing variable service bounded waiting`; `deficit round robin deadline latency service time fairness`; `class-aware admission finite buffer deadline server interruption`; `misclassified priority queue robust scheduling`. Search by mechanism and follow citations, not just the IoT/MQTT label.

## 7. Recommended next action

1. Deep-read G01, then the closest deadline/fair-queue work it leads to. Write down whether RQ-A survives with a meaningful contribution beyond known DRR/latency behavior.
2. Specify an application-backed problem boundary and outcome definitions. Keep RQ-A narrow: trusted labels, one stage and no outages initially. RQ-B/C are separate alternatives/extensions, not extra dimensions to pack into one conference paper.
3. Update this same note with the novelty decision and precise contribution claim. RQ-A is selected, but if it is already answered, reframe or assess B; do not preserve a novelty claim solely because archived implementation exists.
4. Only then finalize an analytical/evaluation plan and begin implementation. The 20-25-paper target can guide effort but is not a mandatory stopping rule or evidence of conference readiness.

**Decision at version 0.2:** RQ-A is the selected research direction. The next concrete task is the closest-theory/full-text novelty check, followed by application-backed requirements. B is parked and C deferred. No algorithm, parameter values, deployment promise or award outcome is asserted.

## 8. Update discipline

Keep candidate wording, citations and status in this file. Record new executed searches in the log and completed relevant reviews in the existing register. When evidence invalidates a candidate, record why and revise the recommendation; do not convert an untested hypothesis into a finding. Numeric results quoted from reviewed papers remain author-reported unless a review explicitly marks an independent check.

## 9. Retained references used in this note

These publication records inherit verification/version qualifications from their linked full-text reviews and [reference metadata](../references.json). They are complete citations to existing retained sources, not newly completed reviews. No venue indexing/quartile status is inferred.

- **R08.** João Carlos N. Bittencourt; Paulo Portugal; Francisco Vasques; Daniel G. Costa. 2026. **Multi-Tier Message Scheduling for IoT-Based Urban Emergency Systems Through Semantic Priority Override**. *IEEE Access, 14, 140988-141015*. IEEE. DOI: [10.1109/ACCESS.2026.3732592](https://doi.org/10.1109/ACCESS.2026.3732592). [Full-text review](../reviews/Multi-Tier%20Message%20Scheduling%20for%20IoT-Based%20Urban%20Emergency%20Systems%20Through%20Semantic%20Priority%20Override.md). Used for: Semantic emergency override, within-band fairness and protected admission; closest alarm/admission overlap.

- **R09.** Rongping Lin; Jinpeng Zhang; Shan Luo; Jing Fu; Xiong Wang; Hui Li; Moshe Zukerman. 2025. **Real-Time Priority Queue Scheduling for Bursty Traffic**. *IEEE Internet of Things Journal, 12(24), 55883-55892*. IEEE. DOI: [10.1109/JIOT.2025.3627212](https://doi.org/10.1109/JIOT.2025.3627212). [Full-text review](../reviews/Real-Time%20Priority%20Queue%20Scheduling%20for%20Bursty%20Traffic.md). Used for: Queue-state priority under bursts and the need to account for training/model assumptions.

- **R16.** Sehrish Malik; Shabir Ahmad; Israr Ullah; Dong Hwan Park; DoHyeun Kim. 2019. **An Adaptive Emergency First Intelligent Scheduling Algorithm for Efficient Task Management and Scheduling in Hybrid of Hard Real-Time and Soft Real-Time Embedded IoT Systems**. *Sustainability, 11(8), article 2192*. MDPI. DOI: [10.3390/su11082192](https://doi.org/10.3390/su11082192). [Full-text review](../reviews/An%20Adaptive%20Emergency%20First%20Intelligent%20Scheduling%20Algorithm%20for%20Efficient%20Task%20Management%20and%20Scheduling%20in%20Hybrid%20of%20Hard%20Real-Time%20and%20Soft%20Real-Time%20Embedded%20IoT%20Systems.md). Used for: Existing urgency/slack/starvation relief, with preemption and prediction boundaries.

- **R18.** Dejian Chen; Dong Li; Renchun Guo. 2022. **Design of topic priority based on industrial publish-subscribe system**. *Frontiers in Energy Research, 10, article 979174*. Frontiers Media SA. DOI: [10.3389/fenrg.2022.979174](https://doi.org/10.3389/fenrg.2022.979174). [Full-text review](../reviews/Design%20of%20topic%20priority%20based%20on%20industrial%20publish-subscribe%20system.md). Used for: Emergency messaging plus low-priority service feedback; exact control rules need clarification.

- **R19.** Faiza Akram; Peng Kang; Palden Lama; Samee U. Khan. 2024. **Data-Priority Aware Fair Task Scheduling for Stream Processing at the Edge**. *2024 IEEE Cloud Summit, 117-122*. IEEE. DOI: [10.1109/Cloud-Summit61220.2024.00026](https://doi.org/10.1109/Cloud-Summit61220.2024.00026). [Full-text review](../reviews/Data-Priority%20Aware%20Fair%20Task%20Scheduling%20for%20Stream%20Processing%20at%20the%20Edge.md). Used for: Priority-mix-sensitive batch service and downstream control-location effects.

- **R22.** Arkadiusz Madej; Nan Wang; Nikolaos Athanasopoulos; Rajiv Ranjan; Blesson Varghese. 2020. **Priority-based Fair Scheduling in Edge Computing**. *2020 IEEE 4th International Conference on Fog and Edge Computing (ICFEC), 39-48*. IEEE. DOI: [10.1109/ICFEC50348.2020.00012](https://doi.org/10.1109/ICFEC50348.2020.00012). [Full-text review](../reviews/Priority-based%20Fair%20Scheduling%20in%20Edge%20Computing.md). Used for: Historical client/class job-count fairness under similar-runtime assumptions.

- **R25.** Mahmoud Daneshvar Farzanegan; Hossein Saidi; Mehdi Mahdavi. 2014. **An Approach to Scheduling Bursty Traffic**. *ETRI Journal, 36(1), 69-79*. Electronics and Telecommunications Research Institute (ETRI). DOI: [10.4218/etrij.14.0112.0524](https://doi.org/10.4218/etrij.14.0112.0524). [Full-text review](../reviews/An%20Approach%20to%20Scheduling%20Bursty%20Traffic.md). Used for: Capped backlog weights, burst compensation and the regular-flow delay penalty.

- **R26.** Shensheng Tang. 2026. **Reliability-Aware Admission Threshold Selection for IoT Gateway–Cloud Systems: Trade-Off-Driven and Constraint-Based Approaches**. *IoT, 7(3), 60*. MDPI. DOI: [10.3390/iot7030060](https://doi.org/10.3390/iot7030060). [Full-text review](../reviews/Reliability-Aware%20Admission%20Threshold%20Selection%20for%20IoT%20Gateway-Cloud%20Systems%20-%20Trade-Off-Driven%20and%20Constraint-Based%20Approaches.md). Used for: Class-neutral finite-buffer admission, offered-task deliverability and stationary failure modeling.

- **R21.** Bo Shen; Naveen Chilamkurti; Ru Wang; Xingshe Zhou; Shiwei Wang; Wen Ji. 2018. **Deadline-aware rate allocation for IoT services in data center network**. *Journal of Parallel and Distributed Computing, 118, 296-306*. Elsevier Inc.. DOI: [10.1016/j.jpdc.2017.09.012](https://doi.org/10.1016/j.jpdc.2017.09.012). [Full-text review](../reviews/Deadline-aware%20rate%20allocation%20for%20IoT%20services%20in%20data%20center%20network.md). Used for: Deadline ranking with recent miss-history feedback, distinct from a per-job waiting bound.

- **R28.** Long Bao Le; Eytan Modiano; Ness B. Shroff. 2012. **Optimal Control of Wireless Networks With Finite Buffers**. *IEEE/ACM Transactions on Networking, 20(4), 1316-1329*. IEEE/ACM (published by IEEE). DOI: [10.1109/TNET.2011.2176140](https://doi.org/10.1109/TNET.2011.2176140). [Full-text review](../reviews/Optimal%20Control%20of%20Wireless%20Networks%20With%20Finite%20Buffers.md). Used for: Conditional internal queue/utility guarantees with unlimited upstream source storage.

- **R15.** Marwa O Al Enany; Hany M. Harb; Gamal Attiya. 2021. **A New Back-off Algorithm with Priority Scheduling for MQTT Protocol and IoT Protocols**. *International Journal of Advanced Computer Science and Applications (IJACSA), 12(11), 349-357*. The Science and Information Organization. DOI: [10.14569/IJACSA.2021.0121140](https://doi.org/10.14569/IJACSA.2021.0121140). [Full-text review](../reviews/A%20New%20Back-off%20Algorithm%20with%20Priority%20Scheduling%20for%20MQTT%20Protocol%20and%20IoT%20Protocols.md). Used for: Frequency-based priority/source back-off as a potentially imperfect urgency proxy.

- **R17.** Jiby J. Puthiyidam; Shelbi Joseph. 2024. **PR-MQTT: a novel approach for traffic reduction and message prioritisation in IoT applications**. *International Journal of Web Engineering and Technology, 19(1), 44-66*. Inderscience Enterprises Ltd.. DOI: [10.1504/IJWET.2024.138096](https://doi.org/10.1504/IJWET.2024.138096). [Full-text review](../reviews/PR-MQTT%20-%20a%20novel%20approach%20for%20traffic%20reduction%20and%20message%20prioritisation%20in%20IoT%20applications.md). Used for: Learned value-range priority and selective forwarding; suppression changes the offered/delivered population.

[Review register](../README.md) · [Cross-paper comparison](comparison.csv) · [Evidence synthesis](findings.md)
