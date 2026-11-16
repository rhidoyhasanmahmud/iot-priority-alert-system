# Stage 6 — Controlled-testbed evaluation protocol (DRAFT / NOT PREREGISTERED)

**Date:** 16 November 2026  
**State:** **REVIEW COPY; NO FROZEN HYPOTHESES, TARGETS, POLICY IMPLEMENTATIONS OR VALID SCIENTIFIC RESULTS**.  
**Basis:** [RQ v1.0](research-questions.md) · [Stage 4B adversarial novelty decision](novelty-decision-stage4b.md) · [Stage 5K.1 audited evidence](workload-calibration-stage5k.md) · [Stage 5K.2 workload design draft](workload-design-stage5k2-draft.md).

## 0. Preregistration seal — NOT COMPLETED

| Required sign-off / artifact | Value |
| --- | --- |
| Accepted contribution and study scope | **TBD: supervisor review** |
| Synthetic-only assumptions or authorized source traces | **TBD** |
| Handler/service model, calibration and hidden work visibility | **TBD** |
| Urgent deadline `D_u`, epsilon; routine `τ`, gamma; waiting capacity `K` | **TBD / present 50ms and K 0/3 are debug only** |
| Frozen comparator list and matched information contracts | **TBD** |
| Independent run count, holdout set and effect-size criteria | **TBD** |
| Statistical method, multiplicity and sensitivity plan | **TBD** |
| Dated professor/researcher approval and versioned protocol SHA-256 | **NOT SIGNED** |

Until all above are filled and reviewed, this is an **experimental design proposal** and MUST NOT be labelled a preregistered trial.

## 1. One question, three linked analyses

**Main objective:** For a *declared finite-capacity single-worker non-preemptive IoT application-processing model*, characterize the empirically observed trade-off between locally offered urgent completion failures and routine timely service starts under controlled burst structure and service-work variability. No universal feasibility proof, scheduling optimality or new algorithm is implied.

1. **RQ1 — Where does the trade-off fail?** Compare burst shape, total offered load, service-work variability and capacity. Explain observed blocking/full-buffer losses and conditions where neither service target can be met **by the tested policies**.
2. **RQ2 — Which mechanism matters?** Compare defensible count-based versus past-consumed-work routine protection with matched conventional baselines, without claiming either accounting approach is new.
3. **RQ3 — Do conclusions survive realistic information and overhead?** Never expose unstarted job's exact future service requirement to an online policy. Measure overhead and, if legitimate estimates exist, disclose/evaluate their errors.

## 2. Exact population and lifecycle

- **Offer boundary:** after trusted validation/dedup, when the local finite-buffer bottleneck is offered one distinct job; **include rejected offers** in all population denominators. Distinguish publisher/broker transmission from local offer time.
- **Resource boundary:** one non-preemptive worker, at most `K` waiting plus at most one active job; same class-neutral *reject on full* rule; no external upstream reservoir or hidden drop suppression.
- **Urgent failure fraction `U`:** rejected, expired or completed after the **declared urgent completion deadline** among **all offered urgent jobs**. Deadline origin (provisional) is local offer.
- **Routine timely-start fraction `R(τ)`:** admitted routine jobs whose service **starts** within `τ` of local offer divided by **all offered routine jobs**; rejected and never-started jobs fail.
- If the denominator for one class is zero, the class-specific empirical fraction is **undefined/N/A**; aggregation/exclusion must be frozen before seeing results.
- Pending decision: expiry before processing, edge equality (`<=`), cancellation, crashed/unfinished work and treatment of incomplete trials. The Stage 5D/5H ledgers already enforce many engineering invariants; do not silently extend them into a reliability guarantee.

## 3. Baseline selection — candidate set, not final implementations

| Candidate | Reviewer question | Caveat before implementation |
| --- | --- | --- |
| FIFO | What is the class-neutral minimum complexity reference? | Implemented/tested as Stage 5J *engineering* baseline, not a paper-level matched comparison |
| Strict urgent priority | Does urgent-first produce routine starvation/loss? | Freeze same within-class order, K and admission semantics |
| EDF or EDF+FIFO | Does deadline-aware information change feasible region? | Exact urgent deadline metadata must be available online; routine adaptation disclosed |
| Aging or bounded routine access | Does routine protection change urgent loss budget? | No ex-post tuning of aging interval against holdout |
| DRR/work-fair adaptation | Is consumed **past** work better than pure counts? | No unstarted-service oracle; justify work-to-queue adaptation and runtime cost |
| Closest applicable prior-work method (N01/N05/N06 where model permits) | Does an established approach equal/dominate our claimed gain? | Verify original mathematical model and input visibility before claiming faithful replication |

The actual comparator family is **subject to Stage 4B full-text checks and professor approval**. If an exact comparator is inapplicable, report why and label a faithful *adaptation* with exact changes; do not create a straw man.

## 4. Experimental units, factors and fairness

- Fix **same offered event IDs, class mapping, planned source times and synthetic hidden service work** for each matched workload seed. Keep hidden work out of online dispatch before service. Record SHA-256 of all fixture components.
- Separate **burst concentration at matched planned horizon/work** from overload **rate/intensity**. Vary service-work dispersion at fixed declared mean work; include sufficient resource/headroom controls that policy overhead is distinguishable from queueing.
- Candidate axes (levels **TBD**): intensity, burst structure, offered job-size variability, urgent fraction, K, deadline/access sensitivity, and estimate error if present. Avoid unmanageable full factorial unless feasible; preregister primary comparisons versus exploratory checks.
- Treat an independently executed workload seed/environment repetition as a **run-level experimental unit**. Individual jobs inside a run are correlated and **must not be treated as independent scientific replications**. Three original Stage 5J seeds are insufficient evidence for inferential claims.
- Randomize policy order within each matched block, control warmup/cold-state effects, clear state properly, use held-out source seeds after pilot tuning, and track host CPU quota/background load and SQLite settings. Never compare monotonic timestamps across different processes as absolute times.

## 5. Reporting plan and error/uncertainty contract

Primary endpoints for the future frozen protocol: `U`, `R(τ)`, and the observed **joint feasibility** of `U <= ε` and `R(τ) >= γ` at declared operating points. Report joint result **only among evaluated policies**; not an existence theorem.

Supporting outcomes: offered/admitted/rejected counts by class; total **offered** work from a declared ex-ante synthetic model; observed handler durations among admitted jobs; queue wait and completion distributions; FIFO/priority decision time, CPU, memory and storage; uncertainty/failure cases and incomplete-run exclusions. Separate source-to-offer transport from local offer-to-effect latency.

**Statistical-analysis plan remains TBD** pending number of independent runs and desired decision thresholds. At minimum provide per-run paired effects, variation and confidence intervals at the run/block level, alongside non-favorable workloads. Decide any hypothesis testing, correction for multiple endpoints and minimum practically meaningful effect **before** held-out observation.

## 6. Scientific falsification and hard stops

Reject or narrow a claimed practical advantage if a strong conventional comparator **matches or dominates at comparable urgent offered failures, routine timely starts and overhead**. Separately report whenever every tested policy fails an infeasible load regime. A negative result is valid evidence within its model but may reduce venue suitability.

Do **not** start result-oriented experiments or write a conclusion while any of the following are missing:

- [ ] Stage 5K.2 workload/service model and numeric factor levels, including hidden work for all offered jobs.
- [ ] Supervisor approval of synthetic-only generalization limits and Stage 4B originality positioning.
- [ ] Verified faithful baselines and exact run-time information contracts.
- [ ] Fixed host, independent replicate count, held-out seed split, timeout and exclusion rules.
- [ ] Signed analysis specification and preregistration checksum.

### Manuscript preparation while approvals remain open

**Draftable now:** background/problem motivation, transparently limited related work, RQ and mathematical endpoint definitions, existing MQTT/SQLite lab architecture and its audit/limitations. **Not finalizable yet:** contribution statement, Experimental Setup's accepted parameters, Results, Discussion of statistical effects, and Conclusion. Do not present Stage 5J/5K engineering accounting as an experimentally established algorithmic improvement.
