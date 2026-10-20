"""Deterministic single-server simulation; no wall-clock or network claims."""
import argparse
import csv
import heapq
import math
import random
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Alert:
    id: int
    arrival: float
    priority: int  # 0 high, 1 medium, 2 low


def workload(count, rate, seed):
    rng = random.Random(seed)
    arrival = 0.0
    events = []
    for index in range(count):
        arrival += rng.expovariate(rate)
        events.append(Alert(index, arrival, rng.choices([0, 1, 2], [1, 2, 7])[0]))
    return events


def simulate(events, policy, service_time, aging_interval=.1):
    if policy not in ('fifo', 'priority', 'aging') or not math.isfinite(service_time) or service_time <= 0:
        raise ValueError('Invalid policy or service time')
    if not math.isfinite(aging_interval) or aging_interval <= 0:
        raise ValueError('Aging interval must be positive and finite')
    events = sorted(events, key=lambda e: (e.arrival, e.id))
    pending, rows = [], []
    clock, index, order = 0.0, 0, 0
    while index < len(events) or pending:
        if not pending:
            clock = max(clock, events[index].arrival)
        while index < len(events) and events[index].arrival <= clock:
            event = events[index]
            key = event.priority if policy == 'priority' else 0
            heapq.heappush(pending, (key, index, event))
            index += 1
        if policy == 'aging':
            # Recompute at dispatch; cached heap priorities would become stale.
            selected = min(range(len(pending)), key=lambda i: (
                max(0, pending[i][2].priority - math.floor((clock-pending[i][2].arrival)/aging_interval)),
                pending[i][1]))
            _, _, event = pending.pop(selected)
            heapq.heapify(pending)
        else:
            _, _, event = heapq.heappop(pending)
        start = clock
        clock += service_time
        rows.append(dict(policy=policy, id=event.id, priority=event.priority,
                         arrival_s=event.arrival, start_s=start, finish_s=clock,
                         wait_s=start-event.arrival, latency_s=clock-event.arrival,
                         completion_order=order))
        order += 1
    return rows


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
