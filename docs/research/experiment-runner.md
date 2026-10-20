# Staged experiment runner

Task 7 implements the [version 1 plan](../../configs/research-v1.json). It separates registration, tuning and held-out evaluation. It does not yet provide the comparative statistical analysis and plots planned for Task 8.

## Check the workflow quickly

Run from the repository root with Python 3.11+:

```bash
python -m iot_alerts.study plan --profile smoke --output results/study-smoke
python -m iot_alerts.study tune --output results/study-smoke
python -m iot_alerts.study evaluate --output results/study-smoke
python -m iot_alerts.study verify --output results/study-smoke
```

The smoke profile uses two scenarios, 200 alerts per trace, two tuning seeds and two different evaluation seeds. It executes 20 tuning and 32 evaluation runs. Its reduced grid and 200 bootstrap resamples are for engineering checks; output is explicitly labelled `engineering-smoke-only-not-paper-evidence`. It does not validate the research hypotheses.

## Register the primary study

```bash
python -m iot_alerts.study plan --profile primary --output results/study-v1
```

This only registers the plan and source; it does not generate the tuning or evaluation traces. The primary matrix is:

| Dimension | Values |
| --- | --- |
| Base rate | 50, 90, 120, 200 alerts/s |
| Traffic | Poisson, event-index burst |
| Actual service | Constant, uniform ±50%, exponential; mean parameter 10 ms |
| Waiting capacity | 100, 1,000 |
| Trace size | 10,000 alerts |
| Deadlines | High 100 ms, medium 500 ms, low 2,000 ms |
| Priority weights | 1:2:7 |
| Tuning seeds | 1001–1010 |
| Held-out seeds | 2001–2030 |

There are 48 scenarios. Every policy/parameter combination within a scenario and seed consumes the same saved workload. Equal seeds across scenarios deliberately preserve pairing; the tuning bootstrap resamples whole seeds across scenarios. Burst compression changes the overall offered rate; it is not a fixed-duration or constant-average-rate burst model.

## Tune, freeze, then evaluate

```bash
python -m iot_alerts.study tune --output results/study-v1
```

Tuning runs strict priority plus nine adaptive guarded and six matched fixed guarded settings: 7,680 simulations in total. `tune/selection.json` records every setting's score, feasibility and the one globally selected setting per method.

For each setting, average high deadline-failure differences versus strict priority equally across scenarios within each seed. Feasibility requires the upper 95% paired percentile-bootstrap limit to be at most 0.01, using 10,000 resamples and fixed bootstrap seed 9173. Among feasible settings, minimize the mean low-priority per-run p95 wait, then mean urgent failure, then the numeric parameter tuple. Undefined metrics make a setting ineligible. Selection is independent for the two tuned methods. The existing legacy fixed-aging baseline remains an untuned 100 ms reference.

A complete tuning phase freezes its selection and inventories every artifact by SHA-256. If either method has no feasible setting, selection status is `infeasible`; evaluation is blocked. Keep that result. Do not silently change the budget or choose a different setting using held-out outcomes.

Only after tuning completes:

```bash
python -m iot_alerts.study evaluate --output results/study-v1
python -m iot_alerts.study verify --output results/study-v1
```

Evaluation verifies the plan, source/Python identity, tuning inventory and selection recomputed from saved tuning summaries before generating any held-out trace. It runs eight policies with fixed global settings: FIFO, strict priority, legacy fixed aging, EDF, adaptive guarded, adaptive without guard, matched fixed guarded and matched fixed without guard. Unguarded controls inherit the corresponding guarded setting. There are 11,520 evaluation runs. No evaluation result feeds back into tuning.

Full tuning and evaluation process 192 million alert instances and retain raw per-event outputs. They are explicit separate commands; CI runs only the reduced profile. Registration prints the planned run counts. Runtime depends on queue length and the current linear-scan scheduler.

## Artifacts and reproduction

| Path under the study directory | Contents |
| --- | --- |
| `plan.json` | Exact matrix, grids, seeds and analysis rules |
| `registration.json` | Plan digest, matrix size, Python/platform, Git commit/status and source hashes |
| `source_snapshot/` | Exact simulator/runner Python sources and primary plan source |
| `tune/started.json`, `evaluate/started.json` | Phase provenance, settings and seed list written before simulation |
| `<phase>/sNNN/<seed>/workload.csv` | One reusable trace per paired scenario/seed |
| `<phase>/sNNN/<seed>/<setting>/` | Raw events, four class/overall summaries and resolved run configuration |
| `<phase>/run_metrics.csv`, `run_metrics.json` | Combined rows keyed by scenario, seed, setting and priority |
| `tune/selection.json` | All tuning scores and frozen global selections |
| `<phase>/complete.json` | Completion marker and file inventory with checksums |

Run configuration includes the canonical workload fingerprint, exact CSV checksum, relative input path, source hash, registered plan hash, parameters and selected-setting hash for evaluation. Source snapshots preserve dirty-worktree code as well as committed code; Git status records that distinction. Use a clean reviewed commit for publication evidence. To reconstruct the captured code, copy `source_snapshot/iot_alerts` and `source_snapshot/configs` into an isolated working directory and use the recorded Python version. Paths and timestamps may differ on reproduction; compare traces, resolved parameters and numeric summaries.

Output directories are exclusive: registration and phase commands refuse to overwrite existing results. There is no resume support in this version. An interrupted phase has no `complete.json`, cannot authorize evaluation, and must be retained as incomplete; restart under a new study directory. Finishing a phase is not evidence that its hypotheses succeeded. Checksums detect file changes; preserve the entire study directory alongside the reviewed code commit.

Task 8 will analyze paired held-out results, uncertainty, deadline/loss tradeoffs and scenario-specific failures. [Research review and claim boundaries](design-review.md) still apply.
