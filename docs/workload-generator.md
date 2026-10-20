# Workload generation and replay

Generate controlled synthetic event streams, save the exact input and replay it through any baseline. These workloads describe an experiment, not measured device behavior.

## Normal traffic

```bash
python -m iot_alerts.foundation --policy all --traffic poisson --count 2000 --rate 90 --priority-weights 1 2 7 --deadlines-ms 100 500 2000 --output results/normal
```

Interarrival gaps follow an exponential distribution, producing Poisson arrivals at the configured expected rate. Priority weights are high, medium and low. They are normalized probabilities, not exact finite-run quotas. Weights 1/2/7 mean expected proportions of 10/20/70 percent; 0/1/0 produces only medium events.

The default constant service time is 10 ms. Default Poisson arrival times and priority draws remain identical to the original seeded generator, preserving the historical pilot. Every new input event records its explicit service time.

## Controlled burst

```bash
python -m iot_alerts.foundation --policy all --traffic burst --count 2000 --rate 90 --burst-start 0.4 --burst-end 0.6 --burst-multiplier 5 --queue-capacity 100 --deadlines-ms 100 500 2000 --output results/burst
```

Burst boundaries are fractions of event indices, not seconds. For N events, gaps from index floor(N × start) up to, but not including, ceil(N × end) use rate × multiplier. Other gaps use the base rate. For N=2000, the example accelerates gaps for events 800 through 1199.

For a fixed seed, the same random draws are used for Poisson and burst traffic. Selected gaps are divided by the multiplier. Event count, priorities and service samples remain comparable, but elapsed arrival duration becomes shorter and overall offered rate increases. This does not preserve the same wall-clock duration or represent a general nonhomogeneous Poisson process. A finite overload run still drains after arrivals stop.

## Variable processing cost

Choose the service distribution independently from traffic shape:

| Option | Per-event service time |
| --- | --- |
| `--service-distribution constant` | Exactly `--service-ms` |
| `--service-distribution uniform` | Uniform between mean × (1 − spread) and mean × (1 + spread) |
| `--service-distribution exponential` | Exponential with expected mean `--service-ms` |

Use `--uniform-spread 0.5` for the default uniform range of 5–15 ms when the mean is 10 ms. Spread must be in [0,1); service times must remain positive and finite. Uniform and exponential parameters specify expected means; realized sample means are not artificially normalized. The exponential distribution is unbounded, so some events can take much longer than the mean.

Service draws use a separate seeded random stream. Changing the service distribution does not change arrival times or priority assignments. Changing priority weights also preserves arrival draws for the same count, rate, traffic and seed.

```bash
python -m iot_alerts.foundation --policy all --traffic burst --service-distribution uniform --uniform-spread 0.5 --priority-weights 3 2 5 --deadlines-ms 100 500 2000 --queue-capacity 20 --output results/variable
```

## Save and replay

Single-policy and comparison runs both save `workload.csv`. It contains exactly these columns: `id`, `arrival`, `priority`, `deadline_s`, `service_time_s`. Times are in seconds; a missing deadline is an empty cell. Service time must be explicit for replay.

```bash
python -m iot_alerts.foundation --policy all --trace-input results/variable/workload.csv --queue-capacity 20 --output results/replayed
```

Replay uses the saved arrivals, priorities, deadlines and service times. Generation settings such as count, rate, seed, priority weights and service distribution are not applied. Scheduler settings still apply: choose the same policy, queue capacity and aging interval to reproduce outcomes. CLI validation still checks shared numeric options. Saved manifests mark `input_mode`, `generation_settings_applied`, `input_event_count` and the input fingerprint, so unused generation arguments cannot be mistaken for trace provenance.

A trace is generated or loaded once per comparison. All schedulers receive the same immutable events. With identical engine settings, replay yields identical per-event outcomes and summaries even if the CLI seed differs. Store each run in a fresh output directory.

## Validation and limits

The loader rejects missing/extra columns, duplicate IDs, invalid priorities, non-finite or negative arrivals, invalid service/deadline values and empty traces. Row errors include a CSV line number. Input order is preserved in the saved trace and fingerprint; the engine uses its documented arrival/ID ordering for admission.

The SHA256 fingerprint normalizes numeric time fields to floats, so equal values such as 2 and 2.0 match after CSV roundtrip. The generator is versioned as 1 in new run manifests. Pin code and Python versions for reproducibility; a seed alone is not a permanent cross-version input specification. Replay is the preferred way to preserve an exact experiment input.

Real datasets, multiple burst windows, exact class quotas, priority-dependent processing costs and batch experiment matrices are future extensions. See [EDF comparison](edf-baseline.md) and [metric definitions](deadline-and-loss-metrics.md) for result interpretation.
