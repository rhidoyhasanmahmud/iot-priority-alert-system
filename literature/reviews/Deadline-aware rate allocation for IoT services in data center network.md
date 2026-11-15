# Deadline-aware rate allocation for IoT services in data center network

## 1. Bibliographic record and source

**Review number:** 12 · **Internal reference key:** R21

Bo Shen; Naveen Chilamkurti; Ru Wang; Xingshe Zhou; Shiwei Wang; Wen Ji. 2018. **Deadline-aware rate allocation for IoT services in data center network**. *Journal of Parallel and Distributed Computing, 118, 296-306*. Elsevier Inc. DOI: [10.1016/j.jpdc.2017.09.012](https://doi.org/10.1016/j.jpdc.2017.09.012).

- **Identity verification:** supplied article matched against the indexed [official ScienceDirect record](https://www.sciencedirect.com/science/article/abs/pii/S0743731517302666) on 15 November 2026. Direct HTML retrieval was blocked. Journal issue year is 2018; online availability/copyright are 2017.
- **Reviewed version:** supplied published PDF, 11 pages; printed page = PDF page + 295. Method/figures on PDF pp. 6-9 visually checked.
- **Source fingerprint (SHA-256):** `8ade1ab801c57bdcfd6478c730861dd0d74d0ad5d35e4e33c2851b2957d4a86e`.
- **Reading status:** full text reviewed; no replication or independent proof verification.
- **Selection:** core conceptual prior art for deadline-aware service combined with historical deprivation feedback. It is a preemptible flow-rate scheduler, not a non-preemptive alert worker. No independently verified quartile/indexing claim.

## 2. Research problem

How should a many-to-one data-center switch share bottleneck bandwidth among flows with heterogeneous deadlines while improving fairness among sender links?

DRA combines remaining deadline with each link's recent deadline-missing history. That directly informs our urgency/fairness question, despite different service units and control assumptions.

## 3. Authors' claimed contribution

The authors formulate a non-cooperative pricing game, derive a per-link price and greedily allocate bandwidth by descending price each slot. They report application throughput close to EDF, better link fairness and shorter successful-flow completion/waiting times.

The paper's language about real-time guarantees must be read against its observed deadline misses and scoped game result. Nash equilibrium of the stated payoff does not itself prove all deadlines, starvation freedom or global scheduling optimality.

## 4. Model and assumptions

- N workers send to one aggregator through a ToR switch; links have separate, infinite flow queues (pp. 299-300 / PDF pp. 4-5).
- Slotted control with arrivals at slot end. Flows may be split across slots and a new urgent flow can displace a partially transmitted head-of-line flow.
- Real-time flows expire and are discarded at deadlines. A partly transmitted flow whose remainder expires still counts as a miss.
- Non-real-time flows use a default deadline for ranking/history but are retained until complete (p. 301 / PDF p. 6).
- Switch receives per-link head-of-line price and remaining-size metadata; proposed control uses SYN/SYN-ACK exchanges. No packet loss, one head-of-line flow per link per slot and equal worker-link capacities are assumed for the evaluated strategy (p. 302 / PDF p. 7).
- Simulation: 14 workers in the main comparisons, 100 packets/slot bottleneck capacity, delta = 0.95, history weight rho = 0.5, history window K = 10, and one million slots (p. 303 / PDF p. 8).
- Flow sizes are initially uniform 1-50 packets, deadlines 1-40 slots; query probability/deadline/size sweeps are reported. This is not a real deployment or an application-event trace experiment.

## 5. Method and decision mechanism

**Deadline and miss history -> price -> order within links -> order links -> allocate rate -> transmit/expire -> update.**

Eq. (8), p. 301 / PDF p. 6 defines historical missing ratio M_i^K from the last K head-of-line flows. Eqs. (10)-(19) yield the evaluated price:

p_i* = delta_i^(D_i) + rho_i M_i^K.

With delta below one, a smaller remaining lifetime raises the deadline term; more recent misses raise the history term. The abstract/prose describe lower historical service, but the explicit statistic is a missing ratio, not directly measured served bandwidth.

Algorithm 1, p. 302 / PDF p. 7 inserts a new flow by descending price. Under equal per-link discount parameters and shared link history, the authors state within-link order is EDF. The switch then sorts current head-of-line prices, greedily allocates remaining bandwidth subject to link/flow limits and breaks price ties by smaller link ID. Each slot reconsiders service, allowing preemption at flow granularity.

**Published specification problems:** Algorithm 2 line 13 prints R_i = C_i when residual C is no larger than C_i, and sets C = 0. Literally, for 20 residual units and link capacity 100, this allocates 100 and violates the budget. Prose says allocate the residual, so source/author clarification is required. Algorithm 1's end-of-list insertion and history-window update details also need care.

The equilibrium proof asserts compactness although the stated strategy space has p_i >= 0 without an explicit upper bound. More importantly, the written payoff is separable in each link's own price once deadline/history state is fixed; the link from that optimization to the greedy network allocation's global guarantees needs a separate argument. These are reviewer concerns, not a claim that the authors' actual simulator used the printed erroneous allocation branch.

## 6. Evidence ledger

All results are author-reported; graph statements below are qualitative rather than digitized estimates.

| Claim examined | Source location | Actual evidence | Interpretation boundary |
| --- | --- | --- | --- |
| Deadline completion performance | Figs. 4-6, p. 303 / PDF p. 8 | DRA and EDF application-throughput curves are close; both decline under heavier query load/larger flows. DRA is not uniformly above EDF at every point. | Application throughput is timely-flow fraction, not raw bits/s. Nonzero miss ratios contradict an unconditional all-deadlines guarantee. |
| Link fairness | Figs. 7-9, p. 304 / PDF p. 9 | DRA has higher plotted Jain-style fairness than EDF over the tested sweeps. | Fairness is over links' transmitted traffic, not per-message waiting or urgent/routine class protection. |
| Waiting/completion metric | Definition 5, p. 300 / PDF p. 5; Figs. 10-12, pp. 304-305 / PDF pp. 9-10 | Averages include successfully transmitted flows only, from generation until completion; authors show lower DRA values on selected links. | Completion delay includes transmission, and excludes expired failures. It is not queue-only or offered-population tail waiting. |
| Objective/guarantee boundary | Theorems 1-2 and Eq. (19), p. 301 / PDF p. 6 | Existence/uniqueness arguments concern the proposed price game. | These do not independently prove deadline satisfaction, bounded waiting or optimal total network utility under all traffic. |
| Experimental scope | Section 5.1, p. 303 / PDF p. 8 | One-million-slot synthetic evaluation with fixed delta/rho/K and EDF comparison. | A long run is not independent replication; sensitivity to feedback weight/window and realistic loss/control overhead remains uncertain. |

## 7. Critical appraisal

**Contribution and overlap.** Deadline ranking combined with historical service disadvantage is already established prior art here. Replacing price notation with a weighted score would not by itself create novelty.

**Internal validity.** The simple shared bottleneck allows a clear comparison, but the history term and expiry policy change which flows complete. Conditional-on-success latency must be read alongside misses. No evidence establishes routine tail protection when sustained urgent demand dominates.

**Theory/reproducibility.** The printed residual-allocation branch is materially unsafe to copy. Clarify it rather than quietly correcting a replica. Compactness, payoff coupling and equivalence between per-price best responses and greedy allocation require independent scrutiny before citing optimality. Historical miss ratio should not be mislabeled as an aging timer or service-deficit counter.

**Statistical/external validity.** Independent run counts, seed-level intervals and parameter-tuning protocol are not established in the reported setup. Synthetic, lossless, equal-rate links with infinite buffers and divisible flows cannot directly establish behavior of finite-capacity non-preemptive alert processing.

**Evidence that would strengthen confidence:** source-level reconciliation, parameter/window sensitivity, matched complete loss/expiry accounting, service of retained non-real-time flows under overload, and offered-population class deadline/tail outcomes.

## 8. Synthesis contribution and open question

Compare with [bursty queue scheduling](Real-Time%20Priority%20Queue%20Scheduling%20for%20Bursty%20Traffic.md), which uses learned queue-state indices, and [adaptive disaster scheduling](Adaptive%20Priority%20Scheduling%20of%20Internet%20of%20Things%20Data%20for%20Disaster%20Management%20in%20Smart%20Cities.md), which combines deadline progress with routing/migration. DRA adds explicit historical deprivation feedback at the flow-rate layer.

**Question for further reading:** Which deadline-plus-history mechanisms improve routine service when expired work, finite buffers and non-preemptive service are counted fairly, and how sensitive are they to history-window delay?

This is a reading lead, not a proven gap or selected baseline.

<details>
<summary>বাংলা reading note</summary>

এটি deadline-এর সঙ্গে সাম্প্রতিক miss history মিশিয়ে service priority বাড়ায়। তাই deadline + fairness feedback নতুন নয়। তবে fairness মাপা হয়েছে link-level throughput দিয়ে, আর waiting average শুধু successful flow নিয়ে। Algorithm-এর residual-capacity line-এও অসংগতি আছে; clarification ছাড়া হুবহু baseline করা যাবে না।

</details>

Return to the [review register](../README.md) or [cross-paper comparison](../synthesis/comparison.csv).
