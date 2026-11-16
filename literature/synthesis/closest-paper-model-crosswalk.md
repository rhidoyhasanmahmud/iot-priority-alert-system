# Stage 4A — Closest-paper model-equivalence crosswalk

**Date:** 16 November 2026 · **State:** primary-source **model crosswalk completed to the stated reading levels**; full-paper/equivalence-proof sign-off still **OPEN**.  
**RQ being tested:** [conference RQ version 1.0](research-questions.md) · **Independent context:** [novelty audit](novelty-assessment.md) · **Progress tracker:** [checklist](research-progress-checklist.md).

**Decision:** **Do not claim a new scheduling concept, a proven research gap, or a new algorithm yet.** There is a credible but unproven *conditional empirical question* concerning finite queue drops and **offered-job** urgent-failure/routine-service-start outcomes, with unknown unstarted-job duration. This paper must earn its contribution by beating/explaining established policies under matched information and by demonstrating that existing theory does not already settle the relevant result.

## Step 4A.1 — Source access and review precision

| ID | Authenticated source inspected | Verified reading level | What remains |
| --- | --- | --- | --- |
| **N01 Gonthier et al., ICPP 2025** | [ACM-publisher indexed article sections](https://doi.org/10.1145/3754598.3754639); [24-slide author presentation hosted by co-author Loris Marchal](https://perso.ens-lyon.fr/loris.marchal/scheduling-in-montreal/slides/maxime.pdf), slides 5–8, 12–13, 15–23 | **Substantive model, objective, algorithm and result cross-check** from primary author slides + ACM indexed text; **not** a complete independent review of the proceedings PDF | [Author-deposited HAL version](https://inria.hal.science/hal-05190988v1/file/main.pdf) identified, but its host returned an anti-bot access denial; the paper's complete formulas, proofs and evaluation details require authorized full-text reading |
| **N02 Tabatabaee & Le Boudec, IEEE RTAS 2021** | [EPFL-hosted original IEEE proceedings](https://infoscience.epfl.ch/bitstreams/e0172e0b-b99c-43cc-9488-31afda35f1fa/download), pp. 171–175 and theorem/assumption text | **Original PDF checked**: arrival/service curves, DRR algorithm and packet→real-time-job mapping, Theorems 1–3 assumptions; proofs **not** independently reproduced | Determine analytically how any bound translates to the proposed finite-K drop-and-wait budget before claiming a new bound |
| **N03 Lenzini, Mingozzi & Stea, IEEE/ACM ToN 2004** | [IEEE publisher record](https://ieeexplore.ieee.org/document/1331430/), [University of Pisa institutional abstract](https://arpi.unipi.it/handle/11568/202043) | Identity/abstract and historical latency/fairness trade-off **only** | Complete paper/model proof or accepted author version before a new work-accounting claim |
| **N04 Dell'Amico, Carra & Michiardi, IEEE TC 2016** | [EURECOM institutional journal record](https://www.eurecom.edu/en/publication/4449) and author-hosted manuscript (as documented in audit) | Verified predictor-error/fairness relevance; not an equivalent fixed non-preemptive system | Complete model only if prediction becomes an active RQ3 mechanism |
| **N05 Hajek & Seri, Mathematics of Operations Research 2005** | [Author-hosted paper](https://hajek.ece.illinois.edu/Papers/HajekSeri05.pdf), especially Sections 1–2, Dlex and the buffer theorem; [INFORMS journal record](https://pubsonline.informs.org/doi/10.1287/moor.1040.0144) | **Original primary paper sections inspected**; 1-server/1-slot job model, lexicographic priority, dropping, deadlines, finite buffer requirements. Formal proof **not independently validated** | Finish full proof/limit mapping, in particular the variable-service-time case |
| **N06 Goldman, Parwatikar & Suri, Journal of Algorithms 2000** | [Elsevier journal abstract](https://www.sciencedirect.com/science/article/pii/S019667749991060X), [1998 university technical-report record](https://repository.library.washu.edu/cse_research/474/) | Primary publisher + university abstract **only**: non-preemptive single server, arbitrary lengths, admitted/rejected jobs and maximum allowed wait until service start | The university PDF returned a download error; obtain full report/journal text via approved scholarly access for theorem applicability |

**Important distinction:** an author slide can verify what the team *presented*, not the exact theorem conditions and all caveats of a published paper. A reported bibliographic DOI never means the entire work was read.

### Checklist — Source access
- [x] Obtain and inspect a first-party technical presentation for N01 (instead of guessing from its title).
- [x] Inspect N02 original IEEE proceedings PDF and real-time-job mapping.
- [x] Inspect N05 author-hosted full-paper definitions and algorithm.
- [x] Check N06 original publisher and institutional report records.
- [ ] Read full N01 proceedings PDF under permitted access; verify claims section by section.
- [ ] Read N03/N06 full paper or authorized equivalent and document exact theorem hypotheses.

## Step 4A.2 — N01 vs selected RQ, dimension by dimension

N01: Gonthier, Chard, Foster, Marchal and Vivien (2025), *Deadline-Aware Scheduling of Mixed-Criticality Tasks*, ACM ICPP; **closest current competitor**. Do not use the phrase “first to balance urgent deadlines and routine work.”

| Dimension | N01 documented from primary slides / indexed paper | Our RQ v1.0 | Reviewer equivalence judgment |
| --- | --- | --- | --- |
| Underlying issue | Mixed criticality, online arrivals, no preemption/checkpointing | Urgent vs routine local processing, online, no preemption | **Direct substantive overlap** |
| Resources | A homogeneous pool of ell processors; paper has a single-processor subcase | Exactly **one** fixed-capacity worker | “Single worker” alone is **not novel**; their theory often has ell = 1 |
| Processing jobs | Release time r, task length **p**, deadline d or none; processing information included in task description at release | Class, arrival/deadline and completed-job service measurements; **no exact future duration of unstarted jobs** in deployable policies | **Information mismatch can matter**; verify exact N01 online observability in full paper |
| Urgent objective | Maximize number of critical tasks completed on time; aim to complete all, with workload-level feasibility/success reported | **U = 1 − on-time urgent completions / urgent jobs offered**; satisfy U ≤ epsilon | Related but not identical constraint. N01 includes feasible-instance/success analysis; cannot claim it “does not consider failures.” |
| Routine objective | Minimize **maximum routine flow time**, including time spent in service | Maximize fraction of **offered** routine jobs started within tau (R(tau) ≥ gamma) | **Mathematically non-equivalent metrics**; see example below. Metric change alone is not novelty. |
| Queue/buffer | Slides and accessed text do **not establish** an explicit finite waiting cap K or a class-neutral reject-on-full rule | Finite K (waiting slots), rejected work stays in offered denominators | **Candidate model distinction, unresolved.** Absence from slides is not evidence of absence in full paper. |
| Primary algorithm | Greedy-Slack, temporal shifting, EDF+FIFO, static provisioning and lower bound | No algorithm selected; classic non-oracle baselines required | **Must compare** an honest compatible EDF+FIFO and slack-policy adaptation |
| Evaluation | Synthetic and real traces, online/offline success and maximum flow; author slides report a computation-overhead case and successful-instance statistics | Offered urgent failure budget, routine timely starts, rejected/expired/unfinished outcomes and measured overhead | **Different focus, but do not claim predecessor ignored failure or overhead** |
| Domain | HPC/cloud tasks with disclosed release, duration and deadline; example practical cases | Local IoT application-processing bottleneck | Domain label alone **not novelty**; must show changed operational assumptions/results |

**Counterexample showing two routine objectives are not identical (not evidence of originality):**

At time 0, two routine jobs arrive. Their non-preemptive durations are **1** and **10** time units. Waiting budget **tau = 1**; queue is large enough for both.

- **Short-first:** service starts at t = 0 and t = 1; **R(1) = 2/2 = 1**. Completions at 1 and 11, hence **max flow = 11**.
- **Long-first:** service starts at t = 0 and t = 10; **R(1) = 1/2 = 0.5**. Completions at 10 and 11, hence **max flow = 11**.

Thus two schedules can have the **same maximum flow** but **different timely routine-start fractions**. This is a useful formal mismatch, **not a proof that R(tau) is an original research objective**. N05 shows that existing hard-deadline theory may already encode such a start budget.

**Fair N01 baseline adaptation:**
1. Implement **urgent EDF + routine FIFO** using only labels/deadlines that the model permits; account for full-buffer rejection, expiry and all offered jobs.
2. Consider a **Greedy-Slack-derived** variant only if its per-task processing-time information is disclosed. If it needs true unstarted durations, label it **oracle/non-deployable upper-reference**, not an equal-information win.
3. Compute N01's **Fmax** as a *secondary metric* alongside our U and R(tau); otherwise we cannot tell whether an “improvement” simply changes the target metric.
4. Include strict priority, FIFO, aging and fair service comparators; use exactly the same offered trace, K, admission rule and runtime budget.
5. Cite author-slide overhead (reported as **36 ms per task in that experiment**) only as a **nonportable case result**. Do not compare it numerically with a simulator running on unrelated hardware.

### Checklist — N01
- [x] Establish central overlap and the single-worker special case.
- [x] Demonstrate with a concrete trace that Fmax ≠ R(tau).
- [x] Show strong baseline and exact information/admission parity requirements.
- [x] Avoid asserting predecessor does not track failures or scheduling overhead.
- [ ] Verify queue cap/rejection, processing-time oracle and evaluation protocol from complete original paper.
- [ ] Implement matched-policy reproductions only **after** experimental protocol approval.

## Step 4A.3 — Theory reduction: N02, N05, N06

### N02 — DRR service curves directly extend to real-time tasks

The IEEE RTAS paper explicitly maps **flow→task, packet→job, packet size→job-execution time** on p. 172. It derives strict service curves and associated worst-case delay bounds for DRR, using aggregate service guarantees and (when available) interfering-flow arrival curves. This is **much stronger** than saying “DRR is about networking, not IoT processing.” Its Algorithm 1 tests head-of-line size against deficit, so a literal size-based implementation **requires duration/size information at selection**.

- **Relevant inherited result:** variable-work share and bounds are already established in a real-time task interpretation. A count-vs-work comparison and any naive service-time fairness claim cannot be sold as an invention.
- **Mapping required for our problem:** (a) document an arrival envelope for each class, (b) justify the total worker's service curve, (c) bound maximum non-preemptive job size if needed, (d) derive the *service-start* wait bound from the service guarantee, then (e) separately handle finite-capacity **rejections** and offered-job deadline failures. A bound on delay for traffic conforming to specified envelopes does **not automatically** bound losses of all offered jobs during overload.
- **Validity test:** in a trace where a genuine DRR waiting bound can be computed, show whether measured routine-access loss or urgent deadline failure is already predicted by it. If yes, do not claim an independently novel regime boundary.
- **Non-oracle policy:** when unstarted-job durations cannot be observed, completing-job work accounting is a **different adapted mechanism**; report how it differs from literal DRR instead of silently charging jobs by true future service demand.

### N05 — Fixed-length single-server multiclass/deadline theory

Hajek & Seri's author-hosted journal paper considers **one server, one packet per time slot, integer deadlines, class labels, dropping and a finite buffer**; the Dlex algorithm is lexicographically throughput-optimal with bounded buffer overhead, under the paper's one-slot job model. This directly challenges any novelty based merely on “finite queue + urgent priority + deadline drops.”

**Mapping warning:** when all jobs have unit duration p = 1, “routine starts before arrival + tau” can be encoded as a **completion deadline of arrival + tau + 1**, subject to the paper's slot/endpoint convention. That makes timely routine access a known deadline-throughput style question in this special case. Its exact lexicographic objective is **not identical** to our joint (U ≤ epsilon, R ≥ gamma) target; a reduction or counterexample is needed before declaring it either equivalent or irrelevant. Its fixed unit duration also does not establish results for variable, unknown processing times.

### N06 — Single-server admission and waiting deadlines are already known

Goldman, Parwatikar & Suri study **online, non-preemptive, single-resource** jobs with processing length and a **maximum wait before service starts**, admitting or rejecting jobs. The stated objective is utilization, not an IoT urgent/routine dual-budget Pareto frontier. This is still a **high-overlap prior theorem family** for our service-start timing and rejection model. The full-text theorem conditions were not verified; do not write “they did not study mixed-class objectives” as a definitive full-paper exclusion without reading it.

### Checklist — Theory reductions
- [x] Record N02's real-time mapping, head-size eligibility and arrival-curve hypotheses.
- [x] Record N05's unit-length, single-server, finite-buffer, multi-class and deadline properties.
- [x] Identify a fixed-length reduction from routine waiting to deadline completion.
- [x] Record N06's admission/start-wait overlap from original publisher/institution.
- [ ] Verify exact finite-K/loss bounds against N02 and N05 theorem hypotheses; write proof or counterexample.
- [ ] Obtain full N06 and N03 manuscripts and check whether a variable-size two-class reduction exists.

## Step 4A.4 — Novelty disposition, with falsifiers

| Candidate claim | Verdict today | What would change verdict |
| --- | --- | --- |
| “First online non-preemptive urgent + routine scheduler” | **REJECT** (N01) | No reasonable evidence will make the broad claim true |
| “First work-aware/fair urgent IoT scheduler” | **REJECT** (N02/N03/R22) | Reframe to a specific measurable result, not algorithm renaming |
| “First to consider waiting deadlines or buffer rejection” | **REJECT** (N05/N06) | Do not claim it |
| “Routine start-within-tau differs from max flow” | **TRUE as a mathematical distinction; NOT independently novel** | Demonstrate a substantive new outcome *not subsumed* by prior deadline-throughput policies |
| “Finite K + unknown processing durations + bursty offered-population two-budget frontier yields a new practical limit” | **OPEN / unproven candidate** | Full model comparisons + real application evidence + matched baselines + held-out experiments |
| “New algorithm / theory / performance improvement” | **NO SUPPORT YET** | Only after legitimate prior-art and outcome tests |

**Narrow working proposition, for testing only:**

> In a finite-capacity, non-preemptive IoT processing stage with unobservable unstarted-job service demand, does there exist a reproducible burst/service-variability regime where an equal-information, conventional online dispatch policy meets both an *offered urgent-deadline-failure budget* and an *offered routine service-start budget*, and where the boundary is not already explained by N01/N02/N05/N06?

This is a **research hypothesis**, not the paper's novelty statement. A valuable outcome may be **“no under these assumptions”**, but an ordinary negative simulation is not automatically publishable.

**Go/no-go gate before algorithm selection:**
1. Obtain complete authorized N01 and N06 text and a defensible N03 reading or mark them as unverified exclusions.
2. Write a table of mathematical assumptions showing which N01/N02/N05/N06 results apply, fail or require extension (and why).
3. Select a credible processing application and source trace; justify epsilon, tau, gamma, K **before** selecting favorable test cases.
4. Show that existing valid bounds or strong matched baselines cannot trivially explain the *specific* contribution claim.
5. Record supervisor approval or reframe RQ v1.0 based on actual findings; do not introduce admission control, outages or classifier errors without a separate reasoned scope decision.

### Checklist — Novelty decision
- [x] Reject the broad novelty claims with published counterexamples.
- [x] Record a concrete non-equivalence example while warning that metric changes are not innovations.
- [x] Preserve RQ v1.0 as a *testable working question*, not a novelty guarantee.
- [ ] Complete signed full-paper/equivalence gate and select defensible practical claim.
- [ ] Pre-register fair experiment and then implement, if gate survives.

## Verified references

Full citation details are repeated here to make this crosswalk independently auditable; no Q-ranking or blanket Scopus-indexing claim is implied.

- **N01:** Maxime Gonthier; Kyle Chard; Ian Foster; Loris Marchal; Frédéric Vivien. (2025). *Deadline-Aware Scheduling of Mixed-Criticality Tasks*. **Proceedings of the 54th International Conference on Parallel Processing (ICPP '25)**, pp. 178–187. **ACM.** DOI: https://doi.org/10.1145/3754598.3754639 . [First-party slides](https://perso.ens-lyon.fr/loris.marchal/scheduling-in-montreal/slides/maxime.pdf) · [HAL deposited edition (access blocked here)](https://inria.hal.science/hal-05190988v1/file/main.pdf). **Relevance:** direct dual-criticality online non-preemptive scheduling comparator.
- **N02:** Seyed Mohammadhossein Tabatabaee; Jean-Yves Le Boudec. (2021). *Deficit Round-Robin: A Second Network Calculus Analysis*. **2021 IEEE 27th Real-Time and Embedded Technology and Applications Symposium**, pp. 171–183. **IEEE.** DOI: https://doi.org/10.1109/RTAS52030.2021.00022 . [Original IEEE proceedings at EPFL](https://infoscience.epfl.ch/bitstreams/e0172e0b-b99c-43cc-9488-31afda35f1fa/download). **Relevance:** service curves/DRR in real-time task interpretation.
- **N03:** Luciano Lenzini; Enzo Mingozzi; Giovanni Stea. (2004). *Tradeoffs between low complexity, low latency, and fairness with deficit round-robin schedulers*. **IEEE/ACM Transactions on Networking**, 12(4), 681–693. **IEEE/ACM.** DOI: https://doi.org/10.1109/TNET.2004.833131 . [IEEE record](https://ieeexplore.ieee.org/document/1331430/). **Relevance:** historical work/latency/fairness trade-offs.
- **N04:** Matteo Dell'Amico; Damiano Carra; Pietro Michiardi. (2016). *PSBS: Practical Size-Based Scheduling*. **IEEE Transactions on Computers**, 65(7), 2199–2212. **IEEE.** DOI: https://doi.org/10.1109/TC.2015.2468225 . [EURECOM institutional record](https://www.eurecom.edu/en/publication/4449). **Relevance:** estimator-error/fairness limits.
- **N05:** Bruce Hajek; Pierre Seri. (2005). *Lex-Optimal Online Multiclass Scheduling with Hard Deadlines*. **Mathematics of Operations Research**, 30(3), 562–596. **INFORMS.** DOI: https://doi.org/10.1287/moor.1040.0144 . [Author-hosted journal manuscript](https://hajek.ece.illinois.edu/Papers/HajekSeri05.pdf). **Relevance:** one-worker, finite-buffer multi-class deadline and drop model.
- **N06:** Sally A. Goldman; Jyoti Parwatikar; Subhash Suri. (2000). *Online Scheduling with Hard Deadlines*. **Journal of Algorithms**, 34(2), 370–389. **Elsevier.** DOI: https://doi.org/10.1006/jagm.1999.1060 . [Publisher](https://www.sciencedirect.com/science/article/pii/S019667749991060X) · [1998 technical report record](https://repository.library.washu.edu/cse_research/474/). **Relevance:** admission and wait-to-start deadlines for non-preemptive variable-size jobs.

**Limitations:** No systematic Scopus/WoS result counts, complete N01/N03/N06 article reading, original proof reproduction, application traces, implementation or experiments were produced in this stage. **Status: Stage 4A source-based crosswalk complete; Stage 4B decisive novelty sign-off pending.**
