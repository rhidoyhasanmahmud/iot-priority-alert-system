# R10 - Scheduling for Periodic Multi-Source Systems with Peak-Age Violation Guarantees

## 1. Bibliographic record and source

Kuan-Yu Lin; Yu-Chih Huang; Yu-Pin Hsu. 2023. **Scheduling for Periodic Multi-Source Systems with Peak-Age Violation Guarantees**. *IEEE Transactions on Communications, 71(12), 7102-7116*. IEEE. DOI: [10.1109/TCOMM.2023.3308959](https://doi.org/10.1109/TCOMM.2023.3308959).

- **Reviewed version:** Reviewed source is 32-page arXiv:2308.05445v1, not the different 2026 ICC paper suggested by its uploaded filename.
- **Reading status:** full-text review retained from the earlier knowledge base; no independent replication.
- **Theme:** Periodic freshness and violation analysis.
- **Provenance:** [earlier detailed English/Bangla review](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/blob/a88623cdbbf08caaccbf102b052c3e05188d7e31/paper-review/papers/R10-grr-peak-age-2023.md). This revision reorganizes existing review evidence; it does not represent a fresh publisher/PDF verification.

## 2. Research problem

How should heterogeneous periodic sources share service to control peak-Age-of-Information violation probabilities?

## 3. Authors' claimed contribution

Frequency-aware Generalized Round Robin (GRR), analyzed with IPQ and SPQ buffer models, yields modeled peak-age violation behavior and asymptotic bounds.

This is the authors' proposed contribution and reported evidence, not a conclusion that it is original across the entire literature.

## 4. Model and assumptions

Periodic heterogeneous status updates, a shared base station and explicit queue-management models. Exponential/geometric service models enter the analysis. Freshness thresholds differ from deadlines attached to distinct emergency events.

## 5. Method and decision mechanism

Allocate service using GRR with source sampling frequencies. Analyze the resulting peak-age violation probabilities under IPQ and SPQ; queue management affects whether old updates accumulate or are replaced.

## 6. Evidence ledger

All measurements below are author-reported. Page numbers refer to the reviewed version.

| Claim examined | Source location | Evidence | Interpretation boundary |
| --- | --- | --- | --- |
| GRR versus RR | Section V, Figs. 5-11, preprint pp. 21-25 | Most evaluated groups favor GRR; the RR-favored final group is an exception | No universal dominance. |
| Analytical/numerical agreement | Figs. 5-11, preprint pp. 22-25 | Bounds often track logarithmic decay trends | Agreement in slope is not exact finite-size probability calibration. |
| Queue management matters | Preprint p. 24 | In a stated SPQ scenario, corresponding IPQ overloads | Does not make distinct alarm events safely replaceable. |

## 7. Critical appraisal

Construct validity: peak AoI violations are not per-event completion deadline failures. External validity: periodic sampling assumptions differ from arbitrary emergency bursts. Reproducibility/statistics: the reviewed account does not clearly provide a seed/replication/CI protocol. Proofs and numerical results have not been independently reproduced.

**What would strengthen confidence:** reproduce the relevant mechanism under its stated model; inspect source/configuration availability; document independent-run uncertainty or proof conditions as appropriate. Missing evidence is not proof that the method fails.

## 8. Synthesis contribution and open question

**What this paper establishes for our review:** Foundational metric/model reference rather than a direct alert comparator. Prevents conflating freshness, delay and fairness.

**Question raised by this review:** When is an IoT item a replaceable state update rather than an event that must be retained, and how should that distinction constrain scheduling objectives?

This question is a lead for further reading, not a demonstrated literature gap or a selected algorithm. Check other papers for contrary evidence before advancing it.

<details>
<summary>বাংলা reading note</summary>

তথ্য fresh রাখা আর প্রতিটি alert deadline-এর আগে শেষ করা এক সমস্যা নয়। Uploaded filename-এর অন্য paper-এর ফল এখানে ব্যবহার করা যাবে না.

</details>

Return to the [review register](../README.md) or [cross-paper comparison](../synthesis/comparison.csv).
