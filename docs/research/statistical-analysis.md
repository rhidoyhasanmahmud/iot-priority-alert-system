# Statistical analysis and plots

Task 8 analyzes complete, verified held-out outputs from the [staged experiment runner](experiment-runner.md). The full primary study has not been run. Smoke artifacts demonstrate the analysis workflow only.

## Run

Core tables and the Markdown report use only the Python standard library:

```bash
python -m iot_alerts.analysis --study results/study-v1 --output results/study-v1-analysis
```

To also render scientific figures:

```bash
python -m pip install -r requirements-analysis.txt
python -m iot_alerts.analysis --study results/study-v1 --output results/study-v1-analysis-with-plots --plots
```

Use a new output directory for every analysis. It must be outside the input study directory. The tool preserves the input, refuses existing output and requires both complete tuning and evaluation artifacts. For a quick check, create and execute the smoke study described in the runner guide, then substitute `results/study-smoke` as the input.

## Registered comparisons

Differences always mean candidate minus reference. Priority 0 is urgent; priority 2 is routine.

| Comparison | Reference | Metric | Exploratory interval criterion |
| --- | --- | --- | --- |
| H1: routine waiting | Tuned matched fixed guarded aging | Per-run p95 waiting, ms | Upper limit < 0 |
| H2: urgent deadline failure | Strict priority | Late completions + deadline-bearing drops / deadline-bearing arrivals | Upper limit ≤ 0.01 |
| Routine drop check | Tuned matched fixed guarded aging | Dropped / generated | Upper limit ≤ 0 |
| Routine deadline-failure check | Tuned matched fixed guarded aging | Same failure definition, routine class | Upper limit ≤ 0 |

Each scenario uses the complete registered evaluation seed list. Compute one difference per paired seed, then bootstrap whole seed differences with replacement. Report their mean and the nearest-rank 2.5th/97.5th percentiles of bootstrap means. Primary studies use the registered 10,000 resamples; smoke uses 200. Bootstrap seeds derive deterministically from the registered base seed, scenario and comparison and are saved with the intervals.

The estimand for routine waiting is the mean difference of run-level p95 values. It is not the p95 of all pooled events. No alert-level resampling is used. Descriptive policy summaries are also means of run metrics, with defined/expected run counts. Any missing paired metric makes the comparison interval undefined; no available-case subset can meet a criterion.

Scenario intervals are **exploratory and unadjusted for multiple comparisons**. The stronger tradeoff flag requires all four marginal interval criteria, but is not a simultaneous confidence claim. No result is promoted into a universal improvement statement. A narrow completed-event waiting benefit must still disclose increased drops or deadline failures. Zero-width bootstrap intervals can occur, especially with small seed counts; they do not prove equality in the underlying population.

Budget sensitivity reuses each urgent-failure interval at 0, 0.005, 0.01 and 0.02. It does not retune a method or rerun held-out traffic. H3 mechanism tests and scheduler sensitivity/ablation are Task 9.

## Validation and provenance

Before analysis, verify the registered plan, archived simulation source and both phase checksum inventories. Validate all scenario/seed/policy/class combinations, frozen global settings, per-class counts and actual shared trace fingerprints. Cross-check the combined metrics against each run's summary and configuration. Incomplete grids, duplicate rows, wrong seeds, nonfinite metrics, mismatched inputs or altered artifacts are rejected.

A newer read-only analysis tool may process older recorded results. The original simulation source snapshot remains verified, and its identity is recorded separately from the current analysis source/Python identity. Strict current-source checks remain enabled for `study tune`, `study evaluate` and `study verify`; this separation does not permit continuing an experiment with changed simulator code. The verifier still recomputes the frozen tuning selection, so incompatible changes to selection semantics must be handled using the original version.

`manifest.json` records input registration/phase/selection hashes, simulation identity, analysis identity, the analysis rules and optional plotting-library versions. `analysis_source_snapshot/` preserves the exact analysis code and optional dependency specification. `complete.json` inventories the generated outputs by checksum. An interrupted analysis without that marker is incomplete.

## Outputs

| File | Contents |
| --- | --- |
| `comparisons.csv` / `.json` | Paired effects, bounds, valid/expected pairs, decisions and exact bootstrap seeds |
| `paired_differences.csv` / `.json` | Every seed-level input, difference, run path and shared workload fingerprint |
| `policy_summary.csv` / `.json` | Descriptive metrics for all eight methods and four class/overall groups |
| `scenario_assessments.csv` / `.json` | Waiting, urgency and loss decisions for every scenario, including failures |
| `budget_sensitivity.csv` / `.json` | Urgent-budget classifications without retuning |
| `scenarios.csv` / `.json` | Mapping of scenario IDs to actual conditions |
| `report.md` | Method, frozen settings, complete scenario table and interpretation limits |
| `plots/` | Four-panel paired-effect figures, grouped by traffic, service distribution and capacity |

Figures export as PNG, SVG and PDF. Horizontal segments show 95% marginal bootstrap intervals and points show mean paired differences. Urgent failure uses strict priority as reference; the other panels use matched fixed guarded aging. Tables store fractions; plots and the report convert failure/drop effects to **percentage points**. The urgent budget appears at one percentage point. Undefined intervals are labelled, not drawn as zero. Smoke plots carry a visible engineering-only label.

The [research review](design-review.md) remains the boundary for publication claims. These tools do not replace the missing closest-method comparison or establish novelty.
