> **Literature-first reset (11 November 2026):** Comparisons to our implementation refer to the archived prototype. They are review observations, not a selected contribution or an instruction to resume implementation. Review the broader literature before choosing the conference-paper idea.

# R02 — Priority-enabled MQTT: a robust approach to emergency event messaging

| Field | Source-verified value |
| --- | --- |
| Authors | P S Akshatha; S Divyashree; S M Dilip Kumar |
| Year / publisher | 2024, Springer Nature |
| Journal | *Journal of Engineering and Applied Science*, **71**, article 67 |
| DOI | [10.1186/s44147-024-00400-2](https://doi.org/10.1186/s44147-024-00400-2) |
| Actual title | Verified from **PDF first page**, irrespective of filename |
| Manuscript reviewed | 14-page published open-access article |
| Status | Full supplied article examined; results not independently reproduced |
| Relevance | **High** — direct MQTT emergency-priority prior art |
| Existing reference ID | **R02** (preserved) |

> **One-minute takeaway:** The authors present an MQTT-to-RabbitMQ/AMQP prototype with **Urgent, Critical and FCFS queues**, plus **MySQL persistence**, and report lower delay, jitter and response time for urgent/critical messages than their FCFS setup. The experiment uses **ten messages per topic**; it does **not** establish deadline-guaranteed fairness or behavior under sustained bursts.

## 1. What? — What problem does this paper solve?

The paper aims to give MQTT emergency messages preferential delivery rather than treating messages from all topics uniformly. It categorizes messages into three classes—**Urgent**, **Critical**, and normal **FCFS**—and uses dedicated virtual queues in a RabbitMQ-backed communication flow. Published messages can also be stored in MySQL for historical analytics.

**System boundary:** Publisher → MQTT-capable RabbitMQ broker / AMQP routing → subscriber, with database persistence. This is **messaging-path priority classification**, not a proposed adaptive worker-aging algorithm.

**Research objective in the authors' words (paraphrased):** Compare total publishing time, response time, end-to-end delay and jitter under prioritized queues and conventional FCFS.

**Source:** Abstract p. 1; Problem statement p. 4; architecture pp. 4–6.

<details>
<summary>🇧🇩 বাংলা ব্যাখ্যা — What?</summary>

এখানে problem হলো: অনেক MQTT message-এর মধ্যে **emergency message আগে deliver** করতে হবে। Authors message-কে তিন ভাগ করেছেন—**Urgent, Critical, FCFS/Normal**। RabbitMQ-এর virtual queue দিয়ে urgent আগে, তারপর critical, তারপর normal message deliver করার design করেছেন। MySQL-এ message history-ও রাখা হয়।

আমাদের alert scheduler-এর সঙ্গে topic কাছাকাছি, কিন্তু এই paper মূলত **static priority queue / messaging architecture**; wait বাড়লে priority কতটা পরিবর্তিত হবে, সেটা এর মূল algorithm নয়।

</details>

## 2. Why? — Why does it matter, and where did existing mechanisms fall short?

MQTT QoS 0/1/2 specifies delivery assurance semantics but **does not itself define a standard order that favors emergency content across topics**. For emergency response or shutdown events, processing all incoming messages in one arrival-order queue can delay critical information.

The authors also seek to retain histories for later analysis, arguing that generic MQTT messaging alone is not a complete database archiving solution.

**Important distinction:** Better latency for a high-priority class can be achieved by **shifting waiting time onto the ordinary class**. Reducing urgent latency alone does not show that routine events remain bounded or that neither class starves.

**Source:** Introduction and contributions pp. 1–2; problem statement p. 4.

<details>
<summary>🇧🇩 বাংলা ব্যাখ্যা — Why?</summary>

MQTT-এর QoS level বলে packet delivery কীভাবে নিশ্চিত করার চেষ্টা হবে; কিন্তু **Urgent message normal message-এর আগে যাবে**—এমন built-in emergency scheduling policy নয়। তাই fire alarm-এর মতো message FIFO queue-তে আটকে যেতে পারে।

তবে urgent আগে পাঠালেই system globally fair হয়ে গেল বলা যায় না। যদি বারবার urgent আসে, normal message দীর্ঘসময় অপেক্ষা করতে পারে। এই tradeoff-টাই আমাদের research-এর জন্য গুরুত্বপূর্ণ।

</details>

## 3. How? — How does the system work? Explain with an example.

### Proposed architecture (Figures 1–2, pp. 5–6)

1. An MQTT publisher selects a message type/topic: **Urgent**, **Critical**, or **FCFS/Normal**.
2. The RabbitMQ broker uses that topic classification to select the corresponding **virtual queue**.
3. Service preference is **Urgent → Critical → FCFS**.
4. MQTT data is also saved in a **MySQL database** for analysis and reporting.
5. The authors describe an **M/G/1 priority queue** analytical model for waiting time, separating per-class arrival rates, loads and average service times (pp. 6–10).

**Illustrative example, not the authors' experimental trace:**

    At t=0: normal sensor status N1
    At t=1: urgent smoke alarm U1
    At t=2: critical temperature alert C1

    In an ordinary FIFO queue: N1, U1, C1
    Under the proposed queue service order, once the server is free:
      U1 -> C1 -> N1

The exact start/completion order in a real run depends on whether a message **is already being served**; the paper does not justify claiming arbitrary in-service interruption.

### Mathematical concept

The analytical section models priority-class waiting under an **M/G/1** queue with Poisson class arrivals and general service-time distributions. Let $\rho_u$ be Urgent class load, $\rho_c$ Critical load, and $\overline{R}$ residual service time. Under the authors' model, their equations express:

$$
\overline W_u=\frac{\overline R}{1-\rho_u},\qquad
\overline W_c=\frac{\overline R}{(1-\rho_u)(1-\rho_u-\rho_c)}.
$$

**Interpretation:** When high-priority load approaches capacity, the lower-priority class can suffer rapidly growing expected waiting time. These are **model assumptions**, not measured per-event deadline guarantees.

**Source:** Equations (2), (5) in the analysis section (PDF pp. 9–10).

<details>
<summary>🇧🇩 বাংলা ব্যাখ্যা — How?</summary>

MQTT client message publish করলে RabbitMQ topic দেখে সেটিকে **Urgent, Critical, Normal** queue-তে রাখে। Server service নিতে প্রস্তুত হলে urgent queue-কে প্রথম সুযোগ দেয়। Authors MySQL-এ message save করার কথাও বলেছেন।

ধরো normal status এসেছে, এরপর fire alarm এসেছে। Server এখনো কাজ শুরু না করলে urgent alarm আগে যেতে পারে। কিন্তু **যে message ইতিমধ্যে process হচ্ছে সেটিকে ইচ্ছামতো interrupt** করার guarantee paper-এ নেই।

M/G/1 formula বোঝায়: high-priority traffic load যত বেশি হবে, low-priority message-এর waiting time তত বেড়ে যাওয়ার ঝুঁকি থাকবে। এটা আমাদের **routine starvation** নিয়ে ভাবতে সাহায্য করে।

</details>

## 4. Evidence? — What experiments, baselines, and outcomes support the claims?

### Actual experiment

- Tools: **RabbitMQ**, **MQTT**, **AMQP**, **Wireshark**, **Python**, and **MySQL**.
- Compared: **Urgent**, **Critical**, and **FCFS** queues.
- Reported experimental sample: **10 messages published to each topic under prioritized and FCFS conditions** (p. 10).
- Reported measures: total publishing time (Fig. 5), end-to-end delay (Fig. 6), mean jitter (Fig. 7) and mean response time (Fig. 8), pp. 11–12.
- Timing procedure: a difference between two Wireshark timestamps ($T_2-T_1$) from the MQTT/AMQP exchange (p. 10).

### What the figures and authors report

| Evidence | Observation reported in the paper | Boundary |
| --- | --- | --- |
| **Fig. 5, p. 11** | FCFS takes more total time than the Urgent and Critical queues | Small setup; no sustained-overload evidence |
| **Fig. 6, p. 11** | FCFS has greater measured mean delay | Authors' specific timing definition; verify its applicability before comparing numbers |
| **Fig. 7, p. 12** | FCFS has more mean jitter | No robust confidence intervals/seed protocol stated |
| **Fig. 8, p. 12** | FCFS has greater mean response time | No proof of upper-bound latency or urgent deadline reliability |
| **Figs. 3–4, pp. 7–8** | Database screenshots show urgent/critical message persistence | Functionality evidence, **not** a quantitative storage or reliability benchmark |

**What not to infer:** The paper does not provide large-scale statistical evidence that *any* urgent event will meet a strict deadline under a burst or that routine events are protected from starvation. It primarily demonstrates a small prototype's comparative timing behavior.

### Measurement-quality questions

The timing description on p. 10 associates $T_1$ with an MQTT publish/**ping** request and $T_2$ with an AMQP receive/**connection start** acknowledgment. The exact application-level timestamps and their alignment to message delivery are **not sufficiently clear** for a strong independently reproducible end-to-end-latency claim. The sample count (10/topic) is also too small for persuasive **p95/p99** or rare-deadline-failure estimation.

This is a critical interpretation of **the supplied article**, not a claim that its plotted measurements are fabricated.

<details>
<summary>🇧🇩 বাংলা ব্যাখ্যা — Evidence?</summary>

Authors তিন ধরনের queue-এর performance compare করেছেন। Graph-এ Urgent/Critical queue-এর **delay, jitter, response time** সাধারণ FCFS-এর তুলনায় ভালো দেখানো হয়েছে।

কিন্তু paper-এ **প্রতি topic-এ মাত্র ১০টি message** পাঠানোর উল্লেখ আছে। এত ছোট sample থেকে bursty traffic-এর p99 latency, rare packet loss, বা deadline guarantee confidently বোঝা যায় না।

Wireshark-এ কোন timestamp দিয়ে “end-to-end delay” হিসাব করা হয়েছে, সেটাও আরও পরিষ্কার হওয়া প্রয়োজন। তাই results useful **proof of concept**, কিন্তু বড়-scale rigorous benchmark নয়।

</details>

## 5. So What? — Strengths, limitations and consequences for our project

### Strengths

- Concrete, accessible MQTT/AMQP prototype showing that emergency message separation is feasible.
- Multiple classes rather than a binary urgent/normal split.
- Added persistence path useful for operational audit/history.
- Analytic introduction to class-dependent waiting time.

### Limitations

1. **No differentiated anti-starvation mechanism:** Urgent always dominates; routine waiting/fairness under sustained emergency traffic is not characterized.
2. **Weak tail evidence:** Few messages, no burst stress, no deadline-miss distribution or loss-confidence analysis.
3. **Metric and timestamp ambiguity:** Measured Wireshark timings are not clearly equivalent to worker queue-to-completion time.
4. **Not algorithmically adaptive:** Authors list *dynamic priority messaging* among **future enhancements** (p. 13).
5. **Comparability:** Broker/AMQP setup and MySQL persistence change the system boundary relative to our single-application-worker simulator.

### Direct comparison

| Dimension | R02 | Our repository |
| --- | --- | --- |
| Priority rule | Static three-tier virtual queues | FIFO / strict priority / fixed aging / EDF / experimental occupancy-aware aging |
| Location | RabbitMQ MQTT/AMQP message queues | After MQTT reception: shared non-preemptive worker |
| Main outcomes | Mean delay, mean jitter, response time | Urgent deadline failure, routine waiting p95, admitted/drop counts, overhead |
| Fairness | Not established for lower priority | Explicit routine protection tradeoff |
| Stress | Small prototype | Planned seeded, repeated burst / sensitivity experiments |

**Research decision:** Cite as **direct prior art for emergency priority-enabled MQTT**, not evidence that priority queueing itself is novel. It motivates a more rigorous evaluation of **the cost to routine traffic**, overload/burst performance, and deadline failures.

**Five things to remember:** (i) three static queues; (ii) RabbitMQ + MySQL; (iii) small ten-message-per-topic test; (iv) urgent latency can improve at routine waiting's expense; (v) dynamic priorities are **future work**, not implemented evidence here.

<details>
<summary>🇧🇩 বাংলা ব্যাখ্যা — So What?</summary>

এই paper আমাদের project-এর অনেক কাছাকাছি, কারণ **MQTT emergency priority** ইতিমধ্যে implement করা হয়েছে। সুতরাং শুধু Urgent/Critical/Normal queue বানানোকে নতুন contribution বলা ঠিক হবে না।

আমাদের সম্ভাব্য contribution হলো **উচ্চ priority-এর deadline performance বজায় রেখে routine alert কতটা অপেক্ষা করে**, burst-এর সময় কী হয়, কত loss হয়—এসব controlled experiment করা। Existing paper-এ high-priority benefit দেখা যায়, কিন্তু **routine fairness ও strong tail statistics** স্পষ্টভাবে দেখানো হয়নি।

তাই এই paper implementation feasibility reference; এর চেয়ে ভালো comparison দেখাতে হলে baseline configuration, workload এবং metrics fair রাখতে হবে।

</details>

---

**Source integrity:** All observations follow the uploaded 14-page Springer Nature article and its identified figures/equations. DOI is printed in the supplied file. The review has **not** reproduced experiment code or verified per-message traces.
