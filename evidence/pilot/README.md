# Baseline pilot results

## Reproduce

```bash
python -m unittest discover -s tests -v
python -m iot_alerts.pilot --output results/pilot
```

Ten paired seeds, 1000 generated events per seed, three rates and three policies produce 90 policy runs and 90000 completed event records. Each policy sees the same input trace for a given seed and rate. All arrivals stop after 1000 events and every queue drains. No events are dropped.

The model uses an unbounded application queue, constant 10 ms service, Poisson arrivals and a 10/20/70 class mix. Fixed aging promotes one class per 100 ms of waiting; equal effective priorities use arrival order. This aging parameter was selected as a simple illustrative baseline, not optimized. No adaptive policy is implemented or evaluated.

## Descriptive results

Values are averages of ten run-level p95 latency estimates, in milliseconds. They are not pooled p95 estimates.

| Rate per second | Policy | High p95 | Low p95 |
| --- | --- | --- | --- |
| 50 | fifo | 29.43 | 30.53 |
| 50 | priority | 19.35 | 35.51 |
| 50 | aging | 19.35 | 35.51 |
| 90 | fifo | 116.41 | 118.68 |
| 90 | priority | 21.11 | 160.49 |
| 90 | aging | 28.61 | 140.37 |
| 120 | fifo | 1568.02 | 1604.50 |
| 120 | priority | 22.67 | 1921.62 |
| 120 | aging | 1568.02 | 1604.50 |

## Paired uncertainty at 90 events per second

Differences are aging minus strict priority. Each paired difference uses the same seed. Percentile bootstrap 95% intervals resample ten run pairs with replacement, using 10000 resamples and bootstrap seed 2026. These intervals are exploratory with only ten independent runs.

| Outcome | Mean paired difference in ms | 95% bootstrap interval in ms |
| --- | --- | --- |
| High p95 latency | 7.50 | [0.22, 20.94] |
| Low p95 latency | -20.13 | [-28.23, -11.78] |

## Interpretation

At 50 events/s, fixed aging matches strict priority on the reported class metrics: waiting rarely reaches the promotion interval. At 90 events/s, aging lowers routine p95 latency but increases urgent p95 latency. At 120 events/s, strict priority preserves low urgent latency while aging loses much of that benefit. This is a failure mode to investigate, not evidence that an adaptive policy will solve it.

The 120 events/s arrival rate exceeds nominal capacity. These are finite overload workloads followed by drain, not steady-state performance. Fixed aging is not a proven starvation solution. With about 100 high-priority events per run, high-class p99 estimates are unstable; the raw values are preserved but do not support tail-improvement claims.

## Evidence and limits

`run_metrics.csv` holds every run/class measurement; `aggregate.csv` holds descriptive averages; `config.json` records parameters, Python version, base commit and SHA256 identifiers for the exact pilot code. The base commit predates the additions; the source hashes identify the code actually executed. The final PR commit identifies the complete evidence bundle.

`example-rate120-seed1-priority.csv.gz` contains one complete per-event raw run. The reproduction command generates all 90 raw CSVs locally under results/pilot; those larger files are not checked in. The bootstrap script is versioned in `iot_alerts/pilot_analysis.py`.

This pilot validates a scheduling tradeoff under a simplified model. It does not validate the candidate policy, bounded queue admission, live MQTT performance, real enrichment costs, security effectiveness or a unique research contribution.
