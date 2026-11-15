# A New Back-off Algorithm with Priority Scheduling for MQTT Protocol and IoT Protocols

## 1. Bibliographic record and source

**Review number:** 06 · **Internal reference key:** R15

Marwa O Al Enany; Hany M. Harb; Gamal Attiya. 2021. **A New Back-off Algorithm with Priority Scheduling for MQTT Protocol and IoT Protocols**. *International Journal of Advanced Computer Science and Applications (IJACSA), 12(11), 349-357*. The Science and Information Organization. DOI: [10.14569/IJACSA.2021.0121140](https://doi.org/10.14569/IJACSA.2021.0121140).

- **Identity verification:** title, authors, year, volume, issue, DOI and publisher checked against the [official publisher record](https://thesai.org/Publications/ViewPaper?Code=IJACSA&Issue=11&SerialNo=40&Volume=12) on 15 November 2026; pagination checked in the supplied PDF.
- **Reviewed version:** supplied publisher-formatted PDF, 9 pages. Printed page = PDF page + 348. The attachment filename mentions self-medication, but its contents are this MQTT paper.
- **Source fingerprint (SHA-256):** `6de590032c9fc5de52c5fe468d83c19c34965fcb30ea123519c0592c5a005260`.
- **Reading status:** full text reviewed; algorithms, tables and result figures visually checked on PDF pp. 5-8; no independent replication.
- **Selection:** core-related prior art for broker-side priority plus overload control. Evidence quality is limited; inclusion is not a strong-baseline endorsement. Journal quartile/Scopus status was not independently verified and is not claimed.

## 2. Research problem

The authors seek to reduce MQTT traffic from publishers whose current sending rate exceeds an initial baseline, while favoring publishers with lower baseline publication frequencies. Decisions occur at the broker: apply per-publisher waiting and arrange processing by publisher priority.

This is relevant to our overload/priority question. Its operational definition of importance is low publication frequency, however, rather than semantic emergency, remaining deadline or time already spent waiting.

## 3. Authors' claimed contribution

The proposed combination learns a baseline rate from initial arrivals, applies an exponential delay to faster subsequent traffic, and assigns priority on the broker side. Mosquitto modifications are compared with the original broker for uplink bytes, CPU, RAM and one high-priority publisher's latency.

Treat reduced bytes and the displayed latency trace as reported observations. They do not by themselves establish malicious-message detection, deadline protection, starvation freedom or general scalability.

## 4. Model and assumptions

- Baseline rate is estimated from the first N messages; the evaluation starts each publisher with four regularly spaced messages before introducing random intervals.
- Publisher identities and arrival times are available at the broker. The initial sample is implicitly trusted as representative.
- The prose favors lower-rate publishers and delays a publisher when its current rate exceeds its own baseline.
- Mosquitto 1.6.12 and Paho publishers/subscribers run on the same Windows 10 Pro workstation: Intel Core i7, 16 GB RAM, 64-bit OS (Section V, printed p. 354 / PDF p. 6).
- Publisher counts range from 2 to 100. Uplink traffic is observed for 10 minutes; CPU/RAM traces cover 240 seconds. Figure 4 also includes 15 publishers although the accompanying text lists a different sequence.
- Queue capacity, overflow policy, preemption, tie-breaking, service-time distribution, priority refresh, exact payload/QoS settings and a fully specified end-to-end timing procedure are not established by the evaluation description.
- The paper does not report class-wide deadline misses, routine tail waiting, loss/delivery accounting over all offered traffic, or starvation guarantees.

## 5. Method and decision mechanism

**Baseline -> current-rate check -> waiting -> priority-based processing.**

Section IV-B, Eqs. (1)-(3), printed p. 353 / PDF p. 5 define consecutive interarrival times, the reciprocal of their mean as the baseline rate, and the reciprocal of the latest interval as the current rate. Algorithm 1 applies waiting when the current rate exceeds the baseline. **Visual verification matters:** its line 10 prints a greater-than sign; plain-text extraction of this PDF reverses that sign.

Equation (4) and Table I describe an exponential rate-dependent delay. The tabulated values approximate exp(rate), e.g. rate 2 gives 7.38 seconds. The exponent's normalization/time scale and numerical cap are not specified sufficiently for transfer across rate units; the text mentions a maximum delay without fixing it. Whether waiting blocks only one publisher, a socket, a queue or the broker's event loop is also not made reproducible.

Section IV-C, printed pp. 353-354 / PDF pp. 5-6 intends lower-frequency publishers to receive higher priority. Algorithm 2 sorts the stored publisher rates and uses array position as priority. Reproduction requires resolving ambiguities:

1. Eqs. (5)-(6) label low/high priorities using minimum/maximum rates without clearly reconciling those labels with the lower-rate-first prose.
2. Algorithm 2 compares a publisher's rate with strict greater-than-maximum / less-than-minimum tests over the array apparently containing that publisher. Those branches cannot be reached under that literal interpretation.
3. Sort direction, ties, arrival/departure of publishers and ongoing baseline updates need explicit decisions.

These are documentation/reproducibility concerns, not proof that the authors' implementation executed an incorrect rule. No implementation is selected in this review.

## 6. Evidence ledger

All results are author-reported; calculations and visual readings are identified separately.

| Claim examined | Source location | Actual evidence | Interpretation boundary |
| --- | --- | --- | --- |
| Reduced uplink traffic | Fig. 4 and Section V-A, printed pp. 354-355 / PDF pp. 6-7 | At 30 publishers: 29,400 vs 24,700 bytes in 10 minutes. Reviewer calculation: about 16.0% fewer bytes. At 50 publishers: 57,300 vs 56,650, about 1.1% fewer. | Workload-specific byte reduction; delayed/suppressed work is not necessarily delivered useful work. Improvement is not monotonic with publisher count. |
| Small CPU overhead | Fig. 5 and Section V-B, printed p. 355 / PDF p. 7 | The prose gives maxima of 2.53% vs 3.53%, a difference of 1.00 percentage point; it also says less than 0.75% and less than 1%. | The statements are internally inconsistent. Do not repeat a precise overhead bound. A desktop trace does not establish microcontroller suitability. |
| Similar RAM | Fig. 6, printed p. 356 / PDF p. 8 | Two nearly overlapping traces; axis labels RAM in kilobytes. | Measurement scope/process attribution is unclear. Avoid interpreting the plotted values as verified total broker memory. |
| High-priority latency benefit | Fig. 7 and Section V-D, printed p. 356 / PDF p. 8 | One selected publisher; the modified trace is lower at several plotted times, approximately equal at 0 and 15 seconds, and slightly higher around 5 seconds (visual reading). | Not uniformly lower. Back-off and priority change together; no scheduling-only effect is identified. Exact timing endpoints, precision and run uncertainty are unclear. |
| Stronger latency claim | Section V-D, same page | Text says modified maximum equals original minimum; the visibly overlapping/crossing plotted ranges do not support that assertion. | Do not cite this sentence as an established result or derive an overall latency-reduction percentage from the graph. |
| Suspicious-traffic detection | Sections IV-A and V-A, printed pp. 352, 354 / PDF pp. 4, 6 | Random intervals after a four-message regular prefix are used to activate rate checks. | No labeled attack benchmark, false-positive/negative analysis or genuine emergency burst discrimination is reported. |

## 7. Critical appraisal

**Contribution and clarity.** The paper is useful evidence that broker-assigned frequency priority and back-off were already combined by 2021. The flow from congestion to rate estimation is understandable. The jump from increased rate to suspicious/fake traffic is insufficiently justified: a legitimate alarm burst can produce the same observable pattern. This is a reviewer inference requiring evaluation, not a demonstrated failure on emergency data.

**Internal and construct validity.** Lower traffic can reduce contention irrespective of scheduling order. Separate original, back-off-only, priority-only and combined configurations under matched offered workloads would isolate effects. A low-rate proxy also does not establish urgent-message recognition. Because the initial prefix determines trust and priority, startup representativeness and baseline manipulation need examination.

**Statistical validity.** Independent repeat counts, seeds, confidence intervals and raw per-message samples are not reported in the evaluation section. The short selected-publisher trace cannot establish a latency distribution, tail bound or significance. The graph/text contradiction further weakens the strongest latency claim.

**External validity and reproducibility.** Same-host desktop experiments provide limited support for real networks, constrained devices or sustained overload. The unexplained measurement attribution, missing delay cap/enforcement semantics and priority-rule ambiguities prevent a faithful comparator from being specified from the paper alone. Missing details should be sought from code/authors before implementation; omissions are not evidence that the mechanism cannot work.

**Novelty boundary.** We should not claim that combining broker priority with source-rate back-off is new. Conversely, this paper does not settle how to protect legitimate emergency bursts while controlling overload and bounding routine waiting. That is an open reading question, not yet a field-wide gap.

## 8. Synthesis contribution and open question

This adds an earlier frequency-based MQTT approach alongside [PrioMQTT](PrioMQTT%20-%20A%20prioritized%20version%20of%20the%20MQTT%20protocol.md) and [Priority-enabled MQTT](Priority-enabled%20MQTT%20-%20a%20robust%20approach%20to%20emergency%20event%20messaging.md). Unlike [semantic priority override](Multi-Tier%20Message%20Scheduling%20for%20IoT-Based%20Urban%20Emergency%20Systems%20Through%20Semantic%20Priority%20Override.md), its priority proxy is publisher frequency rather than an explicit alarm label. Both source control and scheduling order can affect reported latency, so offered/admitted/delivered populations must be kept distinct in later comparisons.

**Question for further reading:** Which approaches distinguish legitimate urgent bursts from rate anomalies, and how do their source controls affect deadline failures and routine tail waiting under the same offered workload?

<details>
<summary>বাংলা reading note</summary>

Paperটি related বলে রাখছি। কম rate-এর publisher-কে বেশি priority দেয় এবং rate বেড়ে গেলে back-off করে। কিন্তু জরুরি অবস্থাতেও rate বাড়তে পারে; তাই rate বেশি মানেই fake message বলা যায় না। Latency graph ও লেখার মধ্যে অসংগতি আছে, আর scheduling ও back-off-এর লাভ আলাদা করা হয়নি। Prior art হিসেবে কাজে লাগবে; ফলাফলকে শক্ত প্রমাণ ধরে ব্যবহার করা যাবে না।

</details>

Return to the [review register](../README.md) or [cross-paper comparison](../synthesis/comparison.csv).
