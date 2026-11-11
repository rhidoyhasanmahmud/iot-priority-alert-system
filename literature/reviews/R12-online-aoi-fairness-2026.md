# R12 - Online age of information scheduling: The power of packet management and fairness

## 1. Bibliographic record and source

Chen-Rui Jien; Tung-Wei Kuo. 2026. **Online age of information scheduling: The power of packet management and fairness**. *Computer Networks, 289, article 112690*. Elsevier. DOI: [10.1016/j.comnet.2026.112690](https://doi.org/10.1016/j.comnet.2026.112690).

- **Reviewed version:** Final published article; 16 PDF pages.
- **Reading status:** full-text review retained from the earlier knowledge base; no independent replication.
- **Theme:** Online fairness and replaceable updates.
- **Provenance:** [earlier detailed English/Bangla review](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/blob/a88623cdbbf08caaccbf102b052c3e05188d7e31/paper-review/papers/R12-online-aoi-packet-management-fairness-2026.md). This revision reorganizes existing review evidence; it does not represent a fresh publisher/PDF verification.

## 2. Research problem

How do fairness and safe replacement of obsolete updates affect the achievable online total-AoI objective when future arrivals and terminal lifetimes are unknown?

## 3. Authors' claimed contribution

With packet management, RR has a constant-order competitive guarantee and delta-Fair algorithms have an O(delta^4) bound; retaining all updates yields a substantially harder worst-case problem.

This is the authors' proposed contribution and reported evidence, not a conclusion that it is original across the entire literature.

## 4. Model and assumptions

A base station serves status updates for arriving/departing terminals. The legality of replacing old updates is central. Competitive analysis is worst-case relative to its own comparator/model, not an absolute emergency deadline guarantee.

## 5. Method and decision mechanism

Analyze online fairness and packet-management policies, contrasting FCFS retention with replace-latest management. Compare RR, OTF, NMF, MITF and Random empirically; theorem conditions and stochastic simulations support different kinds of conclusions.

## 6. Evidence ledger

All measurements below are author-reported. Page numbers refer to the reviewed version.

| Claim examined | Source location | Evidence | Interpretation boundary |
| --- | --- | --- | --- |
| Theoretical guarantees and hardness | Theorem 3 / Section 4; Theorems 15-16 / Section 6 | Fair scheduling with PM admits the stated bounds; FCFS has an Omega(n^(1/5)) lower bound | Proofs read in prior review, not independently verified. |
| Empirical setting | Section 5, PDF p. 8 | Ten independent runs/point; changing terminals, stochastic updates and bounded-Pareto communication latency | Particular stochastic setting, not all theorem inputs. |
| Typical versus worst case | Section 5.5, PDF p. 9 | OTF can look similar to RR in ordinary simulation despite poor proven worst-case behavior | Benign simulation cannot establish worst-case safety. |

## 7. Critical appraisal

Construct validity: total AoI, service fairness and emergency-event completion are different endpoints. External validity: obsolete state replacement may be invalid for unique alarms. Theoretical bounds cannot be transferred when service/packet-management assumptions change.

**What would strengthen confidence:** reproduce the relevant mechanism under its stated model; inspect source/configuration availability; document independent-run uncertainty or proof conditions as appropriate. Missing evidence is not proof that the method fails.

## 8. Synthesis contribution and open question

**What this paper establishes for our review:** Shows why fairness definitions and safe discard semantics must be specified before selecting an objective.

**Question raised by this review:** Which service guarantees are needed for non-replaceable alarms, and which failures remain hidden under ordinary stochastic workload averages?

This question is a lead for further reading, not a demonstrated literature gap or a selected algorithm. Check other papers for contrary evidence before advancing it.

<details>
<summary>বাংলা reading note</summary>

পুরোনো status update replace করা সম্ভব হলেও unique emergency event ফেলে দেওয়া নিরাপদ ধরে নেওয়া যায় না। সাধারণ simulation ভালো হলেই worst-case fairness প্রমাণ হয় না.

</details>

Return to the [review register](../README.md) or [cross-paper comparison](../synthesis/comparison.csv).
