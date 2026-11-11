> **Literature-first reset (11 November 2026):** Comparisons to our implementation refer to the archived prototype. They are review observations, not a selected contribution or an instruction to resume implementation. Review the broader literature before choosing the conference-paper idea.

# R12 — Online age of information scheduling: The power of packet management and fairness

| Field | Verified from supplied article |
| --- | --- |
| Authors | Chen-Rui Jien; Tung-Wei Kuo |
| Year / publisher | 2026, Elsevier |
| Journal | *Computer Networks*, **289**, article **112690** |
| DOI | [10.1016/j.comnet.2026.112690](https://doi.org/10.1016/j.comnet.2026.112690) |
| Actual title | Confirmed from first page of **16-page final published article** |
| Status | Full supplied article examined; proofs/simulations **not independently reproduced** |
| Relevance | **Medium–High**, especially theoretical fairness / replaceable-update distinctions |
| Reference ID | **R12** — new paper not in current R01–R09 catalog |

> **One-minute takeaway:** In an **online** status-update scheduling system with unknown future messages and terminals, **keeping all old packets** can make minimizing total **Age of Information (AoI)** fundamentally difficult: every online algorithm has an $\Omega(n^{1/5})$ worst-case competitive-ratio lower bound under FCFS (Theorem 16). If obsolete status updates can be **replaced**, **Round Robin** is $O(1)$-competitive, and any **$\delta$-Fair** scheduler is $O(\delta^4)$-competitive. This explains why **fairness + packet management** matters for *freshness* but does **not** authorize discarding unique emergency events.

## 1. What? — What problem does this paper solve?

The paper asks how to schedule **online status-update delivery to dynamically arriving/departing terminals** so as to minimize the **sum of Age of Information (AoI)** over active terminals and time. The base station (BS) does not know future messages or when terminals will join/leave.

It compares two distinct **queue management rules**:
- **FCFS / no packet management:** Keep every update for a terminal and deliver them in generation order.
- **Packet Management (PM):** When a new update for a terminal arrives, **discard earlier queued updates** for that terminal; keep only the freshest.

The key question is *not* a network-packet priority ordering problem alone: it is whether **discarding obsolete updates** changes the theoretical worst-case quality achievable by an **online** scheduler.

**Metric:** $\mathrm{AoI}(i,S,t)=t-\text{generation time of terminal $i$'s most recently delivered update}$. The **total AoI objective** sums this over all terminals and time. This is **not** peak AoI (R10) and **not** urgent-event response time.

**Source:** Abstract p. 1; Sections 1–2 pp. 1–4.

<details>
<summary>🇧🇩 বাংলা ব্যাখ্যা — What?</summary>

ধরো একটি base station অনেক ব্যবহারকারীকে তাদের সর্বশেষ traffic/weather/status update পাঠায়। নতুন user যেকোনো সময় join করতে পারে, পুরোনো user leave করতে পারে; future arrival আগেই জানা নেই।

Question: প্রতিটি user-এর কাছে **সর্বশেষ information কতটা fresh** থাকবে?

যদি সব পুরোনো update বাধ্যতামূলক পাঠাতে হয় (**FCFS**), backlog বাড়তে পারে। আর যদি পুরোনো information-এর কোনো দরকার না থাকে, নতুন packet এলে আগের waiting update replace করা যায় (**Packet Management**)। Paper-টি এই দুই অবস্থায় **online algorithm-এর theoretical performance** বিশ্লেষণ করেছে।

</details>

## 2. Why? — Why does this matter, and what is missing from conventional assumptions?

Many AoI studies assume periodic, Bernoulli or Poisson message generation and a fixed set of terminals. The authors aim for worst-case results under **arbitrary online message generation** and dynamically changing receivers—without probabilistic arrival assumptions for their competitive guarantees.

**Competitive analysis** compares an online algorithm with an optimal offline scheduler on the same instance:

$$
\mathrm{CompetitiveRatio}(A)=\max_I\frac{\mathrm{AoI}(A,I)}{\mathrm{AoI}(\mathrm{OPT},I)}.
$$

A **constant ratio $O(1)$** means worst-case cost stays within some constant factor of offline optimum, independent of terminal count (under stated assumptions). A large $\Omega(n)$ lower bound means there exist adverse inputs where the ratio grows with $n$.

**Critical insight:** “Always choose freshest packet” sounds efficient, but it can repeatedly serve a noisy source while starving others. A fairness constraint is not merely cosmetic—it controls harmful worst-case service imbalance.

**Source:** Introduction pp. 1–3; Sections 3–4 pp. 4–8.

<details>
<summary>🇧🇩 বাংলা ব্যাখ্যা — Why?</summary>

অনেক scheduling analysis ধরে নেয় সব sensor নির্দিষ্ট frequency-তে data পাঠায়। কিন্তু বাস্তবে user/device join/leave করে, নতুন message কখন আসবে জানা নাও থাকতে পারে।

Authors **competitive ratio** দিয়ে জানতে চেয়েছেন worst-case-এ online decision কত খারাপ হতে পারে offline best solution-এর তুলনায়। তারা দেখিয়েছেন শুধু **সবচেয়ে নতুন packet** বা **সবচেয়ে important terminal**-কে সবসময় service দিলে অন্যরা অনেকক্ষণ অপেক্ষা করতে পারে—তখন total information age অনেক বেড়ে যায়।

আমাদের **routine starvation**-এর সঙ্গে conceptually মিল আছে, কিন্তু এখানে objective **sum AoI**, আমাদের event deadline নয়।

</details>

## 3. How? — How does the method/theory work? Explain with examples.

### A. Online base-station model

- Time divided into **logical slots**; capacity $C$ messages per slot.
- Terminals join and leave; each has a per-terminal packet queue.
- The algorithm learns about messages **only when they arrive**.
- Delivery is modeled as reliable within a logical slot. Channel-level retransmissions are abstracted away rather than explicitly modeled.
- Performance measure is sum of **terminal information age**, not mean queue delay.

### B. Packet Management (PM)

**FCFS case:** a terminal may accumulate many old packets, and all must be delivered in generation order.

**PM case:** when update $m_{\rm new}$ arrives, remove older **waiting** updates for that same terminal, keeping at most **one** unsent message per terminal (Section 2, p. 4).

**Pedagogical example, not paper experimental data:**

    terminal A statuses at 1, 2, 3; no transmission yet
    FCFS: [status-1, status-2, status-3] --> old data also delivered
    PM:   [status-3]                     --> fresh update supersedes older

This policy is suitable for **replaceable status measurements**, not automatically for separate emergency incidents that each need acknowledgment or action.

### C. Round Robin and the delta-fair condition

The algorithm maintains a list of active terminals. A **round** traverses the list and serves each feasible receiver at most once before cycling; the list is updated at round boundaries (Algorithm 1, PDF p. 5).

A scheduler is **$\delta$-Fair** when **a terminal receiving a new message in RR round $r$ is served during one of rounds $r,\dots,r+\delta$**, subject to the paper's formal definition (Section 3.2, p. 5). RR is **1-Fair**.

- Smaller $\delta$ = stronger regularity/fairness of service.
- A fair scheduler need **not** simply transmit the newest message globally at all times.
- The fairness guarantee is **per terminal/round**, not **per priority-class deadline**.

### D. Main formal results

| Result in supplied paper | Meaning |
| --- | --- |
| **Theorem 2** (Section 3, PDF p. 5) | Several unfair greedy policies, including Newest Message First, Most Important Terminal First and Oldest Terminal First, can be $\Omega(n)$-competitive even with PM |
| **Theorem 3** (Section 3/4, PDF p. 5) | Every $\delta$-Fair algorithm is $O(\delta^4)$-competitive **under PM** |
| **Corollary 4** (Section 4) | RR is $O(1)$-competitive with PM |
| **Theorem 16** (Section 6, PDF p. 10) | Without PM/under FCFS, **any randomized online algorithm** has competitive ratio lower bound $\Omega(n^{1/5})$ for the paper's MinAoI-FCFS problem |

These are **worst-case theoretical scaling claims**, not numerical guarantees that any alarm will meet a 100-ms deadline.

**Source:** Section 2 pp. 3–4; Section 3 pp. 4–6; Section 4 pp. 6–8; Section 6 pp. 9–10.

<details>
<summary>🇧🇩 বাংলা ব্যাখ্যা — How?</summary>

**Packet Management** মানে latest status এলে আগের waiting status বাদ দেওয়া যায়। ফলে একটি terminal-এর queue-তে সর্বোচ্চ একটিই unsent update থাকে।

**Round Robin** active terminal-গুলোকে পর্যায়ক্রমে service দেয়। $\delta$-Fair-এর সহজ অর্থ: নতুন message পাওয়া terminal যেন **পরবর্তী সর্বোচ্চ $\delta$ round-এর মধ্যে** service opportunity পায়। $\delta$ ছোট হলে fairness শক্তিশালী।

Math result: PM থাকলে RR-এর worst-case performance offline optimum-এর তুলনায় **constant-factor ($O(1)$)** সীমার মধ্যে থাকে; আর general $\delta$-Fair-এর জন্য $O(\delta^4)$। PM ছাড়া FCFS বাধ্যতামূলক হলে worst-case অনেক কঠিন—$\Omega(n^{1/5})$ lower bound।

এগুলো **AoI-এর theorem**, আমাদের MQTT emergency event deadline theorem নয়।

</details>

## 4. Evidence? — What proves or tests the claims?

### A. Formal proof evidence

Unlike a purely experimental algorithm paper, the principal evidence is **competitive-analysis proofs**:
- Counterexamples showing some unfair policies starve terminals under carefully constructed instances (Theorem 2 / Appendix A).
- Upper-bound analysis for fair algorithms with PM (Theorem 3 / Section 4).
- Reduction from online $\ell_2$-norm flow-time scheduling to show the **FCFS hardness** bound (Theorems 15–16, Section 6).

**These are derived results in the paper**; this note has read but **not independently validated every proof step**.

### B. Simulation setup (Section 5, PDF p. 8)

- Discrete-time simulator with **long-lived** and **short-lived** terminals.
- Short-lived terminal arrivals follow **Poisson** timing; each active for **240 seconds**.
- Per-terminal messages have exponential inter-arrival times with rate uniformly selected **2–5 messages/s**.
- Communication latency follows a **bounded Pareto distribution** (bounds **1** and **$10^5$**, shape **1.16**).
- Default: **30 long-lived terminals**, short-lived mean inter-arrival **10 s**, channel capacity **$C=1$**, horizon **$10^5$ s**.
- **Ten independent runs per data point**.
- Algorithms: **RR**, **OTF (Oldest Terminal First)**, **NMF (Newest Message First)**, **MITF (Most Important Terminal First)**, **Random**.

**Nuance:** While the theory considers arbitrary arrivals, the **simulation uses particular stochastic arrivals**. Do not confuse broad theorem coverage with broad empirical coverage.

### C. Main empirical observations

| Figure | What is varied | Reported finding | Caution |
| --- | --- | --- | --- |
| **2, PDF p. 8** | Long-lived terminals from 5 to 50 | At 50 terminals, RR beats NMF/MITF by **more than two orders of magnitude** in total AoI | Total AoI, **not latency or deadline misses** |
| **3, PDF p. 9** | Short-lived mean interarrival 10–100 s | RR/OTF/Random improve roughly **55–60%** as contention falls; NMF/MITF gain little | Unfairness caused by persistent starvation |
| **4, PDF p. 9** | Channel capacity $C=1$ to 15 | NMF/MITF remain **2–3 orders** worse at low capacity; the gap shrinks near $C=12$ and essentially disappears at high capacity | Extra capacity can mask poor scheduling fairness |
| **Section 5.5, p. 9** | Typical vs adversarial behavior | OTF looks similar to RR in benign simulation **despite** its bad proven worst case | **Average empirical good behavior does not refute worst-case failure** |

**Insight worth remembering:** A method may look competitive in ordinary simulation while remaining extremely poor under adversarial input. This supports purposeful **stress scenarios**, not only average-load trials.

<details>
<summary>🇧🇩 বাংলা ব্যাখ্যা — Evidence?</summary>

এখানে সবচেয়ে বড় evidence **mathematical proof**, শুধু graph নয়। Authors দেখিয়েছেন unfair greedy scheduling-এ কিছু terminal দীর্ঘসময় service পায় না এবং worst-case total AoI বাড়ে।

Simulation-এ RR, Oldest Terminal First, Newest Message First, Most Important Terminal First ও Random compare করেছেন। Default simulation **১০টি independent run**-এর average।

৫০টি long-lived terminal-এর কাছে RR এবং unfair greedy policy-র total AoI-তে **১০০ গুণেরও বেশি** পার্থক্য দেখা গেছে। Capacity বাড়লে এই unfairness-এর সমস্যা কমতে থাকে।

গুরুত্বপূর্ণ: OTF সাধারণ simulation-এ ভালো দেখালেও theoretical worst-case খারাপ। তাই **শুধু typical workloads দেখে fairness guarantee দাবি করা যায় না**।

</details>

## 5. So What? — Critical assessment and relevance to our study

### Strengths

- Rigorous **online/worst-case** fairness results without relying on stochastic arrival assumptions in the theorems.
- Separates **scheduling** from **packet replacement** as two design dimensions.
- Makes a theoretically grounded case for **service fairness**.
- Explicitly highlights how benign simulations can miss starvation pathologies.

### Limitations and transfer constraints

1. **Objective mismatch:** Total **AoI**, not urgent deadline-miss rate or routine-event waiting p95.
2. **Discard semantics:** PM assumes **obsolete same-terminal status packets** can be discarded. Unique emergency event alerts generally may **not** be interchangeable.
3. **Service model:** Logical reliable-slot delivery, not measured MQTT TCP/UDP failure/retry behavior or variable non-preemptive processing cost.
4. **Fairness unit:** Per-terminal service round—not priority-class fairness or guaranteed processing of each alert.
5. **Theory vs practice:** $\delta$-Fair bound may have large constants and is not a directly quantified millisecond SLA.
6. **Empirical limitations:** Typical stochastic simulation (10 runs per point), not a production IoT incident trace; constructed adversarial instances underpin lower-bound claims.
7. **Capacity effects:** Overprovisioning can hide unfairness in average tests, making overload/burst conditions especially important in empirical work.

### Comparison with our project

| Dimension | R12 | IoT Priority Alert System |
| --- | --- | --- |
| Objective | Minimize sum AoI | Trade off urgent deadline misses, routine waiting, loss |
| Scheduling | Terminal-level RR / $\delta$-Fair | Event-level FIFO, strict, aging, EDF, adaptive guard |
| Queue policy | Per-terminal FCFS vs replace-latest PM | Shared bounded queue with rejection/loss |
| Traffic | Arbitrary online theoretical arrivals; stochastic simulation | Synthetic normal/bursty events; trace replay |
| Fairness | Service within a bounded number of RR rounds | Routine class waiting/anti-starvation under urgency |
| Guarantees | Competitive ratio for AoI | Empirical finite-workload measurements; no equivalent theorem |

### Research decision

**Include as theoretical/fairness-related work, not a directly reproducible alert-deadline baseline.** Use its reasoning to motivate:
- Evaluating **service fairness and long-tail waits** rather than relying only on mean latency.
- Including **adversarial/skewed and burst-heavy workloads**, not just benign average demand.
- Keeping **packet discard/admission** policies separate from dispatch algorithms in any comparison.

**Do not claim:** Our scheduler inherits $O(1)$ AoI competitiveness or a starvation guarantee. Such results do not transfer to this different objective and queue model.

**Memory sentence:** *With replaceable status updates, fairness plus packet management enables strong online AoI guarantees; without safe replacement, the theoretical problem and applicable conclusions change.*

<details>
<summary>🇧🇩 বাংলা ব্যাখ্যা — So What?</summary>

এই paper শেখায়: **fair service + replaceable data management** একসঙ্গে তথ্যকে fresh রাখতে সাহায্য করে। কিন্তু আমাদের সব alert replaceable নয়—একটি fire alarm আর অন্য fire alarm আলাদা incident হলে একটি ফেলে দেওয়া যাবে না।

তাই এই paper-এর theorem সরাসরি আমাদের algorithm-এ প্রযোজ্য নয়। তবে **worst-case starvation** পরীক্ষা করার প্রয়োজন খুব সুন্দরভাবে বোঝায়। সাধারণ load-এ algorithm ভালো দেখাতে পারে, কিন্তু unfair extreme input-এ খারাপ হতে পারে।

আমাদের গবেষণায় তাই শুধু average waiting নয়, **routine tail waiting, urgent miss, loss, high-skew burst workload**-ও মাপতে হবে।

</details>

---

**Source integrity:** Reviewed final publisher PDF (16 pages), DOI and publication metadata printed on page 1. The article distinguishes mathematical worst-case results from ten-run stochastic simulations; this note preserves that boundary. No independent proof-checking or code replication was conducted.
