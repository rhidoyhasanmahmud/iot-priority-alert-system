"""Deterministic single-server simulation; no wall-clock or network claims."""
import argparse
import csv
import math
import random
from pathlib import Path
from .simulator import Alert, run_simulation


def workload(count, rate, seed):
    rng = random.Random(seed)
    arrival = 0.0
    events = []
    for index in range(count):
        arrival += rng.expovariate(rate)
        events.append(Alert(index, arrival, rng.choices([0, 1, 2], [1, 2, 7])[0]))
    return events


def simulate(events, policy, service_time, aging_interval=.1):
    """Backward-compatible unbounded adapter; preserves the original CSV schema."""
    result = run_simulation(events, policy, service_time, aging_interval=aging_interval)
    return [dict(policy=policy, id=c.event.id, priority=c.event.priority,
                 arrival_s=c.event.arrival, start_s=c.start_s, finish_s=c.finish_s,
                 wait_s=c.wait_s, latency_s=c.latency_s,
                 completion_order=c.completion_order) for c in result.completions]


def percentile(values, fraction):
    return sorted(values)[max(0, math.ceil(len(values)*fraction)-1)]


def write_csv(path, rows):
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--count', type=int, default=1000)
    parser.add_argument('--rate', type=float, default=120)
    parser.add_argument('--service-ms', type=float, default=10)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--output', type=Path, default=Path('results/run'))
    args = parser.parse_args()
    if args.count < 1 or not math.isfinite(args.rate) or args.rate <= 0 or not math.isfinite(args.service_ms) or args.service_ms <= 0:
        parser.error('count, rate and service-ms must be positive and finite')
    events = workload(args.count, args.rate, args.seed)
    args.output.mkdir(parents=True, exist_ok=True)
    summary = []
    for policy in ('fifo', 'priority'):
        rows = simulate(events, policy, args.service_ms/1000)
        write_csv(args.output / f'{policy}.csv', rows)
        for priority in (0, 1, 2):
            subset = [r for r in rows if r['priority'] == priority]
            if not subset:
                continue
            latencies = [r['latency_s'] for r in subset]
            summary.append(dict(policy=policy, priority=priority, count=len(subset),
                                mean_latency_ms=sum(latencies)/len(latencies)*1000,
                                p95_latency_ms=percentile(latencies, .95)*1000,
                                max_wait_ms=max(r['wait_s'] for r in subset)*1000,
                                throughput_per_s=len(rows)/(rows[-1]['finish_s']-events[0].arrival)))
    write_csv(args.output / 'summary.csv', summary)
    import json
    (args.output / 'config.json').write_text(json.dumps(dict(count=args.count, rate=args.rate,
        service_ms=args.service_ms, seed=args.seed), indent=2)+'\n')
    print(f'Results: {args.output}/summary.csv')


if __name__ == '__main__':
    main()
