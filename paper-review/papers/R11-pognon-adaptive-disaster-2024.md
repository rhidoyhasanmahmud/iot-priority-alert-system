> **Literature-first reset (11 November 2026):** Comparisons to our implementation refer to the archived prototype. They are review observations, not a selected contribution or an instruction to resume implementation. Review the broader literature before choosing the conference-paper idea.

# R11 — Adaptive Priority Scheduling of Internet of Things Data for Disaster Management in Smart Cities

| Field | Source-verified information |
| --- | --- |
| Authors | Marie C. Pognon; Alejandro Quintero; Samuel Pierre |
| Year / publisher | 2024, IEEE |
| Journal | *IEEE Access*, **12**, beginning p. 83285 |
| DOI | [10.1109/ACCESS.2024.3407672](https://doi.org/10.1109/ACCESS.2024.3407672) |
| Actual title | Verified from the **first page of the 14-page article**, not its filename |
| Review status | Full supplied publisher article reviewed; simulation not independently reproduced |
| Relevance | **High** — deadline-aware adaptive priority plus low-priority packet protection in IoT |
| ID choice | **R11** — new title not present in existing R01–R09 index |

> **One-minute takeaway:** This paper proposes an adaptive **multi-hop clustered WSN scheduling/routing** model combining **priority classes, deadline-progress-aware queue reordering, contingency fallback migration, and next-hop selection using congestion and packet history**. Simulations report **31% improved urgent-data mean delay** and **96% improved least-urgent-data mean delay** for the largest tested network compared with the baseline. However, it assumes **infinite queues**, uses multi-hop topology, and permits packet dropping on failure predictions. Its novel components differ substantially from a **bounded single MQTT application worker**, but its priority/fairness/deadline ideas are important prior art.

## 1. What? — What problem does this paper solve?

In a smart-city **disaster-management** network, sensors must forward urgent data through several **cluster heads (CHs)** toward a base station. Congestion, changing node availability and varying deadlines can delay emergency packets, cause packet losses, and disadvantage less urgent messages.

The authors design **Adaptive Priority Scheduling** with three interacting strategies:
1. **Adaptive queue reordering** using each packet's progress relative to its deadline.
2. **Contingency migration** into a high-priority fallback queue when a packet is at risk of missing its deadline but may still be salvageable.
3. **Adaptive next-hop selection** based on node energy, occupancy and previously observed sojourn times.

The architecture is a **hierarchical wireless sensor network with multi-hop routing**, not an MQTT broker or a single application queue.

**Source:** Abstract p. 1; Section III network architecture pp. 4–5; conclusion p. 13.

<details>
<summary>🇧🇩 বাংলা ব্যাখ্যা — What?</summary>

এখানে smart city-র emergency sensor data কয়েকটি **cluster head** পেরিয়ে base station-এ পৌঁছায়। কোনো packet মাঝপথে বেশি সময় আটকে গেলে deadline শেষ হয়ে যেতে পারে।

Authors তিনটি জিনিস একসঙ্গে করেছেন: queue-র ভেতর **deadline progress দেখে reorder**, বিপদে পড়া packet-কে **fallback high-priority queue**-তে migrate, আর কম congested/উপযুক্ত **next hop** বেছে নেওয়া।

এটি আমাদের MQTT receive হওয়ার পর এক worker-এ process করার system নয়; এখানে পুরো **multi-hop WSN routing**-ও algorithm-এর অংশ।

</details>

## 2. Why? — Why is it important and what is missing in simpler methods?

A rigid priority scheduler may favor emergencies but starve routine traffic. A fixed deadline alone does not express **whether a packet is falling behind its required progress along its route**. In multi-hop networks, choosing an overloaded relay can squander time saved by correct local priority decisions.

The paper addresses this with two distinctive parameters:
- **Deadline-progress ratio** — how much time is available *per remaining hop* compared with the original budget per hop.
- **Migration coefficient** — whether similar packets' observed transmission experience suggests that a threatened packet can still reach its destination.

The design also uses per-node congestion and energy information, so queue scheduling is coupled to **routing**.

**Source:** Introduction pp. 1–2; Section III-C pp. 5–8; Section III-D pp. 8–9.

<details>
<summary>🇧🇩 বাংলা ব্যাখ্যা — Why?</summary>

শুধু “packet-এর deadline ১০ সেকেন্ড” জানলে হবে না। পাঁচ hop যাওয়ার কথা, কিন্তু ইতিমধ্যে আট সেকেন্ড লেগেছে আর মাত্র এক hop পার হয়েছে—এমন packet **critical situation**-এ আছে। আবার packet নতুন হলেও তাকে যদি congested cluster head-এ পাঠানো হয়, delay বাড়তে পারে।

এই জন্য authors **time progress বনাম hop progress** হিসাব করে queue position/migration বদলান এবং **network occupancy/experience** দেখে next hop নির্বাচন করেন। আমাদের ক্ষেত্রে multi-hop নেই, কিন্তু **remaining slack** এবং **risk-aware selection** ধারণা relevant।

</details>

## 3. How? — Explain the model, algorithms, equations and an example.

### A. Four classes of packets

The authors classify by **three criticality levels** and whether a packet originated **locally** or at a lower network tier. Class 1 = most urgent regardless of origin; class 2 = next criticality; class 3 = lower-criticality remote data; class 4 = lower-criticality local data. Each CH maintains **four default priority queues**, with a separate **fallback queue** when enabled.

The article describes **preemptive** service in favor of higher classes (Section III-C, p. 8); this differs from our **non-preemptive** worker.

### B. Deadline-progress-aware reordering (Algorithm 1)

Define:
- $d$: global deadline;
- $n$: number of hop-levels from the packet's origin;
- $p$: number of levels still to traverse;
- $a$: elapsed age of the packet.

Then (Eqs. 1–2, PDF p. 5)

$$
IPLD = d/n,\qquad UPLD = (d-a)/p.
$$

The ratio $UPLD/IPLD$ compares **remaining time per remaining hop** to the **original budget per hop**:
- **Below 1:** packet is falling behind the originally planned rate.
- **Above 1:** packet has progressed faster than necessary.

**Within a priority class, Algorithm 1 sorts with tie-break order:** (i) lowest $UPLD/IPLD$ first; (ii) origin level; (iii) smaller size; (iv) earlier arrival (PDF p. 6).

**Teaching example (not the paper's simulation):**
- Packet A: total deadline $d=10$s, 5 levels originally; 7s elapsed, 2 levels remain. $IPLD=10/5=2$s/hop; $UPLD=(10-7)/2=1.5$s/hop; ratio **0.75** = worse than budget.
- Packet B: same original deadline/levels; 3s elapsed, 3 levels remain. $UPLD=7/3\approx2.33$s/hop; ratio **1.17** = ahead of budget.
- **Within equal criticality class**, Packet A is inserted before B under the ratio criterion.

This is **per-hop urgency tracking**, not simple “older packet always first”.

### C. Contingency migration (Algorithm 2)

A packet is considered critical when

$$
\frac{\mathrm{Age}}{\mathrm{Deadline}} >
\frac{\mathrm{HopsCompleted}}{\mathrm{HopsInitiallyRequired}}
$$

(Eq. 3, p. 7). For endangered packets, the migration coefficient is

$$
MC_P = \frac{ADCL}{d},
$$

where **$ADCL$** is average delay of previously delivered packets with **the same criticality and origin level** (Eq. 10, p. 8).

- If the criticality test holds **and** $MC_P\cdot IPLD \le UPLD$, migrate the packet to a **higher-priority fallback queue**.
- Otherwise, if predicted hopeless under the condition, **drop it** as a lost case (Algorithm 2, p. 7).

**Important:** Claims of "avoiding packet loss" must be reconciled with **explicit loss/drop actions** in the algorithm. The method intentionally attempts to distinguish salvageable from unsalvageable work.

### D. Adaptive next-hop (Algorithm 3)

For a packet advancing toward the base station, candidate next CHs are ranked by:
1. Sufficient available energy.
2. Lower occupancy/buffer load for the relevant criticality.
3. Lower average sojourn time for similar packets.
4. Higher residual energy when tied.

Thus, source-to-destination performance is **a composite of scheduling and routing**. Any end-to-end gain cannot be attributed to queue reordering alone without ablation; the paper supplies multiple component cases (Table 4, p. 10).

<details>
<summary>🇧🇩 বাংলা ব্যাখ্যা — How?</summary>

প্রথমে packet চারটি class-এ ভাগ হয়। একই class-এর queue reorder করার সময় **UPLD/IPLD** দেখা হয়।

ধরো ১০ সেকেন্ড deadline, পাঁচটি hop। প্রতিটি hop-এর জন্য শুরুতে গড় budget **২ সেকেন্ড**। সাত সেকেন্ড শেষ, কিন্তু দুই hop এখনো বাকি থাকলে remaining budget **১.৫ সেকেন্ড/hop**, ratio **0.75**—packet পিছিয়ে পড়ছে। তাই same-priority queue-তে তাকে আগে আনা যায়।

আর packet critical হলে **fallback queue**-তে তোলা সম্ভব, কিন্তু predicted hopeless হলে **drop**-ও হতে পারে। Next-hop নির্বাচনে node occupancy এবং similar packet-এর previous waiting time দেখা হয়। অর্থাৎ এখানে **deadline-aware sorting + migration + routing**—সব একসঙ্গে।

</details>

## 4. Evidence? — What experiments and actual results support the claims?

### Experimental setup

- Simulation in **MATLAB R2023b** (PDF p. 9); **no demonstrated field deployment** in the supplied paper.
- **Phase 1:** 15 configurations, **three repeats** for component/combination comparison; fixed **500 sensors / 50 clusters / 5 levels** (pp. 9–11).
- **Phase 2:** selected policies, **five repeats**, varying **100–700 sensors** and **10–70 clusters**, 10 sensors per cluster, five network levels (pp. 9–11).
- Components compared against **Case 1 baseline**:
  - Cases 2–5 reorder variants.
  - Cases 6–8 migration variants.
  - Cases 9–11 next-hop variants.
  - Cases 12–15 combinations.
  - **Case 15** = final combined model.
- Metrics: **mean end-to-end delay**, **delivery ratio**, and count of packet **critical situations**.
- **Important idealization:** The article explicitly assumes **infinite queues** to avoid buffer-size overflow as a limiting factor (p. 10). Equal likelihood of three criticality classes; network structure fixed; sensor processing delay ignored; no aggregation.

### Reported findings and tradeoffs

| Evidence | Author-reported observation | Nuance |
| --- | --- | --- |
| **Fig. 2, p. 11** | Ratio-first packet reorder (Case 3) improves mean delay over baseline | Deadline-progress signal can be more helpful than fixed deadline |
| **Fig. 3, p. 11** | Reordering alone decreases delivery ratio; migration improves it | One mechanism may improve delay and **harm deliveries** |
| **Fig. 5, p. 11** | Combined Case 15 and adaptive next-hop Case 11 reduce mean delay as network size grows in tested range | Composite result cannot isolate queue-only benefit |
| **Figs. 6–8, p. 12** | Class-specific delays vary, migration can favor less urgent packets | Fairness claim is **context-specific**, not formal starvation freedom |
| **Fig. 9, p. 12** | Combined Case 15 is the strongest/stablest reported delivery-rate option across network sizes | Simulation assumes infinite buffers |
| **Fig. 10, p. 12** | Case 15 shows the largest reduction in counted critical situations | A packet can be counted as critical more than once |
| **Conclusion, p. 13** | Largest tested network: mean delay **48.8 ms** for criticality 1, **54.3 ms** for criticality 3; improvements **31%** and **96%** vs baseline; lowest delivered fraction observed **99.9%** | **Author-reported scenario values**, not guaranteed under unseen loads |

### Subtle and important negative result

The paper observes that **fallback migration alone increases global average delay** for larger networks even while saving packets, because previously lost packets remain in the network and consume additional resources (Discussion, p. 12). This is directly relevant to our requirement to report **admitted/drop/completed counts together with latency**.

### Statistical evidence boundary

The stated **three/five simulation repeats** are limited compared with extensive seed-based robustness evaluations. The supplied figures do not establish broad p99 or probabilistic deadline guarantees for unforeseen burst distributions. The heavy assumptions around infinite buffers materially narrow the packet-loss claim.

<details>
<summary>🇧🇩 বাংলা ব্যাখ্যা — Evidence?</summary>

Authors MATLAB simulation-এ **১৫টি configuration** compare করেছেন। Final **Case 15**-এ queue reorder + fallback migration + next-hop selection একসঙ্গে কাজ করে।

সবচেয়ে বড় tested network-এর জন্য urgent class-এ **48.8 ms** mean delay, least-urgent class-এ **54.3 ms**; baseline-এর তুলনায় authors বলেছেন **31%** এবং **96%** improvement। Lowest delivery rate **99.9%** report করেছেন।

কিন্তু **queue infinite ধরা হয়েছে** এবং simulation repeat মাত্র তিন বা পাঁচবার। তাই bounded buffer-এ burst এলেও একই loss/latency হবে—এমন দাবি করা যাবে না।

আরেকটি গুরুত্বপূর্ণ result: **migration packet loss কমাতে পারে কিন্তু average delay বাড়াতে পারে**, কারণ এখন আরও বেশি packet system-এ বেঁচে থাকে এবং resource ব্যবহার করে।

</details>

## 5. So What? — Strengths, limitations and research implications

### Strengths

- Closely relevant **emergency priority with fairness/deadline tension**.
- Precise **per-hop deadline-progress** feature and **historical migration coefficient**.
- Abation-like comparisons across reorder, migration, routing and combinations.
- Explicit example of loss/latency conflict rather than universal improvement.
- Uses **queue occupancy** as a routing input—congestion awareness is prior art.

### Limitations

1. **Multi-hop + preemptive service:** Resource model differs from our shared bounded non-preemptive worker.
2. **Infinite queue assumption:** Does not validate finite-capacity admission/drop behavior relevant to our project.
3. **Equal criticality proportions:** Does not directly emulate rare-urgent/high-volume-routine burst distributions.
4. **Combined interventions:** Final result depends on rerouting and fallback as well as ordering, complicating direct queue-only comparison.
5. **Limited simulation repeats:** Hard conclusions about p99, tail distributions or rare failures are unsupported here.
6. **Discard policy:** Predictively dropping an event is not automatically safe for distinct urgent incidents.
7. **Fairness interpretation:** Lower-class improvements under tested settings are not a mathematical starvation-freedom guarantee.

### Mapping to our application

| Dimension | R11 Pognon et al. | Our research |
| --- | --- | --- |
| Network | Clustered hierarchical multi-hop WSN | MQTT + single application worker |
| Scheduling | Four classes + preemptive priority + deadline-progress ordering | Non-preemptive policies and aging/guard |
| Added mechanisms | Fallback migration + adaptive next-hop | Shared bounded queue, no multi-hop routing |
| Congestion | Node/route occupancy | Worker queue occupancy |
| Goals | End-to-end delay, delivery ratio, critical situations | Urgent failure, routine wait, loss, overhead |
| Evidence | MATLAB simulation | Simulator plus MQTT prototype, registered tests pending |

### Research decision

**High-value related work** for deadline- and congestion-aware emergency scheduling, but not a ready-to-run directly matched competitor. It directly undermines any claim that **deadline-progress-aware, congestion-aware, fairness-oriented emergency scheduling** is unprecedented.

Extract the *principles* (deadline risk and measurable latency–loss tradeoffs) while being explicit that our candidate operates **at one non-preemptive worker** and has no routing/migration layer. Any proposed comparison must strip or align multi-hop advantages and keep admission/loss definitions consistent.

**Memory sentence:** *Pognon 2024 combines deadline-progress reordering, fallback migration and congestion-aware routing; its strongest simulation result is composite and assumes infinite queues.*

<details>
<summary>🇧🇩 বাংলা ব্যাখ্যা — So What?</summary>

এই paper আমাদের জন্য গুরুত্বপূর্ণ কারণ এখানে deadline, priority, fairness, queue occupancy—একসঙ্গে ব্যবহার করা হয়েছে। তাই “এগুলো একসঙ্গে ভাবা হয়নি”—এমন broad novelty claim সঠিক নয়।

তবে authors **multi-hop WSN**, fallback queue, **preemption** এবং next-hop routing ব্যবহার করেছেন। আমাদের implementation হলো **bounded, non-preemptive application worker**—different resource model।

Paper-এ infinite queue assumption থাকায় finite-buffer overflow test আমরা আলাদাভাবে করি—এটা useful contribution হতে পারে যদি rigorous evidence থাকে। তবে শুধু আলাদা architecture হলেই নতুন algorithm প্রমাণ হয় না।

</details>

---

**Source integrity:** Full 14-page 2024 *IEEE Access* published document reviewed; bibliographic DOI printed in first-page header. Numerical results quoted from Conclusion p. 13 and qualitative results from Figures 2–10. No simulation scripts, randomness or experiment outcomes independently reproduced.
