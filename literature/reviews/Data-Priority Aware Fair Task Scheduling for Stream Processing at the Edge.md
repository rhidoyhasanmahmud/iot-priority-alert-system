# Data-Priority Aware Fair Task Scheduling for Stream Processing at the Edge

## 1. Bibliographic record and source

**Review number:** 10 · **Internal reference key:** R19

Faiza Akram; Peng Kang; Palden Lama; Samee U. Khan. 2024. **Data-Priority Aware Fair Task Scheduling for Stream Processing at the Edge**. *2024 IEEE Cloud Summit*, pp. 117-122. IEEE. DOI: [10.1109/Cloud-Summit61220.2024.00026](https://doi.org/10.1109/Cloud-Summit61220.2024.00026).

- **Identity verification:** supplied authors/title matched against the indexed [IEEE publisher record](https://ieeexplore.ieee.org/abstract/document/10630983), [institutional publication record](https://scholars.csus.edu/esploro/outputs/conferenceProceeding/Data-Priority-Aware-Fair-Task-Scheduling-for/99258167832801671) and [NSF manuscript](https://par.nsf.gov/servlets/purl/10530954) on 15 November 2026. Direct IEEE HTML retrieval was blocked; the indexed official record supplies DOI/venue.
- **Reviewed version:** supplied six-page manuscript without visible proceedings pagination. Locations below are PDF pages, not assumed publisher pages. The filename 10530954 is an NSF repository identifier, not the IEEE article number.
- **Source fingerprint (SHA-256):** `4ff6c52c7aaa75282d83b470ccb532539aa7d488cca6c54737fc2247c114262c`.
- **Reading status:** full text reviewed; Algorithm 1 and Table III visually checked on pp. 3-4; no independent replication.
- **Selection:** particularly close primary work on priority plus routine fairness in edge stream processing. Inclusion does not establish algorithmic correctness, deployment readiness or venue ranking.

## 2. Research problem

How should a stream-processing spout emit high-, medium- and low-priority tuples so that prioritization does not produce excessive lower-priority waiting?

FTS-Hybrid controls tuple emission before downstream Storm operators. It balances priority order with batches of service from every nonempty class. The objective is class-wise end-to-end latency and throughput, not explicit deadline-miss minimization.

## 3. Authors' claimed contribution

The paper combines strict priority ordering with queue-length-dependent round-robin-like service within a fixed-size input batch. It implements FTS-Hybrid in Apache Storm and reports RIoTBench PRED results against FCFS, RR and priority scheduling (PS), plus batch-size sensitivity and baseline queuing calculations.

Reported gains depend strongly on the priority mix. Equal-mix results include lower-priority regressions versus PS, so the abstract's headline improvement is not universal.

## 4. Model and assumptions

- A task is an operation on one tuple; supplied/user-defined labels identify low, medium and high priority (p. 2). Priority correctness is assumed rather than evaluated.
- Incoming tuples form fixed-size batches and are split into three queues. Service emits groups in high -> medium -> low order, using the shortest nonempty queue length.
- This is emission order at a spout, not necessarily preemption or priority enforcement at every downstream operator.
- Testbed: one Chameleon VM, 4 CPU cores, 8 GB RAM, Ubuntu 20.04.6 and Storm 2.1.0. The paper presents only the PRED topology from RIoTBench (p. 4).
- A modified generator uses 2013 NYC taxi data, described as two million trips, to produce varying input intensity.
- Ratios are low/medium/high = 70/20/10, 50/30/20 and approximately equal thirds. Batch 100 is used for the principal comparison.
- Measured latency is source-to-sink timestamp difference by tuple ID. Figure 5 shows one-minute p95 samples over one hour; these are not independent experimental repeats.
- No class deadline, finite-buffer loss policy, universal maximum-wait bound or all-urgent saturation guarantee is established.

## 5. Method and decision mechanism

**Batch -> class queues -> shortest nonempty queue size -> emit high/medium/low groups -> repeat.**

Sections III-A and Algorithm 1, pp. 2-3, describe equal-sized groups from each nonempty class in descending priority order. For low/medium/high counts 5/3/2, the explanation emits 2 per class, then 1 each from remaining medium/low, then the final low tuples.

The prose implies queue lengths must be refreshed after each round, empty queues ignored and dequeues limited to available tuples. The printed pseudocode computes lengths only before the while-loop and still attempts all three dequeue loops; its Qmed/Qmedium naming also differs. Implementers must resolve those omissions with source code or author clarification, not silently claim an exact transcription.

Section III-B assumes an M/M/1 analytical abstraction. Its equations and Table II describe FCFS/RR/PS examples, not a proved FTS-Hybrid waiting bound. The real PRED topology is a multi-operator application running on a four-core VM, so the single-server abstraction's predictive fidelity needs validation.

Future switching to PS when high-priority share grows, and learned/adaptive batch sizing, are explicitly future work on p. 6.

## 6. Evidence ledger

All results are author-reported unless labeled reviewer interpretation.

| Claim examined | Source location | Actual evidence | Interpretation boundary |
| --- | --- | --- | --- |
| Sparse-high-priority improvement | Table III, p. 4, 70/20/10 mix | High-priority reduction: 24.2% vs FCFS, 31.05% vs RR, 25.8% vs PS. Low-priority: 23.8%, 30%, 25.7%. | Workload-specific reported latency reductions; not a deadline-failure result or effect size for every mix. |
| Different mix, different benefit | Table III, p. 4, 50/30/20 mix | High-priority reduction versus PS is 3.4%; low-priority versus PS is 1.9%. | The roughly 26% headline versus PS does not describe this mix. |
| Contrary result | Table III, p. 4, equal-thirds mix | Versus PS: high +10.1%, medium -5.09%, low -15.58% improvement. | Negative improvement means worse latency for medium/low. Do not claim simultaneous universal improvement across classes. |
| Tail observation scope | Section IV-B and Fig. 5, pp. 4-5 | p95 source-to-sink latency measured at one-minute intervals for one hour, plus throughput. | Distribution of window p95 values is not a pooled request p95 or seed-level confidence interval. |
| Batch sensitivity | Section IV-C and Fig. 6, pp. 4-5 | Batch sizes 10, 50, 100 and 500; authors select 100, and describe about 2,000 ms versus about 8,000 ms median of plotted p95 samples at 100 vs 500. | Batch size materially changes waiting. This is not evidence that larger batches always help. |
| Fairness and theory | Algorithm 1/Table II, p. 3 | Service is shared within a batch; Table II has FCFS, RR and PS rows only. | No certified starvation-free or bounded-wait theorem for the full pipeline is supplied. |

## 7. Critical appraisal

**Contribution and closeness.** This is direct prior art against novelty claims based on combining priority, queue occupancy and routine service at the edge. A new weighted queue score alone must be compared with such existing mechanisms.

**Mechanism versus evidence.** The operational example is clear, but pseudocode omits state refresh/empty-queue handling. That does not prove the experimental code is broken. A faithful comparator requires clarification. The analytical examples are not an independent proof of the batch scheduler.

**Internal validity.** Batch formation, emission order and downstream bottlenecks all influence end-to-end latency. Matched input intensity and batch settings matter. Baseline PS is described within data batches; it should not automatically be equated with every online strict-priority implementation.

**Statistical validity.** One-minute samples from one hour may be temporally dependent. Independent run/seed uncertainty and precise aggregation behind Table III are not sufficiently documented. Preserve its negative entries rather than quoting only the abstract.

**External validity.** A single VM and one presented topology do not establish general behavior across gateways, application DAGs, service times or alarm floods. Source-to-sink p95 improvement does not demonstrate hard-deadline assurance.

**Evidence to seek next:** source/configuration, explicit batch-flush/timeout rules, arrival traces, repeated matched runs, downstream queue measurements, class loss/deadline outcomes and sensitivity when urgent share rises.

## 8. Synthesis contribution and open question

Unlike [FEF](An%20Adaptive%20Emergency%20First%20Intelligent%20Scheduling%20Algorithm%20for%20Efficient%20Task%20Management%20and%20Scheduling%20in%20Hybrid%20of%20Hard%20Real-Time%20and%20Soft%20Real-Time%20Embedded%20IoT%20Systems.md), this mechanism controls stream emission rather than preempting CPU tasks. Unlike [topic feedback](Design%20of%20topic%20priority%20based%20on%20industrial%20publish-subscribe%20system.md), it grants repeated within-batch opportunities rather than timer-driven subscriber feedback.

**Question for further reading:** How do batch-based routine-service opportunities behave when priority mix shifts, batches fill slowly and downstream execution can reorder or delay urgent work?

The same control location is not required for prior-art relevance. No candidate algorithm or experiment is selected.

<details>
<summary>বাংলা reading note</summary>

এটি সবচেয়ে কাছের paperগুলোর একটি। Queue length দেখে batch-এর মধ্যে high, medium, low—সব class-কে সুযোগ দেয়। তবে equal workload mix-এ medium/low latency PS-এর চেয়ে খারাপ হয়েছে। তাই headline percentage দিয়ে সব পরিস্থিতিতে ভালো বলা যাবে না; batch size ও downstream queue-ও গুরুত্বপূর্ণ।

</details>

Return to the [review register](../README.md) or [cross-paper comparison](../synthesis/comparison.csv).
