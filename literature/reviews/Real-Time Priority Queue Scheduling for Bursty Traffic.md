# Real-Time Priority Queue Scheduling for Bursty Traffic

## 1. Bibliographic record and source

**Review number:** 04 · **Internal reference key:** R09

Rongping Lin; Jinpeng Zhang; Shan Luo; Jing Fu; Xiong Wang; Hui Li; Moshe Zukerman. 2025. **Real-Time Priority Queue Scheduling for Bursty Traffic**. *IEEE Internet of Things Journal, 12(24), 55883-55892*. IEEE. DOI: [10.1109/JIOT.2025.3627212](https://doi.org/10.1109/JIOT.2025.3627212).

- **Reviewed version:** CityUHK author postprint; 12 PDF pages including two front-matter pages. Manuscript page = PDF page - 2.
- **Reading status:** full-text review retained from the earlier knowledge base; no independent replication.
- **Theme:** Learned queue-state scheduling under bursts.
- **Provenance:** [earlier detailed English/Bangla review](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/blob/a88623cdbbf08caaccbf102b052c3e05188d7e31/paper-review/papers/R09-whittle-bursty-queues-2025.md). This revision reorganizes existing review evidence; it does not represent a fresh publisher/PDF verification.

## 2. Research problem

How should a switch share service among priority queues when a lower-priority queue experiences a burst and approaches overflow?

## 3. Authors' claimed contribution

Offline Whittle-index computation and current queue-state lookup balance priority service and congestion/loss in the reported switch experiments.

This is the authors' proposed contribution and reported evidence, not a conclusion that it is original across the entire literature.

## 4. Model and assumptions

Separate priority queues, slotted service and historical action-dependent transition information. The model discretizes occupancy to 21 levels and the priority-related occupancy ratio to six levels. Optimality claims rely on the cited RMAB/indexability/decoupling conditions.

## 5. Method and decision mechanism

Model queue service as an RMAB, estimate transition matrices, compute state indices offline and select the highest-index queue at runtime. Algorithm 1 initializes index bounds to -1 and 3 and prints exact equality convergence conditions (manuscript p. 6 / PDF p. 8); numerical tolerances, caps and unseen-state handling need explicit implementation choices.

## 6. Evidence ledger

All measurements below are author-reported. Page numbers refer to the reviewed version.

| Claim examined | Source location | Evidence | Interpretation boundary |
| --- | --- | --- | --- |
| No-burst baseline comparison | Table IV, manuscript p. 9 / PDF p. 11 | SP 2170 vs WTI 2294 microseconds delay; loss 0.12% vs 0.16%; both 50 Mbps | SP is slightly better on these no-burst endpoints. |
| Burst-period loss | Section V-C, manuscript p. 9 / PDF p. 11 | WTI 11.7%, SP 17.8%, WRR 26.5% | Reported network experiment, not urgent application-deadline failure. |
| Evaluation tracks | Section V, manuscript pp. 6-9 / PDF pp. 8-11 | Simulation; software-switch track including CQ; network track SP/WRR/WTI | Do not combine baselines or result boundaries across tracks. |

## 7. Critical appraisal

Reproducibility: transition collection, index update budget, convergence details and unseen states matter. Statistical validity: do not invent seed-level CIs absent from the reported result. Theory: the brief proof arguments have not been independently established by this review. External validity: switch-queue results cannot directly establish event-worker performance.

**What would strengthen confidence:** reproduce the relevant mechanism under its stated model; inspect source/configuration availability; document independent-run uncertainty or proof conditions as appropriate. Missing evidence is not proof that the method fails.

## 8. Synthesis contribution and open question

**What this paper establishes for our review:** Strong prior art for instantaneous congestion-aware priority adaptation. Any claimed gap must go beyond using occupancy and priority together.

**Question raised by this review:** How sensitive are the priority/congestion tradeoffs to transition-model mismatch, workload shifts and the cost of acquiring the learned state model?

This question is a lead for further reading, not a demonstrated literature gap or a selected algorithm. Check other papers for contrary evidence before advancing it.

<details>
<summary>বাংলা reading note</summary>

Queue occupancy ও priority একসঙ্গে ব্যবহার নতুন নয়। WTI trained index ব্যবহার করে; একটা simple score বানিয়ে সেটিকে WTI বলা ঠিক হবে না.

</details>

Return to the [review register](../README.md) or [cross-paper comparison](../synthesis/comparison.csv).
