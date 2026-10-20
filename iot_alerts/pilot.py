"""Paired finite-workload baseline pilot. No live MQTT performance claims."""
import argparse
import gzip
import json
import platform
import statistics
import subprocess
from pathlib import Path
from .experiment import workload, simulate, percentile, write_csv


def run(output, count=1000):
    if count < 100:
        raise ValueError('Use at least 100 events per run')
    output.mkdir(parents=True, exist_ok=True)
    summaries = []
    for rate in (50, 90, 120):
        for seed in range(1, 11):
            events = workload(count, rate, seed)
            for policy in ('fifo', 'priority', 'aging'):
                rows = simulate(events, policy, .01, aging_interval=.1)
                raw_path = output / f'rate{rate}-seed{seed}-{policy}.csv'
                write_csv(raw_path, rows)
                for priority in (0, 1, 2):
                    subset = [r for r in rows if r['priority'] == priority]
                    if not subset:
                        continue
                    latency = [r['latency_s']*1000 for r in subset]
                    waits = [r['wait_s']*1000 for r in subset]
                    deadline = (100, 500, 2000)[priority]
                    summaries.append(dict(rate=rate, seed=seed, policy=policy,
                        priority=priority, count=len(subset), mean_latency_ms=statistics.mean(latency),
                        p95_latency_ms=percentile(latency, .95), p99_latency_ms=percentile(latency, .99),
                        p95_wait_ms=percentile(waits, .95), max_wait_ms=max(waits),
                        deadline_miss_fraction=sum(v>deadline for v in latency)/len(latency)))
    write_csv(output/'run_metrics.csv', summaries)
    aggregate = []
    for rate in (50, 90, 120):
        for policy in ('fifo', 'priority', 'aging'):
            for priority in (0, 1, 2):
                group=[r for r in summaries if r['rate']==rate and r['policy']==policy and r['priority']==priority]
                aggregate.append(dict(rate=rate, policy=policy, priority=priority,
                    runs=len(group), mean_of_run_p95_latency_ms=statistics.mean(r['p95_latency_ms'] for r in group),
                    mean_of_run_max_wait_ms=statistics.mean(r['max_wait_ms'] for r in group),
                    mean_deadline_miss_fraction=statistics.mean(r['deadline_miss_fraction'] for r in group)))
    write_csv(output/'aggregate.csv', aggregate)
    config=dict(count=count, rates=[50,90,120], seeds=list(range(1,11)),
        policies=['fifo','priority','aging'], service_ms=10, aging_interval_ms=100,
        priority_weights=[1,2,7], illustrative_deadlines_ms=[100,500,2000],
        queue='unbounded', termination='drain every event', python=platform.python_version(),
        base_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        percentile='nearest rank', note='Source SHA256 manifest identifies uncommitted experiment code')
    import hashlib
    config['source_sha256']={n:hashlib.sha256(Path(n).read_bytes()).hexdigest() for n in
        ('iot_alerts/experiment.py','iot_alerts/pilot.py')}
    (output/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    # Small checked-in raw example; complete raw files remain reproducible from this command.
    (output/'example-rate120-seed1-priority.csv.gz').write_bytes(
        gzip.compress((output/'rate120-seed1-priority.csv').read_bytes(), mtime=0))
    return aggregate


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=Path('results/pilot'))
    parser.add_argument('--count',type=int,default=1000)
    args=parser.parse_args()
    run(args.output,args.count)
    print(f'Pilot evidence written to {args.output}')
