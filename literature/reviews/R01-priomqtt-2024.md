# R01 - PrioMQTT: A prioritized version of the MQTT protocol

## 1. Bibliographic record and source

Gaetano Patti; Luca Leonardi; Giuseppe Testa; Lucia Lo Bello. 2024. **PrioMQTT: A prioritized version of the MQTT protocol**. *Computer Communications, 220, 43-51*. Elsevier. DOI: [10.1016/j.comcom.2024.03.018](https://doi.org/10.1016/j.comcom.2024.03.018).

- **Reviewed version:** Final publisher PDF; 9 PDF pages; journal pages 43-51.
- **Reading status:** full-text review retained from the earlier knowledge base; no independent replication.
- **Theme:** MQTT transmission priority.
- **Provenance:** [earlier detailed English/Bangla review](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/blob/a88623cdbbf08caaccbf102b052c3e05188d7e31/paper-review/papers/R01-priomqtt-2024.md). This revision reorganizes existing review evidence; it does not represent a fresh publisher/PDF verification.

## 2. Research problem

How can industrial MQTT traffic receive priority-differentiated, low-latency transmission while coexisting with conventional clients?

## 3. Authors' claimed contribution

A priority-aware broker and UDP-based time-critical transport improve RTT in the reported industrial setup.

This is the authors' proposed contribution and reported evidence, not a conclusion that it is original across the entire literature.

## 4. Model and assumptions

The decision acts in the broker forwarding/transmission path, not in downstream application processing. Priority metadata is supplied with messages. The evaluated configuration uses a particular industrial network, payload sizes and publication periods.

## 5. Method and decision mechanism

Numeric MQTT v5 User Properties identify priorities. The modified non-preemptive broker transmission queue serves lower numeric priorities first, using FIFO within equal priority (Section 4.1). A UDP path serves time-critical traffic alongside conventional TCP clients.

## 6. Evidence ledger

All measurements below are author-reported. Page numbers refer to the reviewed version.

| Claim examined | Source location | Evidence | Interpretation boundary |
| --- | --- | --- | --- |
| Lower RTT in the tested setup | Table 3, PDF p. 8 | T1/T2: 1.17 vs 2.40 ms; T5/T6: 1.26 vs 6.04 ms, PrioMQTT vs standard MQTT | Transport and queue policy change together. |
| Large transmission population | Section 5.2 and Table 2, PDF p. 7 | Broker-queue experiment reports 11.04 million transmissions | A large within-run count does not establish independent-run uncertainty. |
| Queueing changes with payload | Section 5.1, PDF pp. 6-7 | Priority effects become more visible at larger payload sizes | Hop distance also affects RTT. |

## 7. Critical appraisal

Internal validity: the direct standard-MQTT comparison does not isolate the scheduling effect from UDP/TCP differences. External validity: the tested network and loads do not establish behavior under arbitrary sustained overload. Measurement interpretation: observed low loss is not a universal zero-loss guarantee.

**What would strengthen confidence:** reproduce the relevant mechanism under its stated model; inspect source/configuration availability; document independent-run uncertainty or proof conditions as appropriate. Missing evidence is not proof that the method fails.

## 8. Synthesis contribution and open question

**What this paper establishes for our review:** Establishes priority-enabled MQTT as existing work. Transport semantics must be held constant when attributing gains to scheduling.

**Question raised by this review:** Under identical transport and offered load, how much of the latency benefit remains attributable to dispatch order, and what happens to lower-priority traffic?

This question is a lead for further reading, not a demonstrated literature gap or a selected algorithm. Check other papers for contrary evidence before advancing it.

<details>
<summary>বাংলা reading note</summary>

Priority MQTT আগেই আছে। এই paper-এর RTT benefit-এ UDP ও scheduling একসঙ্গে বদলেছে; তাই শুধু scheduler-এর উন্নতি বলে পুরো gain ব্যবহার করা যাবে না.

</details>

Return to the [review register](../README.md) or [cross-paper comparison](../synthesis/comparison.csv).
