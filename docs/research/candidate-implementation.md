# Candidate scheduler implementation

The [version 1 specification](candidate-spec.md) is implemented in `iot_alerts/scheduling.py` and uses the shared simulator engine. It remains an experimental heuristic. No performance improvement, novelty or deadline guarantee has been established.

## Run all research policies

```bash
python -m iot_alerts.foundation --policy research --count 1000 --queue-capacity 100 --deadlines-ms 100 500 2000 --traffic burst --service-distribution uniform --output results/research-smoke
```

`research` runs the existing four baselines and these four variants on the same immutable workload:

| CLI policy | Selection |
| --- | --- |
| adaptive_guarded | Occupancy-dependent aging with deadline guard |
| adaptive | Same aging without guard |
| fixed_guarded | Constant aging with the same guard and deadline tie-break |
| fixed_deadline | Constant aging with deadline tie-break, without guard |

`--policy all` retains the original four-policy meaning. Each new variant requires `--queue-capacity` greater than zero. Existing policies retain unbounded/zero-buffer support. Use one variant as `--policy adaptive_guarded` for a single run.

Parameters: `--aging-min-ms 100`, `--aging-max-ms 1000`, `--service-estimate-ms 10`; matched fixed variants use `--aging-ms 100`. Bounds are finite positive values with minimum no larger than maximum. Fixed variants use the fixed interval even when adaptive bounds differ. The four variants use deadline/arrival/id ties; legacy fixed aging retains its historical arrival/id ties.

Per-policy `config.json` records parameters, spec version and `guard_activations`, counting actual overrides rather than guard checks. The root manifest records shared settings; workload hashes identify the replay input. Changing `--service-estimate-ms` changes the guard estimate, independently of actual service cost. The selector never reads an alert's actual service duration. Selection uses a linear scan; no efficiency claim is made.

Replay the identical workload using:

```bash
python -m iot_alerts.foundation --policy research --trace-input results/research-smoke/workload.csv --queue-capacity 100 --output results/research-replay
```

Supply the same scheduling options when replaying nondefault runs. Replay restores arrivals, priorities, deadlines and actual service costs; it does not restore scheduler configuration automatically.

## Verification and next work

Tests cover promotion, occupancy, deterministic ties, guard thresholds and overdue behavior, missing deadlines, invalid parameters, service-cost independence, equivalence with matched fixed intervals, bounded accounting and completion/arrival ordering. CI compares generated and replay summaries for all eight policies and preserves the historical pilot regression.

Task 7 adds the registered experiment matrix, separated tuning/evaluation and reproducibility manifests described in the [design review](design-review.md). Smoke results are correctness checks, not paper evidence. The MQTT demo still supports only FIFO and strict priority.
