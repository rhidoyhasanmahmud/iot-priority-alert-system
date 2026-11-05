# R09 — Real-Time Priority Queue Scheduling for Bursty Traffic

| Field | Verified from supplied paper |
| --- | --- |
| Authors | Rongping Lin; Jinpeng Zhang; Shan Luo; Jing Fu; Xiong Wang; Hui Li; Moshe Zukerman |
| Year / publisher | 2025, IEEE |
| Venue | *IEEE Internet of Things Journal*, **12(24)**, pp. 55883–55892 |
| DOI | [10.1109/JIOT.2025.3627212](https://doi.org/10.1109/JIOT.2025.3627212) |
| Actual title | Confirmed on **cover and manuscript title page** |
| Version | **City University of Hong Kong author postprint**, not publisher typeset PDF; PDF 12 pages including 2-page front matter |
| Status | Full supplied postprint reviewed; no faithful replication |
| Relevance | **Very high — important bursty/occupancy-aware scheduling prior art** |
| Existing reference ID | **R09**, preserved |

> **One-minute takeaway:** The authors formulate **switch output-priority-queue scheduling during bursts** as a **restless multi-armed bandit** and use **offline-computed Whittle indices** with **runtime queue-length/priority-state lookup**. Their policy (WTI) trades strict priority service for congestion relief when a lower-priority queue fills, reducing burst packet loss in tested simulations and OVS-DPDK experiments. This is clear prior art for **congestion-aware priority adaptation**—but its **per-queue switch model** and learned transition data differ from our **single application-worker/event-based heuristic**.

## 1. What? — What problem does the paper solve?

The paper addresses the conflict between:
- **Priority differentiation:** High-priority packets should receive favorable service.
- **Burst mitigation:** A heavily congested, potentially *low-priority* output queue may need additional bandwidth before it overflows.

The decision point is a **switch output port containing multiple priority queues** (often eight), where a scheduler selects **one queue** to transmit from at a time. The paper proposes a Whittle-index scheduling method referred to here as **WTI**.

**Crucial scope:** A switch allocates bandwidth among **separate output queues**. This is not identical to selecting one alert from an application-level **shared waiting buffer** with one non-preemptive worker.

**Source:** Abstract (postprint manuscript p. 1 / PDF p. 3), Introduction pp. 1–3, Section III.

<details>
<summary>🇧🇩 বাংলা ব্যাখ্যা — What?</summary>

একটি switch-এর output port-এ ধরো আটটি priority queue আছে। High-priority queue আগে service পায়, কিন্তু low-priority queue-তে একসঙ্গে burst এলে সেটি দ্রুত full হয়ে **packet loss** হতে পারে।

Authors প্রশ্ন করেছেন: কখন strict priority অনুসরণ করব, আর কখন congested lower-priority queue-কে কিছুটা service দিয়ে overflow কমাব?

WTI নামের algorithm-এ **priority + current queue length + estimated state-transition behavior** একসঙ্গে বিবেচনা করা হয়।

</details>

## 2. Why? — Why is this important and why do earlier schedulers fall short?

**Strict Priority (SP)** can starve low-priority queues during bursts, increasing queue lengths and drop rates. **Weighted Round Robin (WRR)** can distribute bandwidth based on weights such as recent traffic volumes, but may undervalue an intrinsically high-priority flow when its recent volume is low. Feedback-based congestion control may react after a delayed network round trip.

The authors view a burst in two phases:
1. **Accumulation:** a queue grows rapidly when arrival intensity exceeds service.
2. **Alleviation:** arrivals subside, but the queue must still be drained effectively.

A scheduler using **instant queue length** can react to both phases without waiting for long-term averages to catch up.

**Novelty boundary for our thesis:** This 2025 publication already uses **occupancy/current queue state in a priority scheduler**, so a claim that “using queue occupancy to adapt priority for bursty IoT traffic is entirely new” would be indefensible.

**Source:** Introduction/Contributions, postprint pp. 2–3; Related Work pp. 3–4.

<details>
<summary>🇧🇩 বাংলা ব্যাখ্যা — Why?</summary>

Strict Priority দিলে high-priority traffic ভালো পায়, কিন্তু bursty low-priority queue full হয়ে যায়। অন্যদিকে WRR শুধু recent traffic weight দেখে service দিলে ছোট কিন্তু গুরুত্বপূর্ণ high-priority flow ক্ষতিগ্রস্ত হতে পারে।

এই paper বর্তমান queue occupancy দেখে সিদ্ধান্ত পরিবর্তন করে। তাই আমাদের project-এ **“queue occupancy অনুযায়ী priority adjust”** একা নতুন contribution বলা যাবে না। পার্থক্য থাকলে সেটি precise rule, resource model ও experimentally demonstrated tradeoff দিয়ে দেখাতে হবে।

</details>

## 3. How? — How does the algorithm work? Explain with an example.

### A. Optimization model

Each output queue $q$ has **queue length $s_{q,t}$** at time slot $t$ and a priority rank. At most **one** queue is selected per slot. The objective combines two rewards:

$$
R_t(S_t,A_t)=\kappa R_{\mathrm{pri}}(S_t,A_t)+(1-\kappa)R_{\mathrm{bur}}(S_t),
$$

where $\kappa$ controls the weight of priority service versus burst handling; $R_{\mathrm{pri}}$ rewards respecting priority and $R_{\mathrm{bur}}$ rewards avoiding crowded queues and loss (Eq. 1, postprint p. 4 / PDF p. 6).

The burst reward uses the queue-fill ratio and a **packet-drop indicator** (Eqs. 3–4). This is not a simple threshold-based aging rule: it is an **MDP reward** evaluated through a Whittle-index formulation.

### B. Offline learning / index table

1. Collect **historical per-queue state-transition data** from the switch to estimate transition matrices.
2. Represent the queue scheduling problem as a **restless multi-armed bandit (RMAB)**, with a queue as an arm.
3. Discretize occupancy to **21 states (0–20)** and approximate the priority-related state with **six levels** $\{0,0.2,0.4,0.6,0.8,1\}$.
4. Use an **offline Q-learning / binary-search-like Whittle index procedure** (Algorithm 1, postprint p. 6 / PDF p. 8) to calculate an index for each modeled queue state.
5. Push the index table to the switch's data plane. At runtime inspect queue states, **look up Whittle indices**, and transmit from the queue with the highest index.
6. Periodically update the transition model and indices using accumulated data.

**Important fairness accounting:** WTI uses **historical transition information/training** not required by our heuristic. Any adapted comparator must disclose data acquisition/training/update cost, discretization, and information access.

### C. Intuitive example (created for learning; not paper simulation)

    Q1 = high priority, 2 packets / capacity 100
    Q8 = low priority, 95 packets / capacity 100

    Strict priority: select Q1 because it has higher priority.
    WTI: may select Q8 if its learned congestion-risk index is higher,
         mitigating imminent overflow before returning to Q1.

This is an **illustration of the objective**, not an assertion of an exact WTI index value or a proven decision for these numbers; the actual decision depends on learned index tables and parameter $\kappa$.

**Source:** Section III (postprint pp. 4–6), Algorithm 1 p. 6, Implementation p. 6.

<details>
<summary>🇧🇩 বাংলা ব্যাখ্যা — How?</summary>

WTI-এর কাজ দুই ধাপে:

**Offline:** পুরোনো queue-state data ব্যবহার করে Whittle index table বের করা হয়। এর জন্য MDP/Q-learning ধরনের calculation লাগে।

**Runtime:** প্রতিটি queue-এর বর্তমান length দেখা হয়, তার index table থেকে value নেওয়া হয়, তারপর **সর্বোচ্চ index-এর queue** থেকে packet পাঠানো হয়।

ধরো Q1 urgent কিন্তু প্রায় empty, আর Q8 low priority হলেও প্রায় full। WTI কিছু পরিস্থিতিতে Q8-কে আগে service দিতে পারে, যাতে packet drop না হয়। **ঠিক কোন queue নির্বাচিত হবে** তা trained index-এর ওপর নির্ভরশীল—এটি fixed formula বা আমাদের aging heuristic নয়।

</details>

## 4. Evidence? — What experiments, baselines, and results support the claims?

### A. Simulation (postprint Section V-A, PDF pp. 8–10)

- **Eight output priority queues**.
- Nominal port capacity **4 Gbps**.
- Background traffic about **70%** of capacity spread across queues.
- Bursty traffic about **20%** directed randomly to a single queue; burst rate assumed **2.5× port capacity**.
- Compared **SP, WRR and WTI**.
- Evaluated queue lengths (Fig. 2), packet loss/other queue metrics (Tables II–III), reward behavior (Figs. 5–6).

**Author interpretation:** SP favors top queues but allows large lower-priority buildup; WRR distributes service but does not consistently preserve urgent priority; WTI balances the two objectives better in tested burst conditions.

### B. Implemented network experiment (Section V-C, PDF pp. 10–11)

The authors implement an **OVS-DPDK** switch setup with a multi-switch test network (Fig. 7), comparing **SP, WRR and WTI** during **normal traffic** and **5-, 7-, 10-, and 15-second injected bursts**.

**No-burst evidence — Table IV (PDF p. 11):**

| Scheduler | Delay (µs) | Loss | Throughput (Mbps) |
| --- | ---: | ---: | ---: |
| SP | **2170** | **0.12%** | **50** |
| WRR | **17913** | **4.22%** | **48** |
| WTI | **2294** | **0.16%** | **50** |

**Meaning:** Under *no burst*, SP is slightly better on latency and loss. WTI remains near SP, while WRR performs substantially worse in this test. **WTI is not universally superior.**

**Burst evidence — Figures 8–9 and associated text (PDF p. 11):**
- Authors report **burst-period loss:** **WRR 26.5%**, **SP 17.8%**, **WTI 11.7%**.
- Reported mean throughput during the burst experiment: **SP 49.6 Mbps**, **WRR 43.7 Mbps**, **WTI 48.7 Mbps**.
- WTI reduces burst-induced maximum delay spikes compared with SP while approaching WRR's burst-handling behavior, but performs much better than WRR under normal load.

### C. Interpretive constraints

- The reported gain is **network switch throughput/loss**, not urgent application-event deadline misses.
- The paper's analytical **asymptotic optimality** claim relies on **decoupled/indexable queues and the RMAB theory conditions** (Theorems 1–2, postprint p. 5). It is not proof of an optimal policy for our shared-queue worker.
- Figures/tables do not establish a fresh statistically independent **per-seed confidence interval** for every burst outcome in the supplied text; do not invent one.

<details>
<summary>🇧🇩 বাংলা ব্যাখ্যা — Evidence?</summary>

Authorরা simulation এবং OVS-DPDK network implementation—দুইভাবে পরীক্ষা করেছেন।

**Burst না থাকলে** Strict Priority-ই সামান্য ভালো: SP delay **2170 µs**, WTI **2294 µs**। কিন্তু **burst চলাকালে** packet loss সবচেয়ে কম WTI-তে: **11.7%**, SP-তে **17.8%**, WRR-তে **26.5%**।

এখানে evidence হলো **burst আসলে queue occupancy-aware decision সাহায্য করতে পারে**, কিন্তু সব workload-এ সব metric-এ WTI winner নয়। আর এগুলো **switch packet**-এর metric; আমাদের application alert deadline-এর সঙ্গে সরাসরি এক নয়।

</details>

## 5. So What? — Critical appraisal and application to our research

### Strengths

- Strong prior work for **real-time, state-aware priority scheduling under bursty traffic**.
- Explicit optimization tradeoff rather than relying only on average traffic weight.
- Both simulation and software-switch implementation.
- Reports baseline conditions where simple strict priority **outperforms** WTI, improving interpretive credibility.

### Limitations and threats to direct portability

1. **Different scheduling object:** switch port selects among **separate class queues**; our worker selects individual events from a **shared** bounded capacity.
2. **Offline training/model cost:** state transitions, index computation, updates and hardware integration are material costs.
3. **State discretization:** 21 occupancy states plus six priority-related levels approximate the model; fidelity under different buffers/workloads is unknown.
4. **Model-dependent optimality:** indexability/asymptotic statements do not imply all finite-size workloads or any non-preemptive single-event queue are optimal.
5. **Different objectives:** packet delay/loss/throughput—not per-alert deadline violations, routine p95 wait or source-level fairness.
6. **Comparator fairness risk:** A simplified “WTI-inspired” heuristic without proper transition modeling is **not a reproduction** of published WTI.

### Model mapping

| Dimension | R09 WTI | Our IoT priority alert system |
| --- | --- | --- |
| Resource | Network-switch output port | One non-preemptive application worker |
| Queue organization | Multiple per-priority output queues | Shared bounded queue |
| Decision | Choose queue each slot | Choose individual event each dispatch |
| State | Class priority, occupancy, transition estimates | Event original priority, waiting age, global occupancy, estimated deadline |
| Learned info | Offline transition/index table | No analogous model-training phase in current candidate |
| Goal | Priority service + burst loss avoidance | Urgent deadline vs routine waiting, admission loss/overhead |

### Research decision

**Closely related prior art, but not a directly equivalent comparator without model alignment.** Read alongside [R08 TRIAGE/4](R08-triage4-semantic-priority-2026.md). If we propose an external WTI adaptation, write down buffer partition, service slots, transition-data generation, training/tuning separation and adaptation names **before running held-out evaluations**.

**Do not claim:** “No earlier bursty IoT scheduler considers occupancy in its priority decisions.”

**Remember:** *WTI is a Whittle-index queue scheduler that balances priority and congestion using learned queue-state transitions. It is not the same as occupancy-weighted event aging, and its empirical gains are specific to switch experiments.*

<details>
<summary>🇧🇩 বাংলা ব্যাখ্যা — So What?</summary>

এই paper আমাদের জন্য খুব গুরুত্বপূর্ণ, কারণ **bursty traffic + priority + queue occupancy** একসঙ্গে আগেই study হয়েছে। আমাদের পার্থক্য প্রমাণ করতে হবে **single-worker event-level scheduling**, **deadline guard**, **routine waiting** এবং **matched evaluation** দিয়ে।

তবে WTI একটি **trained/offline index-based switch scheduler**। আমাদের simple application-worker heuristic-এর সঙ্গে direct numerical comparison করলে model mismatch হবে। WTI-inspired heuristic বানালে সেটিকে **adaptation** বলতে হবে এবং কী বদলানো হয়েছে তা লিখতে হবে।

আরো মনে রাখবে: **no-burst case-এ SP সামান্য ভালো**, তাই সব metric-এ win করা গবেষণার প্রয়োজন বা দাবি নয়; measured tradeoff যথার্থভাবে report করা জরুরি।

</details>

---

**Source integrity:** Uses the supplied 12-page CityUHK author postprint; its journal citation and DOI are printed in the postprint cover. **PDF pages 1–2 are cover/front matter; manuscript p. 1 begins on PDF p. 3.** No independently reproduced training or evaluation. The PDF explicitly restricts re-distribution; only these original analytical notes and DOI links are committed.
