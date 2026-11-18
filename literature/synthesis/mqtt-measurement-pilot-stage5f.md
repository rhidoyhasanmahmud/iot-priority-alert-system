# Stage 5F — Reproducible broker-backed MQTT integration gate

**Date:** 16 November 2026  
**Current status:** **BROKER-BACKED MQTT CI LAB SMOKE VERIFIED (3/3); RESEARCH / APPLICATION CALIBRATION STILL OPEN.**  
**Scope:** an engineering check of MQTT `publish → gateway callback → validation/dedup → local offer → admission → FIFO worker` on a locally provisioned broker. Not sensor-derived workloads, actual security enrichment, a production deadline, policy novelty or a conference experiment.

**Background:** [Stage 5D](workload-measurement-calibration-stage5d.md) established an independent JSONL ledger contract; [Stage 5E](mqtt-measurement-pilot-stage5e.md) executed six **in-process** smoke conditions, but the local environment had no Paho client, Mosquitto broker or container runtime. **Important GitHub correction:** PR #46 was merged into the Stage 5D feature branch after PR #45 was merged to main; the five Stage 5E files did **not** propagate to main. The next PR explicitly targets `main` and carries those five Stage 5E files plus the Stage 5F integration gate, rather than treating a merged PR status as proof of main-branch contents.

## Step 5F.1 — Define a falsifiable MQTT gate before any broker results

The independent [`stage5f_mqtt_gate.py`](../../experiments/stage5f_mqtt_gate.py) reuses the unmodified [Stage 5D oracle](../../experiments/stage5d_lifecycle_audit.py) to validate one JSONL file. Its **real-MQTT mode** requires:

1. Manifest labels the source `stage5e_mqtt_*` and declares a complete publisher record and callback capture, with one gateway process-local monotonic clock.
2. Each distinct intended published logical ID has a gateway callback and exactly one valid post-validation offered job. Source/offered counts match, with no unobserved source ID.
3. Valid source offers satisfy `offered = admitted + rejected` and all admitted synthetic CPU handler jobs complete before trace cutoff. Reject, duplicate, invalid and queue-state checks match Stage 5D.
4. The intentionally republished logical IDs appear as separate deduplicated callback attempts and the deliberately malformed payload appears as invalid; **extra QoS1 retries are permitted** but cannot cover up a *missing logical source ID*.
5. Both classes are present, urgent U and routine R(tau) denominators are nonempty and exact for this fully drained debug run. Worker intervals are nonnegative/nonoverlapping.

The gate reports **descriptive** callback-to-offer, validation-end-to-offer, queue-wait and synthetic CPU-handler p95 (nearest-rank **within one run**) plus offered counts and U/R. It explicitly **does not** estimate publish-to-broker-to-callback latency: the current source `published` rows have unique IDs but no provenance-verified comparable per-message send timestamp. A manifest label is also not cryptographic proof of network provenance; confirm it with broker logs, recorded Paho versions, the executable workflow and its run metadata.

**Local static/self-check status (no broker):**

- The archived **in-process** 36-offer fixture passes the general ledger checks but is explicitly **rejected** if submitted as MQTT evidence.
- An incomplete receiver-capture manifest is explicitly **rejected**.
- The independent Stage 5D checker continues to validate the sample separately.
- Python `py_compile` passes for the Stage 5F gate and Stage 5E pilot; workflow YAML loads under a YAML parser. These checks do **not** execute Paho callbacks.

**Checklist — 5F.1**
- [x] Define exact lab-MQTT acceptance/stop conditions based on offered unique logical IDs and closed lifecycle partitions.
- [x] Implement an independent gate rejecting non-MQTT data and incomplete captures.
- [x] Smoke-check the existing in-process fixture without relabeling it as MQTT.
- [x] Prove the gate works with **actually captured** Mosquitto/Paho data and inspect broker logs for lab provenance (run #43870469820; details below).

## Step 5F.2 — Prepare a versioned, locally isolated broker run

The [GitHub Actions workflow](../../.github/workflows/stage5f-mqtt-integration.yml) executes a Linux/Python 3.12 laboratory job:

1. Install a local Mosquitto broker and `paho-mqtt>=2,<3` in the ephemeral GitHub runner; record the installed client and broker versions. The broker binds to loopback, not a publicly accessible listener. [Eclipse Paho Python documentation](https://eclipse.dev/paho/clients/python/docs/) and [Mosquitto Docker/configuration documentation](https://github.com/eclipse-mosquitto/mosquitto/blob/master/docker/generic/README.md) are the vendor references.
2. Run independent Stage 5D and Stage 5F self-checks and the Stage 5E in-process smoke (separately labelled).
3. With Paho subscriber **connected and subscribed before publishing**, run the two-class bounded FIFO gateway against the local broker at `base`, source-horizon-matched `burst` and deliberate `overload` patterns. Each short pilot attempts 60 synthetic unique logical events, four deliberately repeated application publishes (every 13th), and one malformed publish. QoS1 publish confirmations are checked **after** the paced send loop so the source is not intentionally ACK-paced.
4. Persist the raw per-attempt/per-offer JSONL, independent Stage 5F gate summaries and Mosquitto logs for review as a **short-retention CI artifact**. On missing callbacks, an incomplete run returns nonzero and saves available diagnostic ledgers. Such a failed run must not be silently reused as a valid study trace.

The workflow is enabled for pull requests affecting the research validation paths and for manual dispatch. **Creating the workflow is not itself evidence that it ran.** The actual passed run and independently re-audited JSONLs are recorded under Step 5F.4.

**Checklist — 5F.2**
- [x] Author an isolated broker/Paho integration workflow and an auditable raw-ledger capture path.
- [x] Separate source-shape-only changes from total source intensity changes, and keep debug capacity/50ms timing budgets visibly artificial.
- [x] Preserve failures as test failures and artifacts, not “missing experiments” reclassified as success.
- [x] Confirm GitHub Actions permission/execution, job completion, versioned Mosquitto/Paho logs and independent audit: **PASS, run #43870469820**.
- [ ] Repeat the study outside CI on a known local lab configuration if a publish/subscribe timing result is to be analyzed.

## Step 5F.3 — What a passing lab result still would not establish

All three broker-backed shapes passed the functional gate (Step 5F.4), establishing only **functional pipeline/accounting feasibility on a single-machine local MQTT testbed**. This does not give an application SLA, an empirical arrival distribution from IoT devices, a representative handler-service distribution, reliable source-to-callback timing, a statistically supported scheduling improvement, or novel algorithm proof.

The processing job is still PBKDF2 and in-memory JSON serialization, **not** real enrichment/rule database persistence. The scheduler remains FIFO only. The original paper candidate's novelty statement remains **Stage 4B REVISE/NARROW**, with authorized full-text/database/theorem/supervisor sign-off outstanding. Domain-derived numerical `D_u`, absolute `epsilon`, routine `tau`, `gamma`, `K` and sensitivity/held-out split are not approved. Do not promote the debug 50 ms threshold, small K, 25% urgent mix or workload timing to realistic application requirements.

The following would be required for a **separate application-calibration gate**: authentic anonymized field trace or explicit professor-approved synthetic-only scope, a declared real worker's processing semantics and service-time measurement, queue memory/overhead measurement, and a predeclared parameter decision sheet with evidence and approval. Only then can Stage 6 full evaluation pre-registration be reviewed.

**Checklist — 5F.3**
- [x] Define what a successful local Mosquitto smoke can and cannot support.
- [x] Retain research-wide offered denominator, one-worker/nonpreemptive and no-unstarted-service-oracle boundaries.
- [x] Verify actual MQTT CI artifacts, then record explicit transport-accounting result and limitations here (Step 5F.4).
- [ ] Obtain application/service provenance and professor/supervisor decisions before Stage 6.

## Step 5F.4 — Observed GitHub Actions Mosquitto/Paho run (16 November 2026)

The **initial** PR #47 run #43870256254 failed *before running MQTT* because `mosquitto -h` prints valid help but exits with code 3 under Bash `-e`. The workflow was corrected to use `dpkg-query -W mosquitto`. This is a CI harness setup failure, **not** an unsuccessful MQTT measurement.

The subsequent [run #43870469820](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/actions/runs/43870469820), on head `dc111b5a59b6bf4c1e9a3b9f89a1733373116356`, completed **SUCCESS**. The Actions log confirms Ubuntu 24.04, Python 3.12.16, local Mosquitto `2.0.18-1build3` and Paho MQTT `2.2.0`. Loopback broker readiness, Stage 5D/5E/5F independent smoke checks, three MQTT ledger captures, three Stage 5F gates, and artifact upload all passed.

| Single-run laboratory shape | Unique source / offers | Receiver callbacks | Duplicate / invalid | Completed / rejected | Debug U (urgent failure) | Debug R(tau) (routine timely start) | Independent ledger gate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `base` | 60 / 60 | 65 | 4 / 1 | 58 / 2 | 1/15 | 44/45 | PASS |
| `burst` (same nominal source horizon) | 60 / 60 | 65 | 4 / 1 | 43 / 17 | 4/15 | 32/45 | PASS |
| `overload` (increased source intensity) | 60 / 60 | 65 | 4 / 1 | 6 / 54 | 12/15 | 3/45 | PASS |

Each shape has **15 urgent and 45 routine offers**, `K=3` waiting plus one active/reserved job, FIFO policy, and **unapproved artificial 50 ms** debug thresholds. The fraction changes are illustrative only: *one short run per shape*, no seeds/repetitions or confidence intervals, OS/broker effects uncontrolled. The broker log independently records **195 received publishes**, **195 forwarded publishes**, **195 received PUBACKs**, and **3 subscriptions** (65 publications per shape), consistent with the three gateway ledgers. These are local broker operations, not device-to-broker field measurements or a QoS guarantee under broker failure.

The [Actions diagnostic artifact](https://github.com/rhidoyhasanmahmud/iot-priority-alert-system/actions/runs/43870469820) is `stage5f-broker-mqtt-debug-ledgers` (artifact ID `14228545027`; GitHub SHA-256 ZIP digest `d88318f95eee7cba583b9f6cac16aeb826e7c84821cc46bee08728ff8e9e3922`, 14-day retention). It contains three JSONL ledgers, their three gate JSON outputs and the Mosquitto log. The ZIP was downloaded, passed `unzip -t`, and **each extracted JSONL was rechecked separately with the independent `stage5f_mqtt_gate.py`: 3/3 PASS**.

To retain the key raw ledgers beyond CI artifact expiry, this PR also versions these **synthetic-only** traces:

| Scenario | Retained JSONL in `../../experiments/fixtures/` | SHA-256 |
| --- | --- | --- |
| base | [`stage5f_mqtt_base_ci_run43870469820.jsonl`](../../experiments/fixtures/stage5f_mqtt_base_ci_run43870469820.jsonl) | `3c492beec440f44389c98d52b4c7524fab66cb5dbf9450ac9bbb238e5f6b6e05` |
| burst | [`stage5f_mqtt_burst_ci_run43870469820.jsonl`](../../experiments/fixtures/stage5f_mqtt_burst_ci_run43870469820.jsonl) | `197709903917c4bd2c53c04839b92916b875239e86fedebcd4f2b126d60a4a8d` |
| overload | [`stage5f_mqtt_overload_ci_run43870469820.jsonl`](../../experiments/fixtures/stage5f_mqtt_overload_ci_run43870469820.jsonl) | `833a688e4fafe084f18ddbd0b912cbe1bdd19a2ccd18fdfd9a39ddde83266ce3` |

The broker log SHA-256 is `4fa42714c8b3cce4a7fcf46491aff4a2a59f1757c9ce5d59887587c6d87167fb`. **No publish-to-callback network latency, realistic handler-service distribution, statistical superiority, validated absolute deadline, or algorithm novelty is implied.** The run uses only a single-machine synthetic two-class PBKDF2/FIFO pilot.

**Checklist — 5F.4**
- [x] Diagnose and fix pre-MQTT CI setup error; preserve failed-run provenance.
- [x] Execute real loopback MQTT publish/subscribe using Mosquitto and Paho 2.x.
- [x] Verify independent 3/3 ledger gates and inspect publisher/subscriber broker log counts.
- [x] Download/test the diagnostic archive; independently audit all three retained raw JSONLs.
- [x] Record immutable run ID, tool versions, scenario counts, raw SHA-256 and limitations.
- [ ] Repeat with multiple seeds and a representative application handler **only after** service/workload requirements and study protocol are approved.

## Overall Stage 5F progress

| Item | Status |
| --- | --- |
| Stage 5E files corrected for a normal `main`-targeted PR | **PR #47 OPEN; review/merge pending** |
| Independent Stage 5F JSONL MQTT gate | **IMPLEMENTED; local in-process negative/positive tests pass** |
| Mosquitto/Paho workflow syntax and diagnostic artifact plan | **IMPLEMENTED; CI success verified** |
| A broker-backed MQTT run with captured logs | **3/3 LAB SMOKE PASSED; raw JSONL retained** |
| Service-time / burst / numeric operator calibration | **OPEN** |
| Stage 4B full novelty clearance and supervisor approval | **OPEN** |
| Stage 6 preregistration / conference conclusions | **NOT STARTED** |

**Research recommendation:** **PASS** Stage 5F's limited engineering transport-accounting smoke; **GO** to service/workload calibration and predeclared measurements only after supervisory scope and evidence approval. **NO-GO** to conference-performance claims or unapproved algorithm novelty. CI ledger reconciliation is a necessary engineering check, not an empirical contribution.
