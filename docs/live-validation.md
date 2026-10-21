# Controlled live validation

Task 11 adds registered wall-clock workload replay, overload checks, broker restart/resubscription checks and raw evidence verification. The local smoke profile has been exercised. The full 160-run live profile and primary simulation research study have not been executed. These results are descriptive engineering evidence, not a scheduling-superiority or publication claim.

## Register, run and verify

Install `requirements.txt` and a system Mosquitto executable. Run on a POSIX platform from the repository root:

```bash
python -m iot_alerts.live_validation plan --profile smoke --output results/live-validation-smoke
python -m iot_alerts.live_validation run --output results/live-validation-smoke
python -m iot_alerts.live_validation verify --output results/live-validation-smoke
```

Registration writes the protocol, planned traces, randomized policy execution order, source snapshot and checksums before any live outcomes. The runner owns an isolated loopback broker on port 18884; it refuses an occupied port and never stops another broker. `--port` is a registration option. Registration/phase output directories must be fresh; there is no resume support. Interrupted or failed phases retain their raw files without a completion marker.

The optional AMQTT development broker can be selected at registration:

```bash
python -m pip install -r requirements-live-test.txt
python -m iot_alerts.live_validation plan --broker amqtt --output results/live-validation-amqtt
```

Use the same run/verify commands for that output directory. AMQTT is an alternative test implementation, not a replacement for the Mosquitto deployment. CI runs Mosquitto. Broker/library versions and the host/Python/code identity are captured. A newer read-only verifier may inspect archived results; execution requires the registered source/Python identity.

## Profiles and replay

| Input | Smoke | Validation |
| --- | --- | --- |
| Seeds | 6101 | 6001–6005 |
| Base arrival rates | 200/s | 50/s, 150/s |
| Traffic | Event-index burst | Poisson and event-index burst |
| Alerts per trace | 40 | 200 |
| Waiting capacity | 5 | 50 |
| Policies | All eight | All eight |
| Workload runs | 8 | 160 |

Both profiles use 10 ms configured synthetic service, priority weights 1:2:7 and receiver-relative deadlines 100/500/2,000 ms. The candidate uses explicit development defaults: aging bounds 100/1,000 ms and a 10 ms service estimate. These are **not** settings selected by the pending primary research tuning. The matched fixed interval is 100 ms. The cache uses 10,000 completed IDs and a 60-second TTL. Every fifth event has one deliberate same-ID retry.

Register `--profile validation` under a new output directory to prepare the larger profile. Its four scenario conditions each have five seeds. Policy order is shuffled deterministically within every scenario/seed block and recorded before execution. All methods share the same saved planned trace, but real arrival traces cannot be identical because callbacks, transport and OS scheduling vary. There is no discarded warm-up. Runs are finite and drain after intake stops.

Replay schedules against absolute offsets and enqueues QoS 1 publishes without waiting for each ACK. It records planned time, call-entry time, publish-return time, ACK callback time and scheduling drift. Incremental attempt/ACK journals flush during publishing, preserving partial evidence when a run fails. Times are relative to that publisher connection's monotonic origin. Drift summaries expose late sends and catch-up bursts; the harness does not silently relabel the realized rate as the planned rate. Event-index burst compression also increases the overall offered rate.

A publisher transport ACK does not prove a subscriber receipt. The harness keeps the publisher connected until its attempts have been observed at the receiver, then stops intake and drains. If receipts are missing, it fails rather than reports complete logical-event loss accounting. This also avoids closing the publisher while a broker still has pending forwarding work.

## Functional checks

| Check | Procedure | Required outcome |
| --- | --- | --- |
| Strict-priority overload | 32 immediate events; one waiting slot; 50 ms service | At least one queue-full rejection, bounded waiting and full drain |
| Adaptive-guarded overload | Same stress input/settings | Same accounting/capacity requirements |
| Broker restart and dedup | Complete two events, stop/restart the owned broker, wait for a second successful SUBACK, retry both IDs and send one new ID | Three distinct completions, two duplicate suppressions, recorded disconnect/resubscription and full drain |

Exact overload drop counts depend on realized timing and are recorded rather than fixed as a performance target. The restart check preserves the receiver process and its in-memory cache. It tests deliberate application retries **after** reconnection, not forced MQTT packet retransmission, durable receiver state, offline publishing or crash recovery. Those distinctions remain part of the evidence boundary.

## Logical events versus message attempts

Raw receiver counters describe attempts. For the known planned population, the harness groups receipts by source/ID and reconciles every planned event with completion or never-admitted queue rejection. Duplicate completions, repeated admission, unexpected identities/metadata, missing events, inconsistent attempt counters and unfinished work fail validation.

Logical latency, waiting and deadlines start at the **first receiver receipt** for that ID. If the first attempt was rejected and a later attempt was admitted, the initial rejection remains part of the logical waiting/deadline window. The receiver's native completion row separately uses its admitted callback timestamp. A retry can therefore meet its native receiver deadline while failing the first-receipt logical deadline. No sensor/network end-to-end deadline is inferred.

Logical deadline failure includes late completed logical events plus never-admitted deadline-bearing events, divided by the complete known deadline-bearing population. Completed-event latency percentiles remain conditional on completions, with drops reported beside them. The metrics use the simulator's existing summary formulas on the reconciled receiver-time population; they are not modeled-time simulation results. Synthetic sleeps, file I/O, callbacks and host load affect the measurements.

## Evidence

| Path | Contents |
| --- | --- |
| `plan.json`, `registration.json` | Protocol, matrix/order, hashes and source/Python identity |
| `traces/` | One planned workload per scenario/seed |
| `source_snapshot/` | Registered application/selector/runner sources |
| `runs/started.json` | Actual execution environment and broker/library versions |
| `runs/<scenario>/<seed>/<policy>/publisher.csv/json` | Per-attempt planned/issued/return/ACK times and replay drift |
| Each run's `publisher/` (or reconnect `publisher-before/after/`) | Incremental attempt/ACK journals and connection clock origin |
| Each run's `receiver/` | Config, receipts, completion CSV, lifecycle JSONL and drain summary |
| Each run's `logical_summary.csv/json` | Reconciled logical-event metrics, including never-admitted loss |
| `runs/run_metrics.csv/json` | Combined per-run/per-class descriptive metrics |
| `runs/publisher_timing.csv/json` | Mean/p95/max scheduling drift per workload run |
| `runs/checks.json` | Overload and reconnect check outcomes |
| `runs/report.md` | Complete workload population/drop table and interpretation |
| `runs/complete.json` | Final inventory and SHA-256 checksums |

Verification checks raw inventories, planned trace links, actual receiver settings, receipt/completion identities and timing, publisher delivery records, per-run summaries, aggregated metrics and reconnect lifecycle events. It recomputes logical metrics rather than trusting the report. A completion marker means the registered engineering checks completed; it does not establish a statistically significant scheduling benefit.

CI uploads the complete smoke evidence as `live-validation-evidence`, including failed/incomplete outputs, with 30-day retention. For durable publication evidence, archive the reviewed code and complete results under the Task 12 reproducibility process. Do not use this small smoke profile as the final conference evaluation.
