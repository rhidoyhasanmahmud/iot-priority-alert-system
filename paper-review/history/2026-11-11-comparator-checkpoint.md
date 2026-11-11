> **Literature-first reset (11 November 2026):** Comparisons to our implementation refer to the archived prototype. They are review observations, not a selected contribution or an instruction to resume implementation. Review the broader literature before choosing the conference-paper idea.

# Full-text comparator checkpoint - 11 November 2026

## Sources and reusable review summaries

These are rechecks of existing reviews, not two newly discovered papers. PDFs are not committed. Detailed English/Bangla reviews remain in the established knowledge base.

### R08: TRIAGE/4

João Carlos N. Bittencourt; Paulo Portugal; Francisco Vasques; Daniel G. Costa. 2026. **Multi-Tier Message Scheduling for IoT-Based Urban Emergency Systems Through Semantic Priority Override**. *IEEE Access*, 14, 140988-141015. Publisher: IEEE. DOI: https://doi.org/10.1109/ACCESS.2026.3732592

Source: supplied 28-page accepted author manuscript. The accepted-version banner supplies the DOI; ignore the template placeholder DOI. Final journal pagination is existing catalog metadata, not the manuscript's placeholder footer. [Detailed review](../papers/R08-triage4-semantic-priority-2026.md).

**Problem and mechanism:** Semantic alarms override geographic rank into ALARM; three routine bands retain geographic grouping. Dispatch is non-preemptive strict priority across four bands. Routine bands use tokens and per-device RR. AAP combines sliding-window/hysteresis activation, per-source then global alarm admission budgets, and hierarchical zone/device alarm RR whenever AAP is deployed, including while inactive (pp. 5-10; Algorithm 1 p. 8; Eqs. 11-16 pp. 9-10).

**Evidence:** Single-server simulation, component/sensitivity studies and Raspberry Pi MQTT prototype. Table 12 (p. 24) reports C3 alarm RTT 0.158 s [0.145, 0.172] versus strict geographic priority 2.927 s [2.528, 3.327]; routine RTT is 3.715 versus 3.557 s. C3 scheduling overhead P50/P99 is 15.39/50.19 microseconds. These are author-reported observations, not our measurements.

**Reviewer assessment:** Strong mechanism separation and practical evidence; fairness is primarily within bands and BACKGROUND starvation remains possible under sustained alarms (p. 5). Admission shedding can improve surviving-alarm latency while losing offered alarms. The active-regime bound in Eq. 18 (p. 11) concerns admitted alarms under its service/envelope assumptions; pre-activation backlog and path latency require separate treatment. Alarm-label errors and token calibration matter. The discussion (p. 26) explicitly identifies the tapering-rate deactivation regime as untested.

**Comparison consequence:** High-priority external comparator candidate. An ordinary urgent-first baseline in our project already sees urgency; do not import the paper's geographic-priority inversion advantage as our expected gain. Per-device/zone fairness differs from cross-class routine waiting. Different queue location alone does not establish novelty.

### R09: WTI

Rongping Lin; Jinpeng Zhang; Shan Luo; Jing Fu; Xiong Wang; Hui Li; Moshe Zukerman. 2025. **Real-Time Priority Queue Scheduling for Bursty Traffic**. *IEEE Internet of Things Journal*, 12(24), 55883-55892. Publisher: IEEE. DOI: https://doi.org/10.1109/JIOT.2025.3627212

Source: supplied 12-page CityUHK postprint, including two front-matter pages. Manuscript p. 1 = PDF p. 3. [Detailed review](../papers/R09-whittle-bursty-queues-2025.md).

**Problem and mechanism:** Switch output queues compete for transmission. WTI combines priority and congestion/loss reward in an RMAB model, estimates action-dependent queue transitions from history, computes Whittle indices offline and chooses the highest-index queue at runtime. Occupancy uses 21 discrete levels and the priority-related occupancy ratio uses six levels (manuscript pp. 4-6 / PDF pp. 6-8). It is not a direct occupancy-weight formula.

**Evidence:** Simulation, OVS-DPDK software-switch and multi-hop network tracks. The software-switch track includes CQ; the network track compares SP/WRR/WTI. Table IV (manuscript p. 9 / PDF p. 11) reports no-burst delay SP 2170 microseconds versus WTI 2294, loss 0.12% versus 0.16%, and 50 Mbps for both. Text on the same page reports burst-period loss WTI 11.7%, SP 17.8%, WRR 26.5%. WTI does not dominate SP on every metric.

**Reviewer assessment:** Strong congestion-aware priority prior art and implementation evidence. Reproduction requires transition collection, training/update budget and numerical convergence choices. Algorithm 1's exact equality conditions need declared practical stopping criteria. The short theorem arguments are not independently verified by this review; do not transfer asymptotic claims to our finite shared-buffer worker. Do not invent seed-level confidence intervals absent from the reported result.

**Comparison consequence:** Essential related work; a faithful direct baseline is not ready. Defining class queues, total buffer allocation, slot/service mapping, unseen transitions and train/test separation precedes implementation. A hand-written queue score called WTI would misrepresent the paper.

## Comparator decision and next implementation work

| Item | Decision at this checkpoint |
| --- | --- |
| Existing eight-policy v1 mechanism study | Retain its registered controls and loss-aware endpoints |
| R08 full-text access | Resolved; supplied method rechecked |
| R08 reproduction | Not implemented or validated by these notes |
| R09 reproduction | Not implemented; training/resource mapping unresolved |
| Algorithmic originality / state-of-the-art superiority | Unestablished |
| Full primary experiments | Not run as part of this review |

**Recommended next work unit: a TRIAGE/4 worker-adaptation specification**, before additional algorithm code or revised held-out evaluation:

1. Specify alarm/zone/device metadata. Our three urgency classes are not the original four bands; record every mapping and empty/merged band.
2. Define shared total waiting capacity, per-device queues, overflow accounting, token refill/initialization, source identity and the Eq. 16 selector.
3. Separate token/AAP admission rejection from buffer rejection. Give all policies identical offered traces and service costs.
4. Declare parameter search/training access and the objective. Include legitimate surges as well as abnormal-rate traces if testing AAP; rate anomalies alone are not verified attacks.
5. Validate hand-calculated dispatch, idle-with-no-routine-token, source-first rejection and inactive-vs-disabled AAP cases.
6. If adding methods/metadata/scenarios, register a versioned protocol amendment before revised evaluation. Record whether any prior held-out results were inspected; use fresh seeds when needed.

This adaptation is a proposed next step, not an already approved fidelity specification. WTI can remain scoped related work for a narrow mechanism paper, with explicit limits; it must be reproduced or otherwise addressed before broad external-superiority claims.

## Conference writing reference

Candidate wording to revise after results:

> We investigate the urgent-deadline versus routine-waiting tradeoff of occupancy-dependent aging with an estimated deadline guard in a bounded, non-preemptive application worker. Unlike TRIAGE/4's semantic/geographic bands and source-aware admission protection, the evaluated rule changes event aging using shared occupancy. Unlike WTI's learned switch-queue indices, it requires no transition-model training. These differences motivate a controlled mechanism study; they do not alone establish novelty or superiority.

Report offered, rejected, completed, late and per-class tail-wait outcomes plus overhead. Cite original papers for their findings and these notes only as internal review records.

বাংলা সিদ্ধান্ত: নতুন PDF খোঁজা এখন blocker নয়। আগে TRIAGE/4-এর worker adaptation কীভাবে হবে তা নির্দিষ্ট করব; তারপর দরকারি code, deterministic tests ও protocol amendment। আমাদের মূল প্রশ্ন urgent deadline রক্ষা করতে গিয়ে routine waiting ও loss কতটা বদলায়। ভালো ফল বা novelty এখনো প্রমাণিত নয়।

## Source fingerprints

| Supplied file | Pages | SHA-256 |
| --- | ---: | --- |
| Multi-tier_Message_Scheduling_for_IoT-based_Urban_(1).pdf | 28 | 886ba8a7289a038e397ed1e27952e8e2403e25df7690b064f88002bb41482a4a |
| 347979676.pdf | 12 | 5d8e729e24bc0b86bd1002b1d8698f3670e8255d0e0d036cad8cb3620627fab6 |

Fingerprints identify the copies reviewed, not publisher authentication. No independent code replication, theorem proof or journal-quartile verification was performed.
