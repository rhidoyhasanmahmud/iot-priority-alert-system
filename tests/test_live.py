import json
import threading
import unittest
from iot_alerts.live import LiveProcessor, POLICIES, parse_payload
from iot_alerts.scheduling import AgingConfig
from iot_alerts.simulator import Alert, run_simulation


class Clock:
    def __init__(self):
        self.value = 0.
    def __call__(self):
        return self.value


def payload(id='event', priority=2, source='sensor', **extra):
    return json.dumps(dict(id=id, priority=priority, source=source, **extra))


class PayloadTests(unittest.TestCase):
    def test_legacy_and_optional_deadline(self):
        self.assertEqual(parse_payload('{"id":"a","priority":0}')['source'], 'legacy')
        self.assertEqual(parse_payload(payload(deadline_ms=100))['deadline_ms'], 100.)

    def test_invalid_schema_and_numeric_edge_cases(self):
        invalid = ['[]', 'null', '{', '{"id":"a","id":"b","priority":0}',
                   payload(priority=True), payload(id=''), payload(source=' '), payload(service_ms=1),
                   payload(deadline_ms=0), payload(deadline_ms=True), payload(deadline_ms=float('inf')),
                   payload(deadline_ms=5e-324), payload(deadline_ms=10**400), payload(id='a'*257), payload(source='x'*129),
                   payload(id='\ud800'), b'\xff', ' '*4097]
        for value in invalid:
            with self.subTest(value=repr(value)), self.assertRaises((ValueError, UnicodeError)):
                parse_payload(value)


class LiveTests(unittest.TestCase):
    def setUp(self):
        self.clock = Clock()
        self.core = LiveProcessor(clock=self.clock)

    def finish(self, core=None):
        core = self.core if core is None else core
        item = core.take(block=False)
        self.clock.value += .02
        return core.complete(item)

    def test_pending_active_and_completed_duplicates(self):
        self.assertEqual(self.core.ingest(payload())['status'], 'admitted')
        self.assertEqual(self.core.ingest(payload())['status'], 'duplicate')
        item = self.core.take()
        self.clock.value = 100  # pending/active pin survives any completed-cache TTL
        self.assertEqual(self.core.ingest(payload())['status'], 'duplicate')
        row = self.core.complete(item)
        self.assertEqual(row['id'], 'event')
        self.assertEqual(self.core.ingest(payload())['status'], 'duplicate')
        self.assertEqual(self.core.snapshot()['completed'], 1)

    def test_source_namespaces_and_identity_conflicts(self):
        self.core.ingest(payload())
        self.assertEqual(self.core.ingest(payload(source='other'))['status'], 'admitted')
        self.assertEqual(self.core.ingest(payload(priority=0))['reason'], 'identity_conflict')
        self.finish()
        self.assertEqual(self.core.ingest(payload(deadline_ms=100))['reason'], 'identity_conflict')
        self.assertEqual(self.core.snapshot()['identity_conflicts'], 2)

    def test_ttl_completion_boundary_and_no_refresh_on_duplicate(self):
        core = LiveProcessor(clock=self.clock, dedup_ttl=1)
        core.ingest(payload())
        self.finish(core)  # completes at .02
        self.clock.value = .5
        self.assertEqual(core.ingest(payload())['status'], 'duplicate')
        self.clock.value = 1.02
        self.assertEqual(core.ingest(payload())['status'], 'admitted')
        self.assertEqual(core.snapshot()['ttl_expirations'], 1)

    def test_bounded_cache_eviction(self):
        core = LiveProcessor(clock=self.clock, dedup_capacity=1)
        for name in ('a', 'b'):
            core.ingest(payload(name))
            self.finish(core)
        self.assertEqual(core.snapshot()['cache_evictions'], 1)
        self.assertEqual(core.ingest(payload('a'))['status'], 'admitted')
        self.assertEqual(core.ingest(payload('b'))['status'], 'duplicate')

    def test_full_rejection_does_not_poison_retry_and_zero_buffer(self):
        core = LiveProcessor(clock=self.clock, capacity=0)
        self.assertEqual(core.ingest(payload('a'))['status'], 'admitted')
        self.assertEqual(core.ingest(payload('b'))['reason'], 'queue_full')
        item = core.take()
        self.assertEqual(core.ingest(payload('b'))['reason'], 'queue_full')
        core.complete(item)
        self.assertEqual(core.ingest(payload('b'))['status'], 'admitted')
        self.assertEqual(core.snapshot()['max_waiting'], 0)

    def test_deadline_boundary_and_measurement(self):
        self.core.ingest(payload(deadline_ms=20))
        row = self.finish()
        self.assertEqual(row['deadline_status'], 'met')
        self.assertEqual(row['local_latency_ms'], 20)
        self.assertEqual(row['wait_ms'], 0)
        self.assertEqual(row['service_ms'], 20)
        self.core.ingest(payload('b', deadline_ms=1))
        self.assertEqual(self.finish()['deadline_status'], 'missed')

    def test_shared_selector_matches_simulator_for_all_policies(self):
        for policy in POLICIES:
            clock = Clock()
            core = LiveProcessor(policy, clock=clock, capacity=3, aging_config=AgingConfig(.01, .1, .02))
            events = [Alert(i, 0, p, d/1000) for i, (p, d) in enumerate([(2, 5), (0, 20), (1, 100), (2, 500)])]
            for e in events:
                core.ingest(payload(str(e.id), e.priority, deadline_ms=e.deadline_s*1000))
            selected = []
            while (item := core.take(block=False)) is not None:
                selected.append(item.event.alert.id)
                clock.value += .02
                core.complete(item)
            simulation = run_simulation(events, policy, .02, queue_capacity=3, aging_config=AgingConfig(.01, .1, .02))
            self.assertEqual(selected, [c.event.id for c in simulation.completions], policy)
            self.assertEqual(core.snapshot()['guard_activations'], simulation.guard_activations)

    def test_close_drains_pending_and_unblocks_idle_worker(self):
        for i in range(3):
            self.core.ingest(payload(str(i)))
        self.core.close()
        self.assertEqual(self.core.ingest(payload('new'))['reason'], 'closed')
        for _ in range(3):
            self.finish()
        self.assertIsNone(self.core.take())
        self.assertEqual(self.core.snapshot()['unfinished'], 0)
        empty = LiveProcessor()
        thread = threading.Thread(target=empty.take, daemon=True)
        thread.start()
        empty.close()
        thread.join(1)
        self.assertFalse(thread.is_alive())

    def test_single_worker_and_stale_completion_protection(self):
        self.core.ingest(payload())
        item = self.core.take()
        with self.assertRaises(RuntimeError):
            self.core.take(block=False)
        self.core.complete(item)
        with self.assertRaises(ValueError):
            self.core.complete(item)

    def test_concurrent_duplicate_admission_and_accounting(self):
        threads = [threading.Thread(target=self.core.ingest, args=(payload(),)) for _ in range(30)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(1)
        stats = self.core.snapshot()
        self.assertEqual(stats['admitted'], 1)
        self.assertEqual(stats['duplicate_messages'], 29)
        self.assertEqual(stats['reserved_ids'], 1)
        self.core.ingest('{}')
        stats = self.core.snapshot()
        self.assertEqual(stats['received_messages'], sum(stats[k] for k in ('admitted', 'duplicate_messages',
            'identity_conflicts', 'invalid_messages', 'rejected_queue_full', 'rejected_closed')))

    def test_validation(self):
        for kwargs in (dict(capacity=-1), dict(capacity=True), dict(dedup_capacity=0),
                       dict(dedup_ttl=0), dict(aging_interval=0), dict(policy='bad'),
                       dict(policy='adaptive_guarded', capacity=0)):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                LiveProcessor(**kwargs)

    def test_deadline_guard_overrides_promoted_routine_and_counts(self):
        core = LiveProcessor('adaptive_guarded', clock=self.clock, capacity=2,
                             aging_config=AgingConfig(.1, .1, .02))
        core.ingest(payload('blocker', priority=0))
        blocker = core.take()
        core.ingest(payload('routine', deadline_ms=1))
        self.clock.value = .5
        core.ingest(payload('urgent', priority=0, deadline_ms=15))
        core.complete(blocker)
        selected = core.take()
        self.assertEqual(selected.event.wire['id'], 'urgent')
        self.assertEqual(core.snapshot()['guard_activations'], 1)
