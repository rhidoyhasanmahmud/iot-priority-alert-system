# Supervisor decision brief — Controlled Testbed conference study

**For:** AP Dr. Mahdi H. Miraz / AP Dr. Md. Iftekhar Salam (research-team review)  
**Prepared:** 16 November 2026  
**Status:** **REQUEST FOR DECISION — NOT A SIGNED APPROVAL**

## Proposed paper direction

**Working title:** *Routine-Service Protection Under Bursty IoT Alerts: Deadline Trade-offs and Practical Limits*.

The research investigates a single non-preemptive, finite-buffer IoT alert-processing bottleneck with urgent and routine offers. Two primary offered-population outcomes are: urgent deadline-failure fraction `U` (including local admission rejections) and routine timely-start fraction `R(τ)` (service begins within the waiting budget). The goal is to **characterize conditions and limitations** under which conventional online policies may or may not meet declared service budgets, not to claim invention of priority scheduling.

## Evidence already available (engineering only)

- **19 retained related-paper review notes**, plus targeted adversarial novelty assessment and Stage 4B analytic reduction. Stage 4B decision remains **REVISE/NARROW**, not cleared originality.
- Real loopback Mosquitto/Paho MQTT → finite-K FIFO → SQLite WAL/FULL fictional handler, with full source/callback/offer/commit ledgers and independent SQLite re-open audit.
- Stage 5J original **18/18 verified synthetic broker cases**: 1,080 offered fictional alerts, 697 committed, 383 full-buffer rejected. Stage 5K independent new CI also **18/18**, but its 1,080 offered resulted in 694 commits and 386 rejects. These differing results demonstrate lab timing sensitivity, **not a policy benefit**.
- Stage 5K.1 produces per-run/class **committed-only** service timings; service requirements for rejected offers are **not observed**. Current labels, load, rule/context, queue sizes and 50 ms timing are invented/debug controls.

The current testbed verifies implementation **accounting/reproducibility**, not a field reliability result, actual IoT SLA, or new scheduling policy. All paper-level comparative results remain unrun.

## Highest-priority originality risks

1. **N01:** Maxime Gonthier, Kyle Chard, Ian Foster, Loris Marchal, and Frédéric Vivien (2025), “Deadline-Aware Scheduling of Mixed-Criticality Tasks,” *Proceedings of the 54th International Conference on Parallel Processing*, pp. 178–187, **ACM**, DOI [10.1145/3754598.3754639](https://doi.org/10.1145/3754598.3754639). ACM indexed model and author-hosted slides checked; **full source methodology still to be inspected**. Close urgent-deadline/routine-flow comparator.
2. **N09:** Panayotis D. Sparaggis and Don Towsley (1994), “Optimal Routing and Scheduling of Customers with Deadlines,” *Probability in the Engineering and Informational Sciences*, 8(1), 33–49, **Cambridge University Press**, DOI [10.1017/S0269964800003181](https://doi.org/10.1017/S0269964800003181). Publisher abstract and issue authenticated; **full article pending**. Direct warning against claiming originality for finite buffers plus start/completion deadlines and losses.

Also relevant: existing lexicographic multiclass hard-deadline and online delay/fairness work ([Stage 4B model and citation record](novelty-decision-stage4b.md)). No originality claim is settled by the different endpoint names alone.

## Three decisions requested before the paper protocol

| Decision | Option A | Option B | Supervisor decision |
| --- | --- | --- | --- |
| **1. Data/generalization** | Accept a **strictly synthetic**, reproducible real-MQTT/SQLite controlled-lab paper whose conclusions are conditional on declared assumptions | Require authorized external workload/handler evidence before a paper claim | **TBD** |
| **2. Contribution** | Pursue a narrowed **empirical operating-region/limits comparison** against established online policies | Reframe or stop if existing methods/theorems subsume any plausible contribution | **TBD** |
| **3. Targets and comparators** | Approve nonoperational experimental `D_u/ε/τ/γ/K` sensitivity plan, fair baselines and held-out protocol | Request actual application-owner thresholds and full service calibration | **TBD** |

**Next evidence packet if approved:** [Stage 5K.2 workload candidate contract](workload-design-stage5k2-draft.md) followed by [Stage 6 draft protocol](experimental-protocol-stage6-draft.md). These are **not** frozen experiments and do **not** include fabricated signatures or numeric service requirements.

**Decision record to complete after meeting:** date/time ____ · reviewers ____ · choice 1 ____ · choice 2 ____ · choice 3 ____ · required changes ____ · scope of authorized claims ____ · protocol freeze authorized? YES / NO. No field is prefilled as approved.
