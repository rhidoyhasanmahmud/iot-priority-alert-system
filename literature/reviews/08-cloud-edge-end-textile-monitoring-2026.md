# A Cloud-Edge-End Collaborative Remote Monitoring and Scheduling System for Textile Equipment

## 1. Bibliographic record and source

**Review number:** 08 · **Internal reference key:** R13

Chi Zhang; Peng Lin; Cancan Rao; Hongjun Li; Jun Wang; Chengjun Zhang; Hang Hu. 2026. **A Cloud-Edge-End Collaborative Remote Monitoring and Scheduling System for Textile Equipment**. *Applied Sciences*, 16, article 5773. Publisher: MDPI. DOI: [10.3390/app16125773](https://doi.org/10.3390/app16125773).

- **Publication date in supplied PDF:** 8 June 2026.
- **Reviewed source:** supplied publisher-formatted `applsci-16-05773-v2.pdf`, 32 pages. Printed page numbers match PDF pages. The filename's v2 suffix identifies the supplied copy; it is not independently established as a separate journal edition.
- **Source fingerprint (SHA-256):** `7b937c49072ad0a13ca0feb3f21d318b493dfe4d6bfa1e8e92d54b8111cde779`.
- **Review date:** 15 November 2026.
- **Identity verification:** title, all seven authors, publication date, journal/article number and DOI checked inside the supplied PDF. No indexing/quartile status asserted.
- **Reading status:** full supplied text examined, including method, evaluation, ablation, scope discussion and data-availability statement; Table 6 and Table 9 visually inspected. No independent code, model, experiment or dataset replication.
- **Relevance decision:** include as **supporting industrial systems/evaluation evidence**, not currently a direct queue-policy comparator. This decision follows the paper's own applied-system positioning (abstract p. 1; Section 2 p. 3; Section 4.6 pp. 29-30).

## 2. Research problem

The authors address heterogeneous textile-equipment acquisition, low-latency fault alerting and monitoring-informed resource/production decisions in one cloud-edge-end architecture.

Three distinct decisions must not be conflated:

1. **Alert processing and routing:** detect abnormalities, merge redundant alarms, infer root causes and choose a transmission path.
2. **Compute-resource scheduling:** migrate/allocate real-time, critical and ordinary tasks across edge/cloud nodes using load and bandwidth information.
3. **Production scheduling:** assign textile orders to compatible machines using completion-time, energy and load criteria.

The research objective is integrated workshop-system feasibility and performance. It is not an isolated study of urgent-versus-routine event dispatch under a common bounded queue.

**Source:** abstract p. 1; Section 3.2 pp. 9-18.

## 3. Authors' claimed contribution

The paper claims an applied integration of:

- adaptive protocol parsing and a unified equipment information model;
- hierarchical terminal/edge/cloud alerting, combining a lightweight detector, enhanced OPTICS aggregation and GNN diagnosis;
- monitoring-driven compute coordination and production scheduling.

The abstract explicitly treats scheduling modules as service extensions rather than standalone algorithmic contributions. The authors report improved alarm processing, resource utilization, burst-task response and production performance under their workshop conditions.

**Review boundary:** the paper's contribution is the integration and demonstrated setting. Combining familiar components does not by itself establish a new scheduling algorithm; the authors do not present this as a comprehensive state-of-the-art scheduler benchmark.

**Source:** abstract p. 1; introduction p. 3; Section 4.6 pp. 29-30.

## 4. Model and assumptions

| Dimension | Actual model/evaluation boundary |
| --- | --- |
| Physical deployment | One workshop in Yichang, China; 120 air-jet looms |
| Quantitatively validated acquisition chain | RS485/Modbus RTU to edge nodes, followed by MQTT edge-cloud communication |
| Other protocols | EtherCAT/LoRaWAN described as prototype-supported; OPC UA, Modbus TCP and CANopen are within design/information-model scope, not equivalent field-validation evidence |
| Observation window | 72 h described as three independent 24 h runs; summaries mix run-level and task/event-level mean ± SD |
| Fault population | 2000 labeled instances across six fault types, combining historical replay, non-destructive signal perturbations and operator-confirmed low-risk events |
| Diagnosis evaluation | Multi-label exact-match claimed; five repeated stratified hold-outs, each 70/10/20% train/validation/test |
| Compute platform | Eight Renesas RZ/G2L edge nodes plus cloud ECS instances |
| Compute workload | 35% CPU-intensive, 45% I/O-intensive and 20% burst tasks |
| Scheduling semantics | Preemptive resource allocation; migration/scaling across nodes. No complete bounded shared-queue/admission-loss specification for the studied alert stream |
| Network perturbation | Traffic-shaped uplink varying between nominal and 50% bandwidth; this is not an independently validated physical-node-failure test |
| Production evaluation | Same 1200 orders, three categories/five process types and production constraints; comparison with manual planning plus a conventional-PSO convergence comparison |

**Source:** Sections 3.1 pp. 5-8, 3.2 pp. 10-18 and 4 pp. 18-26.

## 5. Method and decision mechanism

### Hierarchical alerting

1. **Terminal screening:** STM32 detector processes current, temperature, vibration RMS, running status and yarn-break/stop signals. Window length is 20 local samples; an empirical differential threshold of 3.0 must be exceeded for two consecutive windows (p. 10; Table 3 p. 11).
2. **Edge aggregation:** OPTICS is augmented with spatiotemporal similarity  
   `s(i,j) = exp(-lambda * |ti-tj|) * exp(-||xi-xj||²/(2*sigma²))`.  
   The fixed settings are lambda=0.08/s, sigma=1.0 after feature normalization, MinPts=6, neighbor similarity at least 0.62 and a 10 s clustering window (Eq. 2 and Table 3 p. 11). The window is an algorithm parameter; the text does not imply that every alarm waits 10 s.
3. **Cloud diagnosis:** heterogeneous event/component/fault graph; two graph-convolution layers with 64 hidden units, ReLU, dropout 0.30 and sigmoid multi-label output. Training uses weighted binary cross-entropy, Adam at 0.001, batch 32 and early-stopping patience 20 (pp. 11-13).
4. **Routing:** choose the path maximizing a weighted sum of fuzzy urgency, diagnosis-confidence and network-state memberships (Eq. 4 p. 13). This path-selection formula is not a complete per-event queue dispatch algorithm.

### Compute coordination

The controller maps normalized load deviation and bandwidth variation to a task-migration ratio using five linguistic levels, triangular memberships, Mamdani inference and centroid defuzzification (pp. 13-14). A weighted objective combines execution delay, energy and load imbalance with weights 0.6/0.3/0.1 (Eq. 5 p. 14).

Real-time/critical/ordinary tasks receive preemptive resource allocation (pp. 14-15). The authors give decision-window complexity O(NT log NT + NT NN) (p. 15). A complete numeric PID recurrence/gain configuration, exhaustive rule table, allocation-solver procedure and preemption/checkpoint costs would still be needed for faithful independent reproduction.

**Important constraint distinction:** Eq. 6 requires task start time not precede arrival. This is release-time feasibility; it is not a completion-before-deadline constraint or a deadline guarantee.

### Production scheduling

A normalized scalar weighted objective combines completion time, energy and load balance. Adaptive PSO uses decaying inertia and stagnation-dependent Cauchy mutation (Eqs. 7-9 pp. 17-18). This is a scalarized multi-criteria service, explicitly not a Pareto-front optimization study (pp. 16-17, 30).

**Illustration (reviewer's explanation, not a measured trace):** repeated reports of one textile fault may be consolidated before cloud diagnosis; rising edge CPU pressure can trigger migration; a changed machine state can trigger order replanning. These interventions change traffic population, compute placement and production allocation respectively. Their gains cannot all be credited to changing queue order.

## 6. Evidence ledger

All values below are author-reported unless explicitly marked as a reviewer's arithmetic check. Mean ± SD, percentiles and percentages describe different endpoints.

| Claim examined | Page/section/table | Actual evidence | Interpretation boundary |
| --- | --- | --- | --- |
| Communication in the field | Section 4.1, Table 4, p. 21 | 1.02 ± 0.08 s average sampling interval; 0.073% packet loss/invalid frames; p99 jitter 24.8 ms | One acquisition chain; not universal protocol reliability |
| Initial detection | Table 5, p. 22 | 8.2 ± 1.5 vs 136.7 ± 25.3 ms; FPR 2.6 vs 9.4%, FNR 1.9 vs 8.7% | Terminal detection is not full alert delivery latency |
| Redundant-alarm filtering | Table 5, p. 22 | 87.4% vs 61.5%; paper reports +42.1% relative | Arithmetic: +25.9 percentage points, not +42.1 pp. Filtering changes forwarded load |
| Diagnosis | Table 6, p. 23 | Displayed total 2000 and diagonal 1936; paper labels 96.8% as multi-label exact-match | Arithmetic matches, but the displayed single-label-style matrix does not explain label-set accuracy |
| End-to-end alert tail | Table 5, p. 22; Fig. 19, p. 23 | p99 reported 200 vs 452 ms; text says at/below 200 ms during >100 alarms/s | Composite pipeline and filtering/routing effects; not a hard upper bound |
| Compute scheduling | Table 7, p. 24 | Burst-task response 236 ± 48 vs 521 ± 132 ms; CPU utilization 84.3 ± 3.6 vs 58.0 ± 29.0% | These are not the alert p99 endpoint; higher CPU use alone does not prove timeliness |
| Migration decision | Section 4.3 and Table 7, p. 24 | 91.7% vs threshold baseline 76.4%; offline post-execution-log oracle defines correctness | Result depends on oracle definition/counterfactual evaluation details |
| Network fluctuation | Table 7 p. 24; discussion p. 25 | Availability 99.97 vs 88.23% under shaped bandwidth variation | Not evidence of crash recovery, exactly-once handling or physical fault tolerance |
| Production service | Table 8, p. 26 | Order completion 25.9 ± 3.7 vs 36.2 ± 10.5 h; idle rate 6.5 vs 15.6% | Production-order optimization, not alert queue latency |
| Scheduling ablation | Table 9, p. 28 | Removing priority-queue preemption changes burst response from 236 ± 48 to 348 ± 76 ms | Supports a conditional component effect, not the full 521-to-236 gain being due solely to priority |
| Other component effects | Table 9, p. 28 | Without fuzzy adjustment migration accuracy 80.8%; without routing peak bandwidth 19.6 vs full-system 12.3 Mbps | One-component removal does not identify every interaction |
| Production optimizer | Fig. 21 p. 27; Table 9 p. 28 | Approx. 500 iterations for adaptive PSO; 1200 for conventional PSO, 820 without adaptive inertia, 970 without Cauchy mutation | Iterations do not establish global optimality or equal wall-clock budget |

### Experimental and reproducibility interpretation

The baseline alerting service lacks terminal consecutive-window screening, edge spatiotemporal aggregation and cloud GNN inference; it uses fixed-window merging and historical rules. Other baselines are threshold resource scheduling, manual production planning and conventional PSO (pp. 22, 24-27). These are application-level comparisons under shared infrastructure/workloads, not comprehensive modern-algorithm comparisons.

Section 4 (pp. 18-19) states that seeds were fixed, CIs estimated where applicable and paired t/Wilcoxon tests used. The principal tables do not provide claim-by-claim CIs, exact p-values, numeric seed values or clearly consistent per-metric aggregation units. Data are available on reasonable request (p. 31); the supplied article does not provide an executable artifact link sufficient for this review to reproduce the results.

## 7. Critical appraisal

### Strengths

- Real workshop-scale integration rather than simulation alone, with concrete communication and module parameters.
- Explicit distinction between field-tested Modbus RTU and other prototype/design interfaces.
- Component removals under matched replay/workload/order sets (Section 4.5 pp. 27-28).
- Authors appropriately narrow claims about security, physical fault tolerance, cost and cross-workshop generalization (Section 4.6 pp. 29-30).

### Material uncertainties and validity threats

1. **Classification construct ambiguity.** Sections 3.2.1 and 4.2 specify sigmoid multi-label output and label-set exact match, yet Table 6 is a six-by-six true-class/predicted-class matrix whose diagonal/total is used as exact-match evidence. That matrix is consistent with a mutually exclusive class representation, but does not by itself establish multi-label set correctness. Request the label-combination mapping or per-instance target/predicted sets and metric code. This is a reporting/verification concern, not an allegation that the reported accuracy is fabricated.

2. **Repeated hold-out population and leakage control.** Five 20% test partitions of 2000 instances create 2000 test appearances, which need not be 2000 unique independent events. The paper does not clearly reconcile those appearances with Table 6 or specify aggregation. Device/time/incident grouping and graph/normalization construction using training-only information are not established sufficiently to exclude leakage. Leakage is a risk to check, not an observed fact.

3. **Statistical unit and uncertainty.** Three 24 h runs, repeated events and 1200 orders are different units. Mean ± SD cannot be treated as a CI. Within-day alarms/tasks may be correlated; event-level tests need a justified independence or block structure. Explicit replicate counts, CI estimates, paired units and per-claim tests would strengthen the conclusions. Three repetitions are not zero evidence, but provide limited independent-run precision.

4. **Latency denominator and information preservation.** Alarm merging reduces forwarded work. The article reports detector FNR but does not supply a per-incident audit showing whether clustering preserves every distinct urgent event. The p99 population, timestamp boundaries and treatment of missed/merged events need clarification. Faster surviving reports do not alone demonstrate urgent-event reliability or routine protection.

5. **Incomplete isolated scheduler specification.** Urgency/confidence path weights and full queue ties, capacity, admission/drop rules, deadline distributions, preemption costs and resource-assignment solver details are not sufficient for a faithful queue-only replication. The weighted resource terms in Eq. 5 also need scaling/normalization details; unlike Eq. 7, they are not explicitly presented as normalized terms. “Start after arrival” in Eq. 6 must not be read as deadline feasibility.

6. **Model-dependent oracle.** Migration accuracy uses an offline oracle derived from performance logs (p. 24). How unchosen alternatives are evaluated is not adequately specified for this review to establish independent correctness labels. That metric should not be treated as a universally calibrated classifier accuracy.

7. **Generalization and baseline strength.** One 120-loom workshop, controlled/replayed fault instances and limited communication configurations support conditional feasibility. They do not establish performance under new factories, unseen incidents or sustained extreme urgent load. Manual/threshold baselines are useful applied references; they do not show superiority to recent queue/edge schedulers. Table 10 is a qualitative literature comparison, not a shared-benchmark result.

**Overall judgment:** useful applied systems paper and relevant supporting evidence. Stronger for architecture, evaluation scope and interaction awareness than for selecting a faithful direct alert-scheduling baseline. The paper raises worthwhile questions; its reporting uncertainties must not be promoted into proven field-wide gaps.

## 8. Synthesis contribution and open question

### Connection to reviewed work

- [Review 01: PrioMQTT](01-priomqtt-2024.md): both demonstrate that communication-path changes can accompany apparent latency improvements. Here filtering, inference, routing and compute placement co-vary.
- [Review 03: TRIAGE/4](03-multi-tier-message-scheduling-2026.md): traffic admission/suppression changes the measured population. Semantic clustering of redundant alarms is not the same mechanism as source-rate admission shedding.
- [Review 06: disaster scheduling](06-adaptive-priority-disaster-management-2024.md): both combine scheduling with other interventions, so a total-system gain does not identify a queue-only effect.
- [Review 07: online AoI](07-online-aoi-packet-management-fairness-2026.md): suppressing repeated fault reports requires a semantic justification; it is not automatically equivalent to safely replacing obsolete status updates.

**Research-use decision:** retain for industrial motivation, cloud-edge placement, alert aggregation, component ablation and careful metric definition. Do not select it as a direct FIFO/EDF/aging comparator without a separately justified model and implementation specification. No implementation starts from this review.

**Question for further reading:** under identical offered incidents, compute resources and communication paths, what additional urgent/routine benefit comes from scheduling alone once aggregation/placement effects, preemption overhead and distinct-incident loss are accounted for?

This remains an investigation question. More comparable literature is needed before calling it a novel contribution.

<details>
<summary>বাংলা reading note</summary>

এই paper ১২০টি textile machine নিয়ে একটি cloud-edge-end system দেখিয়েছে। Device-এ fault detect হয়, edge-এ একই ধরনের alarm merge হয়, cloud-এ GNN দিয়ে root cause বের হয়। আলাদাভাবে compute task migration/preemption ও production-order scheduling আছে।

**কেন রাখব:** real deployment, alert aggregation, component ablation ও measurement design-এর reference হিসেবে useful।

**কেন direct scheduler baseline নয়:** filtering, routing, diagnosis ও resource placement একসঙ্গে বদলেছে। Alert-এর p99 **200 ms** আর burst compute task-এর **236 ± 48 ms** আলাদা metric। প্রথমটির অর্থ সব alarm 200 ms-এর মধ্যে পৌঁছাবে নয়।

Filtering 61.5% থেকে 87.4% হয়েছে: **25.9 percentage points**, অথবা **42.1% relative improvement**। Accuracy-এর 96.8% arithmetic মিলে, কিন্তু multi-label exact-match-এর ব্যাখ্যায় confusion matrix ও hold-out aggregation পরিষ্কার করা দরকার।

আমাদের শেখা: latency কমলেই যথেষ্ট নয়; কোন incident বাদ পড়ল, কত work কমানো হলো এবং কোন component কত benefit দিল সেটাও জানতে হবে। এখান থেকে এখনই algorithm implement করব না।

</details>

Return to the [review register](../README.md) or [cross-paper comparison](../synthesis/comparison.csv).
