> **Literature-first reset (11 November 2026):** Comparisons to our implementation refer to the archived prototype. They are review observations, not a selected contribution or an instruction to resume implementation. Review the broader literature before choosing the conference-paper idea.

# Literature Review Knowledge Base — IoT Priority Alert System

**Purpose:** One place to **understand each paper again after months without rereading its PDF** and to synthesize what existing research actually demonstrates about urgent-message priority, routine waiting, fairness, overload, deadline risk, and losses.

- **This README combines navigation + cross-paper summary**. No separate SUMMARY.md.
- **Individual technical notes live only in [papers/](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/blob/7e419b7ddd1f2808203a48d91849250a85d6d4dc/docs/research/literature-review/papers/)**.
- **Format of every paper:** exactly **What? / Why? / How? / Evidence? / So What?**; detailed **English first**, followed immediately by a collapsible **বাংলা ব্যাখ্যা** for each question.
- **Identity is always the actual title/authors/DOI inside the PDF, not the uploaded filename.** If they disagree, record the discrepancy and review the *actual document*.
- **No publisher PDFs committed:** link the DOI/publisher and cite PDF page, figure, algorithm, equation as evidence instead.
- **Evidence boundary:** “Full manuscript reviewed” means an original critical reading—not an independent replication of code, theorem, empirical output or journal peer-review process.

**Project research question (current scope):** For a **bounded, non-preemptive application worker after MQTT delivery**, does **occupancy-dependent guarded aging** provide an empirically worthwhile tradeoff between **urgent-deadline failures**, **routine waiting**, and **admission loss** relative to tuned matched controls (including fixed aging and EDF), once overhead is measured?

This is a **candidate empirical question**, not an already validated originality or superiority claim. The project's running implementation/protocol is described in [design review](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/blob/7e419b7ddd1f2808203a48d91849250a85d6d4dc/docs/research/design-review.md), [registered closest-method comparison](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/blob/7e419b7ddd1f2808203a48d91849250a85d6d4dc/docs/research/closest-method-comparison.md), [other related work](catalog-notes.md), and [metadata catalog](catalog.json).

---

## 1. Paper index — read the individual notes

**Seven individual PDF-based reviews** have been written so far: R01, R02, R08, R09, R10, R11 and R12. IDs R03–R07 remain reserved for prior catalog entries and have **not** been labeled as fully reviewed.

| ID | Actual paper title | Authors/year/venue | Major technique | Relevance to our question | Read note |
| --- | --- | --- | --- | --- | --- |
| **R01** | [PrioMQTT: A prioritized version of the MQTT protocol](https://doi.org/10.1016/j.comcom.2024.03.018) | Patti et al., 2024, *Computer Communications*, Elsevier | MQTT priority metadata; UDP/TCP; broker transmit queue | **High:** MQTT priority prior art | [R01](papers/R01-priomqtt-2024.md) |
| **R02** | [Priority-enabled MQTT: a robust approach to emergency event messaging](https://doi.org/10.1186/s44147-024-00400-2) | Akshatha et al., 2024, *Journal of Engineering and Applied Science*, Springer Nature | Urgent/Critical/FCFS RabbitMQ queues | **High:** emergency priority messaging | [R02](papers/R02-priority-enabled-mqtt-2024.md) |
| **R08** | [Multi-tier Message Scheduling for IoT-based Urban Emergency Systems through Semantic Priority Override](https://doi.org/10.1109/ACCESS.2026.3732592) | Bittencourt et al., 2026, *IEEE Access*, IEEE | **TRIAGE/4:** semantic override; per-device RR; AAP admission protection | **Very high:** closest semantic/fairness comparator | [R08](papers/R08-triage4-semantic-priority-2026.md) |
| **R09** | [Real-Time Priority Queue Scheduling for Bursty Traffic](https://doi.org/10.1109/JIOT.2025.3627212) | Lin et al., 2025, *IEEE Internet of Things Journal*, IEEE | **WTI:** Whittle index using queue occupancy/priority | **Very high:** burst-aware scheduling prior art | [R09](papers/R09-whittle-bursty-queues-2025.md) |
| **R10** | [Scheduling for Periodic Multi-Source Systems with Peak-Age Violation Guarantees](https://doi.org/10.1109/TCOMM.2023.3308959) | Lin, Huang & Hsu, 2023, *IEEE Transactions on Communications*, IEEE | **GRR**, IPQ/SPQ, peak-AoI violation bounds | **Medium:** tail/freshness theory, not an alert comparator | [R10](papers/R10-grr-peak-age-2023.md) |
| **R11** | [Adaptive Priority Scheduling of Internet of Things Data for Disaster Management in Smart Cities](https://doi.org/10.1109/ACCESS.2024.3407672) | Pognon, Quintero & Pierre, 2024, *IEEE Access*, IEEE | Deadline-progress ordering; fallback migration; congestion-aware routing | **High:** deadline/fairness-related WSN prior art | [R11](papers/R11-pognon-adaptive-disaster-2024.md) |
| **R12** | [Online age of information scheduling: The power of packet management and fairness](https://doi.org/10.1016/j.comnet.2026.112690) | Jien & Kuo, 2026, *Computer Networks*, Elsevier | Packet replacement + $\delta$-Fair scheduling; online competitive bounds | **Medium–high:** theoretical fairness/replaceability | [R12](papers/R12-online-aoi-packet-management-fairness-2026.md) |

**Review status of all seven:** The **supplied full PDF text and relevant figures** were examined, and an individual evidence-traced note produced. The R08 document is an **accepted author manuscript**; R09 is an **author postprint**; R10 is an **arXiv preprint**. Version-specific page numbering is explained in each note. **None has undergone independent replication here.**

### Exact-title warning for R10

The first uploaded file was **named** like the separate 2026 ICC fairness paper, but **actually contains the 2023 Lin/Huang/Hsu GRR preprint**. We reviewed **R10 by its *internal* PDF title** and **did not mistakenly attribute the 2026 paper's results to it**. If the actual 2026 ICC fairness paper is later uploaded, allocate a new distinct ID.

---

## 2. Cross-paper comparison matrix

The table emphasizes **decision scope, resource parity and outcome parity**. Similar keywords do **not** mean methods are interchangeable.

| ID | Scheduler acts at | Scheduling/admission mechanism | Evaluation outcome | Main mismatch vs our worker |
| --- | --- | --- | --- | --- |
| **R01** | MQTT broker **outgoing transmission queue** | Publisher-set numeric priority + UDP transport | RTT, queue time, loss in industrial testbed | **Transport and priority changed together**; no matched routine anti-starvation |
| **R02** | RabbitMQ MQTT/AMQP virtual queues | Three **static** classes: Urgent/Critical/FCFS | Mean response, delay, jitter on small prototype | **Only 10 messages/topic**; no bursty p95/p99 or fairness evaluation |
| **R08** | Local gateway/broker queue | Four bands; alarm override; **device RR**; routine tokens; AAP shedding | Alarm latency/p95, device fairness, shed counts, broker scheduling overhead | Geography/device fairness vs **routine-class waiting**; admission shedding changes denominator |
| **R09** | **Network switch output port** with multiple priority queues | Learned, offline Whittle indices from instant queue state | Packet delay/loss/throughput, OVS-DPDK under bursts | **Per-class buffers**, slot-based switches, transition-learning phase |
| **R10** | Shared base-station scheduler with per-source buffers | Frequency-aware **GRR**; IPQ vs SPQ | Peak-AoI violation probabilities / asymptotic bounds | **Periodic status freshness**, not per-event urgent deadline |
| **R11** | **Multi-hop clustered WSN** | Preemptive priority + per-hop deadline progress + fallback + next-hop | Average end-to-end delay, delivery ratio, critical situations | **Infinite queues**; routing & preemption confound queue-only performance |
| **R12** | Online base-station messages to terminals | **RR / $\delta$-Fair** + replace-latest packet management | Total AoI; mathematical competitive bounds + simulations | **Replaceable status**; per-terminal service fairness, not distinct event completion |

---

## 3. Consolidated findings — what we have genuinely learned

### Finding A — Priority-based MQTT messaging **already exists**

**R01** introduces protocol-level priority metadata and broker transmission priority, and reports **51.30%–79.14%** reduced RTT in its setting relative to standard MQTT; however, **UDP vs TCP** is a co-varying change. **R02** adds emergency class queues and shows proof-of-concept latency differences, but its timing study is small and does not establish robust lower-class wait guarantees.

**Implication:** Never claim **“priority-enabled MQTT”** or **“urgent messages before normal messages”** as the central novelty of our paper. We must articulate the actual **decision rule** and provide a clean controlled comparison.

### Finding B — Emergency priority, fairness, and adaptive protection are **already combined** in a closely related 2026 work

**R08 TRIAGE/4** now has a **full-text individual review**. It uses:
- An **ALARM** override above geographically ranked routine traffic.
- Per-device round robin for **within-band** fairness.
- **AAP** for high-rate anomalous sources plus global alarm admission control.
- Simulations, five baselines, scenario ablations, sensitivity tests and a **Raspberry Pi 5 MQTT prototype**.

**Specific observed R08 prototype data:** in C3, TRIAGE/4 alarm RTT **0.158 s** vs strict geographic priority **2.927 s**; scheduler overhead **P50 15.39 µs / P99 50.19 µs** (Table 12, accepted PDF p. 24). Its same-band fairness improves, but **cross-band BACKGROUND starvation is deliberately permitted** and routine-band token scarcity can greatly increase routine waiting.

**Implication:** R08 is the **closest conceptual competitor**, not just a related citation. Any novelty claim must explicitly address the overlap and show whether our **urgent deadlines vs routine waiting** objective yields a genuinely distinct, supported finding.

### Finding C — Instantaneous queue occupancy + priority under bursty traffic is **prior art**

**R09 WTI** already balances a **priority reward** against **queue congestion/loss** via queue-state-dependent Whittle indices. In its network implementation, reported burst loss is **11.7% WTI vs 17.8% SP vs 26.5% WRR**; in a no-burst test, strict priority is slightly faster than WTI (**2170 µs vs 2294 µs**).

**Implication:** We cannot claim the simple combination of **priority + occupancy** as unprecedented. Our narrower **event-level occupancy-dependent aging + urgent-deadline guard** must be evaluated against *matched controls*; a faithful/adapted WTI requires explicit resource and training alignment.

### Finding D — Deadline and age risk can be expressed differently

**R10** treats **peak Age of Information violation** for heterogeneous periodic status updates. **R11** dynamically sorts same-class packets using **remaining per-hop deadline budget**, migrates salvageable critical packets, and selects routes based on occupancy and past delays. It reports a **31%** urgent-delay improvement for its largest studied network, but combines several mechanisms under **infinite-buffer simulation**.

**Implication:** Distinguish **per-event deadline miss** from **freshness threshold violation** and **multi-hop per-level deadline progress**. All are relevant ideas, but they are **not interchangeable endpoints**.

### Finding E — Fairness depends on what is being guaranteed and whether status replacement is legal

**R08**: **intra-band device RR** fairness, but not routine service guarantee across strict bands.

**R11**: lower-class delivery/delay can improve through fallback migration, but salvage increases traffic and can **raise total delay**.

**R12**: under **replace-latest PM**, $\delta$-Fair online algorithms are $O(\delta^4)$-competitive for **total AoI**. Without PM, its FCFS problem has an $\Omega(n^{1/5})$ lower bound. These theoretical guarantees are **not** urgent-alert completion guarantees, and **discarding distinct alarms** is not generally safe.

**Implication:** Define exactly what **routine protection** means: per-class waiting, fairness across devices, fairness between classes, starvation-free service, admission probability, or delivered-age objective. These are distinct claims.

### Finding F — Loss and scheduler overhead must not be hidden by a latency-only result

**R08** reduces admitted-alarm latency in flood scenarios partly through selective **admission shedding**. **R11** shows that saving additional packets can increase system load and total latency. **R01** changes transport semantics; **R09** explicitly optimizes loss.

**Implication:** Report **offered / admitted / rejected / completed / deadline-failed** event counts and distributions; avoid reporting latency among **completed events alone** if the algorithms admit different proportions.

---

## 4. Research gaps: evaluated evidence vs hypotheses

| Proposition | Current status | What would establish it? |
| --- | --- | --- |
| Basic MQTT priority support is novel | **Disproved as a broad claim** by R01/R02/R08 | Do not claim |
| Occupancy-aware priority scheduling under IoT bursts is entirely new | **Disproved as a broad claim** by R09 (also R11 occupancy-related routing) | Do not claim |
| Alarm priority and fairness have not been studied together | **Disproved as a broad claim** by R08 | Do not claim |
| Our occupancy-dependent aging produces a **useful urgent-deadline / routine-waiting tradeoff** under matched bounded-worker workloads | **Open empirical hypothesis** | Registered repeated/held-out experiments; tuned fixed controls; latency + loss + overhead with uncertainty |
| The specific proposed combination is algorithmically original relative to closest methods | **Unresolved** | Formal decision-rule comparison, credible external comparator specification and fair model mapping |
| Our method provides hard deadline or starvation-freedom guarantees | **Not established** | Formal model and proof, or use properly qualified empirical language |
| TRIAGE/4 can serve as a faithful direct baseline in our original worker model | **Not yet established** | Full adaptation specification for device identity, geography, tokens, buffer, admitted work, objective and information parity |
| R09 WTI can be fairly reproduced in an event-level shared queue | **Not yet established** | Queue mapping, state transitions, training budget, discretization, resource and time parity |

**Do not frame any “not evaluated by these seven notes” topic as a universal literature gap** without broader and current searching. Our earlier [related-work catalog](catalog-notes.md) includes R03–R07 and other literature that are relevant but not individually reviewed here.

---

## Next review phase

Continue to 20-25 relevant papers. Use the [review protocol](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/blob/7e419b7ddd1f2808203a48d91849250a85d6d4dc/docs/research/literature-review/review-protocol.md) before selecting an idea or simulation design. The prior worker hypothesis above is historical context, not the committed direction of the new study.
