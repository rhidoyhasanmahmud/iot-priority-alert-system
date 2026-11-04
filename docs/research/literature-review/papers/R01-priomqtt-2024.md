# R01 — PrioMQTT: A prioritized version of the MQTT protocol

| Field | Source-verified metadata |
| --- | --- |
| Authors | Gaetano Patti; Luca Leonardi; Giuseppe Testa; Lucia Lo Bello |
| Year / publisher | 2024, Elsevier |
| Journal | *Computer Communications*, **220**, pp. 43–51 |
| DOI | [10.1016/j.comcom.2024.03.018](https://doi.org/10.1016/j.comcom.2024.03.018) |
| Actual title verified from | PDF p. 1, **not filename** |
| Source reviewed | Final publisher PDF, 9 pages |
| Review status | Full supplied article examined; experiments not independently reproduced |
| Relevance | **High** for MQTT priority mechanisms; **limited** direct scheduler comparison |
| Prior repository ID | **R01** — preserved |

> **One-minute takeaway:** PrioMQTT uses MQTT v5 User Properties to attach numeric priorities and a modified broker with a priority-ordered **non-preemptive transmission queue**. Its time-critical transport uses **UDP** rather than standard MQTT's **TCP**. It reports lower RTT in an industrial testbed, but improvement versus standard MQTT jointly reflects **transport change and scheduling**, so it does not isolate priority scheduling's causal effect.

## 1. What? — What problem does the paper solve?

The authors investigate **low-latency, priority-differentiated transmission of industrial IoT messages** using an MQTT-compatible message format. Standard MQTT supplies publish/subscribe communication and QoS levels, but not a standard facility for cross-message **application priority dispatch**. The solution, **PrioMQTT**, distinguishes time-critical and routine messages while retaining coexistence with conventional MQTT clients.

It acts at the **MQTT protocol/broker forwarding path**. This differs from our system's scheduling of alerts at a **post-MQTT, application-level non-preemptive worker**.

**Key terms:** transmission queue; numeric per-message priority; UDP-based urgent channel; mixed UDP/TCP broker; RTT (round-trip time); queueing time; message-loss ratio (MLR).

**Source:** abstract p. 1; Introduction pp. 1–2; Section 4 pp. 4–5.

<details>
<summary>🇧🇩 বাংলা ব্যাখ্যা — What?</summary>

সাধারণ MQTT দিয়ে publisher → broker → subscriber message পাঠানো যায়, কিন্তু **কোন message আগে transmit হবে**, সেটার জন্য built-in priority dispatch নেই। Industrial control message অনেক সময় normal telemetry-এর চেয়ে আগে পৌঁছানো দরকার।

PrioMQTT broker-এর transmission queue-তে priority যোগ করেছে এবং urgent communication-এ TCP-এর বদলে UDP ব্যবহার করেছে। ফলে এটি **broker forwarding ও transport-এর** সমস্যা সমাধান করছে, আমাদের মতো MQTT receive হওয়ার পর application worker-এ event process করার problem নয়।

</details>

## 2. Why? — Why is the problem important?

IIoT systems mix highly time-critical control flows with tolerable-delay updates. TCP's acknowledgments, congestion-control behavior and retransmission policy can add latency to time-sensitive traffic, while ordinary MQTT forwarding does not distinguish message urgency.

The authors also explain why alternative MQTT-SN / SDN solutions may introduce gateways or network equipment dependencies. PrioMQTT tries to support message priorities with **commercial off-the-shelf (COTS)** equipment and an unchanged MQTT packet format.

**Causal caution:** UDP avoids some TCP overhead but does not itself guarantee reliability. PrioMQTT explicitly delegates retransmission and out-of-order handling to applications, which changes failure and consistency semantics.

**Source:** Section 2 (pp. 2–3); Sections 4 and 6 (pp. 4, 8).

<details>
<summary>🇧🇩 বাংলা ব্যাখ্যা — Why?</summary>

একই IoT network-এ emergency control command এবং routine sensor readings একসঙ্গে এলে দুটিকে একইভাবে transmit করলে urgent কাজ দেরি হতে পারে। TCP-এর নিজস্ব reliability mechanism কিছু latency তৈরি করতে পারে। Authors তাই UDP-based critical flow এবং priority queue ব্যবহার করেছেন।

কিন্তু **UDP-তে delivery guarantee থাকে না**; lost/out-of-order packet সামলানোর কাজ application-এ চলে যায়। তাই “RTT কমেছে” মানেই সব ধরনের reliability উন্নত হয়েছে, এমন বলা যাবে না।

</details>

## 3. How? — How does the algorithm / architecture work?

### Broker operation

1. Publisher attaches a numeric priority using an MQTT 5 **User Properties** key/value field; the implementation parses it into a **64-bit unsigned integer**.
2. **Lower numeric value means higher priority**. Priority can be assigned by topic or by individual message.
3. The modified broker's **Message receiver and processor** parses the message, maintains MQTT connection/subscription logic, and enqueues outgoing messages in a priority-ordered **Prio Tx queue**.
4. For **equal priority**, the queue uses **FIFO**. The **Transmitter** sends the selected next message; the policy is **non-preemptive**.
5. The broker manages **UDP** for time-critical PrioMQTT traffic while retaining **TCP** for legacy MQTT traffic. Legacy TCP is treated as low-priority in this design.
6. On fanout to multiple subscribers, the broker can either store one queue element with destination addresses or multiple references to the same payload; experiments use the latter queue-reference configuration.

**Illustrative example (not a measurement):**

    publish(message="alarm", priority=1, via=UDP)
    publish(message="temperature", priority=50, via=UDP)
    publish(message="legacy-status", via=standard TCP)

    Prio Tx order when the transmitter becomes free:
      alarm(priority 1) -> temperature(priority 50) -> legacy-status(lowest)

Once a lower-priority message is transmitting, the paper does not describe interrupting that ongoing send. This matters when translating the policy to our single non-preemptive worker.

### Crucial implementation distinction

The paper changes **both network transport behavior and dispatch order**; it is not simply an application-level dynamic aging algorithm. The priority value is supplied by the publisher, not computed from waiting time or queue occupancy.

**Source:** Section 4.1, pp. 4–5 (priority semantics); Figure 3 p. 4 (broker); Section 4.2 p. 4 (queue and fanout).

<details>
<summary>🇧🇩 বাংলা ব্যাখ্যা — How?</summary>

Publisher MQTT message-এর **User Properties**-এ priority number পাঠায়। এখানে **১ বেশি priority** এবং **৫০ কম priority**। Broker outgoing message-গুলো একটি priority-ordered queue-তে রাখে। একই priority হলে FIFO চলে।

Critical traffic UDP ব্যবহার করতে পারে; standard MQTT client-এর TCP traffic-ও একই broker handle করে। Message transmit শুরু হয়ে গেলে মাঝপথে অন্য message দিয়ে interrupt করার কথা paper-এ বলা হয়নি।

আমাদের scheduler-এর মতো **wait বেড়ে গেলে priority boost** বা **queue occupancy অনুযায়ী priority change** এখানে algorithm-এর মূল বিষয় নয়।

</details>

## 4. Evidence? — What experiments, baselines, and results support the paper?

### Experimental model

- **Real-device industrial topology** with multiple publishers/subscribers, controller and broker (Figure 4, PDF p. 5).
- Topic periods **1, 2, 3, and 5 ms**; packet payload **100, 500, 1000 bytes** (Table 1, p. 6).
- Broker comparison: **PrioMQTT vs standard Eclipse Mosquitto MQTT** in the same stated network scenario, using **1000-byte** payloads for the direct RTT comparison.
- Metrics: **RTT**, broker **queueing time**, queue occupancy, **MLR**.
- The paper reports tens/hundreds of thousands of observations per flow in the payload experiment and **11.04 million total** in the broker-queue experiment (Section 5.2, p. 7).

### Exact reported numeric evidence (Table 3, PDF p. 8)

| Topic pair | PrioMQTT avg RTT | Standard MQTT avg RTT |
| --- | ---: | ---: |
| T1 / T2 | **1.17 ms** | **2.40 ms** |
| T3 / T4 | **1.03 ms** | **2.94 ms** |
| T7 / T8 | **1.24 ms** | **4.03 ms** |
| T5 / T6 | **1.26 ms** | **6.04 ms** |

**Author-reported summary:** **51.30%–79.14%** RTT reductions relative to standard MQTT in the assessed scenario (Section 6, p. 8). This is **not** evidence of that percentage improvement caused by the queue policy alone; the transport stack differs.

**Queue and loss evidence (Table 2, p. 7):** For 2 subscribers, the median/max queue entries were **3 / 33**; for 5 subscribers **6 / 79**, with a 500-entry configured queue. No losses were observed in over $10^7$ transmissions, so authors report **observed MLR < 10^-7**, **not a proof of zero loss** under arbitrary overload.

**Figure interpretation:** At **100 bytes**, priorities have little effect because there is little queueing; at **1000 bytes**, the queueing distinction becomes more visible. Some RTT differences also arise from **hop distance** (Section 5.1, pp. 6–7); do not attribute every difference to scheduling.

### What evidence is missing for our objective?

There is no matched FIFO-vs-aging-vs-EDF **application-worker** experiment, no urgent-deadline miss metric in our model, and no demonstration of routine starvation prevention under sustained alarm load.

<details>
<summary>🇧🇩 বাংলা ব্যাখ্যা — Evidence?</summary>

Paper-এ বাস্তব device/broker setup-এ RTT পরীক্ষা হয়েছে। 1000-byte payload-এ T5/T6 topic-এর **PrioMQTT RTT 1.26 ms**, আর standard MQTT-তে **6.04 ms**—এটি authors-এর Table 3-এর actual number। Total RTT reduction তাঁরা **51.30%–79.14%** বলেছেন।

কিন্তু দুই implementation-এ **transport-ও আলাদা (UDP vs TCP)**। তাই পুরো improvement শুধু priority scheduling-এর জন্য হয়েছে বলা সঠিক হবে না। Table 2-এ over 10 million transmissions-এ loss না পাওয়ায় **observed** MLR খুব কম বলা হয়েছে; mathematical zero-loss guarantee নয়।

</details>

## 5. So What? — Limitations and relevance to our research

### Strengths

- Concrete broker architecture and configurable priority metadata.
- Real-device industrial evaluation and unusually large message count.
- Differentiates queue timing, payload sizes, transport overhead and queue occupancy.
- Shows priority differentiation occurs **when the transmission queue is meaningfully loaded**.

### Critical limitations

1. **Confounding:** UDP/TCP changes and priority ordering occur together in the headline MQTT comparison. Isolating *scheduling contribution* requires a controlled same-transport comparison.
2. **No general fairness guarantee:** A low-priority message may wait behind sustained higher-priority arrivals. No aging/routine waiting guarantee is established.
3. **Reliability tradeoff:** UDP error/retransmission and out-of-order policies are delegated to the application.
4. **Scope:** Prioritization only at the application/broker level; the paper explicitly identifies lack of lower-network-layer priority support (Section 6).
5. **Test limits:** Tested device count, traffic patterns, queue capacity and observed zero loss do not prove adversarial burst resilience.

### Comparison to our project

| Dimension | R01 | Our IoT priority alert research |
| --- | --- | --- |
| Decision point | Broker's outgoing transmission queue | Post-MQTT non-preemptive worker |
| Decision input | Publisher-provided numeric priority | Event priority, wait, deadline/occupancy (policy-dependent) |
| Network transport | UDP critical + legacy TCP | Existing MQTT path; scheduler isolation |
| Comparison | PrioMQTT vs standard MQTT | Matched FIFO, priority, fixed aging, EDF, adaptive candidates |
| Main measures | RTT, queueing time, MLR | Urgent miss/loss, routine waiting, scheduler overhead |

**Decision:** R01 is essential **MQTT priority prior art**, but not a directly equivalent algorithmic comparator. We must not claim that introducing MQTT priorities is novel. Where useful, distinguish **protocol/transmission acceleration** from **post-delivery queue scheduling**.

**Remember:** *PrioMQTT improves RTT by combining priority queueing and UDP; its published gain cannot be credited solely to the scheduler.*

<details>
<summary>🇧🇩 বাংলা ব্যাখ্যা — So What?</summary>

এই paper থেকে clear যে MQTT messaging-এ priority queue **আগেই করা হয়েছে**। আমাদের novelty শুধু “priority message আগে process করি” হতে পারে না।

কিন্তু PrioMQTT **broker থেকে transmit করার আগে** priority দেয়, আর আমাদের experimental worker **MQTT receive হওয়ার পরে** alert schedule করে। তাই আমাদের fair comparison-এ same workload, same service cost, same transport রেখে algorithm পরিবর্তন করা বেশি জরুরি।

Authors নিজেই UDP-এর lost/out-of-order handling এবং lower network layer-এ priority propagation-এর limitation বলেছেন। আর prolonged burst-এ low-priority starvation কীভাবে নিয়ন্ত্রণ হবে, সেটিও এই paper solve করে না।

</details>

---

**Evidence boundary:** All numbers and claims above refer to the supplied **9-page final PDF**, not a web summary. The review is a full-text **critical appraisal**, not an independently reproduced benchmark. PDF page numbers are **1–9**; journal printed pagination is **43–51**.
