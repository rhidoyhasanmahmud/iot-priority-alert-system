# IoT-based smart waste management system: real-time monitoring and environmental compensation

## 1. Bibliographic record and source

**Review number:** 09 · **Internal reference key:** R14

Osama Saeed; Ayesha Noroz; Maimoona Waqar; Abuzar Ali; Daniyal Butt. 2026. **IoT-based smart waste management system: real-time monitoring and environmental compensation**. *Natural and Applied Sciences International Journal (NASIJ)*, 7(1), 42-53. Publisher: IDEA Publishers Group. DOI: [10.47264/idea.nasij/7.1.3](https://doi.org/10.47264/idea.nasij/7.1.3). [Official publisher record](https://www.ideapublishers.org/index.php/nasij/article/view/7.1.3).

- **Publication date:** 19 July 2026, consistent between PDF p. 1 and official publisher record.
- **Reviewed source:** supplied `NASIJ_2026_7(1)_3_42-53_(b).pdf`, 12 pages. **Printed page = PDF page + 41**.
- **SHA-256:** `f8f2dcc97d513cead03ad7c5e9d3b59b9de908b9165e2e7e3163c34b27248df7`.
- **Review/verification date:** 15 November 2026. Title, five authors, date, venue/pages and DOI checked against the supplied PDF and official publisher record. The PDF's suggested citation spells the final surname “Bhutt”; the byline and publisher author list say **Butt**, used here.
- **Reading status:** full text examined; Tables 1-2 and dashboard screenshots visually inspected; not independently replicated.
- **Selection decision:** **exclude from the core scheduling-paper set; retain this assessment as a screening record and optional application example**. It does not count toward the target of 20-25 relevant scheduling reviews.
- **Venue boundary:** verified publication identity does not establish indexing, journal quartile or methodological quality. No Scopus/Q1/Q2 claim is made.

## 2. Research problem

The application monitors bin fill level and rain so that waste-management staff can see local/cloud status and act before overflow.

The implemented decision is a **sensor-threshold/rain-state decision**. It is not a choice among queued jobs or competing alert priorities. Collection-route optimization is discussed as motivation/future benefit, but no route optimizer or collection-scheduling experiment is presented.

**Source:** introduction printed pp. 43-44 / PDF pp. 2-3; methodology printed pp. 45-47 / PDF pp. 4-6; conclusion printed p. 51 / PDF p. 10.

## 3. Authors' claimed contribution

The authors claim a low-cost smart bin combining:

- HC-SR04 fill-distance measurement;
- rain detection to suppress misleading fill alerts;
- ESP32 Wi-Fi transmission to ThingSpeak;
- local LCD and remote dashboard feedback.

They report 99% correct fill/rain readings and cloud-update delay below two seconds around a 15-second reporting interval, and suggest energy efficiency and urban scalability.

**Review interpretation:** these are integration/prototype claims. The supplied evidence does not demonstrate a new scheduler, lower collection-route cost, reduced public-health incidents or scalable municipal deployment.

**Source:** abstract printed p. 42 / PDF p. 1; gap claims printed p. 44 / PDF p. 3; results printed pp. 49-51 / PDF pp. 8-10.

## 4. Model and assumptions

| Dimension | Reported model and boundary |
| --- | --- |
| Physical prototype | One assembled unit on a 3 ft bin; ultrasonic sensor mounted at the top |
| Observation | Distance-to-waste proxy mapped to Empty/Half/Full; not a demonstrated volumetric or mass measurement |
| Controller/cloud | ESP32, Arduino C++, Wi-Fi and ThingSpeak |
| Local feedback | 16x2 I2C LCD; status messages updated on the reporting cycle |
| Acquisition/reporting | Sections 3.3/3.5 describe reads/uploads every 15 s |
| Rain handling | Measurement/alert suspension and paused fill updates; exact resumption/stale-value policy not specified |
| Calibration | Known-height objects, stated ±2 cm; rain simulation with a spray bottle |
| Runtime/network | Continuous 12 h runs described; reconnection retries every 5 s; tests up to 30 m from router |
| Power | 5 V, 10,000 mAh power bank; operation “up to 24 hours” stated |
| Missing scheduling model | No priority levels across event classes, queue capacity, service-cost model, EDF/aging policy, burst process or routine fairness endpoint |

**Source:** printed pp. 45-49 / PDF pp. 4-8. Single-unit evidence should not be conflated with the dashboard's described ability to monitor multiple bins.

## 5. Method and decision mechanism

### Reported workflow

1. Read the ultrasonic distance and rain sensor through the ESP32.
2. Under dry conditions, classify fill level; the method gives approximately 3 ft for empty, 1.5 ft for half-full and at/below 0.3 ft for the 90% alert threshold.
3. When rain is detected, show rain status and suspend the unreliable fill measurement/alert/update.
4. Send processed data to ThingSpeak over Wi-Fi on a 15 s cycle and update the LCD.
5. Retry connection every 5 s after dropout. A 500 ms post-ultrasonic delay is described as a remedy for stuck readings.

**Source:** Sections 3.3-3.6 printed pp. 45-48 / PDF pp. 4-7; implementation printed pp. 48-49 / PDF pp. 7-8.

**Reproduction gaps:** numeric rain ADC threshold, complete firmware, boundary behavior/hysteresis, fill-conversion equation, stale-data indication, buffered retry semantics and preservation of incidents during rain are not sufficiently specified.

### Environmental compensation versus observation suspension

The title uses environmental compensation, but the operational description mainly **pauses measurements/alerts during rain**. This avoids using suspect readings; it does not demonstrate a correction model that estimates true fill while wet.

**Illustrative failure case (reviewer inference, not an observed result):** if genuine overflow occurs during a prolonged rainy interval, a pause-based detector can defer observing it. The paper does not quantify this missed/delayed-event risk or establish that false-alert suppression has no reliability cost.

## 6. Evidence ledger

All performance values are author-reported; the review has not reproduced them.

| Claim examined | Source location | Actual evidence | Interpretation boundary |
| --- | --- | --- | --- |
| Functional states | Table 1, printed p. 49 / PDF p. 8 | Empty, half, full and rain test outcomes listed | No test counts, individual logs or independent replicate count |
| Fill measurement | Section 4 printed p. 48 / PDF p. 7; Table 2 printed p. 50 / PDF p. 9 | Calibration described at ±2 cm; 99% correct readings reported | Tolerance success rate, not 99% volumetric accuracy; denominator absent |
| Rain detection | Table 2, printed p. 50 / PDF p. 9 | 99% correct, no dry-test false positives stated | Wet/dry prevalence, confusion matrix and number of trials absent |
| Cloud timing | Table 2, printed p. 50 / PDF p. 9 | Value column says <2 s average; explanation says within 2 s in 95% of cases around the 15 s reporting interval | Mean, percentile and event-occurrence delay are not interchangeable |
| Connectivity | Section 4 printed p. 49 / PDF p. 8; Table 2 printed p. 50 / PDF p. 9 | Retry every 5 s, 99% successful transmissions and “no data loss observed” stated | Attempt success, eventual delivery and time availability need separate denominators |
| Physical evidence | Prototype photos printed pp. 45, 48 / PDF pp. 4, 7; dashboard printed p. 50 / PDF p. 9 | Hardware assembly and displayed telemetry | Functionality evidence, not scalability/accuracy validation by itself |
| Runtime and energy | Section 4 printed pp. 48-49 / PDF pp. 7-8 | Up to 24 h power-bank operation; continuous 12 h runs described | No current/energy trace, duty-cycle comparison or efficiency baseline |
| Scalability/cost/route benefits | Results/conclusion printed p. 51 / PDF p. 10 | Qualitative assertions | No multi-bin stress test, priced bill of materials or route/collection experiment |

### Calibration inconsistency

The methodology uses **feet** for the 3 ft bin and thresholds (printed pp. 45-46 / PDF pp. 4-5), while Table 1 uses **3 m, 1.5 m and <0.3 m** (printed p. 49 / PDF p. 8). These units cannot represent the same geometry without correction.

**Reviewer arithmetic:** 3 ft = 0.9144 m; 0.3 ft = 9.144 cm. If the same simple height-fraction mapping were applied to an actual 3 ft bin, a 0.3 m gap would imply approximately 67.2% height fill, not 90%. This demonstrates the consequence of the inconsistency; it does not establish which units the firmware actually used.

### Timing interpretation

A <2 s cloud-update statement after scheduled sampling does not establish <2 s anomaly-onset-to-alert latency. An event can occur between 15 s samples; rain suppression and reconnection can delay visibility further. Raw onset, sampling, publication and dashboard timestamps would be required to quantify the complete boundary. The stated 95% observation also provides no hard worst-case deadline.

## 7. Critical appraisal

### Strengths

- Concrete, accessible ESP32 sensor-to-dashboard prototype with both local and remote feedback.
- Environmental state is considered rather than treating every distance reading as trustworthy.
- Calibration, reconnection interval and some practical integration fixes are described.

### Major limitations and requests for evidence

1. **Low relevance to the research decision.** There is no event-service scheduling algorithm or baseline. Keeping it in the principal comparator set would dilute the literature rather than strengthen it.
2. **Measurement inconsistency.** Resolve feet-versus-metres in Table 1 against firmware and physical calibration. Also distinguish distance/height fill from true waste-volume estimation under irregular surfaces.
3. **Unsupported statistical precision.** “99%” lacks sample size, trial composition, failed-case counts and confidence intervals. “No dry false positives” does not by itself establish detection sensitivity or balanced accuracy. No baseline or ablation isolates the rain mechanism.
4. **Unclear latency endpoint.** Table 2 mixes average and 95%-within-threshold phrasing. Sampling delay and end-to-end observation delay must be separated; there is no deadline-miss or p95/p99 queueing study.
5. **Suppression can create a blind interval.** The implementation avoids wet readings rather than correcting them. Testing would need real full-bin events during rain, pause duration, recovery and stale-data signaling. Missing evidence is not proof that a hazardous miss occurred.
6. **Reliability definitions are conflated.** A 99% transmission-attempt success rate could coexist with eventual recovery if retries buffer data, but this needs event IDs, attempt/acknowledgment counts and replay logs. It cannot be read as 99% uptime or proven loss-free operation.
7. **Scalability, energy and economic claims exceed the measured scope.** A single unit and dashboard screenshots do not establish city-wide operation, cost-effectiveness or battery-efficiency superiority. Broad statements about obstruction/interference robustness lack separate quantified tests.
8. **Bibliographic and artifact clarity.** The byline/citation surname discrepancy should be corrected. References cited within this article have not been independently verified by this review and must not be copied into our reference list automatically. Firmware/data are not supplied as a reproducible artifact in the reviewed text.

**Overall judgment:** useful introductory application demonstration, with substantial measurement/reporting limitations. Exclude from the core scheduling review on relevance grounds, independently of any unverified journal ranking. Publication identity is verified; reported performance remains unreplicated.

## 8. Synthesis contribution and open question

### Connection to the existing reviews

- [Review 02](02-priority-enabled-mqtt-2024.md) is also a prototype, but addresses message classes; this smart-bin paper does not.
- [Review 08](08-cloud-edge-end-textile-monitoring-2026.md) studies an integrated alert pipeline. Here rain-based suspension provides a simpler example of why lower observed alert traffic need not mean better scheduling.
- [Review 03](03-multi-tier-message-scheduling-2026.md) explicitly controls admission. Rain-based suspension is not equivalent to rate-aware admission shedding, and neither can be judged from surviving-alert delay alone.

**Use in our research:** retain the full-text exclusion record so we do not re-screen it. It may illustrate periodic telemetry, sensor-validity states and the distinction between sensing and dispatch. It does not establish a priority-scheduling gap or serve as a faithful comparator.

**Question raised:** how should an alert system indicate unavailable sensing and measure incident coverage during deliberate suppression? This is a measurement/application lead, not a selected contribution or a proven field-wide gap.

<details>
<summary>বাংলা reading note</summary>

Paper-টি ESP32, ultrasonic sensor, rain sensor, LCD ও ThingSpeak দিয়ে smart bin বানিয়েছে। Rain হলে fill reading/alert pause করে। এখানে priority queue বা scheduling algorithm নেই—তাই আমাদের মূল ২০-২৫টি scheduling paper-এর target-এ ধরব না।

মূল সমস্যা: methodology-তে **3 feet**, test table-এ **3 metres**; 99% accuracy বললেও কয়টি test হয়েছে জানা নেই। **15-second reporting cycle-এর পরে 2-second update delay** মানে ঘটনা ঘটার 2 seconds-এর মধ্যে alert নয়। Rain-এর সময় সত্যি bin full হলেও কতক্ষণ নজরের বাইরে থাকবে, সেটি পরীক্ষা করা হয়নি।

শেখার বিষয়: sensor monitoring, alert generation ও queue scheduling আলাদা। Recent paper হলেই আমাদের research-এর জন্য relevant বা strong evidence হয়ে যায় না।

</details>

Return to the [review register](../README.md) or [cross-paper comparison](../synthesis/comparison.csv).
