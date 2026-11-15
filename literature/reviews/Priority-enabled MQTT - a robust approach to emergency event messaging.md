# Priority-enabled MQTT: a robust approach to emergency event messaging

## 1. Bibliographic record and source

**Review number:** 02 · **Internal reference key:** R02

P S Akshatha; S Divyashree; S M Dilip Kumar. 2024. **Priority-enabled MQTT: a robust approach to emergency event messaging**. *Journal of Engineering and Applied Science, 71, article 67*. Springer Nature. DOI: [10.1186/s44147-024-00400-2](https://doi.org/10.1186/s44147-024-00400-2).

- **Reviewed version:** Published open-access article; 14 PDF pages.
- **Reading status:** full-text review retained from the earlier knowledge base; no independent replication.
- **Theme:** Emergency messaging architecture.
- **Provenance:** [earlier detailed English/Bangla review](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/blob/a88623cdbbf08caaccbf102b052c3e05188d7e31/paper-review/papers/02-priority-enabled-mqtt-2024.md). This revision reorganizes existing review evidence; it does not represent a fresh publisher/PDF verification.

## 2. Research problem

Can emergency MQTT messages receive preferential treatment rather than being routed through undifferentiated FCFS handling?

## 3. Authors' claimed contribution

Urgent/Critical queue configurations improve the reported timing behavior compared with FCFS in a prototype.

This is the authors' proposed contribution and reported evidence, not a conclusion that it is original across the entire literature.

## 4. Model and assumptions

Messages are assigned to static Urgent, Critical and FCFS classes. The system uses MQTT-capable RabbitMQ/AMQP routing and MySQL persistence. The timing experiment is small.

## 5. Method and decision mechanism

Route classified messages into virtual queues and deliver to subscribers, with persistence for historical use. This is an architecture/classification intervention rather than an adaptive deadline or aging rule (architecture pp. 5-9).

## 6. Evidence ledger

All measurements below are author-reported. Page numbers refer to the reviewed version.

| Claim examined | Source location | Evidence | Interpretation boundary |
| --- | --- | --- | --- |
| Prototype timing comparison | PDF p. 10; Figs. 5-8, pp. 11-12 | Ten messages per topic; plots report lower delay/jitter/response time than FCFS | Does not support robust p99 or rare-failure estimates. |
| Timing boundary | PDF p. 10 | Wireshark timestamp difference across described MQTT/AMQP exchanges | Application-message timestamp alignment needs clarification. |
| Persistence functionality | Figs. 3-4, PDF pp. 7-8 | Database screenshots show message storage | Not a quantitative reliability benchmark. |

## 7. Critical appraisal

Measurement validity: the exact timing endpoints are insufficiently clear for a strong independent end-to-end comparison. Statistical validity: ten messages/topic and unclear independent-run uncertainty limit inference. External validity: sustained overload, routine starvation and deadline guarantees are not demonstrated by this experiment.

**What would strengthen confidence:** reproduce the relevant mechanism under its stated model; inspect source/configuration availability; document independent-run uncertainty or proof conditions as appropriate. Missing evidence is not proof that the method fails.

## 8. Synthesis contribution and open question

**What this paper establishes for our review:** Useful architecture prior art; stronger evaluation is needed to answer urgency-versus-routine tradeoff questions.

**Question raised by this review:** How does static class prioritization affect tail waiting and delivery failures across classes as burst intensity rises?

This question is a lead for further reading, not a demonstrated literature gap or a selected algorithm. Check other papers for contrary evidence before advancing it.

<details>
<summary>বাংলা reading note</summary>

এটি useful prototype, কিন্তু প্রতি topic-এ ১০টি message দিয়ে strong tail-latency বা deadline guarantee বলা যায় না.

</details>

Return to the [review register](../README.md) or [cross-paper comparison](../synthesis/comparison.csv).
