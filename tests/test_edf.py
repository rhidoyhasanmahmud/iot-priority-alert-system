import csv
import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest
from iot_alerts.simulator import Alert, run_simulation


class EDFTests(unittest.TestCase):
    def test_uses_absolute_not_relative_deadlines_and_does_not_preempt(self):
        events = [Alert(0, 0, 2, 10), Alert(1, .25, 2, 2), Alert(2, .75, 0, 1.75)]
        result = run_simulation(events, 'edf', 1)
        # Absolute deadlines: 2.25 then 2.5, despite later event's shorter budget.
        self.assertEqual([c.event.id for c in result.completions], [0, 1, 2])
        self.assertEqual([c.start_s for c in result.completions], [0, 1, 2])
        self.assertEqual(result.completions[0].finish_s, 1)

    def test_missing_deadlines_last_ties_by_arrival_then_id(self):
        events = [Alert(0, 0, 0), Alert(1, .125, 0), Alert(4, .5, 0, 1.5),
                  Alert(3, .25, 2, 1.75), Alert(2, .25, 2, 1.75)]
        result = run_simulation(events, 'edf', 1)
        self.assertEqual([c.event.id for c in result.completions], [0, 2, 3, 4, 1])

    def test_no_deadlines_reduces_to_fifo(self):
        events = [Alert(2, 0, 0), Alert(0, 0, 2), Alert(1, .25, 0)]
        a = run_simulation(events, 'edf', 1)
        b = run_simulation(events, 'fifo', 1)
        self.assertEqual(a.completions, b.completions)

    def test_overdue_work_is_not_expired_and_admission_does_not_favor_edf(self):
        events = [Alert(0, 0, 2, .125), Alert(1, .25, 2, .125), Alert(2, .5, 0, .01)]
        result = run_simulation(events, 'edf', 1, queue_capacity=1)
        self.assertEqual([c.event.id for c in result.completions], [0, 1])
        self.assertEqual([r.event.id for r in result.rejections], [2])
        self.assertGreater(result.completions[1].finish_s, events[1].absolute_deadline_s)

    def test_comparison_cli_reuses_exact_trace_and_exports_every_policy(self):
        with tempfile.TemporaryDirectory() as directory:
            subprocess.run([sys.executable, '-m', 'iot_alerts.foundation', '--policy', 'all',
                '--count', '100', '--deadlines-ms', '100', '500', '2000', '--queue-capacity', '5',
                '--aging-ms', '25', '--output', directory], check=True, capture_output=True)
            root = Path(directory)
            config = json.loads((root/'config.json').read_text())
            self.assertEqual(len(json.loads((root/'summary.json').read_text())), 16)
            with (root/'workload.csv').open(newline='') as stream:
                trace = {r['id']: r for r in csv.DictReader(stream)}
            for policy in ('fifo', 'priority', 'aging', 'edf'):
                settings = json.loads((root/policy/'config.json').read_text())
                self.assertEqual(settings['workload_sha256'], config['workload_sha256'])
                self.assertEqual(settings['aging_ms'], 25)
                with (root/policy/'events.csv').open(newline='') as stream:
                    rows = list(csv.DictReader(stream))
                self.assertEqual(len(rows), 100)
                for row in rows:
                    self.assertEqual({k: row[k] for k in trace[row['id']]}, trace[row['id']])


if __name__ == '__main__':
    unittest.main()
