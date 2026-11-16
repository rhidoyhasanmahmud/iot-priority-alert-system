# Stage 7 — Controlled testbed workload characterization and baseline replay

**Date:** 16 November 2026  
**Status:** **EXPLORATORY ENGINEERING EVIDENCE ONLY; NOT CALIBRATED TO A DEPLOYMENT, NOT PREREGISTERED, NOT A SCIENTIFIC PERFORMANCE CLAIM.**  
**Basis:** [Stage 5K.2 policy-independent fixture](stage5k2_fixture_pilot.md), [unsigned Stage 6 experimental protocol](experimental-protocol-stage6-draft.md), [Stage 4B adverse novelty decision](novelty-decision-stage4b.md).

## 1. What actually exists now

- **Workload generator (existing):** One byte-identical, seed-addressed offer/hidden-work pair per scenario. Every synthetic offered ID—including future rejects—has an ex-ante *fictional* work requirement. The online dispatcher receives only validated arrivals/classes. Initial candidate shape levels are smooth, concentrated-burst and higher-intensity (halved planned horizon), plus a same-mean work-dispersion contrast.
- **Host-only service characterization:** `stage7_calibration_probe.py` executes PBKDF2 SHA-256 work levels 1/4/7 followed by a real context lookup/rule/transaction/SQLite WAL+FULL commit. All raw intervals, SQLite rows and hashes are checked by a **separate** `stage7_calibration_audit.py`. This measures only the runner's artificial handler behavior and **cannot** justify any field arrival rate or deadline.
- **Two conventional online baselines plus one unvalidated research candidate:** `stage7_controlled_replay.py` implements the same class-neutral admission/full-buffer rule and one non-preemptive SQLite worker with `K` *waiting* plus at most one active job. FIFO and strict-urgent-first select exclusively from already waiting, validated arrivals. The provisional `routine_wait_guard` first selects the oldest queued routine job **if its measured age is at least half the configured routine start target** (`age >= τ/2`); otherwise it selects the first urgent job, or FIFO if none. Synthetic work units are consumed by the worker **only after** dispatch. The candidate is an ordinary age-based guard idea, **not verified as novel or scientifically final**.
- **Real transport path:** Stage 7 uses existing Paho/QoS1 loopback Mosquitto publisher/receiver and Stage 5G SQLite WAL/FULL handler; inprocess transport is a distinct smoke mode, never mislabeled MQTT.
- **Independent result gate:** `stage7_independent_replay_audit.py` checks source payloads/schedule, content hashes (not cryptographic signatures), offer/attempt/duplicate lifecycle, **all three policies' online decisions** (including observable wait-age threshold), full- versus rejected-work separation, CPU/SQLite timing order, post-commit results and **actual independently reopened SQLite** backup. `stage7_independent_batch_audit.py` rehashes every run and source triple before reproducing *descriptive-only* paired differences.
- **Negative regressions:** `test_stage7_controlled_replay.py` covers forged source provenance, policy snapshot, hidden-work leak, CPU iterations, SQLite rule/result, missing offers, tampered backup and fake MQTT transport, as well as positive real-SQLite cases.

## 2. Demonstrated outcomes so far

| Execution / audit | Observation | Meaning |
| --- | --- | --- |
| Local calibration probe | 36 artificial samples: 12 each at work units 1, 4, 7; SQLite reopen and independent calibration audit **PASS** | Lab host CPU+SQLite profile only, not a field service model |
| Local policy unit / negative tests | **16/16 Stage 7 PASS**; **38/38 combined** with Stage 5K.2 | Contract, online guard decision and evidence corruption checks |
| Local source replay | **24/24 inprocess trials** (2 synthetic seeds × 4 scenarios × 3 policies at `K=3`) | Fresh SQLite+worker process per run; **not MQTT**, 2 seeds inadequate for inference |
| Independent local batch audit | **24/24 PASS**, 8 matched three-policy blocks, source/hidden file hashes matched | Engineering lifecycle and raw evidence consistency only |
| Real loopback MQTT CI, previously verified code revision | **48/48 synthetic trials PASS** for FIFO/strict-urgent-first at commit `ea529f6` | Actual Mosquitto/Paho QoS1 plus SQLite; **does not test the newly added guard candidate** |
| Updated three-policy real MQTT CI | **72/72 synthetic trials PASS**: 24 matched triples (3 seeds × 2 K × 4 scenarios × 3 policies), independently audited | Real Mosquitto/Paho MQTT → SQLite; engineering proof, **not** publishable scientific results |

For this local host, illustrative *work-level 4* had a CPU+SQLite combined median around **6.8 ms** in 12 standalone executions. This is a **descriptive one-host pilot**, not an accepted service-time distribution, operational constraint or externally sampled data.

The local higher-intensity schedule did **not** always generate saturation: shortening the planned horizon is an intensity contrast, not proof that a system is overloaded. Source times and real local offers can diverge under event loop, broker and OS delays; record both and never equate planned publisher pacing with observed local deadline origin.

### Example commands

```bash
python literature/validation/test_stage7_controlled_replay.py
python literature/validation/stage7_exploratory_batch.py --output-dir /tmp/s7-artificial --transport inproc --seeds 101 202 --capacities 3
python literature/validation/stage7_independent_batch_audit.py --batch-dir /tmp/s7-artificial
```

For a real broker, the reproducible CI workflow starts Mosquitto locally, installs Paho and runs the *same* source/worker/SQLite code with `--transport mqtt`. CI artifacts have a 14-day retention and must be archived under the approved evidence plan if later needed for scientific replication.

### GitHub Actions verification record

The two-baseline code revision `ea529f6dc8c3e8c5db1151dd2e2103f361738419` passed both jobs in [Stage 7 workflow run #2](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/actions/runs/43899100129) on 16 November 2026:

- `inprocess-sqlite-regression`: **PASS** (positive/negative actual-SQLite tests and 16 paired synthetic inprocess runs with independent audit).
- `real-loopback-mqtt-and-sqlite`: **PASS** (48/48 synthetic Mosquitto/Paho-to-SQLite executions; the independent per-run and per-batch auditor completed successfully).
- The runner uploaded artifact `stage7-fictional-real-mqtt-sqlite-not-science` (GitHub Actions artifact ID `14239563556`, SHA-256 archive digest `ecb29fb4005af2bf2f08bc1f045c5af6fd018d89bdbcf6e9c6fdc0dbfeede4b4`) and an inprocess artifact. Both expire **30 November 2026**; preserve them separately if the study later needs reproducible historical evidence. The artifact archive digest is a transfer integrity indicator, not proof of scientific validity.

**This historic run predates the routine-guard candidate.** It is preserved here solely as an earlier independently validated software revision. Any favorable policy contrast is exploratory debugging, not statistical evidence.

### Verified three-policy research-candidate run

Commit `974a92ad0e2f5ebb7aa95f5e4cbda9c866d62145` passed both jobs in [Stage 7 workflow run #4](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/actions/runs/43900333572) on 16 November 2026:

- `inprocess-sqlite-regression`: **PASS** (new guard candidate, independently audited unit/negative tests and synthetic inprocess blocks).
- `real-loopback-mqtt-and-sqlite`: **PASS** (72/72 synthetic Mosquitto/Paho-to-SQLite executions, 24 exact source-matched policy triplets, independent per-run and batch raw audit).
- Raw evidence artifact `stage7-fictional-real-mqtt-sqlite-not-science`: GitHub Actions artifact ID `14240758334`; archive SHA-256 `9e8b980191c6bec519c805e7d2ffb489800a9f1e763f13ef90d17a1e0cebf050`; expiry **30 November 2026**. The inprocess artifact is ID `14241635962`, expiry the same date. Future study replications require independent archival/version pinning and approved protocol; these expiring artifacts are not a durable research dataset.

These results verify software execution and internal accounting under wholly *artificial* input and local runner conditions. There are still **no validated production arrival/service samples, approved SLOs, final novel algorithm or controlled scientific findings**. The recorded `U_debug`/`R_debug` and paired differences are exploratory diagnostics only.

## 3. What remains genuinely uncompleted

**Workload calibration — NOT complete for research:** No owner-backed deadline `D_u`, routine threshold `τ`, constraints `ε/γ`, actual arrival/severity mixes, representative service demand for all offered jobs, or external workload rights/provenance. The artificial 60 IDs/seed, 15 urgent, K=0/3, 1s/0.5s planned horizons and 20ms debug thresholds are *demonstration settings only*. CPU/RAM quotas, real producer availability and field station topology are not independently anchored.

**Final algorithm and fair scientific comparison — NOT complete:** Two conventional baselines and an **illustrative age-guard research candidate** are available for engine testing. Stage 4B identifies serious novelty risks; the candidate cannot honestly be called novel/final without full-text comparison (especially N01/N09), faithful closest-prior-work comparator and professor approval. The `τ/2` guard is arbitrary without owner-approved targets; it cannot be tuned post-hoc to make a favorable result. Additional faithful EDF/aging/DRR or direct prior-work comparator implementation requires agreed model and matching online knowledge; no comparator shopping after seeing results.

**Scientific experiments — NOT complete:** The exploratory pilot is neither preregistered nor approved. No declared primary operating points, threshold tie/expiry rules, confidence/precision target, independently replicated held-out source seeds, matched host-resource controls, power/instrumentation overhead plan, or statistical family-wise error plan has been signed. Do **not** promote any `U_debug`, `R_debug`, medians, figures or favorable treatment differences to an IEEE paper's Results or Abstract.

### Required supervisor/researcher decision gate

1. Approve the **strictly synthetic, single-host, conditional model** or supply an authorized external dataset/handler/owner constraints; document generalization restrictions.
2. Resolve the precise contribution and faithful comparator family after Stage 4B primary-source full-text review.
3. Freeze specific workload levels, service-work-to-time model, finite `K`, queue/admission behavior, `D_u`, `τ`, `ε`, `γ`, failure rules and zero-denominator handling independent of preliminary outcomes.
4. Predeclare sampling units, run/block count, randomization, holdout seed list, CI/host fingerprint, data exclusions, effect-size criteria and statistical analysis before measuring held-out treatment differences.

Only after those gates can we execute and label a scientifically interpretable experiment and complete the STI/IEEE manuscript with honest results. A negative or null finding must remain reportable.
