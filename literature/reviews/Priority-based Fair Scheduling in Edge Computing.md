# Priority-based Fair Scheduling in Edge Computing

## 1. Bibliographic record and source

- **Review 13 · R22 · core-related; closest reading for class/client fairness.** Relevance does not certify starvation freedom or baseline fidelity.
- **Authors:** Arkadiusz Madej; Nan Wang; Nikolaos Athanasopoulos; Rajiv Ranjan; Blesson Varghese.
- **Publication:** 2020 IEEE 4th International Conference on Fog and Edge Computing (ICFEC), pp. 39–48, 2020. Publisher: IEEE.
- **DOI:** [10.1109/ICFEC50348.2020.00012](https://doi.org/10.1109/ICFEC50348.2020.00012).
- **Identity verification, 15 November 2026:** [Queen's University Belfast record](https://pure.qub.ac.uk/en/publications/priority-based-fair-scheduling-in-edge-computing/) confirms authors, proceedings, pages and DOI; [St Andrews record](https://research-portal.st-andrews.ac.uk/en/publications/priority-based-fair-scheduling-in-edge-computing/) also links the author manuscript. No quartile/ranking claim is made.
- **Read source:** supplied `2001.09070v1.pdf`, arXiv v1 dated 24 January 2020, 10 pages. Locations below use the manuscript's own pages 1–10, matching PDF page numbers. Publication identity is verified; this review does not assume the supplied preprint is byte-identical to the final proceedings version.
- **SHA-256:** `ce760f0d9fe826cd995ea7eee599f8f1e07c427c22fb726ceeae84cb9d243e9e`.
- Full-text critical reading; algorithm/figure pages visually checked. No implementation, independent experiment or formal proof verification. The PDF is not redistributed.

## 2. Research problem

An edge device cannot necessarily start every job offloaded by multiple cloud clients. The decision is which queued job to launch when resources permit. FCFS can let early or prolific clients occupy the device; priority-only allocation can overlook some clients or lower classes. EFS separates fairness across clients from service shares across job priorities, then combines them (Sections I–III).

This is admission/start ordering for container jobs on one edge device, rather than MQTT transmission scheduling, hard-deadline feasibility or equal CPU-time sharing.

## 3. Authors' claimed contribution

The paper proposes Client Fair (CF), Priority Fair (PF) and Hybrid schedulers, alongside FCFS. It implements an Edge Fair Scheduler with request handling, job scheduling and monitoring, and evaluates distribution of executed jobs under equal, random and Gaussian request profiles. The authors describe Hybrid as combining client and priority fairness with practical overheads.

The empirical claim concerns observed allocations in the stated prototype. The conclusion explicitly leaves formal asymptotic fairness results, heterogeneous execution times and multiple edge devices to future work (p. 10).

## 4. Model and assumptions

- One constrained edge node accepts requests into a job queue backed by a database. A full queue causes a request rejection (Algorithm 1, p. 3). Queue capacity and rejection populations must therefore be distinguished from jobs that merely remain unstarted at the end of a window.
- Requests identify the client, job and priority. A historical job table supplies execution frequencies. Jobs are moved into history as the scheduling decision is made; this is a count-based accounting mechanism, not a measured delivered-CPU ledger.
- Priority level 3 is highest, level 2 medium and level 1 lowest. The experiment's target shares are respectively 50%, 35% and 15% (pp. 5, 7). These are selection-frequency weights, not hard reservations for every finite interval.
- The experiment assumes equal CPU and memory requirements, similar synthetic workloads, and individual execution times no longer than ten minutes. These assumptions make job counts more comparable than they would be for heterogeneous jobs (p. 7).
- Six clients are observed over one-hour windows. Equal profile: 50 jobs/client, comprising 17 PL1, 17 PL2 and 16 PL3. Random profile: up to 50 requests/client. Gaussian profile counts are 15, 45, 90, 90, 45 and 15, with staggered activity periods (Table II and Section IV, pp. 7–8).
- No task deadline, remaining slack, explicit age promotion, emergency override or finite worst-case waiting bound is part of these selection rules. Oldest-first tie handling is not equivalent to a starvation proof under continuing arrivals.
- Prototype: Odroid-C2, four ARM Cortex-A53 1.5 GHz cores, 2 GB RAM, Ubuntu 16.04; an eight-core Xeon cloud VM with 16 GB RAM. Software is reported as Python 3.5, SQLite 3.11 and Docker 3.6 (pp. 6–7).

## 5. Method and decision mechanism

**CF, Algorithm 2, p. 4:** collect waiting clients, obtain each client's historical job execution frequency, choose the least-served client, then choose that client's oldest queued job. Move the job into history and provision its container. This balances client counts without directly protecting high-priority jobs.

**PF, Algorithm 3, p. 5:** calculate each waiting class's historical fraction of executions. Scan classes from highest to lowest; choose the first below its assigned fraction. If none qualifies, fall back to the highest waiting priority. Choose the oldest job in that class. This supplies low classes service opportunities without explicitly balancing clients.

**Hybrid, Algorithm 4, p. 6:** use PF to choose a class, use CF to choose a client, then select the oldest job matching both. The conceptual aim is class-share control plus client fairness. A reproduction detail needs resolving: the printed algorithm invokes CF's first five lines, whose waiting-client list is not explicitly restricted to the selected class. A selected client/class pair can have no matching queued job. A class-conditioned client set or documented fallback would settle this; the pseudocode ambiguity alone does not prove the experimental implementation failed.

The scheduler launches jobs when concurrent-job/resource limits permit. Monitoring can terminate idle containers (Algorithm 5, p. 6). This lifecycle control also affects available capacity; allocation counts should not be read as complete application-delivery outcomes.

## 6. Evidence ledger

| Claim examined | Source location | Actual evidence | Interpretation boundary |
| --- | --- | --- | --- |
| Client fairness and priority fairness are different | Algorithms 2–4, pp. 4–6; Figure 3 and Scenario 1 discussion, pp. 7–9 | CF balances client counts but executes no PL3 jobs in the equal-profile window; PF favors weighted classes while clients E/F receive no execution. Hybrid serves all clients and favors higher classes. | One finite-window prototype observation, not a universal order or deadline guarantee. |
| Historical shares give low-priority work opportunities | Algorithm 3, p. 5; Figures 3–5, p. 9 | Priority selection uses historical count/total versus configured 50/35/15 weights. | Class admission counts do not establish equal CPU shares, per-client share within every class, or a routine maximum-wait bound. |
| Overhead is practical | Figure 2 and Section IV, p. 7 | At one million history entries, Hybrid takes about 2.8 s; CF/PF about 1.5 s; FCFS about 0.015 s on the edge board. The authors consider this tolerable when dispatch intervals are minutes. | Seconds of decision time cannot be assumed cheap for millisecond alert deadlines. No need to digitize the small-history curve to support this point. |
| Hybrid resolves demand imbalance | Scenario 3, p. 8; Figure 5, p. 9 | Hybrid gives a better observed balance, yet over 50% of clients C/D's jobs are not executed within the hour. | Unexecuted within a window is not synonymous with dropped, rejected or deadline-missed. Fair allocation cannot create missing service capacity. |
| Fairness has a formal guarantee | Conclusion, p. 10 | Formal asymptotic client equality and convergence of class service fractions are explicitly future work. | This manuscript supplies neither those proofs nor a per-job starvation bound. |

## 7. Critical appraisal

**Useful contribution.** This is close prior art against any claim that priority and fairness have not been combined at the edge. It also demonstrates why client fairness alone and class fairness alone can leave different populations underserved. A functioning small-device prototype is stronger feasibility evidence than an unimplemented scheduling sketch.

**Construct validity.** The fairness unit is a job selection/execution count. Different service demands can make equal counts unequal resource use. An aggregate class target can coexist with long waits for an individual routine job, and historical counts can impose a catch-up period when the workload changes. The latter is reviewer inference from the cumulative accounting, not a measured transition result here.

**Reproduction and complexity.** Resolve the Hybrid class/client intersection and tie handling. CF is described as O(1), but its pseudocode scans waiting clients and requests historical counts. Actual cost depends on client population, indexing, cached counters and database access; the measured history-size overhead should accompany any complexity claim. The paper's own Figure 2 limits an unconditional low-overhead interpretation.

**Evidence scope.** The three synthetic profiles on one small edge board establish feasibility under the reported assumptions. They do not isolate urgent deadline success, low-class tails, queue-full rejection rates or heterogeneous-resource fairness. The report does not provide a repeated-seed confidence-interval protocol sufficient to attach statistical certainty to every allocation difference. Multi-edge scaling and heterogeneous runtimes are author-stated future work.

**Research use:** retain for deep comparison of fairness units and service accounting. Do not select it as a faithful message-queue comparator until admission populations, runtime model, database cost and the Hybrid intersection rule are reconciled.

## 8. Synthesis contribution and open question

Compare EFS with [FTS-Hybrid](Data-Priority%20Aware%20Fair%20Task%20Scheduling%20for%20Stream%20Processing%20at%20the%20Edge.md): EFS uses historical class/client counts, whereas FTS-Hybrid controls stream emission through batching and queue lengths. Compare both with FEF's periodic-task protection and DRA's historical deadline-miss feedback. These account for different units of deprivation; none can be exchanged merely because each uses the word fairness.

**Open reading question:** which existing methods connect class-share fairness to per-job routine tail waiting while making the urgent-service cost explicit under bursty, heterogeneous work? This paper motivates that comparison; it does not establish an unfilled field-wide gap.

**Bangla note:** এটি closest fairness reading-এর একটি। 50/35/15 job share মানে প্রতিটি routine task নির্দিষ্ট সময়ের মধ্যে শেষ হবেই—এমন guarantee নয়।

[Register](../README.md) · [Comparison](../synthesis/comparison.csv) · [Synthesis](../synthesis/findings.md)
