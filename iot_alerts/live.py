"""Thread-safe single-worker admission, scheduling and bounded deduplication.

MQTT-independent so scheduling/admission can be tested without a broker.
"""
import json
import math
import threading
import time
from collections import OrderedDict
from dataclasses import dataclass
from types import MappingProxyType
from collections.abc import Mapping

from .scheduling import AgingConfig, VARIANTS
from .simulator import Alert, _WaitingQueue, positive

POLICIES = ('fifo', 'priority', 'aging', 'edf', *VARIANTS)


def parse_payload(payload):
    if not isinstance(payload, (bytes, str)) or len(payload) > 4096:
        raise ValueError('Payload must be JSON of at most 4096 bytes/characters')
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate JSON field')
            result[key] = value
        return result
    value = json.loads(payload, object_pairs_hook=unique)
    if not isinstance(value, dict) or not {'id', 'priority'} <= value.keys() or value.keys() - {'id', 'source', 'priority', 'deadline_ms'}:
        raise ValueError('Expected id, priority and optional source/deadline_ms')
    for name, limit in (('id', 256), ('source', 128)):
        text = value.get(name, 'legacy')
        if not isinstance(text, str) or not text.strip() or len(text) > limit:
            raise ValueError(f'{name} must be a nonblank bounded string')
        text.encode('utf-8')
    if type(value['priority']) is not int or value['priority'] not in (0, 1, 2):
        raise ValueError('priority must be 0, 1 or 2')
    deadline = value.get('deadline_ms')
    if deadline is not None:
        try:
            positive(deadline, 'deadline_ms')
            positive(deadline/1000, 'deadline_s')
        except OverflowError as error:
            raise ValueError('deadline must be representable as finite seconds') from error
    return dict(id=value['id'], source=value.get('source', 'legacy'), priority=value['priority'],
                deadline_ms=None if deadline is None else float(deadline))


@dataclass(frozen=True)
class PendingEvent:
    wire: Mapping
    alert: Alert

    @property
    def key(self):
        return self.wire['source'], self.wire['id']


@dataclass(frozen=True)
class WorkItem:
    event: PendingEvent
    start_s: float


class LiveProcessor:
    def __init__(self, policy='priority', *, capacity=10000, aging_interval=.1,
                 aging_config=None, dedup_capacity=10000, dedup_ttl=60., clock=time.monotonic):
        if policy not in POLICIES:
            raise ValueError('Unknown policy')
        if type(capacity) is not int or capacity < 0:
            raise ValueError('capacity must be a nonnegative integer')
        if policy in VARIANTS and capacity == 0:
            raise ValueError('Experimental aging requires positive capacity')
        positive(aging_interval, 'aging_interval')
        positive(dedup_ttl, 'dedup_ttl')
        if type(dedup_capacity) is not int or dedup_capacity < 1:
            raise ValueError('dedup_capacity must be a positive integer')
        config = AgingConfig() if aging_config is None else aging_config
        if not isinstance(config, AgingConfig):
            raise ValueError('aging_config must be an AgingConfig')
        self.policy, self.capacity = policy, capacity
        self.clock, self.origin = clock, clock()
        self.condition = threading.Condition()
        self.queue = _WaitingQueue(policy, aging_interval, capacity, config)
        self.pending, self.reserved, self.recent = {}, {}, OrderedDict()
        self.active, self.closed, self.sequence = None, False, 0
        self.dedup_capacity, self.dedup_ttl = dedup_capacity, dedup_ttl
        self.counts = {name: 0 for name in ('received_messages', 'invalid_messages', 'duplicate_messages',
            'identity_conflicts', 'rejected_queue_full', 'rejected_closed', 'admitted', 'completed',
            'deadline_met', 'deadline_missed', 'deadline_not_set', 'ttl_expirations', 'cache_evictions')}
        self.max_waiting = 0

    def now(self):
        return self.clock()-self.origin

    def _expire(self, now):
        while self.recent:
            key, (completed, _) = next(iter(self.recent.items()))
            if now-completed < self.dedup_ttl:
                break
            self.recent.pop(key)
            self.counts['ttl_expirations'] += 1

    def ingest(self, payload):
        arrival = self.now()  # callback-entry boundary, before validation
        try:
            wire = parse_payload(payload)
            error = None
        except (ValueError, TypeError, UnicodeError, RecursionError):
            wire, error = None, 'invalid_payload'
        with self.condition:
            self.counts['received_messages'] += 1
            if error:
                self.counts['invalid_messages'] += 1
                return dict(status='rejected', reason=error, arrival_s=arrival)
            receipt = wire | dict(arrival_s=arrival)
            if self.closed:
                self.counts['rejected_closed'] += 1
                return receipt | dict(status='rejected', reason='closed')
            self._expire(self.now())
            key = wire['source'], wire['id']
            signature = wire['priority'], wire['deadline_ms']
            seen = self.reserved.get(key)
            if seen is None and key in self.recent:
                seen = self.recent[key][1]
            if seen is not None:
                if seen == signature:
                    self.counts['duplicate_messages'] += 1
                    return receipt | dict(status='duplicate', reason='already_seen')
                self.counts['identity_conflicts'] += 1
                return receipt | dict(status='rejected', reason='identity_conflict')
            limit = self.capacity + (self.active is None)
            if len(self.queue) >= limit:
                self.counts['rejected_queue_full'] += 1
                return receipt | dict(status='rejected', reason='queue_full')
            alert = Alert(self.sequence, arrival, wire['priority'],
                          None if wire['deadline_ms'] is None else wire['deadline_ms']/1000)
            event = PendingEvent(MappingProxyType(wire), alert)
            self.pending[alert.id] = event
            self.reserved[key] = signature
            self.queue.push(self.sequence, alert)
            self.sequence += 1
            self.counts['admitted'] += 1
            waiting = len(self.queue) - (self.active is None)
            self.max_waiting = max(self.max_waiting, waiting)
            self.condition.notify()
            return receipt | dict(status='admitted', reason='', sequence=alert.id)

    def take(self, *, block=True):
        with self.condition:
            if self.active is not None:
                raise RuntimeError('Only one processing worker is supported')
            while not self.queue:
                if self.closed or not block:
                    return None
                self.condition.wait()
            start = self.now()
            alert = self.queue.pop(start)
            self.active = WorkItem(self.pending.pop(alert.id), start)
            return self.active

    def complete(self, item):
        with self.condition:
            if item is not self.active or item is None:
                raise ValueError('Completion does not match the active item')
            finish = self.now()
            if not math.isfinite(finish) or finish < item.start_s:
                raise ValueError('Completion clock must be finite and monotonic')
            event, alert = item.event, item.event.alert
            deadline = alert.absolute_deadline_s
            status = 'not_set' if deadline is None else 'met' if finish <= deadline else 'missed'
            self.counts['completed'] += 1
            self.counts['deadline_'+('not_set' if status == 'not_set' else status)] += 1
            self.reserved.pop(event.key)
            self._expire(finish)
            self.recent[event.key] = (finish, (event.wire['priority'], event.wire['deadline_ms']))
            while len(self.recent) > self.dedup_capacity:
                self.recent.popitem(last=False)
                self.counts['cache_evictions'] += 1
            self.active = None
            return event.wire | dict(sequence=alert.id, status='completed', arrival_s=alert.arrival,
                start_s=item.start_s, finish_s=finish, absolute_deadline_s=deadline, deadline_status=status,
                wait_ms=(item.start_s-alert.arrival)*1000, local_latency_ms=(finish-alert.arrival)*1000,
                service_ms=(finish-item.start_s)*1000)

    def close(self):
        with self.condition:
            self.closed = True
            self.condition.notify_all()

    def snapshot(self):
        with self.condition:
            self._expire(self.now())
            return self.counts | dict(policy=self.policy, pending=len(self.queue), active=int(self.active is not None),
                unfinished=self.counts['admitted']-self.counts['completed'], max_waiting=self.max_waiting,
                guard_activations=self.queue.guard_activations, recent_completed_ids=len(self.recent),
                reserved_ids=len(self.reserved), accepting=not self.closed)
