# Stage 5F — Reproducible broker-backed MQTT integration gate

**Date:** 16 November 2026  
**Current status:** **CI/LAB HARNESS PREPARED; MQTT-BROKER EXECUTION AND RESULTS NOT YET VERIFIED.**  
**Scope:** an engineering check of MQTT `publish → gateway callback → validation/dedup → local offer → admission → FIFO worker` on a locally provisioned broker. Not sensor-derived workloads, actual security enrichment, a production deadline, policy novelty or a conference experiment.

**Background:** [Stage 5D](workload-measurement-calibration-stage5d.md) established an independent JSONL ledger contract; [Stage 5E](mqtt-measurement-pilot-stage5e.md) executed six **in-process** smoke conditions, but the local environment had no Paho client, Mosquitto broker or container runtime. **Important GitHub correction:** PR #46 was merged into the Stage 5D feature branch after PR #45 was merged to main; the five Stage 5E files did **not** propagate to main. The next PR explicitly targets `main` and carries those five Stage 5E files plus the Stage 5F integration gate, rather than treating a merged PR status as proof of main-branch contents.

## Step 5F.1 — Define a falsifiable MQTT gate before any broker results

The independent [`stage5f_mqtt_gate.py`](../validation/stage5f_mqtt_gate.py) reuses the unmodified [Stage 5D oracle](../validation/stage5d_lifecycle_audit.py) to validate one JSONL file. Its **real-MQTT mode** requires:

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
- [ ] Prove the gate works with **actually captured** Mosquitto/Paho data and inspect broker logs to validate provenance.

## Step 5F.2 — Prepare a versioned, locally isolated broker run

The [GitHub Actions workflow](../../.github/workflows/stage5f-mqtt-integration.yml) proposes a Linux/ Python 3.12 laboratory job:

1. Install a local Mosquitto broker and `paho-mqtt>=2,<3` in the ephemeral GitHub runner; record the installed client and broker versions. The broker binds to loopback, not a publicly accessible listener. [Eclipse Paho Python documentation](https://eclipse.dev/paho/clients/python/docs/) and [Mosquitto Docker/configuration documentation](https://github.com/eclipse-mosquitto/mosquitto/blob/master/docker/generic/README.md) are the vendor references.
2. Run independent Stage 5D and Stage 5F self-checks and the Stage 5E in-process smoke (separately labelled).
3. With Paho subscriber **connected and subscribed before publishing**, run the two-class bounded FIFO gateway against the local broker at `base`, source-horizon-matched `burst` and deliberate `overload` patterns. Each short pilot attempts 60 synthetic unique logical events, four deliberately repeated application publishes (every 13th), and one malformed publish. QoS1 publish confirmations are checked **after** the paced send loop so the source is not intentionally ACK-paced.
4. Persist the raw per-attempt/per-offer JSONL, independent Stage 5F gate summaries and Mosquitto logs for review as a **short-retention CI artifact**. On missing callbacks, an incomplete run returns nonzero and saves available diagnostic ledgers. Such a failed run must not be silently reused as a valid study trace.

The workflow is enabled for pull requests affecting the research validation paths and for manual dispatch. **Creating the workflow is not itself evidence that it ran.** Check the real GitHub Actions job conclusion, log, Paho version, broker start and downloadable JSONL before changing this report's pending status.

**Checklist — 5F.2**
- [x] Author an isolated broker/Paho integration workflow and an auditable raw-ledger capture path.
- [x] Separate source-shape-only changes from total source intensity changes, and keep debug capacity/50ms timing budgets visibly artificial.
- [x] Preserve failures as test failures and artifacts, not “missing experiments” reclassified as success.
- [ ] Confirm GitHub Actions permission/execution, job completion, versioned Mosquitto/Paho logs and independent audit: **PENDING**.
- [ ] Repeat the study outside CI on a known local lab configuration if a publish/subscribe timing result is to be analyzed.

## Step 5F.3 — What a passing lab result still would not establish

Even if all three broker-backed shapes pass, the result establishes only **functional pipeline/accounting feasibility on a single-machine local MQTT testbed**. It does not give an application SLA, an empirical arrival distribution from IoT devices, a representative handler-service distribution, reliable source-to-callback timing, a statistically supported scheduling improvement, or novel algorithm proof.

The processing job is still PBKDF2 and in-memory JSON serialization, **not** real enrichment/rule database persistence. The scheduler remains FIFO only. The original paper candidate's novelty statement remains **Stage 4B REVISE/NARROW**, with authorized full-text/database/theorem/supervisor sign-off outstanding. Domain-derived numerical `D_u`, absolute `epsilon`, routine `tau`, `gamma`, `K` and sensitivity/held-out split are not approved. Do not promote the debug 50 ms threshold, small K, 25% urgent mix or workload timing to realistic application requirements.

The following would be required for a **separate application-calibration gate**: authentic anonymized field trace or explicit professor-approved synthetic-only scope, a declared real worker's processing semantics and service-time measurement, queue memory/overhead measurement, and a predeclared parameter decision sheet with evidence and approval. Only then can Stage 6 full evaluation pre-registration be reviewed.

**Checklist — 5F.3**
- [x] Define what a successful local Mosquitto smoke can and cannot support.
- [x] Retain research-wide offered denominator, one-worker/nonpreemptive and no-unstarted-service-oracle boundaries.
- [ ] Verify actual MQTT CI artifacts, then record explicit transport-accounting result and limitations here.
- [ ] Obtain application/service provenance and professor/supervisor decisions before Stage 6.

## Overall Stage 5F progress

| Item | Status |
| --- | --- |
| Stage 5E files corrected for a normal `main`-targeted PR | **PREPARED; review/merge pending** |
| Independent Stage 5F JSONL MQTT gate | **IMPLEMENTED; local in-process negative/positive tests pass** |
| Mosquitto/Paho workflow syntax and diagnostic artifact plan | **PREPARED; runner result pending** |
| A broker-backed MQTT run with captured logs | **NOT VERIFIED / PENDING** |
| Service-time / burst / numeric operator calibration | **OPEN** |
| Stage 4B full novelty clearance and supervisor approval | **OPEN** |
| Stage 6 preregistration / conference conclusions | **NOT STARTED** |

**Research recommendation:** **GO** to executing and auditing the local broker-backed CI lab smoke. **NO-GO** to conference-performance claims or unapproved algorithm novelty. Check this table and the central progress checklist **after** the actual CI result; never mark an unobserved experiment complete.
