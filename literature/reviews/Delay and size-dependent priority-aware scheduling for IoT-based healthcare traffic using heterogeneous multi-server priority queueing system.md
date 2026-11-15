# Delay and size-dependent priority-aware scheduling for IoT-based healthcare traffic using heterogeneous multi-server priority queueing system

## 1. Bibliographic record and source

**Review number:** 11 · **Internal reference key:** R20

Barbara Kabwiga Asingwire; Louis Sibomana; Alexander Ngenzi; Charles Kabiri. 2023. **Delay and size-dependent priority-aware scheduling for IoT-based healthcare traffic using heterogeneous multi-server priority queueing system**. *IET Communications, 17(16), 1877-1887*. John Wiley & Sons Ltd on behalf of The Institution of Engineering and Technology. DOI: [10.1049/cmu2.12675](https://doi.org/10.1049/cmu2.12675).

- **Identity verification:** title, authors, year, volume/issue, pagination and DOI checked against the [official publisher record](https://ietresearch.onlinelibrary.wiley.com/doi/10.1049/cmu2.12675) on 15 November 2026.
- **Reviewed version:** supplied published PDF, 11 pages; printed page = PDF page + 1876. Key method/equations/parameters/curves visually checked on PDF pp. 4-8.
- **Source fingerprint (SHA-256):** `16e6a0198a1ccfb64d2a5cd4d35b2d745cb47f191939887a0352ce1cc088dac4`.
- **Reading status:** full text reviewed; analytical claims not independently proved; no replication.
- **Selection:** core-related non-preemptive priority scheduling with delay/size classes and heterogeneous servers. Numerical model evaluation is not simulation or clinical validation. Indexing/quartile status is not claimed.

## 2. Research problem

How should a healthcare gateway differentiate delay-sensitive and delay-tolerant packets of different sizes when multiple servers have unequal speeds?

The authors seek lower mean slowdown and improved throughput relative to EDF/Priority EDF while acknowledging lower-priority delay. Their Prioritized Scheduling (PS) policy uses delay sensitivity followed by size class, rather than dynamically aging waiting jobs.

## 3. Authors' claimed contribution

The paper develops analytical expressions for an M/M_i/c-style heterogeneous multi-server priority system and evaluates them numerically in MATLAB. It reports lower mean slowdown for the four delay/size classes and better delay-sensitive throughput than EDF in the studied settings.

It does not present a validated implementation, an independent discrete-event simulation or a general starvation-free/deadline guarantee. The conclusion explicitly leaves simulation validation and a quota on consecutive delay-sensitive service for future work (p. 1886 / PDF p. 10).

## 4. Model and assumptions

- Poisson class arrivals; exponentially distributed service times; heterogeneous servers; infinite queue capacities (p. 1880 / PDF p. 4).
- Delay-sensitive work precedes delay-tolerant work. Each is divided by a packet-size threshold into short and large, with short first.
- Non-preemptive service; FCFS within the same class. Fastest-server-first selects the fastest currently idle server.
- Packet size/class and delay sensitivity are known at arrival. Class-based delay sensitivity is distinct from an online EDF rule using each job's remaining deadline.
- Table 1 (p. 1883 / PDF p. 7) gives five servers, rates 1/2/3/4/5 packets/s, arrival-rate range 0-6.549 packets/s, nominal loads 0.5/0.9, mean packet size 100 Kb and threshold 75 Kb.
- Later figure text/axes use kilobytes, so the Kb versus kilobyte convention needs resolution. The table's rate range and load normalization also require reconciliation with aggregate server capacity.
- Infinite buffers remove overflow loss. Stable high-load cases at rho = 0.9 are not evidence for indefinite overload above service capacity.

## 5. Method and decision mechanism

**Classify delay -> classify size -> choose next eligible class -> assign fastest idle server.**

Section 3.2 and Figure 2 (p. 1880 / PDF p. 4) describe delay-sensitive short, delay-sensitive large, delay-tolerant short and delay-tolerant large handling, FCFS within classes and non-preemption.

Sections 3.3-3.3.2 (pp. 1881-1883 / PDF pp. 5-7) derive occupancy probabilities, mean waits and priority-class expressions. Eqs. (16), (18) and (20) combine other classes' waiting contributions. Their left-hand W has an overbar: plain-text extraction obscures this distinction, so it should not be mistaken for a self-cancelling equality.

**Analytical questions requiring validation:**

- The aggregate birth-death description uses the sum of the fastest n server rates when n servers are occupied. With non-preemption and fastest-idle assignment, the identities of busy servers can matter after completions. A count-only state is not automatically sufficient unless an additional routing/reassignment assumption justifies it.
- Normalization and cross-class waiting terms need independent checking against a server-identity-aware simulation. Numerically plotting the same derived equations is not independent model validation.
- The paper defines slowdown through response time relative to packet size. Packet-size units and conversion to service requirements must be explicit before treating this as the conventional dimensionless response/service-time ratio.
- There is no implemented aging, service quota or maximum-wait override in the stated policy. A future quota cannot be credited to the evaluated mechanism.

These are reviewer validity questions, not an independent disproof of the complete analytical model.

## 6. Evidence ledger

The figures are numerical evaluations of the authors' analytical expressions.

| Claim examined | Source location | Actual evidence | Interpretation boundary |
| --- | --- | --- | --- |
| Delay-sensitive short/large slowdown | Figs. 4-5, p. 1884 / PDF p. 8 | PS curves are below EDF/Priority EDF at nominal loads 0.5 and 0.9, with larger separation in some high-load regions. | Results depend on the derived equations; not independently simulated or measured packet traces. No pooled improvement percentage is established here. |
| Delay-tolerant slowdown | Figs. 6-7, same page | PS curves also show lower modeled mean slowdown for short and large delay-tolerant packets. | A lower mean does not bound maximum waiting, prevent starvation under arbitrary high-priority arrivals or prove deadline compliance. |
| Throughput scope | Figs. 8-9 and Section 4.4, p. 1885 / PDF p. 9 | Delay-sensitive short/large throughput is compared with EDF at 0.5 and 0.9 loads. | Do not extend this to all-class throughput, a Priority EDF throughput experiment or deadline success rates. |
| Workload scope | Table 1, p. 1883 / PDF p. 7 | Hypothetical parameters and infinite buffers; analytic load sweeps. | No burst trace, finite-buffer overflow study or real healthcare system trial. |
| Explicit outstanding work | Conclusion, p. 1886 / PDF p. 10 | Authors plan a threshold on delay-sensitive packets served before delay-tolerant service, and simulation validation. | Routine-service quota and independent simulation are not completed contributions of this paper. |

## 7. Critical appraisal

**Relevance and novelty overlap.** Delay class, packet size and server speed already appear together in IoT priority scheduling. A proposed size/urgency score must account for this work and distinguish its decision mechanism and objective.

**Internal and analytical validity.** The explicit assumptions help scrutiny, but state aggregation, class interaction and load/unit definitions need independent validation. Fastest-idle non-preemptive service cannot simply be assumed identical to a model that always has the fastest servers occupied. Baseline EDF/Priority EDF equations should also be aligned to the same server model and service discipline before attributing gains solely to scheduling.

**Construct validity.** Mean slowdown can emphasize small packets differently from absolute urgent latency. Throughput is described through busy-service behavior and packet size; it is not automatically the fraction of urgent updates completed before deadline. Numerical curves therefore do not settle our offered-load failure/routine-tail question.

**Statistical and external validity.** These are analytical parameter sweeps, so independent-run confidence intervals are not the immediate validation target. Correct equations and simulation agreement are. Poisson/exponential/infinite-buffer assumptions provide no direct evidence for bursty, heavy-tailed, finite-memory alert handling.

**Evidence that would strengthen confidence:** explicit units/load mapping, corrected/verified class formulas, server-identity-aware simulation, matched baseline assumptions, finite-buffer/bursty experiments, and direct low-priority maximum-wait plus urgent-deadline outcomes.

## 8. Synthesis contribution and open question

Compared with [FTS-Hybrid](Data-Priority%20Aware%20Fair%20Task%20Scheduling%20for%20Stream%20Processing%20at%20the%20Edge.md), this policy uses size and heterogeneous server assignment instead of within-batch shared opportunities. Compared with [FEF](An%20Adaptive%20Emergency%20First%20Intelligent%20Scheduling%20Algorithm%20for%20Efficient%20Task%20Management%20and%20Scheduling%20in%20Hybrid%20of%20Hard%20Real-Time%20and%20Soft%20Real-Time%20Embedded%20IoT%20Systems.md), it explicitly uses non-preemption.

**Question for further reading:** What routine waiting and urgent-deadline tradeoffs remain when size-based service and heterogeneous server assignment are evaluated with finite buffers, realistic service requirements and burst arrivals?

This motivates further comparison; it does not establish a field-wide gap or select a baseline.

<details>
<summary>বাংলা reading note</summary>

এখানে delay-sensitive/tolerant এবং short/large—দুইভাবে priority ভাগ করে fastest idle server-এ কাজ দেয়। তবে ফলাফল mathematical model থেকে; simulation validation ভবিষ্যৎ কাজ। Low-priority quota-ও এখনো যোগ হয়নি। তাই paperটিকে starvation সমাধানের পরীক্ষিত প্রমাণ বলা যাবে না।

</details>

Return to the [review register](../README.md) or [cross-paper comparison](../synthesis/comparison.csv).
