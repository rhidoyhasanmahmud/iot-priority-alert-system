# Stage 5C — Two-class offered-metric golden oracle and synthetic smoke

**Date:** 16 November 2026 · **Outcome:** **MEASUREMENT-ORACLE ENGINEERING VALIDATION PASSED** in one local Python 3.12.14 execution environment. **Research workload realism, MQTT boundary, service calibration and numerical requirements are NOT validated.**  
**Scope:** independent tiny verifier; **no novel scheduling algorithm** and **no primary conference-result claim**.  
**Inputs:** [RQ v1.0](research-questions.md), [Stage 5A boundary](application-boundary-stage5a.md), [Stage 5B archive suitability](archived-evidence-audit-stage5b.md), [Stage 4B novelty gate](novelty-decision-stage4b.md).

**Reproducibility:** run `python3 experiments/stage5c_golden_oracle.py` from the repository root. The standard-library-only script is self-checking and exits nonzero if a golden case fails. It deliberately does not import the archived simulator or any candidate scheduler. Its role is an *independent specification of the metrics* against which a later implementation can be compared.

## Step 5C.1 — Freeze exact local measurement semantics

- Two trusted classes only: **urgent** and **routine**.
- One non-preemptive processing worker, **K waiting slots** plus at most one running job.
- Every offered valid event is either admitted or rejected at the local queue boundary.
- At timestamp ties: **finish current worker → admit simultaneous arrivals sorted by (arrival, id) → dispatch**. If worker is idle during admission, it has an extra immediate-service slot beyond K waiting.
- FIFO uses (arrival, id). Strict priority selects urgent before routine and uses (arrival, id) within each class. **Neither selection uses unstarted job duration**, despite synthetic generator truth being stored for offline simulation.
- Runs **drain all admitted jobs** and have **no proactive expiry, cancellation, MQTT ingress or right-censoring**. Do not extrapolate the oracle to incomplete real runs without revising its accounting.

For urgent offers with deadline `d_i`, success means **completion time ≤ d_i**. For routine offers with waiting budget `tau_i`, timely access means **start time ≤ arrival_i + tau_i**. Rejected offers remain in each class's denominator and never count as successes. Rates for a class with zero offered jobs are **undefined (None/N/A)**.

**All times in this script are artificial integer ticks.** No number here represents a measured ms value or a security operator's requirement. In the random smoke only, urgent deadline offset and routine tau are each **5 ticks**, purely to exercise the code.

**Checklist — 5C.1**
- [x] Fix two-class local offer, deadline, waiting and rejection semantics.
- [x] Match the archive's documented completion-before-admission-before-dispatch tie rule.
- [x] Enforce class-neutral capacity and hide p from FIFO/priority selection.
- [ ] Align these semantics with a **new**, correctly instrumented MQTT post-validation `offer_ns` timeline.
- [ ] Decide and register expiry/censoring policy before full experiments.

## Step 5C.2 — Nine hand-checkable deterministic cases

The reference source contains input tuples and hard assertions for every expected **start**, rejected event ID and rate. Each case below is fully drained. `U` is urgent **failure**, so smaller is preferable; `R` is routine **timely start**, so larger is preferable.

| Case | K | Policy | Key condition | Expected U | Expected R(tau) | Observed |
| --- | ---: | --- | --- | ---: | ---: | --- |
| **A_FIFO** | 2 | FIFO | U1=2 ticks; R1=1; U2=1, all offered together; urgent d=3, routine tau=2 | **1/2** | **1** | PASS |
| **A_PRIORITY** | 2 | Priority | **Same offered jobs**, urgent jobs served before routine | **0** | **0** | PASS |
| **B_FIFO** | 1 | FIFO | 3 simultaneous offers, only K+1=2 accepted; third urgent rejected | **1** | **1** | PASS |
| **B_PRIORITY** | 1 | Priority | Same admission/drop set; first urgent completes on time | **1/2** | **1** | PASS |
| **C_BLOCK** | 1 | Priority | Routine already running when urgent arrives; no preemption | **1** | **1** | PASS |
| **D_EQUAL** | 1 | Priority | Completion exactly at urgent deadline; routine start exactly at tau | **0** | **1** | PASS |
| **E_NO_URGENT** | 0 | FIFO | No urgent offers | **N/A** | **1** | PASS |
| **E_NO_ROUTINE** | 0 | FIFO | No routine offers | **0** | **N/A** | PASS |
| **F_TIE** | 0 | Priority | Current job completes at exactly the next offer's timestamp | **0** | **N/A** | PASS |

A paired counterexample is apparent from A: **FIFO vs strict priority** on the *same* offered workload changes outcomes from `(U=1/2, R=1)` to `(U=0, R=0)`. This demonstrates only **that the metric implementation can expose a trade-off**; it does **not** prove a new result, realistic frequency of the trade-off or superiority of a proposed algorithm.

**Checklist — 5C.2**
- [x] Explicitly cover capacity overflow and rejection in the offered denominator.
- [x] Explicitly cover nonpreemptive urgent blocking and inclusive timing boundaries.
- [x] Check zero-denominator rates report N/A instead of fabricated 0 or 1.
- [x] Execute all nine cases; **9/9 PASS**.
- [ ] Compare a later independent production/experiment implementation event-by-event with this oracle.

## Step 5C.3 — Small reproducible paired synthetic *engineering smoke*

Purpose: exercise the reference oracle on multiple two-class finite-K traces with **variable synthetic service time**. It is **not** a preregistered study, a real sensor dataset, an actual MQTT replay or statistical evidence for an academic contribution.

**Declared generator (exactly as in script):**

| Dimension | Synthetic smoke definition |
| --- | --- |
| Offered jobs per trace | 120 |
| Independent generator seeds | Integers 1–6 (six trace seeds) |
| Classes | Each job independently urgent with probability 1/4, otherwise routine |
| Service demand | Independent discrete uniform selection from **1, 2, 3 ticks**; true value used only for offline service completion |
| Base interarrival gaps | Independent discrete choices `0,1,2,3,4` ticks; **not Poisson** |
| Shape A | Base gap sequence (“normal” label means **synthetic baseline**, not calibrated normal IoT traffic) |
| Shape B | “Clustered” gaps at event indices 48–71 reset to zero; removed gap ticks redistributed outside the window so **total arrival horizon, class sequence and offered work for each seed are unchanged** |
| Queue capacity | K=2 and K=10 **waiting slots** |
| Baselines | FIFO and strict priority only; same offered trace passed to each |
| Timing budgets | Urgent absolute deadline `arrival+5 ticks`; routine start within `5 ticks`; **debug constants, not validated requirements** |
| Total executions | 6 seeds × 2 shapes × 2 capacities × 2 policies = **48** |

**Recorded descriptive smoke output** (averages of six **per-seed** proportions, four decimals; total rejection count summed across six runs *within that cell*). These are synthetic self-check numbers. They **must not** enter a conference Results section:

| Shape | K | Policy | Mean seed U | Mean seed R(tau) | Rejections across 6 runs |
| --- | ---: | --- | ---: | ---: | ---: |
| Clustered | 2 | FIFO | 0.3159 | 0.7629 | 171 |
| Clustered | 2 | Priority | 0.2536 | 0.7337 | 172 |
| Clustered | 10 | FIFO | 0.5562 | 0.5050 | 97 |
| Clustered | 10 | Priority | 0.1544 | 0.4726 | 98 |
| Base | 2 | FIFO | 0.2768 | 0.8903 | 83 |
| Base | 2 | Priority | 0.1440 | 0.8441 | 83 |
| Base | 10 | FIFO | 0.5355 | 0.5604 | 8 |
| Base | 10 | Priority | 0.0420 | 0.5168 | 10 |

**Key checks:** all 48 executions satisfied `offered=admitted+rejected`, single-worker nonpreemption, finite waiting occupancy and complete-drain invariants. The generator preserved **per-seed** total offered service work and arrival horizon across the two shape variants. With the same K and *class-neutral* admission rule, the **sets of admitted jobs may still differ across policies** as dispatch changes occupancy; that is visible in unequal rejection totals and is not itself a bug.

No effect size, confidence interval, policy ranking, universal capacity guarantee or novelty inference should be drawn from this intentionally tiny debugging corpus. Note that changing capacity can change **which offered jobs** finish by deadline; monotonic conclusions about U do not follow from queue-size monotonicity alone.

**Execution metadata:** Python **3.12.14**; source SHA-256 `19f88235d1c7a79108fd3d6fa87ed6129478e1bf468b4b51a5598aaeb9a8fc4d` before GitHub upload; ran the script **twice**, byte-identical stdout, both exit code 0, on 16 November 2026. No external package, MQTT broker, original archived experiment harness or user dataset required.

**Checklist — 5C.3**
- [x] Exercise **two classes**, variable synthetic p, finite K and matched offered traces.
- [x] Preserve aggregate offered work/horizon across shape variants *per seed*.
- [x] Execute **48/48** synthetic engineering smoke runs without assertion failure.
- [x] Independently repeat the full run and obtain identical output.
- [ ] Run a statistically preregistered, genuinely calibrated workload study or a declared synthetic-only conference protocol (future Stage 6/7).

## Step 5C.4 — Evidence/implementation gates still open

| Gate | Present state | Required next action |
| --- | --- | --- |
| **Metric oracle correctness** | **PASS** for nine deterministic cases, synthetic smoke invariants | Add edge cases for expiry and partially observed runs if Stage 6 includes them. |
| **Production worker performance** | **NOT MEASURED**; archived MQTT worker used configured sleep | Instrument actual declared handler or approve fully synthetic service model with limited claims. |
| **MQTT offer boundary** | **NOT MATCHED**; archived live callback-entry vs new post-dedup offer | Record both times, reconcile publisher/received/offered logical IDs. |
| **Realistic arrival/service model** | **NOT VALIDATED**; synthetic units, class proportions and debug horizons | Obtain representative traces/calibration, or have professor approve a **synthetic-only** research story. |
| **Numeric epsilon/tau/gamma/K** | **NOT JUSTIFIED**; this script has neither approved epsilon nor gamma | Choose with application evidence before tuning and held-out tests. |
| **Strong baseline comparability** | Only FIFO and strict priority in engineering smoke | Stage 6 preregistration needs suitable EDF+FIFO, aging, work-fair and N01-informed comparators under equal information. |
| **Novelty** | Stage 4B **REVISE/NARROW**, proof/database/supervisor gate open | Do not claim a novel algorithm or conference readiness. |

**What is allowed next:** review this metric oracle; obtain supervisor acceptance of the lab-only use case and operational/synthetic budget status; then prepare a **versioned Stage 6 baseline evaluation protocol**. The old prototype implementation remains archived. Only this **reference measurement verifier** has been introduced under `experiments/` for methodological reproducibility; it is **not** a restored application.

**Checklist — 5C.4**
- [x] Distinguish **measurement validation** from real IoT system validation, algorithm quality or a paper finding.
- [x] Preserve the literature-first main architecture; new code is a small isolated verification artifact under literature.
- [ ] Align post-validation offer timestamp in a future MQTT harness; include external source loss explicitly.
- [ ] Validate operational deadlines and realistic service-demand distributions.
- [ ] Complete Stage 4B novelty sign-off, Stage 5B/5C empirical evidence gates and supervisor review before formal experiments.

**Overall Stage 5C progress**
- [x] Golden two-class oracle defined, implemented and self-checked.
- [x] Nine exact outcomes and 48 synthetic engineering smoke cases passed.
- [x] Repository-ready method/evidence report with test values and caveats prepared.
- [ ] Stage 5C **real application/MQTT evidence clearance**: **NOT COMPLETED**.
