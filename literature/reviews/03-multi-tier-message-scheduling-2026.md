# Multi-Tier Message Scheduling for IoT-Based Urban Emergency Systems Through Semantic Priority Override

## 1. Bibliographic record and source

**Review number:** 03 · **Internal reference key:** R08

João Carlos N. Bittencourt; Paulo Portugal; Francisco Vasques; Daniel G. Costa. 2026. **Multi-Tier Message Scheduling for IoT-Based Urban Emergency Systems Through Semantic Priority Override**. *IEEE Access, 14, 140988-141015*. IEEE. DOI: [10.1109/ACCESS.2026.3732592](https://doi.org/10.1109/ACCESS.2026.3732592).

- **Reviewed version:** Accepted author manuscript; 28 PDF pages. Use DOI in accepted-version banner, not template placeholder.
- **Reading status:** full-text review retained from the earlier knowledge base; no independent replication.
- **Theme:** Semantic alarm priority and source fairness.
- **Provenance:** [earlier detailed English/Bangla review](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/blob/a88623cdbbf08caaccbf102b052c3e05188d7e31/paper-review/papers/R08-triage4-semantic-priority-2026.md). This revision reorganizes existing review evidence; it does not represent a fresh publisher/PDF verification.

## 2. Research problem

How can actual alarms bypass geographically important routine traffic while preventing sources within a priority band from monopolizing service?

## 3. Authors' claimed contribution

TRIAGE/4 combines semantic alarm override, hierarchical service fairness and adaptive admission protection to improve alarm responsiveness in the reported local-queue settings.

This is the authors' proposed contribution and reported evidence, not a conclusion that it is original across the entire literature.

## 4. Model and assumptions

Four strict priority bands share a non-preemptive local server. Alarm labels, geographic/device/source metadata and token parameters are available. The protected delay argument concerns admitted traffic under an arrival envelope and bounded blocking; it is not a path-wide guarantee.

## 5. Method and decision mechanism

Alarm=true maps to ALARM regardless of geography; routine traffic maps to HIGH/STANDARD/BACKGROUND. At completion, select the highest eligible band. Routine bands require tokens and rotate devices. With AAP deployed, ALARM rotates zones then devices in both inactive and active states (Eq. 16, p. 10); statically disabled AAP uses flat device RR. Active protection tests the per-source admission gate before the global gate (Eqs. 11-13, p. 9). Source rejection does not consume global tokens.

## 6. Evidence ledger

All measurements below are author-reported. Page numbers refer to the reviewed version.

| Claim examined | Source location | Evidence | Interpretation boundary |
| --- | --- | --- | --- |
| Local MQTT alarm benefit and routine cost | Table 12, PDF p. 24, C3 | Alarm RTT 0.158 s vs strict geographic priority 2.927 s; routine RTT 3.715 vs 3.557 s | The baseline encodes geographic priority; do not equate it to an already alarm-aware strict-priority policy. |
| Computational cost | Table 12, PDF p. 24, C3 | Scheduling overhead P50 15.39 microseconds; P99 50.19 microseconds | Hardware/workload-specific author measurements. |
| Within-band fairness mechanism | Table 9, PDF p. 20, C2 | Removing device RR lowers device-latency fairness 0.838 to 0.648 | Does not establish cross-band fairness. |
| Conditional bound | Eq. 18, PDF p. 11 | Active admitted ALARM delay bounded by T + bP/C under stated conditions | Pre-activation backlog, admission losses and path delay need separate treatment. |

## 7. Critical appraisal

Construct validity: per-device/zone fairness within a band differs from protecting routine service across bands. Internal validity: AAP admission changes the surviving population, so admitted-only latency must accompany offered/admitted/shed counts. External validity: legitimate surges and incorrect alarm labels can affect admission. BACKGROUND starvation is allowed under sustained alarms (p. 5). The tapering-rate deactivation regime is identified as untested in the discussion (p. 26).

**What would strengthen confidence:** reproduce the relevant mechanism under its stated model; inspect source/configuration availability; document independent-run uncertainty or proof conditions as appropriate. Missing evidence is not proof that the method fails.

## 8. Synthesis contribution and open question

**What this paper establishes for our review:** Closest emergency/fairness conceptual work among these reviewed papers. Alarm priority, fairness and adaptive protection cannot be claimed as an unexplored combination.

**Question raised by this review:** Which routine-service tradeoffs remain when every comparator already recognizes semantic urgency and losses are measured over the full offered population?

This question is a lead for further reading, not a demonstrated literature gap or a selected algorithm. Check other papers for contrary evidence before advancing it.

<details>
<summary>বাংলা reading note</summary>

TRIAGE/4 একই band-এর device fairness দেয়; routine class সবসময় service পাবে এমন দাবি করে না। Alarm latency পড়ার সময় shed হওয়া messages-ও হিসাব করতে হবে.

</details>

Return to the [review register](../README.md) or [cross-paper comparison](../synthesis/comparison.csv).
