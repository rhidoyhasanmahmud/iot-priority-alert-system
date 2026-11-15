# An Adaptive Emergency First Intelligent Scheduling Algorithm for Efficient Task Management and Scheduling in Hybrid of Hard Real-Time and Soft Real-Time Embedded IoT Systems

## 1. Bibliographic record and source

**Review number:** 07 · **Internal reference key:** R16

Sehrish Malik; Shabir Ahmad; Israr Ullah; Dong Hwan Park; DoHyeun Kim. 2019. **An Adaptive Emergency First Intelligent Scheduling Algorithm for Efficient Task Management and Scheduling in Hybrid of Hard Real-Time and Soft Real-Time Embedded IoT Systems**. *Sustainability, 11(8), article 2192*. MDPI. DOI: [10.3390/su11082192](https://doi.org/10.3390/su11082192).

- **Identity verification:** supplied title page matched with the indexed [official publisher record](https://www.mdpi.com/2071-1050/11/8/2192), including authors, year and DOI, on 15 November 2026. Direct HTML retrieval was rate-limited; methodological review uses the supplied full text.
- **Reviewed version:** supplied publisher-formatted PDF, 21 pages; visible page labels equal PDF pages. Extraction also exposes duplicated/proof-layer text, so key algorithm and result claims were checked against rendered pages.
- **Source fingerprint (SHA-256):** `6868a34beeb144f53a6b6e3e75b520901c00f13ae58ba01597dfa5b2714fd01c`.
- **Reading status:** full text reviewed; no independent replication or proof verification. Visual checks: pp. 6, 9, 15 and 17.
- **Selection:** core-related and close conceptual prior art: urgency, deadlines and starvation protection in embedded IoT. A preemptive CPU-task model differs from a broker/application message queue. Quartile/indexing status is not independently verified here.

## 2. Research problem

How should an overloaded embedded IoT processor serve urgent/hard-deadline work while giving lower-priority periodic and soft-deadline work a chance to run?

The authors distinguish urgent and normal event-driven tasks, plus priority and normal periodic tasks (Table 2, p. 6). Their Fair Emergency First (FEF) scheduler seeks fewer missed instances and fewer starved tasks through selective slack use and configurable preemption.

## 3. Authors' claimed contribution

FEF combines an urgency comparison (UM), a learned high-priority execution/failure prediction (FM), reserved CPU units and a preemption bit/threshold. ANN-assisted decisions aim to admit lower-priority execution when it appears safe for higher-priority work.

The reported comparisons favor FEF over classical and combined scheduling policies and a non-intelligent FEF variant. These are empirical claims in the presented workloads; they are not a general schedulability theorem, universal optimality result or certified hard-real-time guarantee.

## 4. Model and assumptions

- A CPU-task scheduler controls execution and can preempt running work. Task metadata includes arrival, execution requirement, deadline, periodicity and urgency/preemption flags (Eqs. (2)-(3), pp. 11-12).
- Urgent event-driven work normally takes precedence. Periodic tasks with PB = 1 may interrupt even urgent work after a configured PT during prolonged starvation (Section 3.4, p. 10).
- UM/FM use current arrived-task information and history. Unexpected future urgent arrivals are not known; the authors explicitly acknowledge resulting prediction failures (p. 9).
- Python/Flask implementations are described for a Windows i5 workstation and Raspberry Pi 3 Model B, with sensing/actuator tasks (Tables 3-6, pp. 10-12). This is not evidence of deployment as a production RTOS scheduler.
- The input-generation guidance restricts periods, sets deadlines to period or half-period and samples execution requirements below deadlines (Table 5, p. 11). Tests emphasize overload, including 100/500 ms sensing and 2/3 s event intervals (pp. 13-14).
- Reserved/PT change between comparison sections: Section 5.1 uses Reserved = 1 and PT = 10; Section 5.2 uses Reserved = 3 and PT = 20; PT = 20 is also stated for Section 5.3 (p. 14). Do not combine tracks as if all controls were fixed.
- Finite-buffer overflow, MQTT delivery, network delay and full per-message loss accounting are outside the established model.

## 5. Method and decision mechanism

**Task flags and slack -> urgent/periodic selection -> learned safety checks -> execution -> history update.**

Figure 1 (p. 6) selects the nearest-deadline urgent event-driven task when urgent work exists. For other combinations, periodic priority and UM/FM determine service; the exact branch nesting needs care in reproduction.

UM compares event-driven and periodic slack through Eq. (1), p. 7: event-driven slack >= x times periodic slack. The initial x is 2. If the condition holds, UM = 0 and periodic work may run; otherwise event-driven work is selected. History is intended to train the ANN to adjust x (pp. 7-8).

FM invokes a prediction of safe high-priority execution based on arrived tasks and historical state. A positive safety prediction sets FM = 0, allowing starving/about-to-miss periodic work; otherwise higher-priority periodic work runs (Figures 4-5, p. 9). Reserved leaves CPU units for unforeseen arrivals.

PB/PT provide a separate override: a PB-enabled periodic task that reaches the threshold may preempt urgent work (p. 10). This is directly relevant prior art for threshold-based starvation relief, but the text does not prove a bound under arbitrary competing PB tasks or arbitrary arrivals.

**Reproduction questions:** ANN architecture, training labels/loss, history size, training/evaluation separation, update schedule, the exact starvation test, units of Reserved/PT and handling of prediction errors require more specification. A heuristic replacement for FM should not be presented as faithful learned FEF.

## 6. Evidence ledger

All experiment results are author-reported. Reviewer arithmetic and visual estimates are identified separately.

| Claim examined | Source location | Actual evidence | Interpretation boundary |
| --- | --- | --- | --- |
| Fewer missed task instances under overload | Section 5.1 and Fig. 8, pp. 14-15 | About 21% missed for FEF versus about 68% for the worst plotted policies. | A selected overloaded workload and different policy objectives; not a general effect size or proof of feasibility. |
| Lower starvation rate | Fig. 9 and accompanying text, p. 15 | About 10% for FEF; text describes baseline weighting over multiple task categories but FEF contributions as soft-deadline tasks only. | Exact weighting/denominators are insufficiently explicit. Starvation and missed-instance rates are different metrics; do not interchange them. |
| Benefit of learning modules | Section 5.3 and Fig. 11, pp. 16-17 | Non-intelligent FEF fixes x = 2 and removes FM. Visual bars are roughly 23% vs 10-11% starvation and 35-36% vs 21-22% missed instances. | Two changes occur together. This is not a one-factor ANN ablation or quantified prediction-accuracy study. Values are graph estimates. |
| Deadline completion versus hybrid priority/FIFO/RR | Table 7, p. 17, visually checked | 40 tasks: hybrid completes 31, FEF 34; both success columns print 77.5%. Reviewer arithmetic: 34/40 = 85%. At 400 tasks, 315 vs 349 complete; both columns print 78.75%, whereas 349/400 = 87.25%. | The FEF percentage column is inconsistent with counts. Count-derived improvements are 7.5 and 8.5 percentage points for these rows, not validated starvation-time reductions. |
| Hard-deadline protection | pp. 15-16 and p. 9 | Authors report no hard-real-time misses for the displayed scenario, but also acknowledge predictions may fail with unforeseen urgent arrivals. | Observed success does not establish universal hard-deadline safety. PB can deliberately interrupt urgent work. |
| Execution-time claim | Fig. 12, p. 18 | A plotted comparison is labeled WCET. | Observed/plot-level execution times do not establish a verified worst-case bound without workload and timing-analysis conditions. |

## 7. Critical appraisal

**Relevance and contribution.** This is particularly important for our idea selection: emergency-first scheduling with slack-based routine opportunities, learned safety checks and threshold preemption already exists. Combining urgency and starvation prevention is therefore not a sufficient novelty claim.

**Internal and construct validity.** The overloaded-task model is relevant, but preemptive CPU control, known execution requirements and history availability materially affect what can transfer to IoT message processing. Less missed work can indicate better useful throughput; it is not by itself a direct CPU-utilization measurement. The starvation definition blends missed instances and tasks that never execute; a reproducible denominator is essential.

**Statistical validity.** Independent-run counts, seed distributions and uncertainty intervals are not sufficiently documented in the displayed evaluation. The Table 7 arithmetic error prevents uncritical reuse of its success percentages. Its final column is the difference of completion rates, despite being named starvation-rate minimization.

**Learning validity and safety.** Training delay is an author-stated limitation (p. 19). The paper does not provide enough ANN training detail or predictive-error evidence to establish safe generalization. Unexpected arrivals and PB/PT interruption explicitly limit hard-deadline assurance. A formal claim would require arrival/service assumptions, admission feasibility and a schedulability argument.

**What would strengthen confidence:** corrected raw result tables; a single task/starvation definition for all methods; repeated workload results; separately controlled UM, FM and PB/PT ablations; documented training/overhead; and hard-class failure measurements when the threshold override is active.

## 8. Synthesis contribution and open question

FEF overlaps strongly with [adaptive disaster-management scheduling](Adaptive%20Priority%20Scheduling%20of%20Internet%20of%20Things%20Data%20for%20Disaster%20Management%20in%20Smart%20Cities.md) on deadline-aware adaptation, and with [semantic alarm scheduling](Multi-Tier%20Message%20Scheduling%20for%20IoT-Based%20Urban%20Emergency%20Systems%20Through%20Semantic%20Priority%20Override.md) on urgent/routine allocation. Their control locations and assumptions differ.

**Question for further reading:** Which urgency/starvation mechanisms remain effective when preemption or reliable execution-time predictions are unavailable, and what urgent failure cost accompanies routine-service protection?

A difference in control location is not sufficient novelty. A limitation here is a search lead, not a demonstrated field-wide gap or chosen contribution.

<details>
<summary>বাংলা reading note</summary>

এটি আমাদের প্রশ্নের খুব কাছের paper: urgent কাজ আগে চালায়, slack ও prediction দিয়ে routine কাজকে সুযোগ দেয়, আর threshold পার হলে preemption করতে পারে। তাই urgency + starvation protection একসঙ্গে ব্যবহারকে নতুন বলা যাবে না। তবে Table 7-এর count ও percentage মেলে না; ANN ও hard-deadline guarantee নিয়েও evidence সীমিত।

</details>

Return to the [review register](../README.md) or [cross-paper comparison](../synthesis/comparison.csv).
