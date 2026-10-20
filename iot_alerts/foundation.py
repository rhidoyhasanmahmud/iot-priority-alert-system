"""Run the foundation engine and export complete event outcomes."""
import argparse
import json
from dataclasses import asdict, replace
from pathlib import Path
from .experiment import workload, write_csv
from .simulator import positive, run_simulation


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--policy', choices=('fifo', 'priority', 'aging'), default='fifo')
    parser.add_argument('--count', type=int, default=1000)
    parser.add_argument('--rate', type=float, default=120)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--queue-capacity', type=int, default=None, help='Waiting slots; omit for unbounded, use 0 for no buffer')
    parser.add_argument('--service-ms', type=float, default=10)
    parser.add_argument('--deadline-ms', type=float, default=None, help='Optional relative deadline for each generated event')
    parser.add_argument('--aging-ms', type=float, default=100)
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
        if args.queue_capacity is not None and args.queue_capacity < 0:
            raise ValueError('queue-capacity must be nonnegative')
        events = [replace(e, service_time_s=args.service_ms/1000,
                          deadline_s=None if args.deadline_ms is None else args.deadline_ms/1000)
                  for e in workload(args.count, args.rate, args.seed)]
        result = run_simulation(events, args.policy, args.service_ms/1000,
                                queue_capacity=args.queue_capacity, aging_interval=args.aging_ms/1000)
    except ValueError as error:
        parser.error(str(error))
    rows = []
    for completion in result.completions:
        event = completion.event
        rows.append(dict(**asdict(event), absolute_deadline_s=event.absolute_deadline_s,
                         status='completed', reason='', start_s=completion.start_s,
                         finish_s=completion.finish_s, wait_s=completion.wait_s,
                         latency_s=completion.latency_s, rejected_at_s=None))
    for rejection in result.rejections:
        event = rejection.event
        rows.append(dict(**asdict(event), absolute_deadline_s=event.absolute_deadline_s,
                         status='dropped', reason=rejection.reason, start_s=None,
                         finish_s=None, wait_s=None, latency_s=None,
                         rejected_at_s=rejection.rejected_at_s))
    rows.sort(key=lambda row: (row['arrival'], row['id']))
    args.output.mkdir(parents=True, exist_ok=True)
    write_csv(args.output/'events.csv', rows)
    config = vars(args) | dict(output=str(args.output), generated=result.generated,
        admitted=result.admitted, completed=result.completed, dropped=result.dropped,
        max_waiting=result.max_waiting, termination='drain all admitted work',
        tie_order='completion, arrival batch sorted by id, dispatch',
        deadline_behavior='metadata only; no expiry or miss aggregation')
    (args.output/'config.json').write_text(json.dumps(config, indent=2)+'\n')
    print(f'Completed {result.completed}; dropped {result.dropped}; output: {args.output}')


if __name__ == '__main__':
    main()
