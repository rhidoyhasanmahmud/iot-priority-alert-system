# QoS-Aware Priority-Based Task Offloading for Deep Learning Services at the Edge

## 1. Bibliographic record and source

- **Review 18 · R27 · core-related priority/admission and completion-quality trade-off.** Offloading changes the resource model; this is not a broker dispatch-only method.
- **Authors:** Minoo Hosseinzadeh; Andrew Wachal; Hana Khamfroush; Daniel E. Lucani.
- **Publication:** 2022 IEEE 19th Annual Consumer Communications & Networking Conference (CCNC), pp. 319-325, 2022. Publisher: IEEE.
- **DOI:** [10.1109/CCNC49033.2022.9700676](https://doi.org/10.1109/CCNC49033.2022.9700676).
- **Verification, 15 November 2026:** [University of Kentucky publication record](https://scholars.uky.edu/en/publications/qos-aware-priority-based-task-offloading-for-deep-learning-servic/) confirms authors, proceedings pages and DOI; the supplied publication matches the [NSF-hosted record/PDF](https://par.nsf.gov/servlets/purl/10317529). Direct publisher/DOI HTML access was unavailable. No unverified ranking claim.
- **Source:** supplied `10317529.pdf`, seven published pages; printed page = PDF page + 318. SHA-256: `0395338d36a46c7a2c6c802f4d6c8d4b47c622869639e277b4fdf96c52646347`.
- Full-text critical review, with gain/algorithm and numerical/testbed figures visually checked. No independent implementation, solver reproduction or proof certification. PDF not redistributed.

## 2. Research problem

Deep-learning requests at resource-limited edge servers differ in importance, desired accuracy and preferred completion time. A task may run locally, move to a neighboring edge server, go to the cloud or be dropped. The paper optimizes server/model assignment and introduces a Priority-Greedy User Satisfaction algorithm (PGUS) that serves higher-priority tasks first while choosing among completion-time/accuracy alternatives.

It is relevant because the distinction between serving a task and satisfying its timing/quality requirement changes how priority scheduling should be evaluated.

## 3. Authors' claimed contribution

The authors define a priority-sensitive Gain of System (GoS), formulate an integer linear program, state an NP-hardness reduction, and propose PGUS as a polynomial heuristic. Numerical comparisons include a small ILP reference and larger task sets; a hardware testbed evaluates two image-recognition model choices.

The abstract/conclusion report roughly 45% more service to the top quarter of priority classes compared with GUS. That aggregate claim should not be treated as a general guarantee: the numerical text separately discusses approximately 60% more service for three highest classes, while the testbed text reports more than 9% higher GoS. They refer to different endpoints/settings.

## 4. Model and assumptions

- Three tiers: users, heterogeneous edge servers and a cloud server. Edge nodes communicate with neighbors, and the cloud is assumed to have unlimited computation/communication capacity in the mathematical model (p. 320).
- A user submits one modeled task; multiple requests are represented by co-located users. Tasks are considered over time slots and accumulated into decision frames. Services/models are pre-placed; each offers a known or estimated accuracy and resource cost.
- Higher numeric priority is more important. Each class specifies normalized minimum accuracy and maximum preferred completion time. Their satisfaction gaps, weighted equally in the numerical baseline, feed GoS (Equations 1-4, p. 321).
- A task is served-satisfied only if both accuracy and completion requirements are met. A task may also be served-not satisfied if one or both are missed. Those are allowed outcomes, not prohibited by the ILP. Dropped work has gain zero.
- Completion combines admission-decision waiting, computation and offload communication; processing-queue waiting and decision computation time are treated as negligible in the model. Common user-to-edge/result-return transmission is omitted from the offloading comparison (pp. 321-322).
- Numerical tests assume delay/resource/accuracy information known. In the prototype, servers share capacity/delay information once per second, and sliding-window estimates predict communication and computation delay (p. 323). Estimation accuracy and stale-state effects are not equivalent to known metadata.
- Capacity, model placement, bandwidth limits and cloud access change which tasks are feasible. No explicit aging, routine quota, per-class waiting bound or no-starvation theorem is provided.

## 5. Method and decision mechanism

User satisfaction combines normalized accuracy surplus and completion-time surplus. GoS then uses an exponential reward with different bases depending on whether both, one or neither requirement is met, and includes normalized priority in the exponent (Equations 1-4). Baseline reward bases are 64, 4 and 2; the utility therefore encodes a particular preference over partial service and full satisfaction, not a neutral QoS metric.

The ILP selects at most one server/model combination per task and constrains per-server computation and source offload communication. It does not impose minimum accuracy or maximum completion time as hard feasibility constraints (Equation 5, p. 322). Its optimality is relative to that utility and capacity model.

PGUS (Algorithm 1, p. 322) sorts tasks by descending priority, enumerates compatible server/model choices, ranks them by predicted GoS, and takes the first capacity-feasible choice. Capacities are updated and tasks with no feasible choice are dropped. This is priority-first assignment, not EDF, global resource-share fairness or a proof of routine protection.

A reproduction detail needs clarification: the offload branch checks source communication capacity `eta_si`, but the printed update says to update `gamma_j` and `eta_j`. Source versus destination communication accounting must match the ILP; do not silently patch that line and call the result faithful. The authors give a polynomial complexity bound, but timing-sensitive reuse also requires measured decision and control-message costs, which a complexity label alone does not supply.

## 6. Evidence ledger

| Claim examined | Source location | Actual evidence | Interpretation boundary |
| --- | --- | --- | --- |
| PGUS approximates the ILP well | Figure 2 and ILP comparison, p. 323 / PDF p. 5 | Nine edge servers plus one cloud, 210 tasks, 100 Monte Carlo runs; total GoS is about 80% of ILP, or 81% in one alternate reward-base setting. | Empirical small-instance ratio, not a worst-case approximation guarantee or proof of optimality at large scale. |
| PGUS drops fewer tasks than GUS | Figure 3 and baseline descriptions, p. 324 | Larger numerical tests use 100-1000 tasks and 20,000 Monte Carlo runs/data point. PGUS allows served-not-satisfied tasks; GUS rejects tasks whose requirements cannot be met. | Different acceptance semantics contribute to fewer drops. Report satisfied, unsatisfied and dropped outcomes on the same offered population. |
| Higher classes receive more service | Figure 3, p. 324; abstract/conclusion | Priority-first PGUS shifts service toward higher classes; the text reports an approximately 60% service improvement for three highest classes in that numerical setup. | Do not substitute this for the abstract's top-25%/45% statement or infer routine waiting protection. The figure's dark/light bars share a zero baseline, not a stacked total. |
| Hardware feasibility and GoS benefit | Figure 4 and testbed, pp. 324-325 | Linux desktop cloud, Jetson Nano and Raspberry Pi 4B edge devices, three Pi 3B users; SqueezeNet at edge, GoogLeNet at cloud; 3000 tasks total. Text reports over 9% higher GoS than GUS on average. | Small controlled testbed with shaped bandwidth and synthetic cloud sleep; not a production deployment or direct hard-deadline demonstration. |
| Resource-state estimation supports deployment | Implementation description, p. 323 | One-second server broadcasts and sliding-window estimates provide delay/capacity inputs. | No independent error/overhead analysis establishes performance under rapidly changing bursts or stale information. |

## 7. Critical appraisal

**Useful contribution.** Priority, task admission and quality/time trade-offs are explicit. A solver comparison plus hardware implementation provides more than a purely conceptual sketch. The 80% small-instance GoS result is also more informative than calling the method near-optimal without quantification.

**Endpoint and comparator alignment.** GUS uses hard accuracy/time acceptance constraints; PGUS permits partial/unsatisfied service. A reduction in drops may be desirable, but cannot alone establish improved timely service. Conversely, GUS's larger satisfied fraction should not be reported without its rejected population. The utility reward bases and class requirement mapping materially influence GoS; prioritization is not isolated from those choices.

**Timing and load scope.** Numerical settings use ten total servers, 50 services, ten models/service, 20 priority classes, average network capacity 600 bytes/ms, preferred completion times 8000-17500 ms, and known delay inputs (p. 323). The testbed generates one request/user every 500 ms, uses finite edge queues of 15/10, shapes cloud links to 9/7 bytes/ms, runs decisions when a queue fills or a time limit passes, and adds synthetic cloud delay (pp. 324-325). This is a specific service-quality study, not an arbitrary burst arrival or saturated-cloud experiment. The unspecified trigger timeout and batch wait matter for alerts.

**Reproduction/statistical limits.** The abstract's 45% top-quarter claim lacks a transparently tabulated aggregation that should be recomputed before citation as an exact comparative result. Monte Carlo counts apply to the numerical tests; they are not hardware-trial counts or confidence intervals. The testbed report does not adequately specify independent repeated runs, uncertainty, delay-prediction errors or control overhead. The NP-hardness argument references a prior special-case problem; this review has not independently verified that reduction.

**Research use:** retain to challenge comparisons that equate completed with satisfactorily completed tasks, and to map priority-aware assignment prior art. Reconcile communication-capacity accounting, acceptance semantics, information access and finite-cloud limits before considering a faithful comparator.

## 8. Synthesis contribution and open question

Compare PGUS with [DPTARA](Dynamic%20priority-based%20task%20scheduling%20and%20adaptive%20resource%20allocation%20algorithms%20for%20efficient%20edge%20computing%20in%20healthcare%20systems.md): both couple priority to placement and resource availability. Compare their service accounting with RAAC's offered-to-completed ratio; an eventually completed or served-not-satisfied task need not meet an alert deadline.

**Open reading question:** which priority schemes improve urgent success while exposing the full cost to routine timely completion, intentional rejection and partial-quality service under matched resources? This is a comparison question, not a selected algorithm or proven gap.

**Bangla note:** কম task drop হয়েছে মানেই সব task-এর deadline/quality পূরণ হয়েছে নয়। PGUS-এর served-not-satisfied outcome আলাদা রাখা জরুরি।

[Register](../README.md) · [Comparison](../synthesis/comparison.csv) · [Synthesis](../synthesis/findings.md)
