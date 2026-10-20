import unittest
import csv
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from iot_alerts.simulator import Alert, run_simulation


class FoundationTests(unittest.TestCase):
    def test_capacity_excludes_worker_and_never_evicts_waiting_work(self):
        events = [Alert(0, 0, 2), Alert(1, .1, 2), Alert(2, .2, 0)]
        for policy in ('fifo', 'priority', 'aging'):
            result = run_simulation(events, policy, 1, queue_capacity=1)
            self.assertEqual([c.event.id for c in result.completions], [0, 1])
            self.assertEqual([r.event.id for r in result.rejections], [2])
            self.assertEqual(result.rejections[0].rejected_at_s, .2)
            self.assertEqual(result.rejections[0].reason, 'queue_full')
            self.assertEqual(result.max_waiting, 1)
            self.assertEqual((result.generated, result.admitted, result.completed, result.dropped), (3, 2, 2, 1))

    def test_completion_before_arrival_and_dispatch_after_admission(self):
        events = [Alert(0, 0, 2), Alert(1, .1, 2), Alert(2, 1, 0)]
        result = run_simulation(events, 'priority', 1, queue_capacity=1)
        self.assertEqual([c.event.id for c in result.completions], [0, 2, 1])
        self.assertEqual(result.dropped, 0)
        self.assertEqual([c.start_s for c in result.completions], [0, 1, 2])

    def test_zero_capacity_allows_service_but_no_waiting(self):
        events = [Alert(0, 0, 2), Alert(1, .5, 0), Alert(2, 1, 1)]
        result = run_simulation(events, 'fifo', 1, queue_capacity=0)
        self.assertEqual([c.event.id for c in result.completions], [0, 2])
        self.assertEqual([r.event.id for r in result.rejections], [1])
        self.assertEqual(result.max_waiting, 0)

    def test_simultaneous_batch_has_deterministic_admission_and_priority(self):
        events = [Alert(2, 0, 0), Alert(0, 0, 2), Alert(1, 0, 1)]
        result = run_simulation(events, 'priority', 1, queue_capacity=1)
        # Admission uses (arrival, id), not urgency; capacity is one worker + one wait.
        self.assertEqual([c.event.id for c in result.completions], [1, 0])
        self.assertEqual([r.event.id for r in result.rejections], [2])

    def test_per_event_service_and_relative_deadline(self):
        events = [Alert(0, 2, 2, deadline_s=.5, service_time_s=.25),
                  Alert(1, 2.1, 0, deadline_s=.1, service_time_s=.5), Alert(2, 2.2, 1)]
        result = run_simulation(events, 'priority', 1)
        self.assertEqual([c.start_s for c in result.completions], [2, 2.25, 2.75])
        self.assertEqual([c.finish_s for c in result.completions], [2.25, 2.75, 3.75])
        self.assertAlmostEqual(result.completions[1].wait_s, .15)
        self.assertEqual(events[0].absolute_deadline_s, 2.5)
        self.assertIsNone(events[2].absolute_deadline_s)
        # Missed deadlines remain metadata: work still completes.
        self.assertGreater(result.completions[1].finish_s, events[1].absolute_deadline_s)

    def test_accounting_and_capacity_for_every_policy(self):
        events = [Alert(i, i*.1, i%3, service_time_s=.25 if i%2 else .5) for i in range(100)]
        for policy in ('fifo', 'priority', 'aging'):
            result = run_simulation(events, policy, queue_capacity=3)
            completed = {c.event.id for c in result.completions}
            rejected = {r.event.id for r in result.rejections}
            self.assertEqual(completed | rejected, set(range(100)))
            self.assertFalse(completed & rejected)
            self.assertEqual(result.generated, result.completed + result.dropped)
            self.assertLessEqual(result.max_waiting, 3)
            self.assertTrue(all(c.wait_s >= 0 for c in result.completions))
            for a, b in zip(result.completions, result.completions[1:]):
                self.assertGreaterEqual(b.start_s, a.finish_s)

    def test_tiny_aging_interval_saturates_without_overflow(self):
        result = run_simulation([Alert(0, 0, 2), Alert(1, .1, 2)], 'aging', 1,
                                aging_interval=1e-320)
        self.assertEqual([c.event.id for c in result.completions], [0, 1])

    def test_cli_exports_every_outcome_and_preserves_rejection_nulls(self):
        with tempfile.TemporaryDirectory() as directory:
            subprocess.run([sys.executable, '-m', 'iot_alerts.foundation', '--count', '100',
                            '--rate', '1000', '--queue-capacity', '0', '--deadline-ms', '100',
                            '--output', directory], check=True, capture_output=True)
            with (Path(directory)/'events.csv').open(newline='') as stream:
                rows = list(csv.DictReader(stream))
            config = json.loads((Path(directory)/'config.json').read_text())
            self.assertEqual(len(rows), 100)
            self.assertEqual(len({r['id'] for r in rows}), 100)
            drops = [r for r in rows if r['status'] == 'dropped']
            self.assertGreater(len(drops), 0)
            self.assertEqual(len(drops), config['dropped'])
            self.assertEqual(config['completed'] + config['dropped'], 100)
            self.assertTrue(all(r['finish_s'] == '' and r['latency_s'] == '' for r in drops))
            self.assertTrue(all(r['deadline_s'] == '0.1' for r in rows))

    def test_empty_and_idle_time(self):
        result = run_simulation([], 'fifo', queue_capacity=0)
        self.assertEqual((result.generated, result.completed, result.dropped, result.max_waiting), (0, 0, 0, 0))
        result = run_simulation([Alert(0, 4, 0), Alert(1, 10, 2)], 'aging')
        self.assertEqual([c.wait_s for c in result.completions], [0, 0])

    def test_invalid_events_and_run_configuration(self):
        for overrides in ({'arrival': -1}, {'arrival': float('nan')}, {'arrival': float('inf')},
                          {'priority': True}, {'priority': 3}, {'id': 1.5},
                          {'deadline_s': 0}, {'service_time_s': -1}, {'service_time_s': float('inf')}):
            with self.subTest(overrides=overrides), self.assertRaises(ValueError):
                Alert(**(dict(id=0, arrival=0, priority=0) | overrides))
        for capacity in (-1, 1.5, True):
            with self.assertRaises(ValueError):
                run_simulation([], 'fifo', queue_capacity=capacity)
        for service in (0, float('nan'), float('inf')):
            with self.assertRaises(ValueError):
                run_simulation([], 'fifo', service)
        with self.assertRaises(ValueError):
            run_simulation([Alert(0, 0, 0), Alert(0, 1, 1)], 'fifo')
        with self.assertRaises(ValueError):
            run_simulation([], 'unknown')


if __name__ == '__main__':
    unittest.main()
