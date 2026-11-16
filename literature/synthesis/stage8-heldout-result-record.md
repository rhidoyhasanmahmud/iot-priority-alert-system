# Stage 8 — Frozen synthetic held-out result record (NOT a manuscript)

**Research line:** STI 2026, controlled IoT alert MQTT-to-SQLite bottleneck study.  
**Date:** 16 November 2026 (UTC).  
**Protocol:** `STI-2026-STAGE8-SYNTHETIC-HOLDOUT-V1`; immutable SHA-256 `1fe656270ce5843af8b26a6a288f712bb4afbf25a05f7d1f2ea9221e93163c52`.  
**Frozen source commit BEFORE any held-out execution:** `1c07dabd49d9505e5dcbb76bf18cbf8357698451`.  
**Workflow:** [GitHub Actions run 43903844289](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/actions/runs/43903844289), successful two-job run.  
**Held-out evidence artifact:** `stage8-frozen-artificial-heldout-data-not-field-evidence`, ID `14244691497`, ZIP SHA-256 `4de56d3577654e9b3c4760abf956502c992769bf0e0df8d8d16889cb412e82d7`; available from the run's Artifacts list, **currently scheduled to expire 14 February 2027 at 16:06:46 UTC**.  
**Separate reserved preflight artifact:** ID `14244715186`—**not eligible for statistical inference**.

## Verification and precommitted decision

All **450/450 real-loopback-MQTT/SQLite trials** completed: 30 new held-out source seeds × five predeclared scenario/capacity cells × three policies; **150/150 matched three-policy blocks**. Independent evidence verification passed for all 450 full raw ledgers and persisted SQLite files, including precommitted policy/threshold identity, offered-population accounting, source fixture hashes, live-MQTT transport, and a separate host-local service calibration audit. The uploaded independent analysis was **recomputed from the downloaded evidence on a separate execution environment**, and its JSON was **byte-identical** (SHA-256 `b09caaef2b614bf87b26494bab9e7d06e163269e4e2683fa4601dbf53f1e2115`).

**Primary predeclared scenario:** synthetic concentrated burst, `K=3` queue waiting places (plus one active worker), 15 offered urgent and 45 offered routine events. `R` is the fraction of **all offered routine** events that **start** within artificial `τ=20 ms`; `U` is the fraction of **all offered urgent** events rejected or **completed** later than artificial `D_u=50 ms`. Larger `R` is better, smaller `U` is better. Source-seed-paired differences use 30 independent source seeds and 10,000 percentile-bootstrap resamples. The null/negative decision is retained with **no post-hoc tuning**.

| Primary outcome | Strict urgent-first | Routine wait guard | Paired guard − strict urgent-first, 95% CI |
| --- | ---: | ---: | ---: |
| Timely routine start, `R` | 24.74% | 52.30% | **+27.56 pp** [24.22, 30.74] |
| Urgent failure, `U` | 47.78% | 63.56% | **+15.78 pp harm** [10.44, 20.89] |
| Joint artificial target `U ≤ 10%` AND `R ≥ 75%` | 0/30 matched seeds | 0/30 matched seeds | Neither meets the synthetic target |

**FROZEN PRIMARY GATE: NOT SUPPORTED.** Although the guard's *routine gain* satisfies the precommitted minimum (lower bound > +5 pp), it **fails** the urgent non-harm condition (urgent upper confidence bound must be ≤ +1 pp; observed +20.89 pp). Do **not** claim that this candidate protects routine traffic while maintaining urgent deadlines. This is an adverse measured trade-off, not an intervention-success result.

## Predeclared secondary cells (descriptive; not confirmatory)

These are mean **offered-population** outcomes across the same 30 independently generated source seeds. All `K=3` except the burst `K=0` no-waiting negative control. Values are percentages; lower `U` is desirable.

| Scenario | Strict urgent-first `R / U` | Routine wait guard `R / U` | Interpretation |
| --- | --- | --- | --- |
| Burst, `K=3` (primary) | 24.74 / 47.78 | 52.30 / 63.56 | Clear routine gain, excessive urgent harm |
| Smooth, `K=3` | 92.59 / 5.78 | 96.22 / 3.78 | Both mostly feasible; small exploratory differences |
| Overload, `K=3` | 3.48 / 61.11 | 30.30 / 85.56 | Severe overload, guard shifts rather than resolves failures |
| Variable work, `K=3` | 91.78 / 3.78 | 88.81 / 12.00 | Guard worsens both outcomes in this model |
| Burst, `K=0` | 45.19 / 56.67 | 44.96 / 58.67 | Near-zero expected scheduling leverage without a waiting queue; observed differences include run noise |

All three policies, including FIFO, have full raw evidence and per-scenario metrics in the artifact. Every source-order-inversion diagnostic reported zero. The main testbed's synthetic offered workload and scheduled producer horizon are **not field traces**. One GitHub-hosted single-worker environment, process/host scheduling noise, artificially selected service requirement and deadlines, 30-seed inferential precision, and finite `K` restrict external generalization.

## Scientific disposition / freeze contract

1. **Freeze stands.** The protocol, thresholds, algorithm, workload family, test order, seed list and primary statistical gate remain as committed **before** held-out data. Do not revise version 1 after observing outcomes.
2. **Do not label an unsuccessful gate as a successful experiment claim.** Engineering/audit execution **passed**; the **substantive hypothesis failed**. The candidate's novelty has not been established (prior Stage 4B REVISE/NARROW), and synthetic SLOs are not owner-approved or field calibrated.
3. **No manuscript drafting authorized at this stage.** Before publication claims, reviewers still need a verified prior-art baseline comparison, clear positioning of the bounded failure envelope, independent real/hardware workload validation, additional capacity/clock/host sensitivity, and institutional/supervisor agreement on scientifically meaningful deadlines/targets. These cannot be inferred from this artificial study.
4. **Evidence retention risk:** GitHub Actions artifacts expire **14 February 2027**. Preserve the complete 6.2 MB ZIP, raw data, analysis JSON, commit, runner metadata and SHA-256 in durable research archive *before expiration*; a Markdown summary is not a substitute for the underlying evidence.
5. A changed algorithm or calibrated deployment model is a **new explicitly versioned future experiment with new held-out source seeds and preregistered gates**; it cannot overwrite or relabel this frozen Stage 8 outcome. Earlier QPAIN 2027 `adaptive_guarded` work is a **different protocol** and is not part of this analysis.

**Record classification:** frozen, fully audited **synthetic model experiment** with a **negative primary treatment decision**, not production benchmarking, algorithm novelty proof, external-validity confirmation, or a publication-ready paper.
