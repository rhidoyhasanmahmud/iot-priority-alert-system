# Stage 5G — Declared application-handler contract and provisional SQLite lab measurements

**Date:** 16 November 2026  
**Status:** **REFERENCE HANDLER + INDEPENDENT AUDIT + CI SMOKE PASSED; APPLICATION REPRESENTATIVENESS / NUMERICAL SLA CALIBRATION NOT APPROVED.**  
**RQ:** [Conference study v1.0](research-questions.md) · **Previous evidence:** [Stage 5D protocol](workload-measurement-calibration-stage5d.md), [Stage 5F broker-backed smoke](mqtt-measurement-pilot-stage5f.md).  
**Boundary:** This work is **not** the conference scheduling experiment. It supplies one openly specified, reproducible **illustrative** event-processing handler and timing method to replace the old *CPU-work surrogate* in a future application testbed **if** the domain owner/supervisor finds the semantics credible.

## Step 5G.1 — Declare what “one alert processed” means

Our historical building/industrial-site scenario is a fictional gateway-side security-event enrichment service. The local *post-validation and post-dedup* worker receives two trusted classes: `tamper` (URGENT) and `health` (ROUTINE). The upstream trusted-class assignment is **outside** this single-worker measurement and is not a claim of authenticated device identity.

**New reference application code:** [`stage5g_reference_handler.py`](../validation/stage5g_reference_handler.py) uses only the Python standard library. For each **synthetic** alert, one non-preemptive worker:

1. Looks up a device's zone and tamper-alert enablement in a 16-row fictional SQLite `device_context` table.
2. Evaluates a fixed rule: `TAMPER_REVIEW`/`TAMPER_DISABLED` for tamper events; `LOW_BATTERY`/`HEALTHY` for routine health events.
3. Serializes the rule output, inserts one uniquely identified row in `handled_alerts`, and invokes `Connection.commit()`.

Database uses file-backed SQLite in a per-run temporary directory with `PRAGMA journal_mode=WAL` and `PRAGMA synchronous=FULL`. **Service start** is immediately before database lookup; **service completion** is immediately after commit **returns**. Validation, source generation, MQTT transport, upstream queueing and post-run verification are **excluded**. Normal close/reopen checks confirm rows were visible again; **no process-crash/power-failure durability test was run**. This avoids falsely treating a `sleep` or PBKDF2-only loop as the declared application task, but it is **still a made-up implementation and database**. SQLite's WAL/FULL behavior is described in the [SQLite official PRAGMA reference](https://www.sqlite.org/pragma.html) and Python's [sqlite3 transaction documentation](https://docs.python.org/3/library/sqlite3.html); observed storage guarantees depend on the actual host/VFS.

**Checklist — 5G.1**
- [x] Define and document worker-side lookup, rule, transaction and commit boundary.
- [x] State exact two-class and single-worker scope; do not change RQ v1.0 or Stage 5F's audit contract.
- [x] Separate handler interval from MQTT callback, trusted offer, queue wait and publisher timings.
- [ ] Have an application owner/supervisor accept or correct the fictional field schema and work semantics.
- [ ] Obtain realistic device context cardinality, lookup/storage backend, record size, error policy and durability need.

## Step 5G.2 — Build and independently check the provisional handler

The source generator uses per-run seeded `random.Random` fixture fields and **one urgent every four events**, a test convenience rather than an observed workload mix. The SQLite reference handler rejects duplicate primary keys, invalid battery percent (including Boolean-as-integer), inconsistent class flags, and unknown device IDs; failed transactions roll back. A separate [`stage5g_service_audit.py`](../validation/stage5g_service_audit.py) uses **no emitter imports** and independently recomputes event IDs/order, source SHA-256, class, context/rule outcome, row count and exact `service = commit_return - work_start` arithmetic; it rejects overlapping worker intervals. It checks manifest declarations but **cannot independently prove** that the emitted host really used the declared SQLite journal/sync settings or actually committed the recorded rows: corroboration still requires the executable/runner and a controlled DB test.

**Executed in Python 3.12.14:**

- `py_compile` for both scripts: **PASS**.
- Reference handler self-tests: three known rule outcomes, duplicate/invalid/unknown rollback, SQLite close/reopen row count, two small generated seeds: **PASS**.
- Independent auditor: hand-checked 8-row fictional positive case plus **6 deliberately malformed negatives rejected**: **PASS**.

**Checklist — 5G.2**
- [x] Implement a declared non-sleep, non-PBKDF2 illustrative worker including SQLite commit.
- [x] Test transactional error handling and normal database close/reopen.
- [x] Independent source/class/rule/interval auditor and 6/6 negative checks.
- [ ] Add controlled crash/recovery and multi-platform filesystem testing **if** deployment persistence is required.
- [ ] Profile validation and metrics-logger overhead separately before any scheduling comparison.

## Step 5G.3 — Three seed-level laboratory traces (NOT a service distribution)

Ran **3 separate synthetic seeds × 120 completed jobs**, with exactly **30 urgent and 90 routine jobs per run**. Each run initializes its own fictional context database and writes one distinct transaction per event; post-run SQL row equality is checked after closing and reopening. Host manifest reported Linux, Python `3.12.14`, SQLite `3.53.1` and nine logical CPUs. No MQTT publisher, offered queue, competing worker or production backend participated in these Stage 5G service-only probes. The generated *trace itself* is deterministic for a seed; the measured durations are **not** expected to be deterministic.

| Seed | Urgent p50 / p95 (µs) | Routine p50 / p95 (µs) | Ledger | Raw SHA-256 |
| --- | ---: | ---: | --- | --- |
| 101 | 30.780 / 100.508 | 29.734 / 52.217 | PASS | `fc6d6325a04ad2048ad1fd247f0b82021ef0b6f88c0c7a8923841c9c489b7637` |
| 202 | 11.452 / 52.808 | 10.826 / 31.487 | PASS | `ca124f47fba14d8eaf1432ebd0ce2e30993975656813bd4c65c982c67692b42b` |
| 303 | 10.475 / 30.044 | 10.421 / 18.998 | PASS | `94e437a9b5013b3af87b4b6335dd97fd2e27f95fcba94b88fd034cfeb4ec805b` |

**What this does and does not mean:** The auditor recomputed the per-class nearest-rank p95 from raw `monotonic_ns` spans and verified nonoverlap; each run has a different seeded fictional input. But the absolute numbers are **tiny and unstable across only three short batches** on an ephemeral host with unknown storage/fsync characteristics. They are **not** a field-service estimate, statistical interval, tail-latency SLO, safe deadline, saturation limit or basis for selecting `D_u`, `epsilon`, `tau`, `gamma` or `K`. There is no fair FIFO/EDF/DRR scheduling comparator here; **no performance improvement claim** follows. Median/p95 depend on run conditions and the handler's intentionally minimal rules and storage volume; class effects should not be interpreted as causal.

The three synthetic raw JSONL ledgers are retained as reproducible fixtures:

- [`stage5g_sqlite_seed101.jsonl`](../validation/fixtures/stage5g_sqlite_seed101.jsonl)
- [`stage5g_sqlite_seed202.jsonl`](../validation/fixtures/stage5g_sqlite_seed202.jsonl)
- [`stage5g_sqlite_seed303.jsonl`](../validation/fixtures/stage5g_sqlite_seed303.jsonl)

**Checklist — 5G.3**
- [x] Execute 3 seed-level, 120-record reference-handler lab probes (360 commits; no queue/MQTT).
- [x] Preserve complete synthetic input, class/rule output, monotonic service spans, manifest and SHA-256.
- [x] Recompute all three traces in independent offline audit with exact handler row conservation and rule checks.
- [x] Record unstable raw timing spread **without** promoting it to real service calibration.
- [ ] Run genuine representative handler with realistic context/storage and controlled hardware, cold/warm/loaded repeats and error samples.

## Step 5G.4 — External-validity and parameter decision gates

| Gate | Available evidence | Status before Stage 6 |
| --- | --- | --- |
| M01 work semantics | Testable SQLite prototype, fixed mock tables/rules | **PARTIAL**: owner/supervisor and actual application work missing |
| M02 local offered lifecycle | Stage 5F MQTT finite-K ledger | **ENGINEERING PASS** only; Stage 5G service probe not yet integrated into offered pipeline |
| M03 service profile | Three short, uncontrolled SQLite worker probes | **LAB FEASIBILITY ONLY**; field handler/hardware variability unverified |
| M04 arrival and burst | Stage 5F generated source shapes | **SYNTHETIC ONLY**; no measured real source/horizon validation |
| M05 operational parameters | No owner-backed `D_u`, `epsilon`, `tau`, `gamma`, `K` | **BLOCKED**; **do not** reuse the 50 ms Stage 5F debug thresholds |
| M06 reproducibility | Script SHA, fixture hashes, independent verifier and GitHub Actions rerun | **LAB REPRODUCTION PASS**; external conditions unverified |
| M07 supervisor decision | No dated approval of measured-lab versus synthetic-only paper scope | **BLOCKED** |
| Stage 4B novelty | Prior **REVISE/NARROW** verdict | **BLOCKED** for a novel-method or best-paper claim |

**Checklist — 5G.4**
- [x] Keep RQ/metric boundary and provisional handler claims separate from publication evidence.
- [x] Preserve source and result reproducibility, negative tests, and unresolved external-validity decisions.
- [ ] Professor/application owner chooses: representative application calibration **or** explicitly synthetic-only claim.
- [ ] Acquire application source/service traces, resource limits and operational objectives; preregister all constants before study tuning.
- [ ] Update Stage 4B novelty verdict using complete closest-work review and supervisor approval.
- [ ] **Only then** design matched-trace baseline comparisons and Stage 6 full evaluation.

## Step 5G.5 — Independent CI run and regression

On pull request #48, [Stage 5G GitHub Actions run #43873927699](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/actions/runs/43873927699) completed **SUCCESS** on Ubuntu/Python 3.12. The job compiled both scripts, passed handler rollback/reopen tests and six auditor negative cases, generated **two new CI-local 32-event traces** (seeds 11 and 22), independently audited both, and independently re-audited the **three archived 120-event JSONLs** (seeds 101, 202 and 303). No CLI benchmark acceptance threshold was applied to noisy absolute service durations; the gate is semantic and accounting-focused.

The existing [Stage 5F MQTT regression run #43873927339](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/actions/runs/43873927339) also completed **SUCCESS** on the same PR. This validates that the new Stage 5G files did not break the previous broker-backed engineering smoke, **not** that Stage 5G's SQLite handler was integrated into that MQTT gateway. The two modules are still separate.

**Checklist — 5G.5**
- [x] Confirm new Stage 5G workflow actually executed, not merely existed in YAML.
- [x] Inspect completed Ubuntu job: handler positive/error checks and 6/6 negative auditor cases PASS.
- [x] Independently validate two fresh CI-local traces and all three committed seed traces.
- [x] Confirm preexisting Stage 5F MQTT regression remains green.
- [ ] Integrate the *approved* application handler into the MQTT worker and then record **joint** offer→start→commit measurements; still blocked by application requirements.

## Reproduction

From the repository root:

```bash
python3 literature/validation/stage5g_reference_handler.py --self-test
python3 literature/validation/stage5g_service_audit.py --self-test
python3 literature/validation/stage5g_reference_handler.py \
  --events 120 --seeds 101 202 303 --output-dir stage5g-local-output
python3 literature/validation/stage5g_service_audit.py stage5g-local-output/*.jsonl
```

Output paths are exclusive-create: use a new `--output-dir` when repeating. A rerun has the *same synthetic source fields and SHA-256*, **not** identical service durations or fixture file SHA-256. **Do not submit these prototype timings as experimental results.**

**Source SHA-256:** `stage5g_reference_handler.py` = `3230042fe950254bf18b5846954ecb9c358df87ace1dbc7454af03b5a26d8eb2`; `stage5g_service_audit.py` = `c9f168b043fcb26ebf4b6c0b0de4540e6029e77532d878e435a2899990a984e`.

**Stage 5G decision:** The **reference handler and its measurement/accounting contract pass a preliminary engineering gate**. The claimed real application handler, service distribution, human-approved priorities, deadlines, source arrival process, resource-constrained queue capacity, and true conference contribution **remain open**. Next is a scoped application-owner/supervisor decision and integration plan, not a declaration of empirical readiness.
