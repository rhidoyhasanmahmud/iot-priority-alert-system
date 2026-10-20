"""Analyze verified held-out studies with seed-paired, exploratory intervals."""
import argparse
import hashlib
import math
import random
import statistics
from collections import Counter
from pathlib import Path

from .experiment import write_csv
from .study import (ROOT, evaluation_settings, file_hash, load_registration, provenance,
                    read_json, scenarios, seal, verify_study, write_json)
from .workloads import load_trace, trace_fingerprint

COMPARISONS = (
    dict(id='routine_wait', target='adaptive_guarded', reference='fixed_guarded',
         priority=2, metric='p95_wait_ms', unit='ms'),
    dict(id='urgent_failure', target='adaptive_guarded', reference='priority',
         priority=0, metric='deadline_failure_fraction', unit='fraction'),
    dict(id='routine_drop', target='adaptive_guarded', reference='fixed_guarded',
         priority=2, metric='drop_fraction', unit='fraction'),
    dict(id='routine_failure', target='adaptive_guarded', reference='fixed_guarded',
         priority=2, metric='deadline_failure_fraction', unit='fraction'),
)
METRICS = ('generated', 'completed', 'dropped', 'drop_fraction', 'deadline_failure_fraction',
           'admitted_deadline_miss_fraction', 'mean_latency_ms', 'p95_latency_ms', 'p99_latency_ms',
           'max_latency_ms', 'mean_wait_ms', 'p95_wait_ms', 'p99_wait_ms', 'max_wait_ms', 'throughput_per_s')


def paired_interval(differences, resamples, seed):
    """Nearest-rank 95% percentile interval for mean paired seed differences.

    A missing pair invalidates inference for the registered scenario. Never
    substitute zero or silently analyze a selected subset of the seeds.
    """
    valid = [d for d in differences if d is not None]
    if any(isinstance(d, bool) or not isinstance(d, (int, float)) or not math.isfinite(d) for d in valid):
        raise ValueError('Paired differences must be finite numbers or None')
    if type(resamples) is not int or resamples < 1:
        raise ValueError('resamples must be a positive integer')
    result = dict(expected_pairs=len(differences), valid_pairs=len(valid), mean_difference=None,
                  ci_low=None, ci_high=None, interval_status='undefined_metric')
    if len(valid) != len(differences):
        return result
    if len(valid) < 2:
        return result | dict(interval_status='insufficient_pairs')
    rng = random.Random(seed)
    samples = sorted(statistics.fmean(rng.choices(valid, k=len(valid))) for _ in range(resamples))
    return result | dict(mean_difference=statistics.fmean(valid),
        ci_low=samples[math.ceil(.025*resamples)-1], ci_high=samples[math.ceil(.975*resamples)-1],
        interval_status='available')


def interval_decision(comparison, interval, budget):
    if interval['interval_status'] != 'available':
        return 'not_assessable'
    low, high = interval['ci_low'], interval['ci_high']
    if comparison == 'urgent_failure':
        return 'within_budget' if high <= budget else 'exceeds_budget' if low > budget else 'inconclusive'
    if comparison == 'routine_wait':
        return ('reduction_supported' if high < 0 else 'increase_supported' if low > 0
                else 'no_difference_observed' if low == high == 0 else 'inconclusive')
    return 'no_increase_supported' if high <= 0 else 'increase_supported' if low > 0 else 'inconclusive'


def validate_rows(plan, registration, selection, rows, study):
    """Check the full registered grid, class accounting, raw trace and run links."""
    settings = {s['policy']: s for s in evaluation_settings(plan, selection)}
    expected = {(s['id'], seed, policy, priority) for s in scenarios(plan)
                for seed in plan['evaluation_seeds'] for policy in settings for priority in ('all', 0, 1, 2)}
    lookup = {}
    selection_sha = file_hash(study/'tune/selection.json')
    for row in rows:
        if type(row['seed']) is not int or not (row['priority'] == 'all' or
                type(row['priority']) is int and row['priority'] in (0, 1, 2)):
            raise ValueError('Invalid seed or priority type')
        key = (row['scenario_id'], row['seed'], row['policy'], row['priority'])
        if key not in expected or key in lookup:
            raise ValueError('Unexpected or duplicate evaluation row')
        parameters = settings[row['policy']]
        expected_path = f'evaluate/{key[0]}/{key[1]}/{parameters["id"]}'
        if row['phase'] != 'evaluate' or row['setting_id'] != parameters['id'] or row['run_path'] != expected_path:
            raise ValueError('Evaluation identity does not match frozen settings')
        for metric in METRICS:
            value = row[metric]
            if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value)):
                raise ValueError(f'Non-finite or nonnumeric evaluation metric: {metric}')
        for metric in ('generated', 'admitted', 'completed', 'dropped', 'unfinished'):
            if type(row[metric]) is not int or row[metric] < 0:
                raise ValueError('Invalid event count')
        if (row['completed'] + row['dropped'] != row['generated'] or row['unfinished'] != 0
                or row['admitted'] != row['completed']):
            raise ValueError('Invalid drained-run accounting')
        lookup[key] = row
    if set(lookup) != expected:
        raise ValueError('Missing registered evaluation rows; no partial-grid analysis')
    for scenario in scenarios(plan):
        for seed in plan['evaluation_seeds']:
            trace = study/'evaluate'/scenario['id']/str(seed)/'workload.csv'
            events = load_trace(trace)
            if len(events) != plan['count']:
                raise ValueError('Trace event count does not match plan')
            counts, fingerprint = Counter(event.priority for event in events), trace_fingerprint(events)
            trace_sha = file_hash(trace)
            for policy, parameters in settings.items():
                run = [lookup[(scenario['id'], seed, policy, priority)] for priority in ('all', 0, 1, 2)]
                if any(row['workload_sha256'] != fingerprint for row in run):
                    raise ValueError('Paired workload fingerprint mismatch')
                if run[0]['generated'] != plan['count'] or any(row['generated'] != counts[row['priority']] for row in run[1:]):
                    raise ValueError('Per-class population does not match input trace')
                if any(sum(row[field] for row in run[1:]) != run[0][field] for field in ('completed', 'dropped')):
                    raise ValueError('Class accounting does not match overall summary')
                directory = study/run[0]['run_path']
                config = read_json(directory/'config.json')
                expected_config = dict(plan_sha256=registration['plan_sha256'], scenario=scenario,
                    source_sha256=registration['provenance']['source']['sha256'], selection_sha256=selection_sha,
                    workload_sha256=fingerprint, trace_file_sha256=trace_sha,
                    resolved_aging_config=dict(minimum_s=parameters['minimum_s'], maximum_s=parameters['maximum_s'],
                                               service_estimate_s=plan['service_estimate_s']),
                    fixed_aging_interval_s=parameters['fixed_interval_s'])
                if any(config.get(name) != value for name, value in expected_config.items()):
                    raise ValueError('Run manifest differs from registered input or settings')
                summaries = read_json(directory/'summary.json')
                if len(summaries) != 4 or {r['priority'] for r in summaries} != {'all', 0, 1, 2}:
                    raise ValueError('Invalid per-run summary classes')
                for summary in summaries:
                    indexed = lookup[(scenario['id'], seed, policy, summary['priority'])]
                    if any(indexed.get(name) != value for name, value in summary.items()):
                        raise ValueError('Combined metrics differ from per-run summaries')
    return lookup


def summarize_policies(plan, rows):
    """Descriptive means of run metrics; never a pooled event-level percentile."""
    groups = {}
    for row in rows:
        key = (row['scenario_id'], row['policy'], row['priority'])
        groups.setdefault(key, []).append(row)
    result = []
    for (scenario, policy, priority), group in groups.items():
        for metric in METRICS:
            values = [r[metric] for r in group if r[metric] is not None]
            result.append(dict(scenario_id=scenario, policy=policy, priority=priority, metric=metric,
                expected_runs=len(plan['evaluation_seeds']), defined_runs=len(values),
                mean_of_run_metric=statistics.fmean(values) if values else None,
                min_run_metric=min(values) if values else None, max_run_metric=max(values) if values else None,
                descriptive_only=True, complete=len(values) == len(plan['evaluation_seeds'])))
    return result


def compare(plan, lookup):
    comparisons, pairs, assessments, sensitivity = [], [], [], []
    for scenario in scenarios(plan):
        decisions = {}
        for definition in COMPARISONS:
            differences = []
            for seed in plan['evaluation_seeds']:
                target = lookup[(scenario['id'], seed, definition['target'], definition['priority'])]
                reference = lookup[(scenario['id'], seed, definition['reference'], definition['priority'])]
                a, b = target[definition['metric']], reference[definition['metric']]
                difference = None if a is None or b is None else a-b
                differences.append(difference)
                pairs.append(dict(scenario_id=scenario['id'], seed=seed, comparison=definition['id'],
                    target=definition['target'], reference=definition['reference'], metric=definition['metric'],
                    target_value=a, reference_value=b, difference=difference,
                    target_run=target['run_path'], reference_run=reference['run_path'],
                    workload_sha256=target['workload_sha256']))
            # Stable across iteration order; store the exact seed with every interval.
            token = f'{plan["analysis"]["bootstrap_seed"]}:{scenario["id"]}:{definition["id"]}'
            bootstrap_seed = int.from_bytes(hashlib.sha256(token.encode()).digest()[:8], 'big')
            interval = paired_interval(differences, plan['analysis']['bootstrap_resamples'], bootstrap_seed)
            decision = interval_decision(definition['id'], interval, plan['urgent_failure_budget'])
            decisions[definition['id']] = decision
            comparisons.append(dict(scenario_id=scenario['id'], rate=scenario['rate'], traffic=scenario['traffic'],
                service_distribution=scenario['service_distribution'], queue_capacity=scenario['queue_capacity'],
                comparison=definition['id'], target=definition['target'], reference=definition['reference'],
                priority=definition['priority'], metric=definition['metric'], unit=definition['unit'],
                **interval, decision=decision, bootstrap_seed=bootstrap_seed,
                bootstrap_resamples=plan['analysis']['bootstrap_resamples'], confidence=.95,
                inference='exploratory_unadjusted', evidence_label=plan['evidence_label']))
            if definition['id'] == 'urgent_failure':
                for budget in plan['analysis']['budget_sensitivity']:
                    sensitivity.append(dict(scenario_id=scenario['id'], budget=budget,
                        decision=interval_decision('urgent_failure', interval, budget),
                        ci_low=interval['ci_low'], ci_high=interval['ci_high'],
                        retuned=False, inference='exploratory_unadjusted'))
        supported = (decisions['routine_wait'] == 'reduction_supported' and
                     decisions['urgent_failure'] == 'within_budget' and
                     decisions['routine_drop'] == decisions['routine_failure'] == 'no_increase_supported')
        assessments.append(dict(scenario_id=scenario['id'], **decisions,
            all_interval_criteria_met=supported,
            interpretation=('engineering_only_no_research_conclusion' if plan['profile'] == 'smoke' else
                            'exploratory_tradeoff_supported' if supported else 'tradeoff_not_established'),
            inference='exploratory_unadjusted'))
    return comparisons, pairs, assessments, sensitivity


def report(plan, registration, selection, comparisons, assessments):
    def display(row):
        if row['mean_difference'] is None:
            return 'undefined'
        scale = 1 if row['unit'] == 'ms' else 100
        return f'{row["mean_difference"]*scale:.6g} [{row["ci_low"]*scale:.6g}, {row["ci_high"]*scale:.6g}]'
    indexed = {(r['scenario_id'], r['comparison']): r for r in comparisons}
    smoke = plan['profile'] == 'smoke'
    lines = ['# Held-out study analysis', '',
        '**Engineering smoke only — not publication evidence.**' if smoke else '**Exploratory scenario-level analysis; no multiplicity adjustment.**', '',
        'All registered scenarios and seeds are retained. Differences are candidate minus reference; '
        'negative waiting differences favor the candidate. Failure/drop differences below are percentage points.', '',
        f'Registered plan SHA-256: `{registration["plan_sha256"]}`.',
        f'Profile: `{plan["profile"]}`; scenarios: {len(scenarios(plan))}; seeds per scenario: {len(plan["evaluation_seeds"])}.', '',
        '## Method', '',
        f'Mean paired seed differences with nearest-rank 95% percentile-bootstrap intervals '
        f'({plan["analysis"]["bootstrap_resamples"]:,} resamples). Seeds, rather than individual alerts, are the replicate units. '
        'The routine metric is the mean of per-run p95 waits, not a pooled percentile. '
        'Missing metrics invalidate the entire comparison interval; no seed is silently removed.', '',
        'H1 requires the routine-wait interval upper limit below zero versus matched fixed guarded aging. '
        f'H2 requires the urgent-failure upper limit at most {plan["urgent_failure_budget"]*100:g} percentage point(s) versus strict priority. '
        'Both routine loss upper limits must be at most zero versus matched fixed guarded aging for the stronger tradeoff interpretation. '
        'These are separate marginal intervals, not a simultaneous confidence region. '
        'Scenario flags are exploratory and do not establish a joint or universal claim.', '',
        '## Frozen settings', '',
        f'- Adaptive guarded: `{selection["selected"]["adaptive_guarded"]}`',
        f'- Matched fixed guarded: `{selection["selected"]["fixed_guarded"]}`', '',
        '## All scenarios', '',
        '| Scenario | Low p95 wait Δ ms [95% CI] | High failure Δ pp [95% CI] | Low drop Δ pp [95% CI] | Low failure Δ pp [95% CI] | Interpretation |',
        '| --- | --- | --- | --- | --- | --- |']
    for assessment in assessments:
        sid = assessment['scenario_id']
        values = [display(indexed[(sid, definition['id'])]) for definition in COMPARISONS]
        lines.append('| '+ ' | '.join([sid, *values, assessment['interpretation']])+' |')
    lines += ['', 'See `scenarios.csv` for each scenario definition; `comparisons.csv` contains exact values, '
        'sample counts and decisions. `policy_summary.csv` describes selected latency, waiting and loss metrics for all eight methods and all classes. '
        'A descriptive mean based on incomplete runs is explicitly marked incomplete and cannot authorize an inference.', '',
        '## Interpretation limits', '',
        'The intervals estimate uncertainty across the registered seeds. '
        'No correction for multiple scenarios or endpoints is applied. Budget sensitivity reuses the same intervals '
        'without retuning. Small seed counts and empirical bootstrap distributions can produce degenerate intervals; '
        'a zero-width interval does not prove exact equality of the underlying systems. '
        'Report increased drops or routine deadline failures even when completed-event waiting improves. '
        'Finite synthetic full-drain experiments do not demonstrate steady-state stability, starvation freedom, '
        'hard deadlines or network latency. H3 mechanism/ablation analysis is reserved for Task 9.', '']
    return '\n'.join(lines)


def run(study, output, *, plots=False):
    study, output = Path(study).resolve(), Path(output).resolve()
    if output.is_relative_to(study):
        raise ValueError('Analysis output must be outside the read-only study directory')
    if output.exists():
        raise FileExistsError(f'Analysis output already exists: {output}')
    plotter = None
    if plots:
        from .analysis_plots import render
        plotter = render
    print('Verifying registered study, source snapshot and raw artifact inventories...', flush=True)
    # Analysis may use newer read-only tools; simulation source checks stay strict for tune/evaluate.
    verify_study(study, require_current_source=False)
    plan, registration = load_registration(study, require_current_source=False)
    selection = read_json(study/'tune/selection.json')
    rows = read_json(study/'evaluate/run_metrics.json')
    print('Validating paired traces, frozen configurations and summary cross-links...', flush=True)
    lookup = validate_rows(plan, registration, selection, rows, study)
    output.mkdir(parents=True, exist_ok=False)
    manifest = dict(analysis_schema_version=1, input_study=str(study), profile=plan['profile'],
        evidence_label=plan['evidence_label'], plan_sha256=registration['plan_sha256'],
        input_registration_sha256=file_hash(study/'registration.json'),
        input_evaluation_marker_sha256=file_hash(study/'evaluate/complete.json'),
        input_tuning_marker_sha256=file_hash(study/'tune/complete.json'),
        selection_sha256=file_hash(study/'tune/selection.json'),
        simulation_source=registration['provenance']['source'], analysis_provenance=provenance(),
        plots_requested=plots, comparisons=list(COMPARISONS), analysis_rules=plan['analysis'],
        multiplicity='none; scenario-level exploratory intervals only',
        bootstrap_seed_rule='first 8 bytes of SHA256(base_seed:scenario_id:comparison), big endian')
    for name in manifest['analysis_provenance']['source']['files']:
        target = output/'analysis_source_snapshot'/name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT/name).read_bytes())
    dependencies = ROOT/'requirements-analysis.txt'
    (output/'analysis_source_snapshot/requirements-analysis.txt').write_bytes(dependencies.read_bytes())
    manifest['plot_requirements_sha256'] = file_hash(dependencies)
    write_json(output/'manifest.json', manifest)
    print('Computing paired seed intervals...', flush=True)
    comparisons, pairs, assessments, sensitivity = compare(plan, lookup)
    for name, data in [('comparisons', comparisons), ('paired_differences', pairs),
                       ('scenario_assessments', assessments), ('budget_sensitivity', sensitivity),
                       ('policy_summary', summarize_policies(plan, rows)), ('scenarios', scenarios(plan))]:
        write_csv(output/f'{name}.csv', data)
        write_json(output/f'{name}.json', data)
    (output/'report.md').write_text(report(plan, registration, selection, comparisons, assessments))
    if plotter is not None:
        manifest['plot_dependencies'] = plotter(comparisons, plan, output/'plots')
        write_json(output/'manifest.json', manifest)
    seal(output, dict(analysis_schema_version=1, plan_sha256=registration['plan_sha256'],
                      profile=plan['profile'], scenario_count=len(assessments), interval_count=len(comparisons)))
    return assessments


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--study', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--plots', action='store_true', help='Requires requirements-analysis.txt')
    args = parser.parse_args()
    try:
        assessments = run(args.study, args.output, plots=args.plots)
        print(f'Analyzed {len(assessments)} scenarios; output: {args.output}')
    except (ValueError, OSError, KeyError, TypeError, ImportError) as error:
        parser.error(str(error))


if __name__ == '__main__':
    main()
