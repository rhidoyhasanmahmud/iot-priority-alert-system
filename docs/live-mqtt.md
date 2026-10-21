# Live scheduling and deduplication

Task 10 integrates all eight simulation policy selectors with a single live MQTT worker. The broker forwards messages to `lab/alerts`; application scheduling occurs after delivery. Functional smoke checks do not establish comparative performance or deadline guarantees. Controlled live validation is Task 11.

## Run locally

Install `requirements.txt` and start the existing `docker compose` broker as described in [getting started](getting-started.md). Then run:

```bash
python -m iot_alerts.mqtt_demo receive --policy adaptive_guarded --queue-capacity 100 --service-ms 20 --service-estimate-ms 20 --output results/live-adaptive
```

After `Ready`, publish in another terminal:

```bash
python -m iot_alerts.mqtt_demo publish --count 100 --deadlines-ms 100 500 2000 --duplicate-every 5
```

The publisher sends 100 distinct application events and 20 deliberate same-ID repeats. Broker acknowledgement confirms transport delivery, not admission or application completion. Check the receiver receipts and summary for the actual outcome. Use Ctrl+C once to stop intake and drain admitted events, or set `--duration-s 5` to stop intake five seconds after subscription readiness and then drain. Duration excludes connection setup and does not cap the drain period.

`--host` and `--port` select the broker, defaulting to localhost:1883. Existing two-field payloads remain accepted:

```json
{"id":"event-42","priority":0}
```

The extended schema is:

```json
{"source":"sensor-a","id":"event-42","priority":0,"deadline_ms":100}
```

Only these fields are accepted. Priority must be integer 0/1/2; IDs and sources are bounded nonblank UTF-8 strings. Missing source uses `legacy`. Deadline is optional, positive finite milliseconds; duplicate JSON fields, booleans as numeric metadata, unrepresentable deadlines and oversized payloads are rejected. Payloads are limited to 4,096 bytes for MQTT input.

## Scheduling and timing

| Option | Meaning |
| --- | --- |
| `--policy` | fifo, priority, aging, edf, adaptive_guarded, adaptive, fixed_guarded, fixed_deadline |
| `--queue-capacity` | Waiting slots, excluding the worker; default 10,000 |
| `--aging-ms` | Fixed-aging interval; default 100 ms |
| `--aging-min-ms`, `--aging-max-ms` | Adaptive bounds; defaults 100 and 1,000 ms |
| `--service-estimate-ms` | Guard estimate; default 20 ms, independent of actual processing cost |
| `--service-ms` | Synthetic non-preemptive processing delay; default 20 ms |
| `--dedup-capacity` | Recent completed ID cache size; default 10,000 |
| `--dedup-ttl-s` | Time from completion before recent ID expiry; default 60 seconds |

Zero waiting capacity is supported for the four original policies. Experimental aging requires positive capacity. If the worker is idle, one extra pending admission reserves its service slot; otherwise capacity counts waiting work only. Arriving work is rejected when full, with no eviction of admitted work.

The live queue uses the same internal selector as the simulator, including tie-breakers and the guard. Reception and worker dispatch are synchronized with one condition lock. Live callbacks can interleave with dispatch, so equal-time batches do not have simulated completion/admission ordering. Work already selected is not preempted.

Arrival uses a receiver-local monotonic timestamp at callback entry, before validation. Waiting ends at worker selection; completion time is captured after the synthetic processing delay and before logging the result. Latency excludes sensor, network and broker time. Deadlines are relative to callback entry. File output, callback scheduling and OS delays affect subsequent waiting, unlike a modeled-time simulation. Service estimates never inspect actual per-message processing time.

## Duplicate handling

The application identity is `(source, id)`, independent of MQTT packet ID or its DUP flag. Pending and active identities are pinned until completion. Recent completed identities are kept in a bounded cache; TTL starts at completion and repeated messages do not extend it. Oldest completions are evicted if the cache fills. Cache memory is bounded by configured recent capacity plus at most queue capacity + one active/reserved event.

An identical key with matching priority/deadline is a duplicate. Reusing it with different priority or deadline is an identity conflict. Both are recorded without another processing operation. Queue-full rejections are not cached: a later application retry may be admitted. Invalid inputs are not remembered. The publisher uses a fresh source namespace per invocation.

This is bounded, in-memory duplicate suppression. After TTL expiry, cache eviction or receiver restart, a previously completed ID may be processed again. State survives a connection reconnect within the same process. Broker redelivery and restart/reconnect stress have not yet been experimentally validated. No persistent or exactly-once application processing is claimed.

## Output and accounting

| File | Contents |
| --- | --- |
| `receipts.jsonl` | Every callback attempt: admitted, duplicate or rejected with reason |
| `completed.csv` | One row per completion with source/ID, priority, local arrival/start/finish, waiting, latency and deadline status |
| `config.json` | CLI options, measurement definition, Python version and scheduler/live source hashes |
| `summary.json` | Message counters, completed/admitted/unfinished counts, cache activity, guard overrides and drain status |

The receipt partition is: received messages = admitted + duplicates + conflicts + invalid + queue-full + closed rejections. These are **message attempts**, not a count of unique generated sensor events. Retrying a full-queue rejection can create more than one rejection attempt. Completion deadline counts refer to admitted work; they are not an end-to-end loss/deadline-failure rate over generated unique events. A successful drain has admitted = completed and unfinished = 0. Repeated completion after cache expiry is allowed by the stated cache contract.

Output directories must be fresh. On orderly shutdown, MQTT intake stops before admission closes; the worker drains and files flush before the final summary. A worker/callback failure makes the process fail and records errors or unfinished work. Forced termination has no drain/recovery guarantee. Priorities and deadlines are supplied by unauthenticated publishers in the existing localhost laboratory broker; this is not a trusted production alert service.

## Functional broker smoke

With a local Mosquitto executable and `requirements.txt` installed:

```bash
python tools/smoke_mqtt.py --output results/mqtt-smoke
```

The harness starts an isolated loopback broker on port 18883, tests each of the eight policies and stops only the broker it started. To reuse an isolated broker already running there, pass `--external-broker`. It verifies 20 distinct completions, ten suppressed repeats, two invalid payloads, one identity conflict and full drain for each policy. Repeats are deliberate application publishes, not forced MQTT retransmissions. CI has a separate Mosquitto smoke job. Local development smoke also supports an external broker; record its implementation when interpreting results.

Run `python -m unittest discover -s tests -v` for deterministic coverage of cache expiry/eviction, full-queue retry, selector parity, guard overrides, invalid payloads, concurrent duplicates and graceful close. Task 11 adds controlled live workloads, reconnect/overload checks and live evidence capture.
