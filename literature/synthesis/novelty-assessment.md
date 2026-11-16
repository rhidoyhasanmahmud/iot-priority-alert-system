# Independent novelty and research-readiness audit (conference RQ v1.0)

**Audit date:** 16 November 2026 · **Status:** focused adversarial literature audit completed; **originality NOT demonstrated** · **Decision owner:** research team/supervisor (no automatic change of the approved RQ).

**Scope of review:** [the currently selected main question and RQ1–RQ3](research-questions.md) on routine timely *service start* under an *offered urgent-job deadline-failure* budget at one finite-capacity, non-preemptive IoT processing bottleneck. This document adds targeted closest-prior-art checks; it **does not replace** RQ v1.0, certify field-wide novelty, claim a complete 19-PDF re-read, establish a theorem, or report experimental results.

**Evidence provenance:** 19 existing reviewed papers in the [register](../README.md), [comparison](comparison.csv) and [synthesis](findings.md); targeted publisher/author-hosted records and sections; new query and candidate entries in the [search log](../search-log.csv). The extra papers below are **leads, not counted as completed reviews**. No independent Scopus/Web of Science systematic search or citation-chaining census was performed. Publisher search/index excerpts may expose significant text without providing verified complete full-text access.

## Step 1 — Freeze the exact claims being evaluated

The current main question asks whether, and in which burst/service-demand regimes, an online scheduler can improve routine timely **access to service** while satisfying a predeclared maximum **offered urgent-job deadline-failure rate**.

| Item | Predeclared operational definition | Why it matters |
| --- | --- | --- |
| Urgent deadline-failure rate, U | 1 − urgent jobs completed on time / all urgent jobs *offered* to the bottleneck | Includes rejected, expired and late urgent jobs; no accepted-only denominator |
| Routine timely service-start, R(tau) | routine jobs started by arrival + tau / all routine jobs *offered* | Includes rejected work; does not silently equate service start with completion |
| Acceptance criterion | U ≤ epsilon AND R(tau) ≥ gamma | Epsilon, tau and gamma must be application-justified **before** held-out experiments |
| System | one non-preemptive fixed-capacity worker; finite waiting room; two externally trusted classes | No workload suppression, outage recovery, admission optimization, perfect duration oracle or multiworker placement |
| Mechanism test | equal admission rule and resources; count-based versus *measured* consumed-work protection | Diagnostic causal contrast, **not** a stand-alone invention claim |

The potential paper is an **explanatory and reproducible characterization of a constrained trade-off**, not a generic “new IoT priority algorithm.” Improvement is unproven, and a different metric combination alone is not a sufficient novelty argument.

**Step 1 checklist**
- [x] Read current RQ version 1.0 without changing its selected direction.
- [x] Fix offered-job denominators and the one-worker, finite-buffer, non-preemptive boundary.
- [x] Separate research questions from unproven method and result claims.
- [ ] Have the application domain justify epsilon, tau, gamma and queue capacity with evidence.

## Step 2 — Adversarial closest-prior-art matrix

**Overlap scale:** *High* = directly attacks the proposed central claim; *Medium* = already covers an important mechanism or subproblem; *Boundary* = theory applies only with substantial assumptions. This is qualitative reviewer judgment, not a bibliometric novelty score.

| Lead | Closely established result (verified reading level) | Overlap | Unsettled distinction / required action |
| --- | --- | --- | --- |
| **N01 Gonthier et al. (2025), ICPP** | Two-class **online, non-preemptive mixed-criticality** scheduling; critical-job deadlines and minimized maximum noncritical **flow time**; approximation/lower bound/heuristics; synthetic and real workload evaluation. ACM indexed full-text sections inspected, direct DOI-page open returned access error. | **High — central threat** | Its published model has task processing times supplied at release and permits homogeneous multiprocessors (including the single-worker case); assess its exact queue/admission assumptions and whether our finite-buffer, *offered-population service-start* constraints produce a genuinely distinct **finding**, not just renamed metrics. Faithfully compare the applicable EDF+FIFO/slack/backfill-style policies. |
| **N02 Tabatabaee & Le Boudec (2021), IEEE RTAS** | DRR with variable-size work, rigorously derived service/delay bounds and explicit mapping from packet→job and size→execution time. Full EPFL-hosted conference PDF: introduction, algorithm and mapping inspected; entire proof not independently checked. | **High for count-vs-work novelty; Medium for the complete RQ** | Work-aware fairness and bounds are old. Determine whether its arrival/service curves can bound the proposed routine waiting objective; never claim packet scheduling is categorically unrelated to real-time jobs. |
| **N03 Lenzini, Mingozzi & Stea (2004), IEEE/ACM ToN** | DRR latency/fairness/complexity trade-offs. Verified official identity/abstract and institutional author record; full paper not audited. | **Medium–High** | A generic switch from counting jobs to consumed service is **not** novelty. Read complete model before declaring a new accounting mechanism. |
| **N04 Dell'Amico, Carra & Michiardi (2016), IEEE Transactions on Computers** | Size-based fairness and sensitivity to inaccurate job-size estimates (PSBS). EURECOM journal record plus accessible primary-hosted manuscript sections; journal-version full-text parity unverified. | **Medium for RQ3** | Prediction error is not new. Their scheduling/processor-sharing model is not a drop-in single non-preemptive baseline; state differences clearly and avoid an oracle estimate advantage. |
| **N05 Hajek & Seri (2005), Mathematics of Operations Research** | Single-server online multiclass hard-deadline scheduling, explicit buffer complexity, lexicographic optimality, unit-length jobs. INFORMS publisher abstract and Illinois institutional record checked; full proof pending. | **High for multiclass/finite-queue framing** | Variable service times and routine **waiting budget** differ from unit-length lexicographic throughput, but must show that difference changes the answer. |
| **N06 Goldman, Parwatikar & Suri (2000), Journal of Algorithms** | Online non-preemptive single-resource admission under hard deadlines, jobs with heterogeneous lengths and maximum wait for start. Elsevier abstract/index record checked; full text pending. | **High for finite non-preemptive timing/admission aspects** | Its maximum-wait-to-start deadline and rejection are particularly relevant to our tau metric. Determine applicable guarantees/limits before portraying this as unstudied. |
| **R22 Madej et al. (2020), IEEE ICFEC** | Priority-based fair scheduling in edge computing. Retained completed review; original source identity in review register. | **Medium for RQ2** | Count-based routine protection and priority/fairness are established; need baseline fidelity. |
| **R08 Bittencourt et al. (2026), IEEE Access** | Semantic priority override for IoT emergency traffic, with scheduling/admission-related trade-offs. Retained completed review. | **Medium for application overlap** | Keep dispatch distinct from classification/admission; include a realistic urgency-based comparator. |
| **R26 Tang (2026), IoT** | IoT gateway finite admission/buffering trade-offs. Retained completed review. | **Medium for finite capacity** | Do not introduce admission control as an undeclared co-intervention. Explain why finite K matters with offered arrivals. |
| **R09 Lin et al. (2025), IEEE IoT Journal** | Real-time priority queueing for bursty traffic. Retained completed review. | **Medium–High for burst angle** | Burst-awareness by itself is not an original contribution; isolate offered burst shape and service-work load. |

**Most consequential finding:** N01 explicitly optimizes urgent deadlines against routine completion/flow, in a non-preemptive online setting. It defeats a **broad novelty claim** that nobody has jointly studied urgent-deadline protection and routine progress. N02/N03 defeat “work-aware fairness is new.” N04 defeats “service-time estimation sensitivity is new.” N05/N06 weaken novelty based solely on finite buffers, deadlines, or rejection accounting.

**Differences are hypotheses, not established gaps:** The combined evaluation of **source-offered urgent failures**, **routine start-within-tau**, **finite queue loss**, **bursty variable service work** and **equal-information non-preemptive policies** is a reasonable *conditional* study focus. Existing results could still cover it after proper model reduction or a stronger comparator. “IoT” in the title and a new metric do not, alone, create novel research.

**Step 2 checklist**
- [x] Inspect all retained reviews through existing synthesis and register.
- [x] Identify verified central threats, including N01–N06 not previously in the active 19.
- [x] Record publisher/DOI identities and exact reading limits; keep leads separate from completed reviews.
- [x] Reject generic priority, DRR, estimation-error and “no one combined both objectives” claims.
- [ ] Complete N01 and N02 model/proof-to-RQ mapping; N03/N05/N06 full-text checks where accessible.
- [ ] Run independent database search and forward/backward citation chasing with explicit screening counts.

## Step 3 — RQ-by-RQ verdict and falsification tests

| Current RQ | Reviewer verdict | Evidence that could make it publishable | Immediate falsifier / scope revision trigger |
| --- | --- | --- | --- |
| **RQ1: regimes/limits** | **Conditional, not yet novel.** Likely overlaps queue overload, DRR bounds, existing mixed-criticality trade-offs. | An accurately bounded **new** regime boundary or robust, application-relevant finding that existing theory and comparators do **not** already predict, with explicit offered-denominator analysis. | A prior bound explains all observed transitions; frontier is just one arbitrary parameter sweep; feasibility budgets chosen after seeing outcomes. |
| **RQ2: mechanism** | **Important experiment, not a novelty claim.** Count and work accounting already well established. | Controlled attribution under matched resources, arrival traces, measurement availability and tuning; report effects, including when no advantage exists. | Results disappear against DRR/EDF+FIFO/strong aging baselines or are caused by different admission decisions, oracle durations or under-tuned comparators. |
| **RQ3: realism/cost** | **Necessary validation, not automatically novel.** Size estimation error is well studied. | Evidence for a **specific operational consequence** of information constraints/overhead in the chosen domain, tied back to the constrained RQ1 frontier. | Claimed gain requires unobservable exact processing times, ignores overhead or relies on one favorable synthetic error model. |

**Candidate contribution statement — NOT READY for an abstract:** “We empirically characterize the regimes in which timely routine *service start* is possible at a specified *offered urgent-deadline-failure* budget for a finite-capacity, non-preemptive IoT processing bottleneck, and show which conventional policy and information constraints explain the trade-off.” This must be **withdrawn or narrowed** if N01/N02/N05/N06 already cover its substantive result.

**Formal go/no-go criterion (after evidence):**
1. **Prior-art non-equivalence:** an exact table shows why closest results cannot answer the proposed claim under matching assumptions, or reproducing them reveals a materially new boundary.
2. **Fair comparator:** a strong established policy does not already explain/achieve the claimed benefit under equal information, offered work, capacity and tuning.
3. **Credible utility:** application-derived deadlines/queue budgets; measured/reasonable service-time distributions; non-negligible effect with uncertainty; failure regimes disclosed.
4. **Reproducibility:** simulator/lifecycle invariants tested, code and trace-generation seeds reported, full negative and positive results.

If any gate fails, **reframe** the question or report negative findings honestly; do not retrofit a “novel algorithm” adjective.

**Step 3 checklist**
- [x] Express positive and negative novelty tests for all three RQs.
- [x] Set an explicit stop/reframe criterion.
- [x] Identify N01 as the top-priority full-text competitor.
- [ ] Supervisor/team sign-off of the conditional contribution after theory comparison.
- [ ] No claim of original algorithm or Best Paper likelihood has been made.

## Step 4 — Minimal fair experimental protocol (design only, NOT executed)

1. **Application credibility:** specify a real local processing step (not broker/network delay); collect/anonymize service-time and arrival-burst samples or identify a defensible trace source. Justify urgent absolute deadline, tau and epsilon/gamma **in advance**. Do not invent clinical/safety guarantees.
2. **Model and invariants:** single busy/idle worker, capacity K for *waiting* jobs, FIFO tie rule, explicit expiry policy, deterministic service completions; preserve offered = rejected + admitted and admitted = completed + expired/cancelled + unresolved. Decide whether a started job is allowed to finish after its deadline; count outcome consistently.
3. **Baselines:** FIFO, strict urgent-priority with within-class FIFO, urgent-EDF + routine-FIFO, simple aging/bounded-wait priority, conventional weighted/deficit service fairness, and a faithfully **adapted** N01 deadline/slack comparator wherever its input requirements are met. **Classic DRR uses known head-of-line job size for eligibility**: if unstarted processing time is unknown, never supply its true future duration. Treat completion-accounted class budgets as an explicitly labeled *adaptation*, and evaluate any oracle-DRR only as an unattainable reference. Do not label a preemptive PSBS or clairvoyant backfilling policy as an equivalent deployable baseline. Show exact information available to each policy.
4. **Ablations:** count-based vs **completed-job measured work**; learned/predicted work only as a separate explicitly labeled variant; matched rejection rule (but disclose occupancy-induced differences in the actually admitted population). Use service-cost overhead measured outside simulator bookkeeping where possible.
5. **Workloads:** independently vary burst correlation/intensity, urgent share, processing-time variance/heavy tails, deadline slack and K; isolate variability while holding **mean offered service work** fixed. Include low-load, stable, overload and adversarial blocking regimes.
6. **Outcome integrity:** U over *all offered urgent*, R(tau) over *all offered routine*, admission/rejection rates, urgent deadline outcomes, routine completion and waiting-time distributions, per-class consumed-work share, decision-time and memory. Follow deadlines/waiting windows to completion or report censored cases; do not treat end-of-run censoring as observed failure.
7. **Statistical protocol:** identical offered traces/seeds for paired comparisons, multiple **independent** trace replications, held-out test scenarios after tuning, uncertainty intervals over independent runs (not individual jobs), multiplicity/selection caveats and no cherry-picked winner cases. State effect-size threshold before interpreting practical significance.
8. **Reproducibility tests:** conservation under arrivals/rejections/expiry, finite-capacity bound, single-worker non-overlap, deadline accounting, same offered trace across policies, no future-information access. Write failures as test cases first.

**Step 4 checklist**
- [x] Establish a concrete design-quality protocol with non-oracle baselines and falsification.
- [ ] Obtain real workload evidence and predeclared targets.
- [ ] Complete competitor model reduction and choose exact baseline adaptations.
- [ ] Pre-register parameters, hypotheses, tuning split and statistical analysis.
- [ ] Implement validated simulation and run independent experiments.
- [ ] Confirm contribution from held-out results; only then prepare submission.

## Step 5 — Decision and next actions

**Current decision: KEEP research-questions.md v1.0 as the working direction, but DO NOT claim established novelty or start an elaborate new algorithm.** The next work item is a careful *N01-vs-our-RQ* model comparison (task duration available at arrival? single worker? rejection/finite buffer? objective? online information? constraints and baselines), followed by N02 network-calculus applicability and N05/N06 full-text coverage. A clean implementation cannot substitute for this gate.

| Milestone | Status | Exit evidence |
| --- | --- | --- |
| M1 — RQ/scope and metric definitions | **Done (provisional domain budgets)** | RQ v1.0 with U/R(tau) boundary |
| M2 — Focused adversarial novelty screening | **Done; limited evidence coverage** | This matrix, verified identities, reading-level flags, search log |
| M3 — Closest-paper full-text/model equivalence | **Blocked / pending reading** | N01/N02/N03/N05/N06 side-by-side formulation; explicit conclusion |
| M4 — Independent database/citation search | **Pending** | Search strings, dates, results, exclusions, forward/backward records |
| M5 — Application and service-level budgets | **Pending** | Measurements or justified traces, epsilon/tau/gamma, K |
| M6 — Pre-registered evaluation specification | **Pending** | Final baselines, workload grid, integrity tests and statistics |
| M7 — Validated experiments | **Not started** | Trace/seed ledger, executed tests, charts, confidence intervals |
| M8 — Contribution/supervisor decision | **Not ready** | Go/no-go memo against prior art, paper contribution phrasing |

**Step 5 checklist**
- [x] Keep current RQ v1.0 unchanged while documenting newly found novelty threats.
- [x] Mark novelty claim and algorithm selection as unresolved.
- [x] Identify closest-paper/model comparison as the next research gate.
- [ ] Complete N01/N02/N05/N06 crosswalk and supervisor review.
- [ ] Decide final contribution and move to pre-registration only if it survives the gate.

### Audit limitations and integrity statement

“Rigorous” here means **explicit competing hypotheses, source-backed prior-art challenges, operational definitions, falsification, reproducibility gates and a reproducible *partial* search trail**. This is **not** a completed systematic literature review or a conclusive proof that no similar paper exists. Some results are verified only at abstract/targeted-section level; full-text proofs and exhaustive searches remain open. No simulations were executed and no performance percentages or publication-award probabilities are implied.

## Verified research references and source access

Only authenticated publisher/academic-institution or author-hosted identities are listed. The reading status above must travel with any paper comparison.

1. **N01.** Gonthier, Maxime; Chard, Kyle; Foster, Ian; Marchal, Loris; Vivien, Frédéric. (2025). **Deadline-Aware Scheduling of Mixed-Criticality Tasks.** *Proceedings of the 54th International Conference on Parallel Processing (ICPP '25)*, pp. 178–187. **ACM.** DOI: https://doi.org/10.1145/3754598.3754639 . [ACM publisher page](https://dl.acm.org/doi/10.1145/3754598.3754639). **Relevance:** same urgent-deadline/routine-service trade-off in non-preemptive online jobs; primary high-risk competitor.
2. **N02.** Tabatabaee, Seyed Mohammadhossein; Le Boudec, Jean-Yves. (2021). **Deficit Round-Robin: A Second Network Calculus Analysis.** *2021 IEEE 27th Real-Time and Embedded Technology and Applications Symposium (RTAS)*, pp. 171–183. **IEEE.** DOI: https://doi.org/10.1109/RTAS52030.2021.00022 . [EPFL proceedings PDF](https://infoscience.epfl.ch/bitstreams/e0172e0b-b99c-43cc-9488-31afda35f1fa/download). **Relevance:** known variable-work fairness and delay bounds; explicitly maps packet to real-time job.
3. **N03.** Lenzini, Luciano; Mingozzi, Enzo; Stea, Giovanni. (2004). **Tradeoffs between low complexity, low latency, and fairness with deficit round-robin schedulers.** *IEEE/ACM Transactions on Networking*, 12(4), 681–693. **IEEE/ACM.** DOI: https://doi.org/10.1109/TNET.2004.833131 . [IEEE record](https://ieeexplore.ieee.org/document/1331430/). **Relevance:** work-aware round-robin trade-offs are prior art.
4. **N04.** Dell'Amico, Matteo; Carra, Damiano; Michiardi, Pietro. (2016). **PSBS: Practical Size-Based Scheduling.** *IEEE Transactions on Computers*, 65(7), 2199–2212. **IEEE.** DOI: https://doi.org/10.1109/TC.2015.2468225 . [EURECOM academic record](https://www.eurecom.edu/en/publication/4449). **Relevance:** estimator-error and fairness prior art; model is not an equivalent non-preemptive comparator.
5. **N05.** Hajek, Bruce; Seri, Pierre. (2005). **Lex-Optimal Online Multiclass Scheduling with Hard Deadlines.** *Mathematics of Operations Research*, 30(3), 562–596. **INFORMS.** DOI: https://doi.org/10.1287/moor.1040.0144 . [INFORMS publisher page](https://pubsonline.informs.org/doi/10.1287/moor.1040.0144). **Relevance:** finite-buffer online single-server multiclass/deadline optimality (unit work).
6. **N06.** Goldman, Sally A.; Parwatikar, Jyoti; Suri, Subhash. (2000). **Online Scheduling with Hard Deadlines.** *Journal of Algorithms*, 34(2), 370–389. **Elsevier.** DOI: https://doi.org/10.1006/jagm.1999.1060 . [Elsevier publisher page](https://www.sciencedirect.com/science/article/pii/S019667749991060X). **Relevance:** online single-server non-preemptive jobs with length, rejection and allowed waiting to start.
7. **R22.** Madej, Arkadiusz; Wang, Nan; Athanasopoulos, Nikolaos; Ranjan, Rajiv; Varghese, Blesson. (2020). **Priority-based Fair Scheduling in Edge Computing.** *2020 IEEE 4th International Conference on Fog and Edge Computing (ICFEC)*, pp. 39–48. **IEEE.** DOI: https://doi.org/10.1109/ICFEC50348.2020.00012 . **Relevance:** existing priority/class-fairness edge scheduling.
8. **R08.** Bittencourt, João Carlos N.; Portugal, Paulo; Vasques, Francisco; Costa, Daniel G. (2026). **Multi-Tier Message Scheduling for IoT-Based Urban Emergency Systems Through Semantic Priority Override.** *IEEE Access*, 14, 140988–141015. **IEEE.** DOI: https://doi.org/10.1109/ACCESS.2026.3732592 . **Relevance:** IoT emergency priority/admission overlap.
9. **R26.** Tang, Shensheng. (2026). **Reliability-Aware Admission Threshold Selection for IoT Gateway–Cloud Systems: Trade-Off-Driven and Constraint-Based Approaches.** *IoT*, 7(3), article 60. **MDPI.** DOI: https://doi.org/10.3390/iot7030060 . **Relevance:** finite IoT gateway admission/overload trade-offs.
10. **R09.** Lin, Rongping; Zhang, Jinpeng; Luo, Shan; Fu, Jing; Wang, Xiong; Li, Hui; Zukerman, Moshe. (2025). **Real-Time Priority Queue Scheduling for Bursty Traffic.** *IEEE Internet of Things Journal*, 12(24), 55883–55892. **IEEE.** DOI: https://doi.org/10.1109/JIOT.2025.3627212 . **Relevance:** burst-aware priority queueing is not itself new.

**Linked project material:** [RQ v1.0](research-questions.md) · [full review register](../README.md) · [search trail](../search-log.csv) · [overall step-by-step tracker](research-progress-checklist.md).
