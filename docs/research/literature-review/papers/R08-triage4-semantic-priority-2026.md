# R08 — Multi-tier Message Scheduling for IoT-based Urban Emergency Systems through Semantic Priority Override

| Field | Source-verified information |
| --- | --- |
| Authors | João Carlos N. Bittencourt; Paulo Portugal; Francisco Vasques; Daniel G. Costa |
| Year / publisher | 2026, IEEE |
| Journal | *IEEE Access*; publication metadata already cataloged in the repository: vol. 14, pp. 140988–141015 |
| DOI | [10.1109/ACCESS.2026.3732592](https://doi.org/10.1109/ACCESS.2026.3732592) |
| Exact title | Confirmed from **page 1 of the uploaded document**, not its filename |
| Supplied version | **28-page accepted author manuscript**; top banner states manuscript not fully edited. The template's placeholder DOI **10.1109/ACCESS.2024.0429000** must **not** be cited. Use the accepted-version banner DOI above. |
| Status | **Full supplied accepted manuscript reviewed**; no independent implementation/replication |
| Relevance | **Very high — closest current conceptual comparator** |
| Existing reference ID | **R08**, preserved |

> **One-minute takeaway:** **TRIAGE/4** introduces **semantic priority override** for alarms, four strict bands, **per-device round-robin fairness inside a band**, routine-band token buckets and **Adaptive Alarm Protection (AAP)** that selectively sheds abnormal-source traffic. Extensive simulations plus a **Raspberry Pi 5 MQTT broker** study support alarm responsiveness. However, the method deliberately permits **cross-band BACKGROUND starvation under sustained alarms**, and overload protection can involve **dropping admitted attempts/false alarms**. This combination strongly overlaps our emergency/fairness topic and must be considered before claiming algorithmic novelty.

## 1. What? — What problem does the paper solve?

The paper targets **semantic–geographic priority inversion** in smart-city emergency monitoring. A geographic priority scheme can cause routine telemetry from an important zone to be served **before a genuine emergency alarm from a lower-ranked zone**. In the same band, a noisy device can monopolize FIFO service, preventing another device's emergency observations from reaching responders.

**Proposed approach:** **TRIAGE/4** (Tiered Resource Allocation for IoT Alarm and Geographic-priority Emergency) gives true alarm semantics precedence over zone priority while promoting **device-level fairness** and resisting high-rate faulty/attacker alarm sources.

Three distinct protections matter:
- **Cross-band alarm dominance:** An alarm gets highest service precedence independent of geographic zone.
- **Within-band fairness:** Device-level round-robin prevents a single source dominating its band.
- **Flood protection:** AAP shapes admission during sustained abnormal alarm rates.

**Problem boundary:** Local queueing point, for example **gateway egress or MQTT broker queue**; the authors do **not** establish full multi-hop end-to-end guarantees.

**Source:** Abstract p. 1; Introduction pp. 2–3; Section III pp. 5–11.

<details>
<summary>🇧🇩 বাংলা ব্যাখ্যা — What?</summary>

ধরো Zone A-তে হাসপাতাল আছে বলে ওই এলাকার normal sensor data সবসময় high geographic priority পায়। অন্যদিকে Zone F কম গুরুত্বপূর্ণ হিসেবে চিহ্নিত, কিন্তু সেখান থেকে **fire alarm** এসেছে। শুধু zone priority দেখলে emergency alarm-ও normal data-এর পেছনে আটকে যেতে পারে—এটাই **semantic–geographic priority inversion**।

TRIAGE/4 alarm flag দেখেই message-কে সর্বোচ্চ **ALARM band**-এ তোলে। একই band-এর মধ্যে কোনো এক device অতিরিক্ত message পাঠিয়ে অন্য device-কে আটকে না দেয়, এজন্য **per-device round robin** আছে। অস্বাভাবিক alarm flood হলে **AAP** নামের protection mechanism চালু হয়।

</details>

## 2. Why? — Why is the problem important, and why do earlier approaches fall short?

Life-safety alerts should not be blocked by unrelated telemetry simply because of static geographic rankings. Even a strict alarm priority queue is vulnerable to **one prolific source overwhelming other alarms** in its own band. The authors contrast geographically ranked strict priority/FIFO, fair-queueing, token bucket priority, SDN schemes and adaptive/event-driven designs.

**Crucial nuance:** The paper itself does **not** attempt a blanket guarantee of routine starvation freedom. It deliberately prioritizes life-safety alarms above all routine bands; the authors explicitly accept that **BACKGROUND may starve during sustained alarm activity** (Section III-A, p. 5).

The fairness it emphasizes is **primarily intra-band/per-device**. Our project's objective of *urgent deadline reliability versus routine-event waiting* therefore overlaps, but is **not identical**.

**Source:** Section II (pp. 3–5), Section III-A (p. 5), Section VI (pp. 25–26).

<details>
<summary>🇧🇩 বাংলা ব্যাখ্যা — Why?</summary>

একটি policy একইসঙ্গে **কোনো এলাকার importance**, **actual emergency message-এর urgency** এবং **কোন device কতবার service পাচ্ছে**—এই তিনটি বিষয় বিবেচনা না করলে priority inversion বা একই class-এর unfairness হতে পারে।

TRIAGE/4 urgency এবং **same-band device fairness** address করেছে। কিন্তু এটি বলে না যে normal/background alert কখনো starve হবে না। Alarm flood চললে background অপেক্ষা করতে পারে—authors নিজেরাই limitation স্বীকার করেছেন।

আমাদের গবেষণায় “routine event waiting”-এর প্রশ্নটি তাই কিছুটা ভিন্ন, যদিও TRIAGE/4-এর substantial overlap আছে।

</details>

## 3. How? — How does the algorithm work? Explain with an example.

### A. Classification into four bands

1. **ALARM (Band 0)** — if the message's semantic alarm flag is true, **regardless of geographic priority**.
2. **HIGH (Band 1)** — routine traffic from high-priority zones.
3. **STANDARD (Band 2)** — routine traffic from middle-priority zones.
4. **BACKGROUND (Band 3)** — lowest-ranked routine telemetry.

A message carries fields such as **alarm**, **priority**, **device_id**, **zone**, **payload**. The paper suggests a tertile partition of the active geographic priority range for routine bands; ALARM is a semantic override.

### B. Dispatch algorithm

At each **job completion** (non-preemptive service):
- Iterate the bands in strict order **0 → 1 → 2 → 3**.
- If ALARM has pending messages, choose an alarm source/device using the alarm selector; serve it first.
- For routine bands, require **pending messages AND a token** in that band's bucket.
- **Within each band**, choose the next eligible **device** by round-robin; that device's own messages are FIFO.
- A token is consumed on routine dispatch; routine buckets do **not borrow** from each other.

This is **strict priority across bands**, not global fairness. It does not mean an in-progress lower-priority message is interrupted: dispatch happens when service becomes free.

### C. Adaptive Alarm Protection (AAP)

Under ordinary load the ALARM band has **no active admission-rate restriction**. AAP monitors alarm rates over a **sliding window**, activates when rate exceeds configured thresholds, and uses **hysteresis** to avoid rapid toggling.

Once active, admission protection combines:
- **Per-source token bucket:** selectively limits an abnormal source's alarm rate.
- **Band-global token bucket:** caps total admitted alarms and bounds the admitted burst.
- **Source-aware queue selection:** prevents one source from monopolizing alarms that have passed admission.

**Important:** An excess alarm may be **shed at admission**. "No genuine alarms shed" is an **observed result in selected calibrated traces**, not an unconditional property for any load/parameter set.

**Verified selector detail (11 November 2026, PDF p. 10, Eqs. 15-16):** When AAP is deployed, ALARM selection is two-level round robin: first among non-empty zones, then among devices in the selected zone. This applies in both the inactive and active protection states. Only statically disabling AAP restores flat per-device RR. Do not implement a switch from flat RR to hierarchical RR at activation time.

**Admission detail (PDF p. 9, Eqs. 11-13):** Check the per-source gate before the global gate. A source-rejected arrival consumes no global token. A source passing its own gate can still be rejected by the band-global budget. The source-rate identity and zone/device hierarchy must be specified explicitly in any adaptation.

### D. Paper example plus our explanatory trace

**Paper scenario (Section II, p. 2):** Low-ranked Zone F generates a fire alarm while the high-ranked Zone A generates a burst of routine telemetry. Under TRIAGE/4, Zone F's alarm enters **Band 0**, ahead of Zone A's routine messages. With two alarm devices in Band 0, per-device RR alternates *service opportunities* instead of draining every message from the fastest sensor first.

**Pedagogical schematic (not a captured trace):**

    incoming:
      Zone A, routine, device A1 -> HIGH
      Zone F, fire alarm, device F1 -> ALARM
      Zone B, fire alarm, device B1 -> ALARM

    next dispatch after current job completes:
      ALARM: F1 -> B1 (device RR, if both continuously eligible)
      then HIGH -> STANDARD -> BACKGROUND when higher bands unavailable

### E. Guarantees and their precise boundary

The protected-regime analysis gives a conditional **admitted ALARM delay** bound of the form

$$
D_{\mathrm{active},0}\le T+\frac{b_P}{C},\qquad r_P\le C,
$$

where **$T$** is non-preemptive blocking by a lower-class message already being served, **$b_P$** the allowed alarm admission burst and **$C$** service rate (Eq. 18, p. 11). The authors explain that transient pre-activation queueing must be treated separately; the bound does **not** apply blindly to unadmitted/dropped alarms, arbitrary service times or the entire communication path.

They also derive routine priority waiting-time relationships and a **work-conservation tradeoff**: improving alarm service redistributes waiting cost to lower bands rather than magically eliminating total contention (Eqs. 19–20, p. 11).

**Source:** Algorithms and Figures 1–2, pp. 6–9; AAP Eqs. 7–16 pp. 8–10; Eq. 18 p. 11.

<details>
<summary>🇧🇩 বাংলা ব্যাখ্যা — How?</summary>

প্রথমে প্রতিটি message কে **ALARM / HIGH / STANDARD / BACKGROUND** band-এ রাখা হয়। Fire alarm এলে zone-এর rank কম হলেও **ALARM** band-এ যাবে।

Worker যখন free হবে, আগে ALARM band দেখবে; সেখানে কিছু না থাকলে HIGH, তারপর STANDARD, তারপর BACKGROUND। একই band-এ message অনেক device থেকে এলে **device round robin** চালায়।

Routine band-এ **token bucket** আছে, তাই একেক class কত rate-এ service পাবে তা control করা যায়। AAP কেবল unusual alarm flood detection হলে চালু হয়; তখন faulty/attacker source-এ rate limit এবং ALARM band-এ admission limit দেয়। অতিরিক্ত arrival **drop** হতে পারে।

এখানে guarantee-এর সীমা খুব গুরুত্বপূর্ণ: protected mode-এর **admitted alarm** এবং নির্দিষ্ট rate/service assumptions-এর জন্য delay bound; পুরো network-এর প্রতিটি alarm পৌঁছাবে এমন universal guarantee নয়।

</details>

## 4. Evidence? — Which experiments, baselines and results support the claims?

### Experimental design

- **Five baselines:** strict geographic priority, **FIFO**, **Weighted Fair Queueing (WFQ)**, **Deficit Round-Robin (DRR)**, **Token-Bucket Priority (TBP)**.
- **Discrete-event simulation**, scenarios for semantic inversion (C1), device monopolization (C2), multi-zone emergency (C3); plus flood/malfunction/legitimate emergency (R1–R3), scarcity, ablations and parameter sweeps.
- **Core simulation service rate $C=20$ messages/s** (Table 2, PDF p. 12).
- **C1:** 5 s, 81 total messages, 1 alarm.
- **C2:** 60 s, 528 messages, no alarms, 10:1 rate imbalance.
- **C3:** 20 s, 126 messages, 6 alarms.
- **Ablations** test removal of semantic override, intra-band RR, tokens, AAP or per-source protection.
- **MQTT broker prototype on Raspberry Pi 5**, saturation near $\rho\approx1.4$; **30 runs per prototype scenario**. Some broader simulation experiments report **50 independent runs with 95% CI**; individual stress sweeps may be one run per point (do not silently generalize all plots to replicated CIs).

### High-value source-traced results

| Evidence | Actual result | Important interpretation |
| --- | --- | --- |
| **Table 12, PDF p. 24, C3 MQTT** | TRIAGE/4 alarm RTT **0.158 s [0.145, 0.172]** vs Strict **2.927 s [2.528, 3.327]** and FIFO **3.926 s [3.751, 4.102]** | Very strong **alarm semantic-override** demonstration; routine RTT TRIAGE/4 **3.715 s** vs Strict **3.557 s** → routine cost |
| **Table 12, p. 24, C3** | TRIAGE/4 scheduler overhead **P50 15.39 µs**, **P99 50.19 µs** vs strict **4.63 / 10.11 µs** | Explicit computational price for richer scheduling |
| **Table 12, p. 24, flood** | TRIAGE/4 **476 flood alarms shed/run**, **0 legitimate alarms shed/run** in that configured trace | **Selective** admission protection in this scenario; not zero-loss for all alarms |
| **Ablation, p. 20** | Removing device RR reduces device-latency fairness **0.838 → 0.648** in C2 | Fairness gain attributable to per-device rotation |
| **Ablation, p. 20** | Removing AAP raises alarm latency **34 → 724 ms** (R1) and **53 → 645 ms** (R2) | Overload benefit depends on AAP admission restriction |
| **Ablation, p. 20** | Removing per-source limit increases legitimate alarm loss to **25.5% (R1)** / **18.9% (R2)** | Band-global limiting alone may harm genuine messages |
| **Token scarcity, p. 20** | With rate-limited BACKGROUND, mean wait **7.506 s**; without token limits **1.186 s** | **Routine latency tradeoff** is material, not solved away |
| **Table 11, p. 22** | False-negative alarm labels in flood can suffer **1.422 s** at 30% FNR and **5.733 s** at 50% FNR | Correct upstream alarm classification is a crucial dependency |

**Figure/table references:** Core summary Figure 5 and Table 5 (pp. 17–18), AAP Table 7 (p. 19), component Table 9 and Figure 7 (p. 20), sensitivity Tables 10–11 (pp. 21–22), hardware Table 12/Figure 10 (p. 24).

### What the evidence does not justify

- No guarantee that *every genuine alarm* survives **all** parameter settings or extreme legitimate rates; Table 10 shows legitimate losses for poorly tuned AAP parameters.
- No global starvation-freedom guarantee for routine bands.
- No full network-wide deterministic deadline guarantee across arbitrary multihop paths.
- A prototype confirms local-queue behavior, but does not reproduce real urban radio/interference, heterogeneous links, or production incident rates.

<details>
<summary>🇧🇩 বাংলা ব্যাখ্যা — Evidence?</summary>

এই paper শক্তিশালী কারণ শুধু FIFO/Strict-এর সঙ্গে compare করেনি; **WFQ, DRR, TBP**-ও baseline হিসেবে নিয়েছে, simulation, ablation, parameter sensitivity এবং **Raspberry Pi MQTT prototype** ব্যবহার করেছে।

উদাহরণ: Real broker C3 scenario-তে TRIAGE/4-এর **alarm RTT 0.158 s**, strict priority-এর **2.927 s**। কিন্তু একই table-এ routine RTT কিছুটা বেশি—অর্থাৎ urgent সুবিধার **cost** routine class বহন করে।

Fairness ablation-এ device RR তুলে দিলে Jain's device-latency fairness **0.838 থেকে 0.648** হয়। AAP বাদ দিলে overload-এ alarm delay অনেক বেড়ে যায়। আবার কিছু ভুল protection configuration-এ **legitimate alarm drop** হয়—এটাও authors দেখিয়েছেন।

অতএব এটি **আমাদের সবচেয়ে গুরুত্বপূর্ণ closest paper**গুলোর একটি। শুধু “আমাদের system-এও priority আছে” কোনো novel claim হতে পারে না।

</details>

## 5. So What? — Limitations and implications for our project

### Strengths

- Precisely states *semantic* priority inversion and *within-band* fairness as distinct concerns.
- Provides a fully described dispatch path plus admission-control logic and conditional bounds.
- Uses diverse baselines, ablations, sensitivity studies, error labels, device-scale stress and physical MQTT prototype.
- Reports **routine costs, admission shedding and scheduling overhead**, not only alarm improvement.

### Critical limitations

1. **Not cross-band starvation protection:** BACKGROUND may starve under sustained alarm load **by design** (Section III-A, p. 5).
2. **Admitted-vs-dropped distinction:** AAP bounds and low alarm latency apply to *admitted traffic*; a dropped alarm has no delivery latency. Never optimize admitted-only p95 while hiding losses.
3. **Upstream alarm classifier dependency:** False negatives bypass the semantic override entirely (Table 11).
4. **Parameter sensitivity:** Rate limits and thresholds depend on legitimate/abnormal source behavior. AAP can shed legitimate alerts under miscalibration.
5. **Model scope:** A local, non-preemptive queue and bounded-service assumption, not complete end-to-end networking; prototype does not validate heterogeneous urban deployments.
6. **Tradeoff exists:** Routine service can deteriorate sharply when routine token budgets bind (S1 scenario).
7. **Fairness definition differs from ours:** Device fairness **inside a band** versus our routine-class waiting and high-priority deadline balance.

### Mapping to our implementation

| Dimension | R08 TRIAGE/4 | Our IoT Priority Alert System |
| --- | --- | --- |
| Dispatch point | Local gateway/broker queue | Application-level worker after MQTT delivery |
| Core semantics | Alarm flag overrides geography | Original priority, wait, occupancy, optional deadline |
| Scheduling | Four strict bands + device RR + tokens | FIFO / strict / fixed aging / EDF / experimental guarded adaptive aging |
| Overflow strategy | Token-based admission shaping, selectively sheds abnormal sources | Shared bounded queue; explicit admission losses |
| Fairness | Device-level within-band | Routine-event waiting/tradeoff across urgency levels |
| Evidence | Simulations + Raspberry Pi MQTT prototype | Simulation + MQTT prototype; full runs pending |

### Research decision — **high-priority external comparator**

This paper **closes the earlier full-text-access gap** in the repository's [closest-method review](../../closest-method-comparison.md). Its rules can now be studied in detail. However, a faithful external comparison still requires a **registered model-alignment decision**:

- Do we have geographic zones and device-level identities equivalent to TRIAGE/4's input?
- How do we equate buffer capacity, event service cost, token admission, and event loss?
- If we adapt TRIAGE/4 to our worker, what parts are modified and how do we label that adaptation?
- Which objective is truly comparable: urgent deadline failure, alarm RTT, routine waiting, device fairness or shed counts?
- Can our candidate outperform **matched fixed aging** without hiding loss or sacrificing urgent reliability?

**Do not automatically add TRIAGE/4 to the frozen v1 experiment after outcomes are observed.** First specify the comparator, validate deterministic dispatch examples, register an amendment, and use fresh held-out evaluation runs if needed.

**Memory sentence:** *TRIAGE/4 already combines alarm priority, per-device fairness and adaptive flood protection; its main tradeoff is global routine protection, conditional admission and resource assumptions.*

<details>
<summary>🇧🇩 বাংলা ব্যাখ্যা — So What?</summary>

এই paper আমাদের research novelty নিয়ে **সবচেয়ে গুরুত্বপূর্ণ সতর্কতা** দেয়। এখানে alarm আগে যায়, device fairness আছে, overload protection আছে, mathematical bound আছে, real MQTT prototype-ও আছে। তাই আমাদের adaptive aging algorithm-এর contribution প্রমাণ করতে হলে এই prior work-এর সঙ্গে পার্থক্য খুব পরিষ্কার করতে হবে।

আমাদের focus হলো **urgent deadline failures কমানো + routine waiting control**, কিন্তু TRIAGE/4 **same-band device fairness** দেয়; high-priority alarm এলে background starving মেনে নেয়। এখানেই problem-definition-এর একটি সম্ভাব্য পার্থক্য রয়েছে—এটি নিজের থেকেই novelty proof নয়।

আরেকটি শিক্ষা: যদি algorithm কিছু alert **drop** করে, শুধু delivered alarm-এর latency report করলে misleading ফল হবে। **admitted, shed, completed, deadline-missed** আলাদাভাবে হিসাব করা জরুরি।

</details>

---

### Publication/version note

The supplied document is a **28-page IEEE accepted author manuscript** with editable placeholders (including a contradictory template DOI). The **banner** identifies final DOI **10.1109/ACCESS.2026.3732592**. All page/figure references are to this **accepted version**, not necessarily publisher typesetting. No third-party PDF is committed.

**Evidence boundary:** Full text analyzed; analytical proofs, code, hardware measurements, and figures are **not independently reproduced**. This review should inform, not silently modify, the registered experimental protocol.


Rechecked against the supplied 28-page accepted manuscript on 11 November 2026. Source SHA-256: `886ba8a7289a038e397ed1e27952e8e2403e25df7690b064f88002bb41482a4a`. Page numbers refer to this PDF, not final journal pagination. See [verification and comparator checkpoint](../../../../paper-review/2026-11-11-comparator-checkpoint.md).
