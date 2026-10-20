"""Seeded synthetic workloads and exact CSV replay; no real device claims."""
import csv
import hashlib
import json
import math
import random
from dataclasses import asdict
from pathlib import Path

from .simulator import Alert, positive

FIELDS = ('id', 'arrival', 'priority', 'deadline_s', 'service_time_s')
GENERATOR_VERSION = 1


def generate_workload(count=1000, rate=120, seed=42, *, traffic='poisson',
                      priority_weights=(1, 2, 7), service_time=.01,
                      service_distribution='constant', uniform_spread=.5,
                      deadlines=(None, None, None), burst_start=.4,
                      burst_end=.6, burst_multiplier=5):
    """Generate a fixed count. Burst compresses interarrivals in an index window.

    uniform_spread is a fraction of mean service time. Exponential service has
    the configured expected mean, not an exactly normalized finite-sample mean.
    """
    if type(count) is not int or count < 1:
        raise ValueError('count must be a positive integer')
    if type(seed) is not int:
        raise ValueError('seed must be an integer')
    positive(rate, 'rate')
    positive(service_time, 'service_time')
    if traffic not in ('poisson', 'burst'):
        raise ValueError('Unknown traffic shape')
    if service_distribution not in ('constant', 'uniform', 'exponential'):
        raise ValueError('Unknown service distribution')
    if service_distribution == 'exponential' and not math.isfinite(1/service_time):
        raise ValueError('Exponential mean is too small for finite sampling')
    if len(priority_weights) != 3 or any(isinstance(v, bool) or not isinstance(v, (int, float)) or
            not math.isfinite(v) or v < 0 for v in priority_weights):
        raise ValueError('priority_weights must contain three finite nonnegative values')
    total_weight = sum(priority_weights)
    if not math.isfinite(total_weight) or total_weight <= 0:
        raise ValueError('priority_weights must have a positive finite total')
    if len(deadlines) != 3:
        raise ValueError('deadlines must contain high, medium and low budgets')
    for deadline in deadlines:
        if deadline is not None:
            positive(deadline, 'deadline')
    if isinstance(uniform_spread, bool) or not isinstance(uniform_spread, (int, float)) or not math.isfinite(uniform_spread) or not 0 <= uniform_spread < 1:
        raise ValueError('uniform_spread must be finite and in [0, 1)')
    if not all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)
               for v in (burst_start, burst_end)) or not 0 <= burst_start < burst_end <= 1:
        raise ValueError('burst window must satisfy 0 <= start < end <= 1')
    positive(burst_multiplier, 'burst_multiplier')
    if burst_multiplier < 1:
        raise ValueError('burst_multiplier must be at least 1')
    if not math.isfinite(rate*burst_multiplier):
        raise ValueError('burst rate must be finite')
    rng = random.Random(seed)
    # Keep service draws independent of arrival/class draws and legacy defaults.
    service_rng = random.Random(f'{seed}:service')
    start, end = math.floor(count*burst_start), math.ceil(count*burst_end)
    events, arrival = [], 0.0
    for index in range(count):
        multiplier = burst_multiplier if traffic == 'burst' and start <= index < end else 1
        arrival += rng.expovariate(rate*multiplier)
        priority = rng.choices((0, 1, 2), weights=priority_weights)[0]
        duration = service_time
        if service_distribution == 'uniform':
            duration = service_rng.uniform(service_time*(1-uniform_spread), service_time*(1+uniform_spread))
        elif service_distribution == 'exponential':
            duration = 0.0
            while duration == 0:
                duration = service_rng.expovariate(1/service_time)
        events.append(Alert(index, arrival, priority, deadlines[priority], duration))
    return events


def trace_fingerprint(events):
    # Normalize numeric time types so 2 and 2.0 identify the same replay input.
    rows = [dict(id=e.id, arrival=float(e.arrival), priority=e.priority,
                 deadline_s=None if e.deadline_s is None else float(e.deadline_s),
                 service_time_s=None if e.service_time_s is None else float(e.service_time_s))
            for e in events]
    payload = json.dumps(rows, sort_keys=True, separators=(',', ':'), allow_nan=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def save_trace(path, events):
    with Path(path).open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator='\n')
        writer.writeheader()
        writer.writerows(asdict(e) for e in events)


def load_trace(path):
    """Validate saved input; do not accept result CSVs or silently ignore fields."""
    events, ids = [], set()
    with Path(path).open(newline='') as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames is None or len(reader.fieldnames) != len(FIELDS) or set(reader.fieldnames) != set(FIELDS):
            raise ValueError('Trace must contain exactly: '+', '.join(FIELDS))
        for line, row in enumerate(reader, 2):
            try:
                if None in row or any(value is None for value in row.values()):
                    raise ValueError('Unexpected or missing columns')
                event = Alert(int(row['id']), float(row['arrival']), int(row['priority']),
                              None if row['deadline_s'] == '' else float(row['deadline_s']),
                              None if row['service_time_s'] == '' else float(row['service_time_s']))
                if event.service_time_s is None:
                    raise ValueError('Replay requires explicit per-event service time')
                if event.id in ids:
                    raise ValueError('Duplicate event ID')
            except (ValueError, TypeError) as error:
                raise ValueError(f'Invalid trace row {line}: {error}') from error
            ids.add(event.id)
            events.append(event)
    if not events:
        raise ValueError('Replay trace must contain at least one event')
    return events
