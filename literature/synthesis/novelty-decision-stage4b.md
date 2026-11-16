# Stage 4B — Adversarial novelty decision and analytical reductions

**Date:** 16 November 2026 · **Decision:** **REVISE / NARROW (research direction may proceed to a *requirements + baseline pilot*, not to an algorithm-novelty claim).**  
**Status:** Targeted primary-source checks and the model-independent algebra below are complete. **A definitive no-prior-publication/theorem-subsumption sign-off is NOT complete**; restricted full texts, independent database export/citation chasing, application evidence and supervisor review remain open.  
**Subject:** [RQ v1.0](research-questions.md) · [Stage 4A](closest-paper-model-crosswalk.md) · [progress checklist](research-progress-checklist.md) · [query/source provenance](../search-log.csv).

> **One-line reviewer conclusion:** Keeping offered urgent deadline failures under a declared budget while improving routine start access in a finite, non-preemptive, online queue is a valid *experimental problem*. It is **not yet a defensible original scheduling concept**. The start-time metric, finite buffer, admission losses, urgent/routine priorities, and service-information limits all have close prior-art antecedents.

## 4B.1 — Scope and exact claim to be falsified

Current model: one non-preemptive worker; at most **K waiting** jobs (besides a possible running job); online urgent/routine offered arrivals; unknown exact duration of **unstarted** work; class-neutral reject-on-full admission. Let $a_i$ be arrival time, $s_i$ service start, $p_i>0$ uninterrupted processing time, $c_i=s_i+p_i$ completion and $d_i$ urgent completion deadline.

- **U:** (urgent offered jobs that were rejected, expired or completed after $d_i$) / (urgent offered jobs).
- **R(τ):** (routine offered jobs that began service by $a_i+\tau$) / (routine offered jobs).
- **Decision question:** For declared $\epsilon,\tau,\gamma$, is there a feasible and worthwhile $U\leq\epsilon,\ R(\tau)\geq\gamma$ operating region, compared with credible *matched-information, matched-capacity* prior policies?
- An empty urgent or routine offered population has an **undefined** corresponding empirical rate (N/A), not a convenient zero; predeclare exclusion/aggregation.

The study is **conditional and empirical** unless a genuinely new theorem/method is shown. “IoT” in a title and an unusual combination of metrics are not enough to establish scholarly novelty.

**Checkpoint 4B.1**
- [x] Preserve the selected RQ v1.0 and exact offered-population endpoints.
- [x] Specify what would count as a distinctive contribution (generalizable explanation or demonstrated practical gap, not a new label for a classic metric).
- [ ] Validate actual IoT device/application service boundary, urgency, arrival process and job-duration information.

## 4B.2 — Analytical reductions and unavoidable limits

### Reduction A: routine *start* deadline is a job-dependent *completion* deadline

For each **admitted, fully processed, uninterrupted** routine job,

$$
 c_i=s_i+p_i,\qquad
 (s_i-a_i\leq\tau)\iff(c_i\leq a_i+\tau+p_i).
$$

So define a synthetic routine completion deadline $D_i^{R}=a_i+\tau+p_i$. The Boolean indicator for routine *start by τ* equals that for routine *completion by the synthetic deadline*. Set **both indicators to false for rejected/offered-but-never-started jobs**. This preserves the offered denominator **under the explicit same-population conventions**.

**Important qualifications:**
1. This is an **algebraic, per-job outcome reduction**, **not** an executable information-preserving reduction when $p_i$ is unknown at dispatch. The synthetic deadline cannot be constructed online from an unknown $p_i$; it can be used post hoc when true processing time is observed.
2. Interruptions, preemption, cancellation after start, partial work and unknown counterfactual processing time for rejected jobs require amended semantics; for rejected jobs use the categorical failed indicator, **not an invented $p_i$**.
3. The equivalence of success indicators does **not** make the optimization of an offered proportion identical to minimizing **maximum flow time** (N01) or a class-specific lexicographic throughput objective (N05). It does remove “a new start-deadline formulation” as a safe novelty claim.
4. N01 is especially close: it already treats critical completion deadlines and routine flow, and uses artificial deadline ideas. N06 directly studies maximum waits until service *start* for non-preemptive online jobs.

**Reviewer verdict:** **REJECT** a claim that routine start within a waiting budget is an unstudied deadline concept.

### Bound B: instantaneous finite-buffer overload

Suppose the worker is initially idle, K is the count of **waiting positions**, $n$ urgent jobs arrive as one admission wave, **no job completes during that wave**, and there is no external holding reservoir. The local system can retain at most $K+1$ jobs (one running plus K waiting). At least $\max(0,n-K-1)$ urgent offers cannot be processed from that batch under the declared no-overflow policy, so the batch's offered urgent failure rate satisfies

$$
 U_{\rm batch}\geq\frac{\max(0,n-K-1)}{n}\quad(n>0).
$$

This says nothing universal about the overall empirical U if other batches are included or if upstream backpressure delays the boundary. **Not a new theorem**: it is a conservation/finite-capacity feasibility check.

### Bound C: remaining non-preemptive blocking time

If an urgent job arrives while another job is running with remaining time $b\geq0$, urgent processing needs $p_u$, and its remaining relative deadline is $\delta_u=d_u-a_u$, then

$$
 b+p_u>\delta_u\quad\Longrightarrow\quad
 \text{the urgent job must miss its completion deadline, even if dispatched next.}
$$

This is a *necessary* miss condition for a single non-preemptive worker. The scheduler might cause other misses even when this inequality does not hold. **Not novel**; use it as a sanity-check/test invariant and as a source of explained infeasibility, never as a universal algorithmic lower-bound contribution.

### Counterexample against an overstrong reduction

Even for one routine job arriving at a=0 with p=100 and τ=10, starting at s=0 versus s=9 gives the same R(τ)=1, while its flow time (c−a) is 100 versus 109. A thresholded success indicator discards flow-time magnitude. More generally, different policies can have identical R(τ) and different maximum routine flow. **Thus N01's maximum-flow objective and R(τ) are not the same mathematical objective**, but different metrics alone do **not** demonstrate novelty.

**Checkpoint 4B.2**
- [x] Establish the conditional start-to-completion deadline algebra exactly.
- [x] Distinguish ex-post outcome equivalence from online implementability with unknown $p_i$.
- [x] State narrow finite-buffer and blocking feasibility checks with assumptions.
- [x] Separate metric non-equivalence from evidence of conceptual novelty.
- [ ] Obtain complete primary texts/proofs required to determine whether any claimed *new result* follows from established guarantees.

## 4B.3 — Targeted additional primary-source threats

The following are **verified source identities and limited model-level readings**, **not four new completed 19-paper-style full reviews**:

| ID | Publisher-authenticated paper and what was actually checked | Specific overlap | Limitation / next check |
| --- | --- | --- | --- |
| **N07** | **Shunji Tanaka; Bertrand M. T. Lin (2025).** “Single-Machine Scheduling to Minimize the Size of Input Buffer.” *Naval Research Logistics* **72**(6), 810–824. **Wiley**. DOI [10.1002/nav.22256](https://doi.org/10.1002/nav.22256). **Open full publisher HTML**, abstract, model and section description examined. | Single non-preemptive machine with input-buffer occupancy/release-time reasoning; finite-buffer-only originality is indefensible. | Optimizes minimum required buffer size with known job attributes; **not** our online urgent-failure/routine-access objective. Do not copy its NP-hardness to our model. |
| **N08** | **Hyeongboo Baek; Namyong Jung; Hoon Sung Chwa; Insik Shin; Jinkyu Lee (2018).** “Non-Preemptive Scheduling for Mixed-Criticality Real-Time Multiprocessor Systems.” *IEEE Transactions on Parallel and Distributed Systems* **29**(8), 1766–1779. **IEEE**. DOI [10.1109/TPDS.2018.2806443](https://doi.org/10.1109/TPDS.2018.2806443). **IEEE abstract/model summary** examined. | Non-preemptive mixed-criticality deadline-aware scheduling already extensively studied. | Multi-processor MC schedulability/virtual deadlines; **not** the same one-worker offered-job drop-fraction objective. Full methods not reviewed. |
| **N09** | **Panayotis D. Sparaggis; Don Towsley (1994).** “Optimal Routing and Scheduling of Customers with Deadlines.” *Probability in the Engineering and Informational Sciences* **8**(1), 33–49. **Cambridge University Press**. [Official issue/abstract](https://www.cambridge.org/core/journals/probability-in-the-engineering-and-informational-sciences/issue/F781E552A4A3B17462969AEBBF2B7AC5); DOI [10.1017/S0269964800003181](https://doi.org/10.1017/S0269964800003181). **Cambridge original volume, abstract and issue reviewed**, article full text gated. | **Strong new threat**: finite buffer, service-start **or** service-completion deadlines, loss via buffer overflow vs deadline, scheduling/routing. | Parallel homogeneous stations, exponentially distributed times/deadlines, stochastic loss optimum; not an established single-worker unknown-$p_i$ routine/urgent comparison. Check the full paper before any “first to combine buffer + start deadlines + losses” claim. Note: **1994 print** despite Cambridge “online 2009” metadata. |
| **N10** | **Xinshang Wang; Van-Anh Truong (2017 online; 2018 volume).** “Multi-Priority Online Scheduling with Cancellations.” *Operations Research* **66**(1), 104–122. **INFORMS**. DOI [10.1287/opre.2017.1653](https://doi.org/10.1287/opre.2017.1653). **Publisher abstract/metadata** examined. | Online jobs at differentiated priorities, waiting losses/cancellations, performance/cost trade-off. | The paper includes costly optional overtime, and uses total cost under stochastic arrival and cancellations; does not establish identical finite K + urgent deadline and routine τ constraints. Full model pending. |

**Existing still-highest priority comparator set** (see [Stage 4A](closest-paper-model-crosswalk.md), with exact provenance):
- **N01:** Maxime Gonthier; Kyle Chard; Ian Foster; Loris Marchal; Frédéric Vivien (2025). “Deadline-Aware Scheduling of Mixed-Criticality Tasks.” *Proceedings of the 54th International Conference on Parallel Processing*, 178–187. **ACM**. [DOI 10.1145/3754598.3754639](https://doi.org/10.1145/3754598.3754639). ACM indexed model and coauthor-hosted 24-slide presentation; full text pending.
- **N02:** Seyed Mohammadhossein Tabatabaee; Jean-Yves Le Boudec (2021). “Deficit Round-Robin: A Second Network Calculus Analysis.” *IEEE 27th Real-Time and Embedded Technology and Applications Symposium*, 171–183. **IEEE**. [DOI 10.1109/RTAS52030.2021.00022](https://doi.org/10.1109/RTAS52030.2021.00022). Original IEEE PDF checked, no proof reproduced.
- **N05:** Bruce Hajek; Pierre Seri (2005). “Lex-Optimal Online Multiclass Scheduling with Hard Deadlines.” *Mathematics of Operations Research* **30**(3), 562–596. **INFORMS**. [DOI 10.1287/moor.1040.0144](https://doi.org/10.1287/moor.1040.0144). Author PDF model and algorithm sections checked, no complete proof reproduction.
- **N06:** Sally A. Goldman; Jyoti Parwatikar; Subhash Suri (2000). “Online Scheduling with Hard Deadlines.” *Journal of Algorithms* **34**(2), 370–389. **Elsevier**. [DOI 10.1006/jagm.1999.1060](https://doi.org/10.1006/jagm.1999.1060). Publisher abstract + university report metadata only.

**Search limits:** targeted public web searches were executed and logged in [search-log.csv](../search-log.csv), including publisher-site checks and related-model queries. This is **not** a PRISMA systematic literature review, exhaustive independent Scopus/IEEE Xplore/ACM export, citation graph, or reproducible corpus with hit counts.

**Checkpoint 4B.3**
- [x] Verify four additional authentic publisher-level leads, distinguishing 1994 print from 2009 online metadata.
- [x] Identify N09 as a strong direct warning against buffer/start-deadline/loss novelty.
- [x] Record evidence level rather than treating an abstract as a full methodological review.
- [ ] Obtain N01, N03, N06, N09 authorized full text and inspect exact theorem/applicability; N08/N10 are secondary-depth checks if mechanism requires them.
- [ ] Independently search Scopus + IEEE Xplore + ACM DL with saved result counts, and perform backward/forward citation chasing of N01/N05/N06/N09.

## 4B.4 — Decision gates and the exact defensible wording

| Candidate novelty claim | 4B verdict | Reason |
| --- | --- | --- |
| “First priority-aware IoT scheduler to protect routine service under urgent deadlines” | **REJECT** | N01, N05, N08 and many older models already cover critical/non-critical trade-offs or multiclass deadlines. |
| “First finite-K online system to account for deadline misses and rejected offers” | **REJECT** | N05 and N09 directly discuss capacity/drop/deadline phenomena; any narrower claim requires proof, not an absence assertion. |
| “Start by τ is a new deadline formulation” | **REJECT** | Reduction A and N06, N09. |
| “Consumed-work vs count-aware fairness is intrinsically new” | **REJECT** | DRR and long-standing service/delay analyses already make work accounting established. |
| “A new universal impossibility result follows from finite K or non-preemption” | **REJECT** | Bounds B and C are elementary; universal bounds need stronger assumptions and nontrivial proof. |
| “A reproducible finite-buffer offered-population *empirical operating-region* comparison with unknown pre-service durations and honest overhead may yield useful new evidence” | **CONDITIONAL, unproven** | Could be contribution only if application requirements and controls exist and matched strong baselines leave a clear, transferable insight. |
| “We have validated an original algorithm/theorem” | **NO-GO NOW** | No proposed formal novelty mechanism, proof or pilot evidence. |

### Recommended narrow claim **for proposal only**

> We investigate how finite waiting capacity, burst structure and unavailable pre-service execution times affect the observed trade-off between offered urgent-deadline failures and offered routine timely-start access, under carefully matched online scheduling baselines in a declared IoT processing application. We report when declared service budgets can or cannot be met within the evaluated policy family, without claiming an optimal algorithm or universal impossibility theorem.

**Use “investigate” and “observed”**, not “first”, “guarantees”, “optimal” or “solves starvation”. A no-benefit outcome against a strong baseline remains a scientifically honest result, but may need a different venue/contribution.

### Falsifiable Go / Revise / No-Go rule

- **GO to a bounded *pilot* (not submission):** actual application and transparent thresholds; at least FIFO, strict priority, EDF+FIFO, aging, suitable DRR/work-fair adaptation and a faithful applicable N01-style comparator; matched offered traces, same K/admission policy, identical available information and overhead charged.
- **REVISE further:** only differences are metric naming; count/work effects disappear under matched service information; the “new” policy is an unacknowledged old algorithm; or study still relies on invented thresholds.
- **NO-GO for an algorithm novelty paper:** established prior model strictly subsumes claimed method/results, or conventional baselines match/dominates at comparable urgent failure and runtime cost on valid independent workloads. A negative empirical observation is **not** a proof of all-policy dominance.

**Overall decision:** **REVISE/NARROW the potential *contribution claim*; preserve RQ v1.0 as a working research question pending supervisor decision.** Do **not** begin authoring “novel scheduler” code now. A small baseline-only feasibility pilot after Stage 5+6 protocol is legitimate.

**Checkpoint 4B.4**
- [x] Record explicit claim-by-claim accept/reject/conditional verdicts.
- [x] Produce an honest supervisor-facing narrowing statement and falsifiers.
- [x] Avoid changing the frozen research question or preselecting an algorithm.
- [ ] Supervisor approves the narrowed contribution direction.
- [ ] Complete the full-paper/database/citation checks needed for definitive novelty clearance.

## Next handoff — Stage 5 and Stage 6 preparation

**Blocker to unblock next:** choose **one actual IoT context** (e.g., local gateway alert classification/notification, industrial safety event handler, or clinical telemetry ingestion) only if its *own* event trace, processing semantics and deadline budget can be defended. Define the local queue arrival boundary, K waiting positions, one-worker model, per-class offered rate/bursts, duration distribution, start/completion timestamps and actual deadline origin.

1. Write **application-and-threshold provenance memo**: operational need for $\epsilon,\tau,\gamma$, and sensitivity ranges.
2. Produce a **baseline equivalence protocol** before comparing mechanisms.
3. Bring the Stage 4B decision and high-threat N01/N06/N09 to the supervisor, along with gated full-text requests.

**Stage 5 checkpoint**
- [ ] One real application and permitted trace/synthetic calibration basis.
- [ ] Explicit start-vs-completion semantics, K and deadline origin.
- [ ] Justified budgets and predeclared sensitivity ranges.
- [ ] Supervisor review and 4B full-text/database sign-off.
