# Stage 5E — Instrumented gateway measurement feasibility pilot

**Date:** 16 November 2026 · **Status:** **IN-PROCESS GATEWAY ENGINEERING SMOKE PASS; REAL MQTT TRANSPORT MEASUREMENT NOT RUN.**  
**Research track:** [RQ v1.0](research-questions.md), [Stage 5D lifecycle contract](workload-measurement-calibration-stage5d.md), [Stage 5C metric oracle](two-class-metric-validation-stage5c.md).  
**No claim:** this is *not* a field-sensor trace, validated application service time, experimental scheduler comparison, conference result, or novelty sign-off.

The isolated [`stage5e_gateway_pilot.py`](../../experiments/stage5e_gateway_pilot.py) exercises a **single non-preemptive FIFO worker, K waiting slots plus one reserved/running slot**, two synthetic event kinds, and timestamped source/callback/validation/offer/start/completion/rejection. An optional Eclipse Paho MQTT 2.x transport mode uses a **separately running broker**; the mode is **unexecuted in this environment**. The [Stage 5D independent ledger auditor](../../experiments/stage5d_lifecycle_audit.py) is reused unchanged for every run.

## Step 5E.1 — A working source-to-local-offer instrumented probe

The pilot separates four critical code paths:

1. **Producer.** Creates deterministic JSON logical events: `kind=tamper` maps to urgent; `kind=health` maps to routine. Every fourth logical event is urgent; synthetic CPU work parameter cycles through 4,000/8,000/16,000 iterations. One application-level duplicate is deliberately sent after every 13 events, and one invalid JSON payload is injected per run. This is a **lab classification assumption, not authenticated security priority**.
2. **Callback/validation.** `callback_ns` is the first receiver action; payload syntax/type validation and run-scoped logical-ID dedup precede `validation_end_ns` and `offer_ns`. Invalid and duplicate deliveries have **no offer**. A repeated rejected logical ID does not silently get re-offered.
3. **Finite local admission.** Under a single condition lock, snapshot `waiting_at_offer`, `running_at_offer`, then admit to the available single reserved/running slot, append to the K-slot waiting deque, or mark a **class-neutral** queue-full rejection. The offered row always exists, including for rejections. The worker's reserved-but-not-yet-started slot counts as busy for admission.
4. **FIFO worker.** Records actual handler entry and finish on one process-local monotonic clock. Its handler runs **PBKDF2/SHA-256 CPU computation + tiny deterministic rule and JSON serialization**, rather than `time.sleep` as a service surrogate. This is **measured synthetic CPU work**, not a real enrichment lookup, database transaction, authenticated alert processor, or durable side effect. The worker reads the synthetic work amount only after dispatch; FIFO selection does not inspect it.

The processing queue is finite and the run is drained before the manifest cutoff. The pilot's **in-memory telemetry list** is a separate small-sample collection buffer; its memory/cost and any production telemetry drops require independent measurement before claiming scalability. In-process source calls are direct function invocations and **do not exercise MQTT broker/network behavior**.

**Checklist — 5E.1**
- [x] Record callback vs post-validation offer timestamps distinctly; identify every logical attempted delivery and every unique offer.
- [x] Use one real non-preemptive CPU-executing worker with K waiting slots; do not silently treat its synthetic CPU work as representative application processing.
- [x] Emit the JSONL manifest/attempt/offer schema compatible with Stage 5D and preserve rejected offers.
- [ ] Measure logging overhead and compare against an independently defined real enrichment/rule/persist handler.
- [ ] Authenticate or independently validate the class mapping before calling it a deployed security-system measurement.

## Step 5E.2 — Source workload controls and transport distinction

| Shape | Generated source interarrival schedule | Causal interpretation |
| --- | --- | --- |
| `base` | First event at zero, then **8 ms** target gaps | Synthetic reference schedule; not an empirical device arrival model. |
| `burst` | Middle one-third of gaps set to zero; removed time redistributed across other gaps | **Same intended source horizon, event IDs, class/work sequence and count** as base, but different source burst shape. |
| `overload` | All target gaps zero | **Higher offered source intensity / shorter horizon**; cannot attribute differences to burst shape alone. |

These are **source-schedule targets**, not equal measured callback/offer timestamps. A real MQTT replay has broker, publisher, OS and callback timing drift; even the in-process producer and worker contend for CPU. Record realized per-policy offers separately. One logical event is published once plus any deliberate repeated application publish; the latter is not the same as an observed protocol-layer retransmission. Use the same generated class/work/ID list and gap vector when comparing policies later; the current pilot contains **FIFO only**.

**Checklist — 5E.2**
- [x] Specify distinct rate-matched shape-only and source-intensity-change interventions.
- [x] Programmatically assert base and burst planned source horizons equal, overload horizon intentionally different.
- [x] Preserve source class/work order across shapes; do not expose unstarted service time in the FIFO scheduler.
- [ ] Obtain real published/callback/offer traces; test realized arrival and worker-service distributions under MQTT.
- [ ] Calibrate class fractions, sources, burst lengths and service-work intensity from a declared application or label the study synthetic-only with supervisor approval.

## Step 5E.3 — Exactly what ran, and independent audit results

**Execution environment:** Python 3.12.14, standard library only for in-process mode. Local inspection found **no Mosquitto executable, no Paho MQTT Python module and no Docker/Podman**. The optional `--transport mqtt` code path was therefore **not executed or characterized**. It is an unverified integration path requiring a local-broker smoke test; the presence of MQTT API code must not be reported as a successful MQTT experiment.

### Six short *in-process* smoke checks

Executed `python3 experiments/stage5e_gateway_pilot.py --self-test` after creating the code. Each cell has **36 unique synthetic intended source events**, 2 deliberate duplicate callback attempts, 1 invalid callback attempt, 36 valid local offers; `K` is **waiting slots**. `D_u=50 ms` and `tau=50 ms` are **unvalidated debug constants**.

| K | Shape | Offered | Rejected | Completed | Audit |
| ---: | --- | ---: | ---: | ---: | --- |
| 0 | Base | 36 | 0 | 36 | PASS |
| 0 | Burst | 36 | 12 | 24 | PASS |
| 0 | Overload | 36 | 35 | 1 | PASS |
| 3 | Base | 36 | 0 | 36 | PASS |
| 3 | Burst | 36 | 9 | 27 | PASS |
| 3 | Overload | 36 | 32 | 4 | PASS |

**These numbers are one observed local engineering smoke**, and even rerunning the same source schedule may change them due to runtime scheduling and CPU contention. They are **not reproducible per-cell performance targets, independent samples, calibrated results or conference effect estimates**. All six generated ledgers passed the independent Stage 5D invariants with offered = admitted + rejected, correct class denominators, bounded waiting snapshots, one non-preemptive worker, and no unresolved offers at drain.

A second successful self-test run illustrates this distinction: `K=3, burst` rejected **10** instead of **9** offers while both runs passed conservation and timing invariants. The synthetic source schedule is reproducible; real thread/worker timing and outcome counts are **not bit-for-bit reproducible**.

### One retained inspectable *in-process* sample (not MQTT)

Generated with:

```bash
python3 experiments/stage5e_gateway_pilot.py --transport inproc --shape burst --events 36 --queue-capacity 3 --output stage5e_inproc_sample.jsonl
python3 experiments/stage5d_lifecycle_audit.py stage5e_inproc_sample.jsonl
```

Raw sample: [`experiments/fixtures/stage5e_inproc_burst_k3_debug.jsonl`](../../experiments/fixtures/stage5e_inproc_burst_k3_debug.jsonl); SHA-256 `cff13fa6531b14e46deb2e153e723ffa3eface2eebc33418a8086cbd61d60f65`. This captures real monotonic timestamps of **locally executed synthetic CPU work**, not data from a broker or sensor. The 36-unique-offer sample has 39 callbacks (36 valid first deliveries, 2 duplicates, 1 invalid), 27 completed and 9 rejected; both independent checker runs returned the same offered denominators. In this **one sample only**, urgent offered U = 2/9, routine timely start R(50 ms) = 20/27; these are debug outcomes and **must not** enter paper Results or be used to choose budgets.

The independent command reads the recorded JSONL back from disk and confirms the same counts/rates without trusting the pilot's stdout. One source-shape/source-horizon assertion passes. `py_compile` succeeds.

**Stage 5F follow-up source revision:** the initial Stage 5E source SHA-256 was `46ec51d562f7d60bcae767257dbf7a43043397211dce2196d5973490f3038e55`. The subsequent *Stage 5F preparation* accepts extra legitimate QoS1 callbacks while requiring independent per-ID source/offer reconciliation; the updated pilot script SHA-256 is `9dec57cae344250913eab406f259e387c9f1e0207b6a07971a49bc869b653b16`. The retained sample above came from the initial source version. Neither checksum is a publication-grade reproducibility guarantee.

**Checklist — 5E.3**
- [x] Execute six in-process tests and audit all of their produced lifecycles: **6/6 PASS**.
- [x] Retain a small auditable synthetic CPU-handler sample and independently recompute U and R from its JSONL: **PASS**.
- [x] Keep test outcomes explicitly non-generalizable and require new repeats, clocks and capture assertions before empirical claims.
- [ ] Execute a broker-backed MQTT run and audit its gateway-received/offered timeline; **NOT RUN**.
- [ ] Obtain an independently justified service-time/workload model and repeat calibrated conditions across independent seeds/machines.

## Step 5E.4 — Running the missing real MQTT integration gate

The optional integration uses **Eclipse Paho MQTT 2.x** callback API version 2 and an **external broker**. Use a broker bound to localhost for this **isolated lab**, not an internet-exposed unauthenticated broker. Follow [official Eclipse Paho Python API documentation](https://eclipse.dev/paho/clients/python/docs/) and [official Eclipse Mosquitto setup guidance](https://github.com/eclipse-mosquitto/mosquitto/blob/master/docker/generic/README.md). Check and record the actual versions; no broker is provisioned by this repository. Example commands after installing broker/client in a separate test environment:

```bash
# Start a locally configured Mosquitto broker bound to loopback, e.g. localhost:1883.
python3 -m pip install 'paho-mqtt>=2,<3'
python3 experiments/stage5e_gateway_pilot.py \
  --transport mqtt --host 127.0.0.1 --port 1883 \
  --shape burst --events 60 --queue-capacity 3 \
  --output stage5e_mqtt_lab.jsonl
python3 experiments/stage5d_lifecycle_audit.py stage5e_mqtt_lab.jsonl
```

The broker-backed mode uses a distinct run-scoped topic, subscribed receiver, separately connected publisher, QoS 1, **nonblocking scheduling of source publishes** (confirmation is checked after sending), and callback→validation→offer logs. It waits for the **expected demonstration callback attempts**, but network/broker/Paho retransmissions and publisher drift may differ from expectations. A timeout or incomplete receiver capture is **not a successful fully reconciled trace**; record and investigate mismatches. MQTT mode still uses the **same synthetic CPU handler**, so it is a transport-accounting test, **not real-service calibration**. Do not claim source-to-gateway nanosecond latency across clocks; this particular lab publisher/subscriber live in one Python process, which is a narrower setting than separate IoT devices.

Before treating Stage 5E as complete, capture at least one broker-backed run with a complete ledger and source→callback→offer reconciliation, run the independent audit, report subscriber/broker/client/library versions, inspect redeliveries/missing source IDs and quantify monitoring overhead. If actual enrichment is unavailable, ask the professor whether the explicitly synthetic-only conference story is acceptable.

**Checklist — 5E.4**
- [x] Provide executable optional Paho MQTT entry point and explicit local setup/verification instructions.
- [x] Keep source-publish acknowledgement outside the source interarrival loop so the burst is not intentionally ACK-paced.
- [ ] Execute actual MQTT broker + Paho integration and record versioned raw logs.
- [ ] Independently establish complete capture, source/received/valid-offered reconciliation and callback→offer offset distribution.
- [ ] Measure or justify handler-service and numeric D_u/epsilon/tau/gamma/K; record supervisor's measured-lab or synthetic-only decision.

## Overall Stage 5E decision / next step

- [x] Instrument a **working** one-worker two-class finite-K local gateway and validate post-dedup offered semantics.
- [x] Run and independently audit six synthetic CPU-handler **in-process** smoke conditions.
- [x] Retain one small redaction-free lab-only debug JSONL and reproducibility checksum.
- [ ] **Real broker-backed MQTT measurement:** **NOT COMPLETED** (broker/client unavailable here).
- [ ] **Realistic worker/source calibration:** **NOT COMPLETED** (PBKDF2 surrogate only).
- [ ] **Operational target sign-off and novelty clearance:** **NOT COMPLETED** (Stage 4B remains REVISE/NARROW).

**GO:** a broker-backed **Stage 5F real MQTT measurement pilot** in a separately provisioned local testbed, or a dated supervisor choice of synthetic-only claims.  
**NO-GO:** full Stage 6 preregistration/held-out evaluation, deployed security claims, scheduler improvement claims, or conference results from these debugging figures.
