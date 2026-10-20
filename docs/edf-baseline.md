# EDF baseline and fair comparison

Earliest deadline first (EDF) selects the waiting event with the earliest absolute deadline: arrival plus relative deadline. Processing remains non-preemptive. EDF changes selection only; it uses the same worker, capacity, admission rule and accounting as FIFO, strict priority and fixed aging.

## Run EDF

```bash
python -m iot_alerts.foundation --policy edf --queue-capacity 10 --deadlines-ms 100 500 2000 --output results/edf
```

An alert with a short relative budget does not necessarily have the earliest absolute deadline. For example, an arrival at 0.25 s with a 2 s budget has deadline 2.25 s; an arrival at 0.75 s with a 1.75 s budget has deadline 2.5 s. EDF serves the former first when both wait.

## Scheduling rules

- Known deadlines sort before missing deadlines. Missing deadlines are treated as infinity for selection only; they stay missing in results.
- Equal absolute deadlines use arrival order, then event ID for simultaneous arrivals.
- If every deadline is missing, EDF behaves as FIFO.
- An overdue event remains eligible and is processed; it is not silently removed.
- An urgent arrival cannot interrupt active work or evict a waiting event from a full queue.
- Severity does not break EDF ties. It remains available for per-class reporting.

This is an empirical non-preemptive baseline. It makes no claim of universal optimality or guaranteed deadline satisfaction.

## Compare all four policies

```bash
python -m iot_alerts.foundation --policy all --queue-capacity 10 --deadlines-ms 100 500 2000 --aging-ms 100 --output results/baselines
```

The workload is generated once, then replayed through all policies. Each receives identical event IDs, arrivals, original priorities, deadlines and service times. Capacity and processing settings are identical. Different processing orders may legitimately change admission outcomes when service times vary.

The output root contains `workload.csv`, combined `summary.csv`, combined `summary.json` and `config.json`. Each policy subdirectory contains its own events, summaries and configuration. A SHA256 fingerprint of the canonical input trace is stored in every manifest, allowing you to verify that the compared workloads match. It identifies input data, not the entire code or environment.

Fixed aging is configurable with `--aging-ms`; this setting is recorded even in a comparison run. The existing default of 100 ms is preserved. Use separate output directories for different scenarios so old run files are not mistaken for new evidence.

No deadlines are supplied by default. Set an explicit common or per-priority budget when studying EDF; otherwise its FIFO-like behavior is expected. These CLI budgets remain illustrative and require application justification. Normal/burst traffic and variable service costs are now available; see [workload generation and replay](workload-generator.md). Batch experiment matrices remain a later task.

The original experiment CLI and historical pilot stay compatible. EDF is available in the shared simulator and foundation CLI, not the live MQTT demo. See [metric definitions](deadline-and-loss-metrics.md) when interpreting drops and deadlines.
