import csv
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from iot_alerts.metrics import deadline_status, summarize
from iot_alerts.simulator import Alert, Rejection, SimulationResult, run_simulation


class MetricsTests(unittest.TestCase):
    def test_hand_calculated_loss_deadline_and_latency(self):
        events = [Alert(0, 0, 0, .25), Alert(1, .125, 0, .125),
                  Alert(2, .1875, 0, .125), Alert(3, .75, 1),
                  Alert(4, .875, 2, .25), Alert(5, .9375, 2)]
        result = run_simulation(events, 'fifo', .25, queue_capacity=1)
        overall, high, medium, low = summarize(result)
        self.assertEqual((overall['generated'], overall['admitted'], overall['completed'], overall['dropped']), (6, 4, 4, 2))
        self.assertEqual(overall['deadline_generated'], 4)
        self.assertEqual(overall['deadline_admitted'], 3)
        self.assertEqual(overall['deadline_met'], 1)
        self.assertEqual(overall['deadline_missed_completed'], 2)
        self.assertEqual(overall['deadline_dropped'], 1)
        self.assertEqual(overall['deadline_failed'], 3)
        self.assertEqual(overall['without_deadline'], 2)
        self.assertAlmostEqual(overall['drop_fraction'], 1/3)
        self.assertEqual(overall['deadline_failure_fraction'], .75)
        self.assertAlmostEqual(overall['admitted_deadline_miss_fraction'], 2/3)
        self.assertEqual(overall['mean_latency_ms'], 312.5)
        self.assertEqual(overall['p95_latency_ms'], 375)
        self.assertEqual(overall['p99_latency_ms'], 375)
        self.assertEqual(overall['max_wait_ms'], 125)
        self.assertEqual(overall['latency_samples'], 4)
        self.assertEqual(overall['observation_duration_s'], 1.25)
        self.assertEqual(overall['throughput_per_s'], 3.2)
        self.assertAlmostEqual(high['deadline_failure_fraction'], 2/3)
        self.assertIsNone(medium['deadline_failure_fraction'])
        self.assertEqual(low['dropped'], 1)
        self.assertEqual(low['deadline_dropped'], 0)
        for key in ('generated', 'admitted', 'completed', 'dropped', 'deadline_failed', 'deadline_generated'):
            self.assertEqual(overall[key], sum(r[key] for r in (high, medium, low)))
        self.assertAlmostEqual(overall['throughput_per_s'], sum(r['throughput_per_s'] for r in (high, medium, low)))

    def test_exact_deadline_counts_as_success_without_hidden_tolerance(self):
        event = Alert(0, 1, 0, .25)
        self.assertEqual(deadline_status(event, 1.25), 'met')
        self.assertEqual(deadline_status(event, math.nextafter(1.25, math.inf)), 'missed')
        self.assertEqual(deadline_status(event), 'dropped')
        self.assertEqual(deadline_status(Alert(1, 0, 0), 1), 'not_set')

    def test_empty_run_and_absent_classes_are_not_fake_successes(self):
        for row in summarize(run_simulation([], 'fifo')):
            self.assertEqual(row['generated'], 0)
            self.assertEqual(row['latency_samples'], 0)
            for key in ('drop_fraction', 'deadline_failure_fraction', 'admitted_deadline_miss_fraction',
                        'mean_latency_ms', 'p95_latency_ms', 'p99_latency_ms', 'max_wait_ms', 'throughput_per_s'):
                self.assertIsNone(row[key], key)
        rows = summarize(run_simulation([Alert(0, 0, 0, .5)], 'fifo', .25))
        self.assertEqual(rows[1]['deadline_failure_fraction'], 0)
        self.assertIsNone(rows[2]['deadline_failure_fraction'])

    def test_no_completions_does_not_hide_drops(self):
        result = SimulationResult('fifo', 2, (), (Rejection(Alert(0, 0, 0, 1), 0),
                                                 Rejection(Alert(1, 1, 0, 1), 1)), 0)
        overall = summarize(result)[0]
        self.assertEqual(overall['drop_fraction'], 1)
        self.assertEqual(overall['deadline_failure_fraction'], 1)
        self.assertIsNone(overall['admitted_deadline_miss_fraction'])
        self.assertIsNone(overall['p95_latency_ms'])
        self.assertEqual(overall['throughput_per_s'], 0)

    def test_nearest_rank_percentiles_and_common_window(self):
        events = [Alert(i, i*100, 2, service_time_s=i+1) for i in range(20)]
        overall = summarize(run_simulation(events, 'fifo'))[0]
        self.assertEqual(overall['p95_latency_ms'], 19000)
        self.assertEqual(overall['p99_latency_ms'], 20000)
        self.assertEqual(overall['mean_latency_ms'], 10500)
        self.assertEqual(overall['max_wait_ms'], 0)
        self.assertEqual(overall['observation_duration_s'], 1920)

    def test_unaccounted_result_is_rejected(self):
        with self.assertRaises(ValueError):
            summarize(SimulationResult('fifo', 1, (), (), 0))

    def test_cli_exports_agree_and_missing_deadlines_are_null(self):
        with tempfile.TemporaryDirectory() as directory:
            for deadlines in ([], ['--deadlines-ms', '20', '50', '100']):
                subprocess.run([sys.executable, '-m', 'iot_alerts.foundation', '--count', '100',
                                '--rate', '1000', '--queue-capacity', '0', '--output', directory,
                                *deadlines], check=True, capture_output=True)
                summary = json.loads((Path(directory)/'summary.json').read_text())
                with (Path(directory)/'summary.csv').open(newline='') as stream:
                    csv_rows = list(csv.DictReader(stream))
                with (Path(directory)/'events.csv').open(newline='') as stream:
                    events = list(csv.DictReader(stream))
                overall = summary[0]
                self.assertEqual(int(csv_rows[0]['dropped']), sum(e['status']=='dropped' for e in events))
                self.assertEqual(overall['generated'], 100)
                self.assertEqual(overall['completed']+overall['dropped'], 100)
                if not deadlines:
                    self.assertIsNone(overall['deadline_failure_fraction'])
                    self.assertEqual(csv_rows[0]['deadline_failure_fraction'], '')
                    self.assertTrue(all(e['deadline_status']=='not_set' for e in events))
                else:
                    self.assertEqual(overall['deadline_generated'], 100)
                    self.assertTrue(any(e['deadline_status']=='dropped' for e in events))
                    self.assertGreaterEqual(overall['deadline_failure_fraction'], overall['drop_fraction'])
                self.assertNotIn('NaN', (Path(directory)/'summary.json').read_text())
            invalid = subprocess.run([sys.executable, '-m', 'iot_alerts.foundation',
                                      '--deadline-ms', '1', '--deadlines-ms', '1', '2', '3'], capture_output=True)
            self.assertNotEqual(invalid.returncode, 0)


if __name__ == '__main__':
    unittest.main()
