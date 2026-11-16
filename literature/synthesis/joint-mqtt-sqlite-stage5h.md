# Stage 5H — Joint MQTT gateway + SQLite handler; independently auditable lab pipeline

**Date:** 16 November 2026  
**Status:** **IN-PROCESS + REAL BROKER-TRANSPORT CI ENGINEERING PASS; INDEPENDENT SQLITE ARTIFACT AUDIT PASS. SYNTHETIC ONLY; NO EXPERIMENTAL/SLA SIGN-OFF.**  
**Research question:** [RQ v1.0](research-questions.md) · **Upstream evidence:** [Stage 5D lifecycle contract](workload-measurement-calibration-stage5d.md), [Stage 5F real-broker MQTT smoke](mqtt-measurement-pilot-stage5f.md), [Stage 5G mock SQLite handler](application-handler-calibration-stage5g.md).  
**Purpose:** Close the missing **engineering integration** between the MQTT finite-`K` offer/queue model and the reference application handler, without designing or evaluating a new scheduling algorithm.

## 5H.1 — Explicit joint measurement boundaries

The unchanged Stage 5E MQTT publisher helper sends a seeded **fictional** Stage 5G two-class input via Eclipse Paho and a local Mosquitto broker (in MQTT mode). The new [`stage5h_joint_gateway.py`](../validation/stage5h_joint_gateway.py) builds on Stage 5E's *one worker + `K` waiting slots* `PilotGateway`, and connects its worker to Stage 5G's `process_one` SQLite lookup/rule/INSERT/commit. No priority scheduler has been introduced: the admission/worker baseline is **non-preemptive FIFO**, both classes see the same full-buffer rejection rule. A reserved not-yet-started active slot still consumes one of the `1+K` places.

The instrumentation records **different events**, not interchangeable latency numbers:

| Event | Trace field | Meaning and clock |
| --- | --- | --- |
| Published logical source | `published` + `source` | The sender's input listing; **no gateway timestamp or source→callback latency** |
| First receiver callback | `attempt.callback_ns` | Inside same-process gateway callback; MQTT subscription begins outside instrumented interval |
| End validation/dedup | `attempt.validation_end_ns` | Before acceptance/rejection; invalid/duplicate attempts cannot become new offers |
| Offered decision | `offer.offer_ns` | After validation/dedup, just before taking `K`-capacity decision |
| Worker reservation/run | `offer.start_ns` | One nonpreemptive worker selects already admitted work |
| Actual handler start | `offer.db_handler_start_ns` | Right before per-alert transaction + context lookup; worker/handler preamble is excluded |
| Commit returned | `offer.db_commit_return_ns` | After `Connection.commit()` returns; handler span is exactly `commit_return - handler_start` |
| Completion accounting | `offer.complete_ns` | After recording commit result; never before commit return |

The worker is the **only SQLite writer**, creates and closes its connection on its own thread (no disabled thread-safety flag), has a per-run file-backed DB and `WAL`/`synchronous=FULL`. Each admitted event has one primary-keyed `handled_alerts` record. Duplicate callbacks do not create another offer or DB INSERT. Rejections produce no DB work. This proves neither device authenticity nor persistence through a crash or storage failure.

**Checklist — 5H.1**
- [x] Document publisher/callback/offer/queue/worker/SQL/commit boundaries separately.
- [x] Preserve single-worker, class-neutral finite-`K` FIFO and offered-population metrics.
- [x] Use Stage 5G fictional context/rules with one commit per admitted unique alert.
- [ ] Confirm a real application owner would actually implement this schema, workload and completion effect.
- [ ] Confirm whether callback/dedup timing and broker retention are representative of deployment.

## 5H.2 — Independent replayable accounting and persisted-row evidence

[`stage5h_joint_audit.py`](../validation/stage5h_joint_audit.py) runs in **a separate process**, imports neither the Stage 5H gateway nor Stage 5G handler, and applies Stage 5D's generic lifecycle audit plus its own independent reconstruction of the seeded source fixture and three source schedules. It checks every source/offer class and deterministic SQL rule, exact service-timestamp arithmetic, `offer ≤ start ≤ db_handler_start ≤ db_commit_return ≤ complete`, all final lifecycle states, one worker, and **admitted = committed = SQL row count**. It fails on partial receiver capture or a published logical ID without one offer. A SHA-256-attested, post-run **SQLite backup file** is read directly in `mode=ro`; the auditor checks `PRAGMA integrity_check`, 16 context rows and exact saved event IDs/classes/device IDs/rule/JSON against the independently calculated offers. It does not merely trust the emitter's `db_reopen_exact` assertion.

The backup is produced with the SQLite backup API **after the worker completes**, separately from service time. It is a consistent **normal post-run snapshot** only, not a power-off/corruption/durability experiment. The recorded `source_sha256` and `schedule_sha256` identify the fictional inputs, while `sqlite_backup_sha256` binds the offline database file to the JSONL manifest. Source clock is not subtracted from receiver time. The derived p95 durations are diagnostic with no SLA threshold.

An in-process deterministic-input regression fixture is preserved:

- [Publisher/callback/offer ledger — `stage5h_inproc_debug.jsonl`](../validation/fixtures/stage5h_inproc_debug.jsonl)
- [SQLite backup encoded as base64 — `stage5h_inproc_debug.sqlite.b64`](../validation/fixtures/stage5h_inproc_debug.sqlite.b64)

The encoded file is purely to keep a binary SQLite snapshot in a text-only repository upload; CI decodes it and independently replays both positive and negative audits. Source fields are deterministic, but event timing and row counts under overload are **OS/host-dependent** and must never be used as a golden performance threshold.

**Archived raw fingerprints:** JSONL SHA-256 `627f25788b1c0daf1163df0f3d36c1f6fed4a5d19506130f92b103c39c3f7f2f`; decoded SQLite SHA-256 `e712a74a89c658c9871ee5104ecf1fb66e993a46e37fb4e6e359518017c83c27`. Code SHA-256: gateway `2fcbcd91a95cdbf6f6010da36005e7bc3d2127481811550773606242b4d62a91`; independent auditor `9c557373f971b23ecd51277dc9d250f95755168bf6369526a57c2301246b5742`.

**Local Python 3.12 smoke (16 November 2026):**

| Mode | Shape | K | Unique offers | SQL-completed | Full-buffer rejected | Result |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| In-process | base | 0 | 36 | 36 | 0 | PASS |
| In-process | burst | 0 | 36 | 24 | 12 | PASS |
| In-process | overload | 0 | 36 | 1 | 35 | PASS |
| In-process | base | 3 | 36 | 36 | 0 | PASS |
| In-process | burst | 3 | 36 | 27 | 9 | PASS |
| In-process | overload | 3 | 36 | 4 | 32 | PASS |

These are **non-independent single-host smoke counts**, not stable measurements or estimates of the proposed policy's merit. Each test received 36 intended unique alerts + two deliberate duplicate sends + one malformed payload; `admitted` matched all reopened SQLite rows and no active/waiting jobs remained. The archived in-process burst `K=3` fixture had 27 independently rechecked SQL rows, 9 full-buffer rejects, 2 duplicate callbacks, 1 malformed callback, and **zero unknown published IDs**. The auditor rejected 13 corrupted ledger mutations, an inproc attempt at the MQTT-only gate, and a mutated real SQLite database.

**Checklist — 5H.2**
- [x] Implement independent source/schedule/class/rule/timestamp verifier.
- [x] Reopen a separate SQLite file and match every persisted row to admitted completion; hash the backup.
- [x] Pass six synthetic in-process joint smoke shapes/capacities.
- [x] Reject 13 deliberate malformed ledgers, a false inproc-at-MQTT gate and changed SQLite contents.
- [ ] Test process crash between INSERT/commit and after commit; prove recovery/dedup policy under redelivery if that is part of real requirements.
- [ ] Measure logging, validation, backup, WAL checkpoint and resource overhead separately.

## 5H.3 — Real broker-backed CI evidence (independently verified)

The [Stage 5H GitHub Actions workflow](../../.github/workflows/stage5h-joint-mqtt.yml) installs local Mosquitto and Eclipse Paho 2.x on Ubuntu/Python 3.12, executes prior Stage 5D/5G regression self-tests, the new six-shape smoke and full independent positive/negative audit, **decodes and re-audits the committed in-process fixture**, and conducts three real broker-backed MQTT→SQLite runs (`base`, `burst`, `overload`, **60 synthetic unique messages per run**, `K=3`, seed 101). It captures a complete JSONL callback/offer/commit ledger, per-run post-run SQLite backup, independent gate JSON and broker log. The audit requires `--require-mqtt` for all three broker-backed runs.

On [PR #49](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/pull/49), **[Stage 5H CI run #43877369913](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/actions/runs/43877369913) succeeded**. The actual Ubuntu job installed/started the broker, ran the expected positive/negative checks, published through Paho, independently audited all three source/offer/SQL backups and uploaded [artifact #14230686972](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/actions/runs/43877369913/artifacts/14230686972) (temporary GitHub retention through approximately **30 November 2026**). The earlier [Stage 5F MQTT regression run #43877369587](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/actions/runs/43877369587) also succeeded. I **downloaded the complete 19-file Stage 5H CI artifact** and re-executed `stage5h_joint_audit.py ... --require-mqtt` against all three saved JSONL + SQLite pairs in a separate workspace; **3/3 passed**.

| **One CI execution only** | Published/offered unique | Duplicates / malformed | SQLite committed = independently saved | Full-buffer rejects | Unresolved | Independent audit |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| MQTT `base` | 60 / 60 | 4 / 1 | 58 = 58 | 2 | 0 | PASS |
| MQTT `burst` | 60 / 60 | 4 / 1 | 49 = 49 | 11 | 0 | PASS |
| MQTT `overload` | 60 / 60 | 4 / 1 | 24 = 24 | 36 | 0 | PASS |

These acceptance counts are **observations from a single shared GitHub runner**, not repeatability statistics, scheduling benefits, throughput or deadline evidence. For example, overload's stronger rejection is a synthetic source-pacing consequence; it cannot establish any desired `U`/`R(tau)` operating point for a real IoT system. All 180 intended unique synthetic events reached gateway offers; all 131 admitted events committed one row; 49 offers were rejected by the finite queue; the three runs logged 12 duplicate callback attempts and three malformed callbacks in addition to their 180 offers.

For evidence beyond the artifact's 14-day lifetime, the exact MQTT JSONLs, SQLite backups (base64 text) and gate JSON were archived per shape:

| Shape | Saved raw ledger / DB snapshot / gate | JSONL SHA-256 | Decoded DB SHA-256 |
| --- | --- | --- | --- |
| `base` | [`base` records](../validation/fixtures/stage5h_mqtt_base_ci43877369913.jsonl) · [SQLite backup](../validation/fixtures/stage5h_mqtt_base_ci43877369913.sqlite.b64) · [gate result](../validation/fixtures/stage5h_mqtt_base_ci43877369913.gate.json) | `eed8279c467d8aeb6c3eceb508a646a51b74d0903d1df5f489b84d6282545456` | `f8523c9dc4a1391a8720a5d57a3dfa8132a87b920be454180f1c93b163de34df` |
| `burst` | [`burst` records](../validation/fixtures/stage5h_mqtt_burst_ci43877369913.jsonl) · [SQLite backup](../validation/fixtures/stage5h_mqtt_burst_ci43877369913.sqlite.b64) · [gate result](../validation/fixtures/stage5h_mqtt_burst_ci43877369913.gate.json) | `722b943200938b7376e20de96e3b684c91c80b7dca15aeb9c047aafe0cdf7471` | `fde007718b84a5f9f469dedfbc6bc4e064ee2deeea134205713cecfa00f1191a` |
| `overload` | [`overload` records](../validation/fixtures/stage5h_mqtt_overload_ci43877369913.jsonl) · [SQLite backup](../validation/fixtures/stage5h_mqtt_overload_ci43877369913.sqlite.b64) · [gate result](../validation/fixtures/stage5h_mqtt_overload_ci43877369913.gate.json) | `9cf5f2bea4453f067ec9690d8484e036a66473bcd62d4e72c24f3553ddd53fa1` | `475428efa4058c25d2a6bf85284c6fe0f9ec7b990b6b37c2b3c598d73db1bffc` |

The workflow has been extended to **re-audit all three archived broker datasets** before producing new cases on future PR runs. This tests stable accounting, not unstable real-time duration thresholds. The original Mosquitto log SHA-256 was `a80b38a630dfe554f2f017bb35a612052e81b72fe9f3fb84c24b00a52c0fdbc4` and remains in the downloadable CI artifact. The following checks are therefore verified against **CI run #43877369913**; reruns after evidence/documentation commits are separate runs and should be inspected independently.

**Transport caveat:** the manifest's `scenario_id=stage5h_mqtt_*` is a claimed mode and is not cryptographic proof of MQTT; it is corroborated by the actual checked-out runner command and broker log. QoS 1 may redeliver; repeated callbacks are deduplicated, so audit uses minimum intended duplicate count rather than an exact callback count. No end-to-end device-to-effect timestamp is asserted, and an ACK'd publisher alone would not prove all receiver offers.

**Checklist — 5H.3**
- [x] Provide repeatable local broker-backed integration CI workflow and short-lived raw capture artifact.
- [x] Verify workflow **actually ran to SUCCESS** on the Stage 5H PR, including broker-backed runs and independent SQLite checks.
- [x] Download/replay CI JSONLs + actual SQLite backups, save run/artifact links and exact per-shape accounting; retain source and DB hashes.
- [x] Archive broker-backed raw evidence for future independent re-audit after GitHub artifact expiry.
- [x] Verify prior Stage 5F MQTT regression remains green; Stage 5G self-tests passed within the Stage 5H job.
- [ ] Verify the new workflow revision also re-audits the archived broker snapshots on its subsequent PR run.

## 5H.4 — Decision gate for conference work

| Requirement | What Stage 5H can substantiate | What remains blocked |
| --- | --- | --- |
| Finite-`K` offered lifecycle | Every synthetic accepted/rejected/duplicate/invalid callback accounted for | Real ingress broker backpressure and complete deployment event population |
| Worker service boundary | Context lookup + rule + INSERT + **commit return** within measured nonpreemptive worker interval | Real application code, storage, device data, failures and deployment hardware |
| Completion persistence | External auditor read actual post-run SQLite snapshot, exact admitted row match | Crash/power-loss recoverability and broker/system end-to-end guarantees |
| Offered urgent `U` / routine `R(tau)` | Stage 5D computes offered-population rates on lab traces | Approved real `D_u`, `epsilon`, `tau`, `gamma`, `K`, held-out experiment plan |
| Research novelty | No new scheduling algorithm was implemented or compared | Stage 4B **REVISE/NARROW**, complete N01/N03/N06/N09 and professor decision |

**Checklist — 5H.4**
- [x] Keep prototype timings from being reinterpreted as field service-level or scheduling improvements.
- [x] Show Stage 5G actual fictional DB work inside Stage 5F-like transport/queue trace.
- [ ] Obtain a representative application trace and application-owner sign-off, including real deadline/success semantics.
- [ ] Resolve prior-art/novelty overlap with full-text evidence and professor sign-off.
- [ ] Preregister evaluation and matched-workload baselines **only after** above gates; Stage 6 remains pending.

### Reproduction

```bash
# From repository root; no third-party dependencies for in-process diagnostics
python3 literature/validation/stage5h_joint_gateway.py --self-test
python3 literature/validation/stage5h_joint_audit.py --self-test

# Capture a fresh in-process SQLite-backed run; choose NEW output names
python3 literature/validation/stage5h_joint_gateway.py \
  --transport inproc --shape burst --events 36 --seed 101 --queue-capacity 3 \
  --output scratch-5h.jsonl --sqlite-output scratch-5h.sqlite
python3 literature/validation/stage5h_joint_audit.py \
  scratch-5h.jsonl --sqlite scratch-5h.sqlite

# Requires paho-mqtt>=2,<3 and a local Mosquitto listener on 127.0.0.1:1883
python3 literature/validation/stage5h_joint_gateway.py \
  --transport mqtt --shape base --events 60 --queue-capacity 3 \
  --output scratch-5h-mqtt.jsonl --sqlite-output scratch-5h-mqtt.sqlite
python3 literature/validation/stage5h_joint_audit.py \
  scratch-5h-mqtt.jsonl --sqlite scratch-5h-mqtt.sqlite --require-mqtt

# Independently replay permanently archived broker records (example: base)
base64 --decode literature/validation/fixtures/stage5h_mqtt_base_ci43877369913.sqlite.b64 \
  > scratch-5h-archived-base.sqlite
python3 literature/validation/stage5h_joint_audit.py \
  literature/validation/fixtures/stage5h_mqtt_base_ci43877369913.jsonl \
  --sqlite scratch-5h-archived-base.sqlite --require-mqtt
```

**Stage 5H provisional verdict:** The joint MQTT+SQLite experiment is a **verification and instrumentation milestone**, not evidence of an IoT-specific scheduling contribution. Gate remains **closed** to real-world service calibration and all conference result claims until independent, representative data and a supervisor-approved novelty/evaluation plan exist.
