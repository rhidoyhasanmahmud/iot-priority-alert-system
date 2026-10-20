"""Staged, reproducible tuning and held-out evaluation. No work at import time."""
import argparse
import hashlib
import itertools
import json
import math
import platform
import random
import statistics
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from .experiment import write_csv
from .foundation import export_run
from .scheduling import AgingConfig
from .simulator import run_simulation
from .workloads import GENERATOR_VERSION, generate_workload, save_trace, trace_fingerprint

ROOT = Path(__file__).resolve().parents[1]
PLAN_SOURCE = ROOT/'configs/research-v1.json'


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def file_hash(path):
    sha = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024*1024), b''):
            sha.update(chunk)
    return sha.hexdigest()


def write_json(path, value):
    path = Path(path)
    # Completion markers are only visible after their entire payload is written.
    temporary = path.with_suffix(path.suffix+'.tmp')
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+'\n')
    temporary.replace(path)


def read_json(path):
    return json.loads(Path(path).read_text())


def source_identity():
    paths = sorted((ROOT/'iot_alerts').glob('*.py')) + [PLAN_SOURCE]
    hashes = {str(p.relative_to(ROOT)): file_hash(p) for p in paths}
    return dict(files=hashes, sha256=digest(hashes), python=platform.python_version(),
                implementation=platform.python_implementation(), generator_version=GENERATOR_VERSION)


def provenance():
    def git(*args):
        try:
            return subprocess.check_output(['git', *args], cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
        except (OSError, subprocess.CalledProcessError):
            return None
    return dict(created_utc=datetime.now(timezone.utc).isoformat(), git_commit=git('rev-parse', 'HEAD'),
                git_status=git('status', '--porcelain'), platform=platform.platform(), source=source_identity())


def make_plan(profile='primary'):
    plan = read_json(PLAN_SOURCE)
    if profile == 'smoke':
        plan.update(profile='smoke', evidence_label='engineering-smoke-only-not-paper-evidence',
                    count=200, rates=[50, 70], traffic=['burst'], service_distributions=['uniform'],
                    capacities=[10], tuning_seeds=[3101, 3102], evaluation_seeds=[4101, 4102],
                    adaptive_minimum_grid_s=[1., 2.], adaptive_maximum_grid_s=[2.], fixed_grid_s=[1., 2.])
        plan['analysis']['bootstrap_resamples'] = 200
    elif profile != 'primary':
        raise ValueError('Unknown study profile')
    validate_plan(plan)
    return plan


def validate_plan(plan):
    sets = []
    for name in ('tuning_seeds', 'evaluation_seeds', 'diagnostic_seeds'):
        seeds = plan[name]
        if not seeds or any(type(seed) is not int for seed in seeds) or len(set(seeds)) != len(seeds):
            raise ValueError(f'{name} must contain unique integer seeds')
        sets.append(set(seeds))
    if any(a & b for a, b in itertools.combinations(sets, 2)):
        raise ValueError('Diagnostic, tuning and evaluation seeds must be disjoint')
    for name in ('rates', 'traffic', 'service_distributions', 'capacities',
                 'adaptive_minimum_grid_s', 'adaptive_maximum_grid_s', 'fixed_grid_s'):
        values = plan[name]
        if not values or len(set(values)) != len(values):
            raise ValueError(f'{name} must be nonempty and unique')
    if any(type(cap) is not int or cap < 1 for cap in plan['capacities']):
        raise ValueError('Research capacities must be positive integers')
    if not 0 <= plan['urgent_failure_budget'] <= 1:
        raise ValueError('Invalid failure budget')
    if type(plan['analysis']['bootstrap_resamples']) is not int or plan['analysis']['bootstrap_resamples'] < 1:
        raise ValueError('Invalid bootstrap resample count')
    if plan['analysis']['confidence'] != .95:
        raise ValueError('Version 1 requires 95% confidence')
    # Exercise existing workload/config validators before creating any output.
    for scenario in scenarios(plan):
        generate_workload(1, scenario['rate'], 0, **workload_options(plan, scenario))
    if type(plan['count']) is not int or plan['count'] < 1:
        raise ValueError('count must be a positive integer')
    for setting in tuning_settings(plan):
        AgingConfig(setting['minimum_s'], setting['maximum_s'], plan['service_estimate_s'])


def scenarios(plan):
    return [dict(id=f's{index:03d}', rate=rate, traffic=traffic,
                 service_distribution=service, queue_capacity=capacity)
            for index, (rate, traffic, service, capacity) in enumerate(itertools.product(
                plan['rates'], plan['traffic'], plan['service_distributions'], plan['capacities']))]


def workload_options(plan, scenario):
    return dict(traffic=scenario['traffic'], service_distribution=scenario['service_distribution'],
                service_time=plan['service_time_s'], priority_weights=plan['priority_weights'],
                deadlines=plan['deadlines_s'], uniform_spread=plan['uniform_spread'],
                burst_start=plan['burst_start'], burst_end=plan['burst_end'],
                burst_multiplier=plan['burst_multiplier'])


def setting(policy, minimum=.1, maximum=1., fixed=.1):
    return dict(id=f'{policy}-{minimum:g}-{maximum:g}-{fixed:g}', policy=policy,
                minimum_s=minimum, maximum_s=maximum, fixed_interval_s=fixed)


def tuning_settings(plan):
    adaptive = [setting('adaptive_guarded', lo, hi) for lo, hi in itertools.product(
        plan['adaptive_minimum_grid_s'], plan['adaptive_maximum_grid_s']) if lo <= hi]
    fixed = [setting('fixed_guarded', value, value, value) for value in plan['fixed_grid_s']]
    if not adaptive or not fixed:
        raise ValueError('Both tuning grids must contain valid settings')
    return adaptive + fixed


def inventory(directory):
    return {str(path.relative_to(directory)): file_hash(path) for path in sorted(directory.rglob('*'))
            if path.is_file() and path.name != 'complete.json'}


def seal(directory, details):
    write_json(directory/'complete.json', details | dict(files=inventory(directory)))


def verify(directory):
    marker = read_json(directory/'complete.json')
    if marker['files'] != inventory(directory):
        raise ValueError(f'Artifact checksum mismatch: {directory}')
    return marker


def initialize(output, profile='primary'):
    plan = make_plan(profile)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    manifest = dict(plan_sha256=digest(plan), provenance=provenance(), scenarios=scenarios(plan),
                    tuning_runs=len(scenarios(plan))*len(plan['tuning_seeds'])*(1+len(tuning_settings(plan))),
                    evaluation_runs=len(scenarios(plan))*len(plan['evaluation_seeds'])*8)
    for name in manifest['provenance']['source']['files']:
        target = output/'source_snapshot'/name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT/name).read_bytes())
    write_json(output/'plan.json', plan)
    write_json(output/'registration.json', manifest)
    return manifest


def load_registration(output):
    plan, registration = read_json(output/'plan.json'), read_json(output/'registration.json')
    if digest(plan) != registration['plan_sha256']:
        raise ValueError('Frozen plan checksum mismatch')
    for name, expected in registration['provenance']['source']['files'].items():
        if file_hash(output/'source_snapshot'/name) != expected:
            raise ValueError('Registered source snapshot checksum mismatch')
    if source_identity() != registration['provenance']['source']:
        raise ValueError('Source or Python version changed since registration; use the registered environment')
    validate_plan(plan)
    return plan, registration


def paired_upper(values, resamples, seed):
    """Tuning only: percentile bootstrap over paired seed-level differences."""
    rng = random.Random(seed)
    ordered = sorted(statistics.fmean(rng.choices(values, k=len(values))) for _ in range(resamples))
    return ordered[math.ceil(.975*resamples)-1]


def select_parameters(plan, rows):
    """Equal scenario weight within seed; retain all tuning scores, including failures."""
    lookup = {(r['setting_id'], r['scenario_id'], r['seed'], r['priority']): r for r in rows}
    scores, selected = [], {}
    for candidate in tuning_settings(plan):
        differences, waits, failures = [], [], []
        eligible = True
        for seed in plan['tuning_seeds']:
            seed_diffs, seed_waits, seed_failures = [], [], []
            for scenario in scenarios(plan):
                high = lookup[(candidate['id'], scenario['id'], seed, 0)]
                low = lookup[(candidate['id'], scenario['id'], seed, 2)]
                strict = lookup[('priority', scenario['id'], seed, 0)]
                metrics = (high['deadline_failure_fraction'], low['p95_wait_ms'], strict['deadline_failure_fraction'])
                if any(value is None for value in metrics):
                    eligible = False
                    continue
                seed_diffs.append(metrics[0]-metrics[2])
                seed_waits.append(metrics[1])
                seed_failures.append(metrics[0])
            if eligible:
                differences.append(statistics.fmean(seed_diffs))
                waits.append(statistics.fmean(seed_waits))
                failures.append(statistics.fmean(seed_failures))
        upper = (paired_upper(differences, plan['analysis']['bootstrap_resamples'],
                              plan['analysis']['bootstrap_seed']) if eligible else None)
        scores.append(dict(setting=candidate, eligible=eligible,
                           urgent_difference_upper_95=upper,
                           mean_low_p95_wait_ms=statistics.fmean(waits) if eligible else None,
                           mean_urgent_failure=statistics.fmean(failures) if eligible else None,
                           feasible=eligible and upper <= plan['urgent_failure_budget']))
    for policy in ('adaptive_guarded', 'fixed_guarded'):
        feasible = [score for score in scores if score['setting']['policy'] == policy and score['feasible']]
        if feasible:
            best = min(feasible, key=lambda s: (s['mean_low_p95_wait_ms'], s['mean_urgent_failure'],
                       s['setting']['minimum_s'], s['setting']['maximum_s'], s['setting']['fixed_interval_s']))
            selected[policy] = best['setting']
        else:
            selected[policy] = None
    return dict(status='ready' if all(selected.values()) else 'infeasible', selected=selected, scores=scores)


def evaluation_settings(plan, selection):
    adaptive, fixed = (selection['selected'][p] for p in ('adaptive_guarded', 'fixed_guarded'))
    def variant(original, policy):
        return setting(policy, original['minimum_s'], original['maximum_s'], original['fixed_interval_s'])
    return ([setting(p, fixed=plan['legacy_aging_interval_s']) for p in ('fifo', 'priority', 'aging', 'edf')]
            + [adaptive, variant(adaptive, 'adaptive'), fixed, variant(fixed, 'fixed_deadline')])


def run_phase(output, phase):
    output = Path(output)
    plan, registration = load_registration(output)
    if phase not in ('tune', 'evaluate'):
        raise ValueError('Unknown phase')
    selection_sha = None
    if phase == 'evaluate':
        tuning_marker = verify(output/'tune')
        if tuning_marker['plan_sha256'] != registration['plan_sha256']:
            raise ValueError('Tuning belongs to a different plan')
        selection = read_json(output/'tune/selection.json')
        if selection['status'] != 'ready':
            raise ValueError('No feasible tuning setting; held-out evaluation is blocked')
        # Recompute the selection from saved tuning summaries before opening evaluation output.
        saved_rows = read_json(output/'tune/run_metrics.json')
        if selection != select_parameters(plan, saved_rows):
            raise ValueError('Saved tuning selection does not match recorded scores')
        settings = evaluation_settings(plan, selection)
        seeds = plan['evaluation_seeds']
        selection_sha = file_hash(output/'tune/selection.json')
    else:
        settings = [dict(id='priority', policy='priority', minimum_s=.1, maximum_s=1., fixed_interval_s=.1)] + tuning_settings(plan)
        seeds = plan['tuning_seeds']
    directory = output/phase
    directory.mkdir(exist_ok=False)
    write_json(directory/'started.json', dict(phase=phase, plan_sha256=registration['plan_sha256'],
               selection_sha256=selection_sha, settings=settings, seeds=seeds, provenance=provenance()))
    rows = []
    for scenario in scenarios(plan):
        for seed in seeds:
            pair = directory/scenario['id']/str(seed)
            pair.mkdir(parents=True)
            events = generate_workload(plan['count'], scenario['rate'], seed, **workload_options(plan, scenario))
            trace = pair/'workload.csv'
            save_trace(trace, events)
            fingerprint, trace_sha = trace_fingerprint(events), file_hash(trace)
            for parameters in settings:
                config = AgingConfig(parameters['minimum_s'], parameters['maximum_s'], plan['service_estimate_s'])
                result = run_simulation(events, parameters['policy'], service_time=plan['service_time_s'],
                    queue_capacity=scenario['queue_capacity'], aging_interval=parameters['fixed_interval_s'], aging_config=config)
                run_output = pair/parameters['id']
                identity = dict(phase=phase, scenario_id=scenario['id'], seed=seed, setting_id=parameters['id'],
                                run_path=str(run_output.relative_to(output)), workload_sha256=fingerprint)
                manifest = identity | dict(scenario=scenario, plan_sha256=registration['plan_sha256'],
                    trace_path='../workload.csv', trace_file_sha256=trace_sha,
                    source_sha256=registration['provenance']['source']['sha256'],
                    generator_version=GENERATOR_VERSION, candidate_spec_version=1,
                    resolved_aging_config=vars(config), fixed_aging_interval_s=parameters['fixed_interval_s'],
                    selection_sha256=selection_sha, evidence_label=plan['evidence_label'])
                summaries = export_run(result, run_output, manifest)
                rows.extend(identity | row for row in summaries)
            print(f'{phase}: {scenario["id"]}, seed {seed}: {len(settings)} runs', flush=True)
    write_csv(directory/'run_metrics.csv', rows)
    write_json(directory/'run_metrics.json', rows)
    selection_status = None
    if phase == 'tune':
        selection = select_parameters(plan, rows)
        selection_status = selection['status']
        write_json(directory/'selection.json', selection)
    seal(directory, dict(phase=phase, plan_sha256=registration['plan_sha256'],
                         selection_sha256=selection_sha, selection_status=selection_status, run_count=len(rows)//4,
                         finished_utc=datetime.now(timezone.utc).isoformat()))
    return read_json(directory/'complete.json')



def verify_study(output):
    output = Path(output)
    plan, registration = load_registration(output)
    selection = None
    for phase in ('tune', 'evaluate'):
        marker = verify(output/phase)
        expected = registration['tuning_runs' if phase == 'tune' else 'evaluation_runs']
        if (marker['phase'] != phase or marker['plan_sha256'] != registration['plan_sha256']
                or marker['run_count'] != expected):
            raise ValueError('Phase completion marker does not match registration')
        if phase == 'tune':
            selection = read_json(output/'tune/selection.json')
            if selection != select_parameters(plan, read_json(output/'tune/run_metrics.json')):
                raise ValueError('Frozen selection does not match tuning summaries')
        elif (selection['status'] != 'ready' or
              marker['selection_sha256'] != file_hash(output/'tune/selection.json')):
            raise ValueError('Evaluation does not reference the frozen feasible selection')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=('plan', 'tune', 'evaluate', 'verify'))
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--profile', choices=('primary', 'smoke'), default='primary', help='Only used by plan')
    args = parser.parse_args()
    try:
        if args.stage == 'plan':
            result = initialize(args.output, args.profile)
            print(f'Registered {len(result["scenarios"])} scenarios; {result["tuning_runs"]} tuning and {result["evaluation_runs"]} evaluation runs')
        elif args.stage == 'verify':
            verify_study(args.output)
            print('Plan, source environment and both phase inventories verified')
        else:
            result = run_phase(args.output, args.stage)
            print(f'{args.stage}: complete, {result["run_count"]} runs')
            if result['selection_status'] is not None:
                print(f'Tuning selection: {result["selection_status"]}')
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.error(str(error))


if __name__ == '__main__':
    main()
