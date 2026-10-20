# Sensitivity and ablation

Task 9 provides secondary exploratory component contrasts and parameter sensitivity. Full primary experiments and full secondary experiments have not been executed. Smoke runs verify orchestration only. These tools do not establish novelty or replace the closest-method comparison.

## Ablation on completed held-out results

```bash
python -m iot_alerts.robustness ablation --input results/study-v1 --output results/ablation-v1
```

Add `--plots` after installing `requirements-analysis.txt` to export PNG, SVG and PDF. The command verifies a complete parent study, shared traces, frozen parameters and all summary/configuration links. It reads existing held-out results and never reruns or retunes a method.

Let AG be adaptive guarded aging, A adaptive unguarded, FG matched fixed guarded, and F matched fixed unguarded. A inherits AG's tuned aging parameters, and F inherits FG's tuned interval. Their deadline tie-breaker is identical.

| Effect | Paired seed contrast | Interpretation |
| --- | --- | --- |
| Occupancy with guard | AG − FG | Adaptive versus matched fixed when the guard is enabled |
| Occupancy without guard | A − F | Adaptive versus matched fixed without the guard |
| Guard with adaptation | AG − A | Guard effect at the frozen adaptive setting |
| Guard with fixed aging | FG − F | Guard effect at the frozen fixed setting |
| Interaction | (AG − A) − (FG − F) | Difference between the two guard effects |

Each contrast is evaluated for routine p95 waiting, urgent deadline failure, routine drops and routine deadline failure. Negative urgent failure in a guard contrast supports a benefit in that scenario; waiting and loss costs must still be reported. Negative interaction means the guard's failure reduction is larger under adaptation, for that endpoint. There is no single favorable sign across all metrics.

These are fixed-parameter component contrasts. The unguarded controls are not independently retuned, so their results do not establish comparisons against the best possible unguarded policies. Independently tuned adaptive and fixed rules also differ in their aging schedules. The interaction is an empirical difference of differences, not a causal or optimality guarantee.

## Register fresh sensitivity experiments

Start from a completed parent study with frozen feasible selections:

```bash
python -m iot_alerts.robustness plan --input results/study-v1 --output results/sensitivity-v1
```

Registration freezes the [secondary protocol](../../configs/robustness-v1.json), the parent plan/selection hashes, exact global settings, new seeds and source snapshot before generating secondary traffic. The simulation engine must match the parent's engine files. No method is retuned and no evaluated parameter is automatically selected as a replacement.

| Setting | Aging bounds | Guard service estimate |
| --- | --- | --- |
| Baseline | Frozen AG minimum and maximum | Parent estimate, normally 10 ms |
| `interval-0.5` | Both bounds × 0.5 | Unchanged |
| `interval-2` | Both bounds × 2 | Unchanged |
| `estimate-0.5` | Unchanged | Estimate × 0.5, normally 5 ms |
| `estimate-2` | Unchanged | Estimate × 2, normally 20 ms |

This is a one-factor-at-a-time design: aging bounds scale together, preserving their ratio, or the estimate alone changes. It does not independently identify minimum/maximum effects or test their full factorial interactions. Actual service times, traffic, class mix and deadlines stay identical within a scenario/seed pair; changing an estimate does not change actual processing cost.

The primary extension uses seeds **5001–5030**, disjoint from all parent diagnostic, tuning and evaluation seeds. It reuses the parent's 48 scenario definitions and trace size, producing 7,200 runs over five settings. All five settings share one newly generated saved workload per scenario/seed. The smoke extension uses seeds 5101–5102, two parent smoke scenarios and 20 runs. Smoke output stays visibly labelled as engineering-only evidence.

Execute the registered extension, then analyze it separately:

```bash
python -m iot_alerts.robustness run --output results/sensitivity-v1
python -m iot_alerts.robustness sensitivity --input results/sensitivity-v1 --output results/sensitivity-v1-analysis --plots
```

Sensitivity effects are each modified setting minus the frozen baseline on the new seeds. They describe parameter robustness rather than confirm primary hypotheses. Promoting a setting based on these outcomes would require a new protocol and fresh evaluation data. Historical primary results and selections remain unchanged.

## Statistics and artifacts

Both analyses resample whole paired seed contrasts and report mean effects with nearest-rank 95% percentile-bootstrap intervals. Primary plans use 10,000 resamples; smoke uses 200. Missing component metrics invalidate that interval. All scenarios and unfavorable directions are retained. No multiplicity correction is applied: intervals are secondary and exploratory, not simultaneous confidence statements. Zero-width bootstrap intervals do not prove population equality.

The analysis output contains `effect_intervals.csv/json`, `paired_effects.csv/json`, `scenarios.csv/json`, `report.md`, source snapshots and a provenance manifest. Exact terms, signs, bootstrap seeds and run links are retained; paired input details are easiest to consume from JSON. Plots show one effect per facet with all four endpoints. Tables store failure/drop differences as fractions; reports and plots convert them to percentage points.

Sensitivity registration stores `plan.json`, `registration.json` and the source snapshot. Execution writes `runs/<scenario>/<seed>/workload.csv`, one raw-event/summary/configuration directory per setting, combined run metrics and a checksum completion inventory. Analysis verifies that inventory plus trace fingerprints, class populations and the resolved settings. Changed plans, sources during execution, parent artifacts, partial phases, overlapping seeds and overwritten output are rejected. Newer read-only analysis tools may inspect archived outputs, while execution requires its registered code/Python identity.

The parent location is stored relative to the sensitivity registration, so preserve their relative layout when archiving or moving both studies. Outputs must remain outside the read-only parent/input directories. Existing results are never overwritten. There is no resume support; preserve incomplete runs and restart under a new registration. Run the same commands against a completed smoke study for a quick workflow check.
