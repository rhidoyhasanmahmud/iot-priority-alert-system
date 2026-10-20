"""Run scheduling baselines and export loss-aware metrics."""
import argparse
import json
from dataclasses import asdict
from pathlib import Path
from .experiment import write_csv
from .simulator import positive, run_simulation
from .scheduling import VARIANTS, AgingConfig
from .metrics import deadline_status, summarize
from .workloads import GENERATOR_VERSION, generate_workload, load_trace, save_trace, trace_fingerprint

POLICIES = ('fifo', 'priority', 'aging', 'edf')


def export_run(result, output, config):
    """Export one fully drained run; all-policy mode uses one directory per policy."""
    rows = []
    for completion in result.completions:
        event = completion.event
        rows.append(dict(**asdict(event), absolute_deadline_s=event.absolute_deadline_s,
                         status='completed', reason='', deadline_status=deadline_status(event, completion.finish_s),
                         start_s=completion.start_s, finish_s=completion.finish_s,
                         wait_s=completion.wait_s, latency_s=completion.latency_s, rejected_at_s=None))
    for rejection in result.rejections:
        event = rejection.event
        rows.append(dict(**asdict(event), absolute_deadline_s=event.absolute_deadline_s,
                         status='dropped', reason=rejection.reason, deadline_status=deadline_status(event),
                         start_s=None, finish_s=None, wait_s=None, latency_s=None,
                         rejected_at_s=rejection.rejected_at_s))
    rows.sort(key=lambda row: (row['arrival'], row['id']))
    output.mkdir(parents=True, exist_ok=True)
    write_csv(output/'events.csv', rows)
    summary = summarize(result)
    write_csv(output/'summary.csv', summary)
    (output/'summary.json').write_text(json.dumps(summary, indent=2, allow_nan=False)+'\n')
    manifest = config | dict(policy=result.policy, output=str(output), generated=result.generated,
        admitted=result.admitted, completed=result.completed, dropped=result.dropped,
        max_waiting=result.max_waiting, guard_activations=result.guard_activations, termination='drain all admitted work',
        tie_order='completion, arrival batch sorted by id, dispatch',
        deadline_behavior='finish <= absolute deadline succeeds; no expiry',
        summary_schema_version=1, undefined_metrics='JSON null / CSV empty cell',
        deadline_failure_denominator='all generated events with deadlines',
        admitted_deadline_miss_denominator='admitted events with deadlines',
        latency_population='completed events only')
    (output/'config.json').write_text(json.dumps(manifest, indent=2)+'\n')
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--policy', choices=(*POLICIES, *VARIANTS, 'all', 'research'), default='fifo')
    parser.add_argument('--count', type=int, default=1000)
    parser.add_argument('--rate', type=float, default=120)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--queue-capacity', type=int, default=None, help='Waiting slots; omit for unbounded, use 0 for no buffer')
    parser.add_argument('--service-ms', type=float, default=10)
    deadlines = parser.add_mutually_exclusive_group()
    deadlines.add_argument('--deadline-ms', type=float, default=None, help='Relative deadline shared by all events')
    deadlines.add_argument('--deadlines-ms', type=float, nargs=3, metavar=('HIGH', 'MEDIUM', 'LOW'), help='Relative deadlines for each priority class')
    parser.add_argument('--aging-ms', type=float, default=100)
    parser.add_argument('--aging-min-ms', type=float, default=100)
    parser.add_argument('--aging-max-ms', type=float, default=1000)
    parser.add_argument('--service-estimate-ms', type=float, default=10)
    parser.add_argument('--traffic', choices=('poisson', 'burst'), default='poisson')
    parser.add_argument('--priority-weights', type=float, nargs=3, default=(1, 2, 7), metavar=('HIGH', 'MEDIUM', 'LOW'))
    parser.add_argument('--service-distribution', choices=('constant', 'uniform', 'exponential'), default='constant')
    parser.add_argument('--uniform-spread', type=float, default=.5)
    parser.add_argument('--burst-start', type=float, default=.4)
    parser.add_argument('--burst-end', type=float, default=.6)
    parser.add_argument('--burst-multiplier', type=float, default=5)
    parser.add_argument('--trace-input', type=Path, help='Replay saved workload CSV; generation settings are ignored')
    parser.add_argument('--output', type=Path, default=Path('results/foundation'))
    args = parser.parse_args()
    try:
        if args.count < 1:
            raise ValueError('count must be positive')
        positive(args.rate, 'rate')
        positive(args.service_ms, 'service-ms')
        positive(args.aging_ms, 'aging-ms')
        if args.deadline_ms is not None:
            positive(args.deadline_ms, 'deadline-ms')
        if args.deadlines_ms is not None:
            for value in args.deadlines_ms:
                positive(value, 'deadlines-ms')
        if args.queue_capacity is not None and args.queue_capacity < 0:
            raise ValueError('queue-capacity must be nonnegative')
        if args.trace_input is not None:
            events = load_trace(args.trace_input)
        else:
            budgets = (tuple(v/1000 for v in args.deadlines_ms) if args.deadlines_ms is not None
                       else (None if args.deadline_ms is None else args.deadline_ms/1000,)*3)
            events = generate_workload(args.count, args.rate, args.seed, traffic=args.traffic,
                priority_weights=args.priority_weights, service_time=args.service_ms/1000,
                service_distribution=args.service_distribution, uniform_spread=args.uniform_spread,
                deadlines=budgets, burst_start=args.burst_start, burst_end=args.burst_end,
                burst_multiplier=args.burst_multiplier)
        candidate_config = AgingConfig(args.aging_min_ms/1000, args.aging_max_ms/1000, args.service_estimate_ms/1000)
        policies = ((*POLICIES, *VARIANTS) if args.policy == 'research' else
                    POLICIES if args.policy in ('all', 'research') else (args.policy,))
        results = [run_simulation(events, policy, args.service_ms/1000,
                                 queue_capacity=args.queue_capacity, aging_interval=args.aging_ms/1000, aging_config=candidate_config)
                   for policy in policies]
    except (ValueError, OSError) as error:
        parser.error(str(error))
    config = vars(args) | dict(output=str(args.output),
        trace_input=None if args.trace_input is None else str(args.trace_input),
        input_mode='replay' if args.trace_input is not None else 'generated',
        generator_version=None if args.trace_input is not None else GENERATOR_VERSION,
        generation_settings_applied=args.trace_input is None,
        input_event_count=len(events), workload_sha256=trace_fingerprint(events),
        candidate_spec_version=1, resolved_aging_config=asdict(candidate_config),
        fixed_aging_interval_s=args.aging_ms/1000,
        edf_rule='earliest absolute deadline, missing deadline last, arrival order breaks ties')
    args.output.mkdir(parents=True, exist_ok=True)
    save_trace(args.output/'workload.csv', events)
    summaries = []
    for result in results:
        output = args.output/result.policy if args.policy in ('all', 'research') else args.output
        summaries.extend(export_run(result, output, config))
        print(f'{result.policy}: completed {result.completed}; dropped {result.dropped}; output: {output}')
    if args.policy in ('all', 'research'):
        write_csv(args.output/'summary.csv', summaries)
        (args.output/'summary.json').write_text(json.dumps(summaries, indent=2, allow_nan=False)+'\n')
        (args.output/'config.json').write_text(json.dumps(config | dict(policies=list(policies)), indent=2)+'\n')


if __name__ == '__main__':
    main()
