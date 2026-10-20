# Deadline and loss metrics

The foundation runner now writes an overall summary and one summary for each original priority class. Read deadline and loss results alongside latency: a low completed-event latency can hide work rejected at admission.

## Run it

```bash
python -m iot_alerts.foundation --policy priority --queue-capacity 10 --deadlines-ms 100 500 2000 --output results/metrics
```

`--deadlines-ms` assigns relative budgets to high, medium and low priority. Use `--deadline-ms 100` instead for one common budget, or omit both options when deadlines are unknown. These options cannot be combined. The example budgets are illustrative, not validated application requirements.

The output directory contains:

| File | Contents |
| --- | --- |
| `events.csv` | Every generated event, completion or drop, timestamps, original priority and deadline status |
| `summary.csv` | Overall and high/medium/low summary rows |
| `summary.json` | The same summaries with numeric types and explicit nulls |
| `config.json` | Run settings, basic counts, schema version and denominator definitions |

A deadline is met when completion time is less than or equal to arrival plus relative deadline. A later completion is a miss. Times use simulation floating-point seconds; comparison is strict without an implicit tolerance. A drop with a deadline is a deadline failure, but is not a late completion. No event expires or changes scheduling because of these metrics.

## Counts and denominators

| Metric | Definition |
| --- | --- |
| `generated` | All events in the group, including drops |
| `admitted` | Events accepted for processing |
| `completed` | Admitted events that finished |
| `dropped` | Events rejected because the queue was full |
| `unfinished` | Zero for this engine, which drains every admitted event |
| `drop_fraction` | Dropped / generated |
| `deadline_generated` | Generated events with a configured deadline |
| `deadline_admitted` | Admitted events with a configured deadline |
| `deadline_completed` | Completed events with a configured deadline |
| `deadline_dropped` | Dropped events with a configured deadline |
| `without_deadline` | Generated events without a deadline |
| `deadline_met` | Deadline-bearing completions on time |
| `deadline_missed_completed` | Deadline-bearing completions that finished late |
| `deadline_failed` | Late deadline-bearing completions + deadline-bearing drops |
| `admitted_deadline_miss_fraction` | Late completions / admitted events with deadlines |
| `deadline_failure_fraction` | Deadline failures / all generated events with deadlines |

Every admitted event drains, so admitted equals completed. Generated equals completed plus dropped. Deadline met plus deadline failed equals deadline generated. Missing deadlines are reported, not invented; deadline fractions use only events whose deadlines are known. Compare those fractions only when deadline coverage and workload are comparable. The overall drop fraction always includes all generated events.

Example: ten deadline-bearing arrivals, two drops and three late completions give an admitted miss fraction of 3/8 and a deadline failure fraction of 5/10. Reporting only 3/8 would hide the two drops.

## Latency and waiting

The summary reports sample count, mean, p95, p99 and maximum for both response latency and waiting time, in milliseconds. Response latency is finish minus arrival. Waiting is start minus arrival. Both distributions include completed events only. Dropped events have no fabricated latency.

Percentiles use nearest rank: sort the samples and choose position ceil(p × sample count), counting from one. Small samples can make p99 unstable; inspect the sample counts before making tail claims. Overall percentiles are computed from all completions, not averaged from class percentiles.

All groups share one observation window, from the first generated arrival to the last completion or rejection. It includes idle gaps and the final drain. Throughput is each group's completions divided by that common duration. Class throughputs add to overall throughput; fractions and percentiles generally do not add.

## Empty and missing values

A zero denominator or empty distribution gives JSON `null` and an empty CSV cell. An absent priority class is still exported with zero counts and undefined rates/latencies. No NaN or Infinity is emitted for normal runs. Empty API runs are supported; the CLI requires at least one generated event.

Per-event `deadline_status` is `met`, `missed`, `dropped` or `not_set`. The last value means no configured deadline, including for dropped events without deadlines. Combine it with `status` to distinguish completion from admission loss.

## Scope and evidence

These summaries describe fully drained finite runs, not steady-state throughput. Observation cutoffs, service failures, deadline-based expiry and live MQTT integration are not implemented. An incomplete or duplicate event partition is rejected instead of silently producing a summary. The original experiment CLI, legacy summary schema and historical pilot evidence remain unchanged.
