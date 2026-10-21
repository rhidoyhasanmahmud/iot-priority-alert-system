# Local controlled live smoke evidence

This archive is **engineering smoke evidence**, not a primary research experiment or proof of scheduler superiority. It records one local AMQTT 0.11.3 / Paho 2.1.0 validation: eight planned-trace policy runs, two overload checks and one broker-restart/resubscription/duplicate-cache check. Exact versions, source/plan/archive hashes and observed counts are indexed in [summary.json](summary.json).

[artifacts.tar.gz](artifacts.tar.gz) contains the complete successful registered smoke output, including raw evidence and captured sources. To inspect and independently verify it from the repository root:

```bash
mkdir -p results/reviewed-live-evidence
tar -xzf evidence/live-validation-smoke/artifacts.tar.gz -C results/reviewed-live-evidence
python -m iot_alerts.live_validation verify --output results/reviewed-live-evidence/live-validation-smoke
```

Read the extracted `runs/report.md`, `runs/checks.json` and `runs/publisher_timing.csv`. Native receiver counters measure attempts; reconciled metrics measure the known logical-event population from its first receiver receipt. Reconnect retries are deliberate application publishes after resubscription; forced MQTT retransmission/offline delivery is not tested. Results depend on host timing and must not be treated as a deterministic benchmark ranking.

During harness development, an earlier incomplete overload run exposed a publisher-disconnect/forwarding race after transport ACKs. The harness now keeps the publisher connected until receiver receipts reconcile. The archived run was made after that correction and passed raw-evidence verification. This is a development validation sample, not a selected positive research replicate.

The [controlled validation guide](../../docs/live-validation.md) documents reproduction, profiles and limitations. CI independently exercises Mosquitto and retains its own complete smoke output as an artifact. The 160-run live profile and full primary simulation experiments remain unexecuted.
