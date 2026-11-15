# Dynamic priority-based task scheduling and adaptive resource allocation algorithms for efficient edge computing in healthcare systems

## 1. Bibliographic record and source

- **Review 14 · R23 · core-related; dynamic urgency/age/load and routine-resource handling.** Conceptual relevance is stronger than the evidence for faithful reproduction.
- **Authors:** J. Anand; B. Karthikeyan. Initials follow the supplied publication; names are not expanded speculatively.
- **Publication:** Results in Engineering, volume 25, article 104342, 2025. Publisher: Elsevier B.V. Available online 13 February 2025; issue March 2025.
- **DOI:** [10.1016/j.rineng.2025.104342](https://doi.org/10.1016/j.rineng.2025.104342). [Official ScienceDirect record](https://www.sciencedirect.com/science/article/pii/S2590123025004232).
- **Verification, 15 November 2026:** DOI/title/venue identity checked against indexed official Elsevier records; direct ScienceDirect HTML retrieval returned 403. Method and numerical evidence below come from the supplied full text, not an abstract-only inference. No indexing/quartile claim.
- **Read source:** supplied `1-s2.0-S2590123025004232-main.pdf`, published PDF, 16 pages. Article pages 1–16 match PDF pages. SHA-256: `b3f8a9a0037178f4a194e21c532ce7f229b37d26529552d567b74db1bf465090`.
- Full-text critical reading, with priority/algorithm and result pages visually checked. No independent replication, source-code validation or clinical validation. PDF not redistributed.

## 2. Research problem

Healthcare IoT produces urgent and routine computation requests for constrained local/edge resources, with cloud fallback. DPTARA combines task prioritization and resource placement to reduce latency, execution time and energy while improving utilization. Its decision affects both which work is favored and where/how much resource is available (Section 3).

For our review, the relevant issue is the interaction between urgent priority, elapsed waiting, system load and routine progress. Its multi-resource offloading model differs materially from dispatching messages through one fixed-capacity queue.

## 3. Authors' claimed contribution

The authors propose dynamic priority assignment, adaptive allocation, predictive load balancing and energy-aware operation. They describe reallocating resources from normal tasks to urgent ones, offloading incomplete normal work to the cloud, and splitting normal tasks for sequential/parallel processing as fairness mechanisms (Section 3.2.3, p. 7).

The reported simulation advantages apply to this combined framework. They do not identify the standalone effect of the priority score, establish a routine waiting bound or prove hard-deadline safety.

## 4. Model and assumptions

- Local resources, edge nodes and one cloud server form a hierarchy. Requests carry initial priority, arrival time, deadline and task size. Routine monitoring may be promoted when an abnormal condition appears (p. 7).
- Capacity allocation may reclaim normal-task resources, offload incomplete work and split tasks. Migration, partial execution and parallelism therefore change the service model. Their overheads and execution semantics require clarification before transfer to indivisible alert messages.
- Table 3 (p. 12): 50 IoT devices, 10 edge servers, one cloud; Poisson arrivals at 5 tasks/s; task size uniform 5–50 MB; deadlines uniform 10–100 s; edge transmission latency 5–10 ms and cloud 50–100 ms.
- Table 4 (p. 12): edge 500–3000 MIPS and 32 GB RAM; cloud 2000–10000 MIPS and 64 GB RAM. CPU utilization and efficiency factors also enter the model.
- Processing-time equations divide task size by processing capacity (Equations 6 and 9, p. 6). The notation permits MB versus MIPS/tasks-per-second without a supplied conversion of data volume to instruction demand. The normalized CPU/RAM capacity scalar described on p. 6 also needs alignment with `task.size` in the allocation test.
- Local/cloud latency formulas add transmission and computation (Equations 5 and 7, p. 6); queue waiting is not explicit in those expressions. Reported latency should not silently be reinterpreted as full arrival-to-completion response time.
- Fig. 4's latency tolerances are 250 ms for urgent and 400 ms for normal requests (p. 12), distinct from Table 3's 10–100 s task deadlines. Mean latency relative to a class tolerance is not a per-task completion guarantee.

## 5. Method and decision mechanism

The priority rule is Equation 11 (pp. 7–8), also printed in Algorithm 2 (p. 9):

`P_i = α P_orig,i + β (T_current − T_arrival,i) / D_i − γ L_current,i`.

It rewards initial importance and normalized elapsed waiting while penalizing the assigned resource's load. The age/deadline ratio is not remaining slack: it does not subtract predicted service time, and its interpretation depends on whether `D_i` is a relative budget or an absolute due time. Weight calibration, refresh frequency and ordering/tie rules are not specified sufficiently for an unambiguous comparator.

Algorithm 1 (p. 9) loops over tasks, calls dynamic prioritization, selects a feasible least-loaded resource, and falls back to the cloud. Resource queues are then drained to simulate execution and record metrics. The printed loop does not show an explicit priority re-sort/re-enqueue after score updates; Algorithm 2 computes `P_i` but returns `T_i.priority` without an explicit assignment. These are reproduction questions, not evidence that the authors' implementation necessarily ignored priority.

Two further boundaries matter. First, if all resources are overloaded, the algorithm prints an overload message yet then reaches an unconditional enqueue through `selected_resource`; a null/no-capacity branch and drop/defer policy are needed. The surrounding prose allows defer/drop but does not provide a complete rule. Second, the forecast call occurs after processing in the printed Algorithm 1. The causal path from forecast to subsequent resource decisions needs documentation before attributing measured gains specifically to prediction.

Resource balancing, energy efficiency and prediction equations are additional interventions (Equations 13–16, pp. 10–11). The paper should therefore be read as a framework with coupled components, rather than as a fully specified new queue-order formula alone.

## 6. Evidence ledger

| Claim examined | Source location | Actual evidence | Interpretation boundary |
| --- | --- | --- | --- |
| Dynamic priority uses waiting, deadline and load | Equation 11, pp. 7–8; Algorithms 1–2, p. 9 | Explicit weighted priority/normalized-age/load expression plus hierarchical resource allocation. | Score assignment, ordering refresh, units and weights need reconciliation. An aging term alone is not a starvation bound. |
| Urgent requests meet timing needs without abandoning routine work | Section 3.2.3, p. 7; Figure 4, p. 12 | Routine reallocation/offloading is described; mean urgent/normal latencies remain below the stated 250/400 ms tolerances in the plotted request range. | No class-tail distribution, per-task miss ratio, routine maximum wait or migration/loss accounting establishes a guarantee. |
| Framework improves performance at 100 requests | Table 5, p. 12 | DPTARA/A-PBRA/NBIHA/CORA-GT: latency 320/350/480/560 ms; utilization 88/57/48/35%; execution time 335/540/570/1100 ms; energy 321/600/700/802 J. | Author-reported simulation values. Different timing endpoints should not be conflated, and the combined interventions prevent queue-only attribution. |
| Advantage persists across request/configuration changes | Figures 5–9 and Table 6, pp. 13–14 | Plots compare execution time, energy and utilization across request counts and configurations. | Request count is not by itself an offered-load utilization or controlled burst profile. Configuration, repeats and variance are insufficiently specified for statistical/general overload claims. |
| Comparator implementation is traceable | Evaluation text, p. 12; related work, pp. 2–3; references, pp. 15–16 | Evaluation labels NBIHA with [9] and CORA-GT with [13], whereas related work identifies NBIHA [10] and CORA-GT [15]. | Resolve exact baseline identity/version and parameter mapping before a faithful comparison; do not invent a substitute implementation. |

## 7. Critical appraisal

**Contribution and relevance.** This paper blocks a novelty claim based solely on combining urgency, elapsed waiting/deadline normalization and current resource load. It explicitly considers routine progress alongside urgent work. It is worth retaining as close conceptual prior art despite being a computation-placement framework.

**Internal validity and reproducibility.** The printed score/ordering connection, task/resource unit conversion, all-overloaded path and forecast feedback are unresolved. Source code, configuration/weight values and event-level traces could settle them. Do not silently fix these choices and then present that new implementation as the published algorithm.

**Causal and statistical limits.** Allocation, resource reclamation, partial offload, energy control and prioritization change together. No clearly isolated component ablation or adequately specified repeated-seed uncertainty protocol establishes which component causes each gain. Baseline citation mismatches add a separate alignment concern. These observations limit interpretation; they are not an allegation that the reported data were fabricated.

**Fairness and timing validity.** Offloading routine work can preserve progress while adding network delay and consuming cloud capacity. That is reviewer reasoning from the model, not an observed universal penalty. Mean class latency and balanced resource utilization do not establish low-class tail protection, hard deadlines or behavior when the cloud also saturates. The Poisson experiment is also not a validated burst-overload stress study.

**Research use:** conceptual comparator and source of precise questions. Its quantitative superiority claims remain author-reported and its mechanism is not ready for faithful implementation without clarification. Scopus/quartile standing and clinical impact are not independently assessed here.

## 8. Synthesis contribution and open question

Alongside the existing disaster-scheduling review, DPTARA shows that dynamic urgency/deadline handling often comes coupled to placement or migration. Compare it with [EFS](Priority-based%20Fair%20Scheduling%20in%20Edge%20Computing.md), whose fairness is historical class/client job shares: DPTARA's resource balancing and routine offload use a different fairness unit.

**Open reading question:** which published mechanisms protect routine progress when extra cloud capacity, task splitting or migration is unavailable, and which results separate queue-order benefits from added resources? This remains a question for comparison, not a selected algorithm or demonstrated research gap.

**Bangla note:** urgency + age/deadline + load score আগেই আছে। তবে এই paper-এর fairness ও latency claim সরাসরি আমাদের single-queue alert model-এ বসানো যাবে না।

[Register](../README.md) · [Comparison](../synthesis/comparison.csv) · [Synthesis](../synthesis/findings.md)
