# Adaptive Priority Scheduling of Internet of Things Data for Disaster Management in Smart Cities

## 1. Bibliographic record and source

**Review number:** 06 · **Internal reference key:** R11

Marie C. Pognon; Alejandro Quintero; Samuel Pierre. 2024. **Adaptive Priority Scheduling of Internet of Things Data for Disaster Management in Smart Cities**. *IEEE Access, 12, beginning p. 83285 (end pagination not established in retained review)*. IEEE. DOI: [10.1109/ACCESS.2024.3407672](https://doi.org/10.1109/ACCESS.2024.3407672).

- **Reviewed version:** Published article; 14 PDF pages.
- **Reading status:** full-text review retained from the earlier knowledge base; no independent replication.
- **Theme:** Multi-hop deadline-progress scheduling.
- **Provenance:** [earlier detailed English/Bangla review](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/blob/a88623cdbbf08caaccbf102b052c3e05188d7e31/paper-review/papers/R11-pognon-adaptive-disaster-2024.md). This revision reorganizes existing review evidence; it does not represent a fresh publisher/PDF verification.

## 2. Research problem

How can multi-hop disaster-monitoring networks deliver urgent data while protecting less urgent packets under congestion and changing progress toward deadlines?

## 3. Authors' claimed contribution

A combined adaptive scheduling/routing model improves reported class-specific delays and delivery behavior.

This is the authors' proposed contribution and reported evidence, not a conclusion that it is original across the entire literature.

## 4. Model and assumptions

Clustered multi-hop WSN, priority classes, queue reordering, fallback migration and next-hop choice. Infinite queues remove overflow as a limiting factor (PDF p. 10); processing and topology assumptions further narrow the model.

## 5. Method and decision mechanism

Reorder using deadline progress, migrate salvageable packets into fallback handling and choose next hops using congestion/history. The final combined Case 15 includes several interventions; its gain is not a queue-only effect.

## 6. Evidence ledger

All measurements below are author-reported. Page numbers refer to the reviewed version.

| Claim examined | Source location | Evidence | Interpretation boundary |
| --- | --- | --- | --- |
| Evaluation design | PDF pp. 9-11 | MATLAB R2023b; 15 configurations with three repeats; scaling phase with five repeats | Limited independent repeats. |
| Reported composite benefit | Conclusion, PDF p. 13 | Largest tested network: class delays 48.8 and 54.3 ms; stated improvements 31% and 96% | Author scenario results; not universal guarantees. |
| Delivery/delay cost | Discussion and Figs. 6-10, PDF p. 12 | Fallback migration can save packets but increase global average delay | Retained traffic consumes service; latency cannot be interpreted alone. |

## 7. Critical appraisal

Internal validity: combined routing/reordering/migration benefits need component separation. External validity: infinite buffers do not test finite-buffer burst loss. Statistical validity: three/five repeats do not establish rare-tail guarantees. Definition risk: a packet may count as critical more than once.

**What would strengthen confidence:** reproduce the relevant mechanism under its stated model; inspect source/configuration availability; document independent-run uncertainty or proof conditions as appropriate. Missing evidence is not proof that the method fails.

## 8. Synthesis contribution and open question

**What this paper establishes for our review:** Important adaptive deadline/priority prior art and evidence that preserving deliveries can increase latency.

**Question raised by this review:** What tradeoffs remain when resource capacity is bounded and routing, migration and scheduling effects are isolated?

This question is a lead for further reading, not a demonstrated literature gap or a selected algorithm. Check other papers for contrary evidence before advancing it.

<details>
<summary>বাংলা reading note</summary>

এই paper-এর benefit একাধিক mechanism-এর combined ফল। Infinite queue ধরে পাওয়া result bounded overload-এর evidence নয়.

</details>

Return to the [review register](../README.md) or [cross-paper comparison](../synthesis/comparison.csv).
