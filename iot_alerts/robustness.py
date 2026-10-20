"""Read-only factorial ablation and separately registered sensitivity experiments."""
import argparse
from collections import Counter
import hashlib
import math
import os
from pathlib import Path

from .analysis import COMPARISONS, METRICS, paired_interval, validate_rows
from .experiment import write_csv
from .foundation import export_run
from .scheduling import AgingConfig
from .simulator import run_simulation
from .study import (ROOT, digest, file_hash, load_registration, provenance, read_json, scenarios,
                    seal, source_identity, verify, verify_study, workload_options, write_json)
from .workloads import generate_workload, load_trace, save_trace, trace_fingerprint

PROTOCOL = ROOT/'configs/robustness-v1.json'
ENGINE_FILES = ('simulator.py', 'scheduling.py', 'workloads.py', 'metrics.py', 'foundation.py', 'experiment.py')
ABLATIONS = {
    'occupancy_guarded': {'adaptive_guarded': 1, 'fixed_guarded': -1},
    'occupancy_unguarded': {'adaptive': 1, 'fixed_deadline': -1},
    'guard_adaptive': {'adaptive_guarded': 1, 'adaptive': -1},
    'guard_fixed': {'fixed_guarded': 1, 'fixed_deadline': -1},
    'interaction': {'adaptive_guarded': 1, 'adaptive': -1, 'fixed_guarded': -1, 'fixed_deadline': 1},
}


def outside(parent, output):
    if output.resolve().is_relative_to(parent.resolve()):
        raise ValueError('Output must be outside the read-only input directory')
    if output.exists():
        raise FileExistsError(f'Output already exists: {output}')


def capture_sources(output, identity):
    for name in identity['files']:
        target = output/'source_snapshot'/name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT/name).read_bytes())


def load_parent(parent):
    verify_study(parent, require_current_source=False)
    plan, registration = load_registration(parent, require_current_source=False)
    selection = read_json(parent/'tune/selection.json')
    rows = read_json(parent/'evaluate/run_metrics.json')
    lookup = validate_rows(plan, registration, selection, rows, parent)
    return plan, registration, selection, lookup


def parent_hashes(parent):
    return {name: file_hash(parent/name) for name in
            ('plan.json', 'registration.json', 'tune/selection.json', 'tune/complete.json', 'evaluate/complete.json')}


def sensitivity_settings(selection, service_estimate, protocol):
    chosen = selection['selected']['adaptive_guarded']
    settings = [dict(id='baseline', minimum_s=chosen['minimum_s'], maximum_s=chosen['maximum_s'],
                     service_estimate_s=service_estimate)]
    for name, factors in (('interval', protocol['interval_factors']), ('estimate', protocol['estimate_factors'])):
        for factor in factors:
            if factor == 1:
                continue
            settings.append(dict(id=f'{name}-{factor:g}',
                minimum_s=chosen['minimum_s']*(factor if name == 'interval' else 1),
                maximum_s=chosen['maximum_s']*(factor if name == 'interval' else 1),
                service_estimate_s=service_estimate*(factor if name == 'estimate' else 1)))
    for item in settings:
        AgingConfig(**{k: v for k, v in item.items() if k != 'id'})
    if len({s['id'] for s in settings}) != len(settings):
        raise ValueError('Duplicate sensitivity settings')
    return settings


def register(parent, output):
    parent, output = Path(parent).resolve(), Path(output).resolve()
    outside(parent, output)
    plan, registration, selection, _ = load_parent(parent)
    current = source_identity()
    for name in ENGINE_FILES:
        key = 'iot_alerts/'+name
        if current['files'][key] != registration['provenance']['source']['files'][key]:
            raise ValueError('Sensitivity engine must match the parent simulation')
    protocol = read_json(PROTOCOL)
    seeds = protocol['smoke_seeds' if plan['profile'] == 'smoke' else 'primary_seeds']
    excluded = set(plan['diagnostic_seeds'] + plan['tuning_seeds'] + plan['evaluation_seeds'])
    if (len(seeds) < 2 or any(type(seed) is not int for seed in seeds)
            or len(set(seeds)) != len(seeds) or set(seeds) & excluded):
        raise ValueError('Sensitivity seeds must be unique and disjoint from every parent split')
    settings = sensitivity_settings(selection, plan['service_estimate_s'], protocol)
    frozen = dict(schema_version=1, parent=os.path.relpath(parent, output), parent_hashes=parent_hashes(parent),
        profile=plan['profile'], evidence_label=plan['evidence_label'], protocol=protocol,
        seeds=seeds, settings=settings, parent_plan=plan, parent_plan_sha256=registration['plan_sha256'],
        fixed_interval_s=selection['selected']['adaptive_guarded']['fixed_interval_s'])
    output.mkdir(parents=True)
    write_json(output/'plan.json', frozen)
    write_json(output/'registration.json', dict(plan_sha256=digest(frozen), provenance=provenance(),
        run_count=len(scenarios(plan))*len(seeds)*len(settings)))
    capture_sources(output, current)
    return frozen


def load_sensitivity(output, *, executing=False):
    frozen, registration = read_json(output/'plan.json'), read_json(output/'registration.json')
    if digest(frozen) != registration['plan_sha256']:
        raise ValueError('Sensitivity plan checksum mismatch')
    source = registration['provenance']['source']
    for name, expected in source['files'].items():
        if file_hash(output/'source_snapshot'/name) != expected:
            raise ValueError('Sensitivity source snapshot checksum mismatch')
    if executing and source_identity() != source:
        raise ValueError('Source/Python changed after sensitivity registration')
    parent = (output/frozen['parent']).resolve()
    if parent_hashes(parent) != frozen['parent_hashes']:
        raise ValueError('Parent study changed after sensitivity registration')
    plan, original, _, _ = load_parent(parent)
    for name in ENGINE_FILES:
        key = 'iot_alerts/'+name
        if source['files'][key] != original['provenance']['source']['files'][key]:
            raise ValueError('Sensitivity engine differs from the parent simulation')
    if plan != frozen['parent_plan'] or original['plan_sha256'] != frozen['parent_plan_sha256']:
        raise ValueError('Parent plan mismatch')
    return frozen, registration


def execute(output):
    output = Path(output).resolve()
    frozen, registration = load_sensitivity(output, executing=True)
    plan, directory = frozen['parent_plan'], output/'runs'
    directory.mkdir(exist_ok=False)
    write_json(directory/'started.json', dict(plan_sha256=registration['plan_sha256'], provenance=provenance()))
    rows = []
    for scenario in scenarios(plan):
        for seed in frozen['seeds']:
            pair = directory/scenario['id']/str(seed)
            pair.mkdir(parents=True)
            events = generate_workload(plan['count'], scenario['rate'], seed, **workload_options(plan, scenario))
            save_trace(pair/'workload.csv', events)
            fingerprint, csv_sha = trace_fingerprint(events), file_hash(pair/'workload.csv')
            counts = Counter(event.priority for event in events)
            for item in frozen['settings']:
                config = AgingConfig(**{k: v for k, v in item.items() if k != 'id'})
                result = run_simulation(events, 'adaptive_guarded', service_time=plan['service_time_s'],
                    queue_capacity=scenario['queue_capacity'], aging_interval=frozen['fixed_interval_s'], aging_config=config)
                identity = dict(scenario_id=scenario['id'], seed=seed, setting_id=item['id'],
                                workload_sha256=fingerprint, run_path=f'runs/{scenario["id"]}/{seed}/{item["id"]}')
                summaries = export_run(result, output/identity['run_path'], identity | dict(scenario=scenario,
                    sensitivity_plan_sha256=registration['plan_sha256'], resolved_aging_config=vars(config),
                    source_sha256=registration['provenance']['source']['sha256'],
                    trace_path='../workload.csv', trace_file_sha256=csv_sha,
                    fixed_aging_interval_s=frozen['fixed_interval_s'], evidence_label=frozen['evidence_label']))
                rows.extend(identity | row for row in summaries)
            print(f'Sensitivity: {scenario["id"]}, seed {seed}: {len(frozen["settings"])} runs', flush=True)
    write_json(directory/'run_metrics.json', rows)
    write_csv(directory/'run_metrics.csv', rows)
    seal(directory, dict(plan_sha256=registration['plan_sha256'], run_count=len(rows)//4))
    return len(rows)//4


def sensitivity_rows(output, frozen, registration):
    marker = verify(output/'runs')
    if marker['plan_sha256'] != registration['plan_sha256'] or marker['run_count'] != registration['run_count']:
        raise ValueError('Sensitivity completion marker mismatch')
    rows = read_json(output/'runs/run_metrics.json')
    plan = frozen['parent_plan']
    expected = {(s['id'], seed, item['id'], priority) for s in scenarios(plan)
                for seed in frozen['seeds'] for item in frozen['settings'] for priority in ('all', 0, 1, 2)}
    lookup = {}
    for row in rows:
        if type(row['seed']) is not int or not (row['priority'] == 'all' or
                type(row['priority']) is int and row['priority'] in (0, 1, 2)):
            raise ValueError('Invalid sensitivity row types')
        key = (row['scenario_id'], row['seed'], row['setting_id'], row['priority'])
        if key not in expected or key in lookup or row['policy'] != 'adaptive_guarded':
            raise ValueError('Unexpected or duplicate sensitivity row')
        for metric in METRICS:
            value = row[metric]
            if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value)):
                raise ValueError('Sensitivity metrics must be finite numbers or None')
        lookup[key] = row
    if set(lookup) != expected:
        raise ValueError('Missing sensitivity rows')
    for scenario in scenarios(plan):
        for seed in frozen['seeds']:
            pair = output/'runs'/scenario['id']/str(seed)
            events = load_trace(pair/'workload.csv')
            fingerprint, csv_sha = trace_fingerprint(events), file_hash(pair/'workload.csv')
            counts = Counter(event.priority for event in events)
            if len(events) != plan['count']:
                raise ValueError('Sensitivity trace count mismatch')
            for item in frozen['settings']:
                config = read_json(pair/item['id']/'config.json')
                if (config['resolved_aging_config'] != {k: v for k, v in item.items() if k != 'id'}
                        or config['sensitivity_plan_sha256'] != registration['plan_sha256']
                        or config['workload_sha256'] != fingerprint or config['trace_file_sha256'] != csv_sha
                        or config['source_sha256'] != registration['provenance']['source']['sha256']
                        or config['fixed_aging_interval_s'] != frozen['fixed_interval_s']
                        or config['scenario'] != scenario):
                    raise ValueError('Sensitivity run configuration mismatch')
                summaries = read_json(pair/item['id']/'summary.json')
                if len(summaries) != 4 or {r['priority'] for r in summaries} != {'all', 0, 1, 2}:
                    raise ValueError('Invalid sensitivity summary classes')
                for summary in summaries:
                    row = lookup[(scenario['id'], seed, item['id'], summary['priority'])]
                    expected_path = f'runs/{scenario["id"]}/{seed}/{item["id"]}'
                    expected_count = len(events) if summary['priority'] == 'all' else counts[summary['priority']]
                    if (row['run_path'] != expected_path or row['generated'] != expected_count or
                            row['workload_sha256'] != fingerprint or any(row.get(k) != v for k, v in summary.items())):
                        raise ValueError('Sensitivity summary or paired trace mismatch')
    return lookup


def effect_tables(plan, seeds, lookup, effects):
    intervals, pairs = [], []
    for scenario in scenarios(plan):
        for effect, terms in effects.items():
            for metric in COMPARISONS:
                differences = []
                for seed in seeds:
                    inputs = {name: lookup[(scenario['id'], seed, name, metric['priority'])] for name in terms}
                    if len({r['workload_sha256'] for r in inputs.values()}) != 1:
                        raise ValueError('Ablation effects require paired input traces')
                    values = [r[metric['metric']] for r in inputs.values()]
                    value = None if any(v is None for v in values) else sum(terms[name]*r[metric['metric']] for name, r in inputs.items())
                    differences.append(value)
                    pairs.append(dict(scenario_id=scenario['id'], seed=seed, effect=effect,
                        metric_id=metric['id'], difference=value, workload_sha256=next(iter(inputs.values()))['workload_sha256'],
                        terms=terms, run_paths={name: row['run_path'] for name, row in inputs.items()}))
                token = f'{plan["analysis"]["bootstrap_seed"]}:robustness:{scenario["id"]}:{effect}:{metric["id"]}'
                bootstrap_seed = int.from_bytes(hashlib.sha256(token.encode()).digest()[:8], 'big')
                interval = paired_interval(differences, plan['analysis']['bootstrap_resamples'], bootstrap_seed)
                direction = ('not_assessable' if interval['interval_status'] != 'available' else
                             'negative' if interval['ci_high'] < 0 else 'positive' if interval['ci_low'] > 0 else
                             'zero_observed' if interval['ci_low'] == interval['ci_high'] == 0 else 'inconclusive')
                intervals.append(dict(scenario_id=scenario['id'], effect=effect, metric_id=metric['id'],
                    metric=metric['metric'], unit=metric['unit'], priority=metric['priority'], **interval,
                    bootstrap_seed=bootstrap_seed, bootstrap_resamples=plan['analysis']['bootstrap_resamples'],
                    direction=direction, inference='secondary_exploratory_unadjusted', evidence_label=plan['evidence_label']))
        print(f'Effects: {scenario["id"]}', flush=True)
    return intervals, pairs


def analyze(input_path, output, *, kind='ablation', plots=False):
    input_path, output = Path(input_path).resolve(), Path(output).resolve()
    outside(input_path, output)
    if kind == 'ablation':
        plan, registration, _, lookup = load_parent(input_path)
        effects, seeds = ABLATIONS, plan['evaluation_seeds']
        input_hashes = parent_hashes(input_path)
    elif kind == 'sensitivity':
        frozen, registration = load_sensitivity(input_path)
        outside((input_path/frozen['parent']).resolve(), output)
        plan, seeds = frozen['parent_plan'], frozen['seeds']
        lookup = sensitivity_rows(input_path, frozen, registration)
        effects = {item['id']: {item['id']: 1, 'baseline': -1}
                   for item in frozen['settings'] if item['id'] != 'baseline'}
        input_hashes = dict(registration=file_hash(input_path/'registration.json'),
                            plan=file_hash(input_path/'plan.json'), runs=file_hash(input_path/'runs/complete.json'))
    else:
        raise ValueError('Unknown analysis kind')
    renderer = None
    if plots:
        from .robustness_plots import render
        renderer = render
    output.mkdir(parents=True)
    identity = provenance()
    manifest = dict(schema_version=1, kind=kind, input=str(input_path), input_hashes=input_hashes,
        profile=plan['profile'], evidence_label=plan['evidence_label'], effects=effects, seeds=seeds,
        analysis_rules=plan['analysis'], provenance=identity, no_retuning=True,
        interpretation='secondary exploratory effects, not causal or simultaneous guarantees')
    write_json(output/'manifest.json', manifest)
    capture_sources(output, identity['source'])
    intervals, pairs = effect_tables(plan, seeds, lookup, effects)
    for name, data in [('effect_intervals', intervals), ('paired_effects', pairs), ('scenarios', scenarios(plan))]:
        write_json(output/f'{name}.json', data)
        write_csv(output/f'{name}.csv', data)
    lines = [f'# {kind.title()} analysis', '',
        '**Engineering smoke only — not publication evidence.**' if plan['profile'] == 'smoke' else
        '**Secondary exploratory analysis — no multiplicity adjustment.**', '',
        'Terms and their signs are frozen in `manifest.json`. Guard effects are guarded minus unguarded; '
        'negative urgent failure favors the guard. Occupancy effects are adaptive minus matched fixed. '
        'Interaction is (adaptive guarded − adaptive unguarded) − (fixed guarded − fixed unguarded). '
        'Sensitivity effects are changed parameter minus frozen baseline, with no retuning. '
        'A negative waiting effect alone does not demonstrate a better scheduler; inspect loss effects too.', '',
        'Intervals resample whole paired seeds, not individual events. Missing inputs invalidate the interval. '
        'These are fixed-parameter component contrasts, not optimal-policy comparisons or causal guarantees. '
        'A zero-width empirical interval does not prove population equality. All scenarios are retained.', '',
        '| Scenario | Effect | Metric | Mean [95% CI] | Unit | Direction |', '| --- | --- | --- | --- | --- | --- |']
    for row in intervals:
        scale = 100 if row['unit'] == 'fraction' else 1
        display = ('undefined' if row['mean_difference'] is None else
                   f'{row["mean_difference"]*scale:.6g} [{row["ci_low"]*scale:.6g}, {row["ci_high"]*scale:.6g}]')
        unit = 'percentage points' if scale == 100 else row['unit']
        lines.append(f'| {row["scenario_id"]} | {row["effect"]} | {row["metric_id"]} | {display} | {unit} | {row["direction"]} |')
    (output/'report.md').write_text('\n'.join(lines)+'\n')
    if renderer is not None:
        dependencies = ROOT/'requirements-analysis.txt'
        (output/'source_snapshot/requirements-analysis.txt').write_bytes(dependencies.read_bytes())
        manifest['plot_requirements_sha256'] = file_hash(dependencies)
        manifest['plot_dependencies'] = renderer(intervals, plan, kind, output/'plots')
        write_json(output/'manifest.json', manifest)
    seal(output, dict(kind=kind, profile=plan['profile'], interval_count=len(intervals)))
    return len(intervals)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=('ablation', 'plan', 'run', 'sensitivity'))
    parser.add_argument('--input', type=Path, help='Completed parent study, or sensitivity registration for sensitivity analysis')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--plots', action='store_true')
    args = parser.parse_args()
    try:
        if args.stage == 'run':
            print(f'Completed {execute(args.output)} sensitivity runs')
        elif args.input is None:
            parser.error('--input is required for this stage')
        elif args.stage == 'plan':
            frozen = register(args.input, args.output)
            print(f'Registered {len(frozen["settings"])} settings and {len(frozen["seeds"])} independent seeds')
        else:
            print(f'Produced {analyze(args.input, args.output, kind=args.stage, plots=args.plots)} intervals')
    except (ValueError, OSError, KeyError, TypeError, ImportError) as error:
        parser.error(str(error))


if __name__ == '__main__':
    main()
