"""Shared non-preemptive, single-worker discrete-event simulation.

At equal timestamps: complete work, admit arrivals in (arrival, id) order,
then dispatch. An idle worker reserves one admission slot beyond waiting capacity.
"""
import heapq
import math
from dataclasses import dataclass
from numbers import Real


def positive(value, name):
    if isinstance(value, bool) or not isinstance(value, Real) or not math.isfinite(value) or value <= 0:
        raise ValueError(f'{name} must be positive and finite')


@dataclass(frozen=True)
class Alert:
    id: int
    arrival: float
    priority: int
    deadline_s: float | None = None  # relative to arrival; used for EDF selection
    service_time_s: float | None = None  # overrides run default when supplied

    def __post_init__(self):
        if type(self.id) is not int or self.id < 0:
            raise ValueError('id must be a nonnegative integer')
        if isinstance(self.arrival, bool) or not isinstance(self.arrival, Real) or not math.isfinite(self.arrival) or self.arrival < 0:
            raise ValueError('arrival must be nonnegative and finite')
        if type(self.priority) is not int or self.priority not in (0, 1, 2):
            raise ValueError('priority must be 0, 1 or 2')
        if self.deadline_s is not None:
            positive(self.deadline_s, 'deadline_s')
            if not math.isfinite(self.arrival + self.deadline_s):
                raise ValueError('absolute deadline must be finite')
        if self.service_time_s is not None:
            positive(self.service_time_s, 'service_time_s')

    @property
    def absolute_deadline_s(self):
        return None if self.deadline_s is None else self.arrival + self.deadline_s


@dataclass(frozen=True)
class Completion:
    event: Alert
    start_s: float
    finish_s: float
    completion_order: int

    @property
    def wait_s(self):
        return self.start_s - self.event.arrival

    @property
    def latency_s(self):
        return self.finish_s - self.event.arrival


@dataclass(frozen=True)
class Rejection:
    event: Alert
    rejected_at_s: float
    reason: str = 'queue_full'


@dataclass(frozen=True)
class SimulationResult:
    policy: str
    generated: int
    completions: tuple[Completion, ...]
    rejections: tuple[Rejection, ...]
    max_waiting: int

    @property
    def admitted(self):
        return len(self.completions)  # every admitted event drains

    @property
    def completed(self):
        return len(self.completions)

    @property
    def dropped(self):
        return len(self.rejections)


class _WaitingQueue:
    """All policies share admission and execution; only selection differs."""
    def __init__(self, policy, aging_interval):
        self.policy, self.interval, self.items = policy, aging_interval, []

    def __len__(self):
        return len(self.items)

    def push(self, sequence, event):
        if self.policy == 'edf':
            key = event.absolute_deadline_s if event.deadline_s is not None else math.inf
        else:
            key = event.priority if self.policy == 'priority' else 0
        heapq.heappush(self.items, (key, sequence, event))

    def pop(self, clock):
        if self.policy != 'aging':
            return heapq.heappop(self.items)[2]
        def aging_key(index):
            _, sequence, event = self.items[index]
            waited = clock - event.arrival
            # Saturate before dividing to avoid overflow for tiny valid intervals.
            effective = 0 if waited >= event.priority*self.interval else (
                event.priority - math.floor(waited/self.interval))
            return effective, sequence

        index = min(range(len(self.items)), key=aging_key)
        event = self.items.pop(index)[2]
        heapq.heapify(self.items)
        return event


def run_simulation(events, policy, service_time=.01, *, queue_capacity=None, aging_interval=.1):
    """Drop arriving work when waiting capacity is exhausted; drain admitted work.

    queue_capacity counts waiting events, excluding the worker. None is unbounded;
    zero permits service with no waiting buffer. Deadlines do not expire work yet.
    """
    if policy not in ('fifo', 'priority', 'aging', 'edf'):
        raise ValueError('Unknown policy')
    positive(service_time, 'service_time')
    positive(aging_interval, 'aging_interval')
    if queue_capacity is not None and (type(queue_capacity) is not int or queue_capacity < 0):
        raise ValueError('queue_capacity must be a nonnegative integer or None')
    events = list(events)
    if any(not isinstance(event, Alert) for event in events):
        raise ValueError('events must contain Alert instances')
    if len({event.id for event in events}) != len(events):
        raise ValueError('event IDs must be unique within a run')
    events.sort(key=lambda event: (event.arrival, event.id))
    waiting = _WaitingQueue(policy, aging_interval)
    completions, rejections = [], []
    index, max_waiting = 0, 0
    active = None
    while index < len(events) or waiting or active is not None:
        arrival = events[index].arrival if index < len(events) else math.inf
        finish = active.finish_s if active is not None else math.inf
        clock = min(arrival, finish)
        if active is not None and finish <= clock:
            completions.append(active)
            active = None
        # Reserve a worker slot for this timestamp's batch if the worker is idle.
        limit = None if queue_capacity is None else queue_capacity + (active is None)
        while index < len(events) and events[index].arrival <= clock:
            event = events[index]
            if limit is None or len(waiting) < limit:
                waiting.push(index, event)
            else:
                rejections.append(Rejection(event, event.arrival))
            index += 1
        if active is None and waiting:
            event = waiting.pop(clock)
            duration = event.service_time_s if event.service_time_s is not None else service_time
            end = clock + duration
            if not math.isfinite(end) or end <= clock:
                raise ValueError('service time cannot advance the finite simulation clock')
            active = Completion(event, clock, end, len(completions))
        max_waiting = max(max_waiting, len(waiting))
    return SimulationResult(policy, len(events), tuple(completions), tuple(rejections), max_waiting)
