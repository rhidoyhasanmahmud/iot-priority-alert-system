# PR-MQTT: a novel approach for traffic reduction and message prioritisation in IoT applications

## 1. Bibliographic record and source

**Review number:** 08 · **Internal reference key:** R17

Jiby J. Puthiyidam; Shelbi Joseph. 2024. **PR-MQTT: a novel approach for traffic reduction and message prioritisation in IoT applications**. *International Journal of Web Engineering and Technology, 19(1), 44-66*. Inderscience Enterprises Ltd. DOI: [10.1504/IJWET.2024.138096](https://doi.org/10.1504/IJWET.2024.138096).

- **Identity verification:** title, authors, year, venue, pagination and DOI matched against the [official publisher record](https://www.inderscience.com/info/inarticle.php?artid=138096) on 15 November 2026.
- **Reviewed version:** supplied publisher-formatted PDF, 23 pages. Printed page = PDF page + 43. Hidden/proof text appears in extraction; rendered pages were used to verify equations, algorithms and selected results.
- **Source fingerprint (SHA-256):** `182be371f4534318b496f0da3ffdfc42c684e94b93bccb45467258620e41e07a`.
- **Reading status:** full text reviewed; no independent replication. Visual checks: PDF pp. 11-12, 15 and 18.
- **Selection:** core-related broker-side value classification, urgent-first queueing and selective forwarding. This is a distinct paper from PrioMQTT (R01). No independent quartile/indexing claim.
- **Version relationship:** p. 45 identifies this journal article as an expanded conference paper. Do not count an earlier version as an independent study without checking overlap.

## 2. Research problem

How can a resource-constrained MQTT broker identify important sensor updates and forward them promptly while reducing nearly unchanged routine updates?

The broker learns each publisher's initial min-max range. Out-of-range values become urgent; near-identical in-range values may be suppressed. This is directly relevant to priority and overload handling, but it changes both service order and the population forwarded to subscribers.

## 3. Authors' claimed contribution

PR-MQTT modifies HBMQTT without changing the standard MQTT packet/header format. It combines normal-range estimation, a trivial-interval filter with a skip limit, and front-of-queue insertion for priority messages.

The authors report roughly constant priority latency, less forwarded traffic/CPU use and shorter normal-message delay. These describe the combined intervention in the tested settings, not isolated scheduling gains or a general real-time guarantee.

## 4. Model and assumptions

- Multiple publishers feed one subscriber. Values are elementary sensor data; a publisher's first n messages are assumed adequate to define its normal range (Section 4, pp. 52-55).
- Out-of-range means priority. This is a value-based anomaly proxy, not independently validated emergency semantics.
- Normal updates sufficiently close to the preceding update can be omitted; a skip limit periodically forces forwarding. Such omissions alter delivery semantics even when permitted by the application.
- Broker: Raspberry Pi 3, 1.4 GHz, 1 GB RAM; HBMQTT. Publishers: ESP32 with BME280 sensors. The prose says i7 subscriber laptop while Table 2 says i5/8 GB (p. 57); exact configuration needs clarification.
- Table 3 and pp. 57-58 describe 10/40 simultaneous publishers, one subscriber, about 50 messages/s per publisher, about 250 normal plus 25 priority messages per publisher, QoS 0, trivial interval fixed at 10 points and skip limit 5.
- The evaluation's fixed interval does not establish the efficacy of the learned interval formula across sensor units/workloads.
- Queue limits, overflow handling, sustained all-urgent workloads, aging, execution preemption and class-wide deadline/tail metrics are not established.

## 5. Method and decision mechanism

**Learn normal range -> classify update -> suppress similar routine updates or enqueue -> prioritize forwarding.**

Eqs. (1)-(2) and Algorithm 1 (pp. 53-54 / PDF pp. 10-11) compute initial publisher-specific minima/maxima. Eq. (3) computes a mean of consecutive value differences as the trivial interval.

Out-of-range messages go to queue position zero; other forwarded messages go to the back (Eq. (4), Algorithm 2, pp. 55-56 / PDF pp. 12-13). Normal messages whose change is within the trivial interval are skipped until the skip-limit condition triggers.

**Material ambiguities, visually checked:**

1. Eq. (3) and Algorithm 2 print signed differences without absolute values, while the temperature example on p. 56 sums absolute changes. Signed changes can cancel or become negative; the intended rule must be resolved.
2. Eq. (4) uses strict outside-range inequalities, but Algorithm 2 flags equality with min/max as high priority. Boundary behavior differs.
3. The p. 56 example says skip limit 3 forwards the third update after two omissions; p. 54 describes a maximum number skipped followed by forwarding the subsequent message. The counter convention/reset is not fully reproducible.
4. Inserting every priority arrival at the first queue position can let newer urgent updates overtake older urgent updates under a literal implementation. Within-priority order is not resolved.
5. Broker-side filtering cannot by itself prevent the publisher-to-broker transmission already needed for classification. Some prose says not forwarded to the broker, whereas the architecture shows filtering there.

These are concerns about the published specification; they do not prove the authors' source code used the literal ambiguous behavior.

## 6. Evidence ledger

All measurements are author-reported. Approximate visual readings and reviewer calculations are labeled.

| Claim examined | Source location | Actual evidence | Interpretation boundary |
| --- | --- | --- | --- |
| Priority delivery at low delay | Fig. 5, p. 58 / PDF p. 15; discussion p. 62 | Priority points mostly lie far below normal-message points; prose claims 10-15 ms and over 90% speed improvement. Some plotted priority points visibly exceed 15 ms. | The prose range is not an established maximum/tail bound. Comparing urgent and normal messages inside PR-MQTT does not isolate its effect versus an equally urgent-aware baseline. |
| Traffic reduction | Fig. 8, p. 61 / PDF p. 18 | At 1,100 input messages, 853 forwarded vs 1,100; at 11,000, 8,548 vs 11,000. Reviewer calculation: about 22.5% and 22.3% fewer forwarded messages. | Plot counts forwarded messages, not network bytes or publisher uplink savings. The authors' nearly 25% description is approximate and does not establish equal delivered work. |
| Lower normal delay | Fig. 9, p. 61 / PDF p. 18; conclusion p. 63 | Filtered routine-message trace is substantially below standard MQTT; authors summarize about 50% reduction. | Filtering reduces offered work to the forwarding stage. No filtering-only versus scheduling-only ablation identifies the cause. |
| CPU/RAM | Figs. 6-7, pp. 59-60 / PDF pp. 16-17 | Authors report lower CPU and approximately similar RAM, attributing savings to suppressed forwarding. | Lower total work can offset added classification cost. The 25% CPU statement is not a per-dispatch overhead result. |
| Evaluation scope | Tables 2-3, p. 57 / PDF p. 14 | Two publisher sizes, QoS 0, a fixed filter interval and skip limit. | Does not demonstrate deadline reliability under QoS 1/2, distribution shift, multiple subscribers or persistent urgent saturation. |

## 7. Critical appraisal

**Contribution and relevance.** This is close prior art for broker-side classification, queue reordering and congestion reduction without adding priority flags to the wire format. An idea based solely on moving classification to the broker or skipping routine duplicates would overlap.

**Internal validity.** The standard HBMQTT comparison changes classification, filtering and queue order together. Same input data do not mean equal forwarded/delivered workloads. A controlled comparison should report source-offered, intentionally suppressed, admitted, delivered and failed populations separately. There is no need to call application-approved suppression accidental packet loss, but it still changes what the receiver sees.

**Construct validity.** Initial min/max learning assumes a representative baseline and stationarity. Normal drift, an already abnormal training period, persistent abnormal values or clinically/industrially important changes inside the learned range can change priority correctness. These are reviewer hypotheses, not observed classification failures. The paper does not establish that every discarded value is irrelevant to downstream decisions.

**Statistical and reproduction limits.** Repeated independent runs, confidence intervals, timestamp synchronization/endpoint details and per-class tails are insufficiently documented. Signed-versus-absolute differences, range boundaries and skip-limit semantics materially affect any replication. A message-count skip limit is not a universal wall-clock waiting bound.

**What would strengthen confidence:** resolve the formula/example differences; publish matched-stage timing and raw samples; separate filter/order effects; test sensor drift and abnormal training; measure low-priority waiting and older urgent-message overtaking during long bursts.

## 8. Synthesis contribution and open question

Compare this with [frequency-based back-off](A%20New%20Back-off%20Algorithm%20with%20Priority%20Scheduling%20for%20MQTT%20Protocol%20and%20IoT%20Protocols.md): both infer treatment from observed publisher data, but PR-MQTT uses values while the earlier approach uses publication rate. Unlike [PrioMQTT](PrioMQTT%20-%20A%20prioritized%20version%20of%20the%20MQTT%20protocol.md), it changes forwarded traffic via value filtering.

**Question for further reading:** How do priority mechanisms protect important updates and routine freshness when urgency classification and selective forwarding are imperfect or the sensor distribution changes?

This is a reading question, not yet a literature gap or an implementation choice.

<details>
<summary>বাংলা reading note</summary>

PrioMQTT আর PR-MQTT আলাদা paper। এটি sensor value-এর normal range শিখে abnormal value-কে urgent করে এবং কাছাকাছি routine update বাদ দেয়। ফলে latency কমলেও সব লাভ queue order থেকে এসেছে বলা যাবে না। Equation-এ signed difference, example-এ absolute difference; এই অসংগতি ঠিক না করে baseline বানানো যাবে না।

</details>

Return to the [review register](../README.md) or [cross-paper comparison](../synthesis/comparison.csv).
