import csv
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from iot_alerts.experiment import workload
from iot_alerts.workloads import generate_workload, load_trace, save_trace, trace_fingerprint


class WorkloadTests(unittest.TestCase):
    def test_default_preserves_legacy_arrivals_and_classes(self):
        events = generate_workload(100, 90, 42)
        legacy = workload(100, 90, 42)
        self.assertEqual([(e.id, e.arrival, e.priority) for e in events],
                         [(e.id, e.arrival, e.priority) for e in legacy])
        self.assertEqual(events, generate_workload(100, 90, 42))
        self.assertNotEqual(trace_fingerprint(events), trace_fingerprint(generate_workload(100, 90, 43)))

    def test_controlled_burst_compresses_only_selected_interarrivals(self):
        normal = generate_workload(20, 100, 7)
        burst = generate_workload(20, 100, 7, traffic='burst', burst_start=.25, burst_end=.5, burst_multiplier=4)
        old_a = old_b = 0
        for index, (a, b) in enumerate(zip(normal, burst)):
            multiplier = 4 if 5 <= index < 10 else 1
            self.assertAlmostEqual(a.arrival-old_a, (b.arrival-old_b)*multiplier)
            self.assertEqual(a.priority, b.priority)
            old_a, old_b = a.arrival, b.arrival
        self.assertEqual(len(normal), len(burst))
        self.assertLess(burst[-1].arrival, normal[-1].arrival)

    def test_weights_deadlines_and_service_draws_are_independent(self):
        events = generate_workload(50, priority_weights=(0, 1, 0), deadlines=(.1, .5, 2))
        self.assertTrue(all(e.priority == 1 and e.deadline_s == .5 for e in events))
        baseline = generate_workload(50)
        self.assertEqual([e.arrival for e in events], [e.arrival for e in baseline])
        for distribution in ('uniform', 'exponential'):
            variable = generate_workload(50, service_distribution=distribution)
            self.assertEqual(variable, generate_workload(50, service_distribution=distribution))
            self.assertEqual([(e.arrival, e.priority) for e in variable], [(e.arrival, e.priority) for e in baseline])
            self.assertGreater(len({e.service_time_s for e in variable}), 1)
            self.assertTrue(all(math.isfinite(e.service_time_s) and e.service_time_s > 0 for e in variable))
            if distribution == 'uniform':
                self.assertTrue(all(.005 <= e.service_time_s <= .015 for e in variable))

    def test_exact_trace_roundtrip_with_missing_deadlines(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'trace.csv'
            original = generate_workload(100, traffic='burst', service_distribution='uniform', deadlines=(.1, None, 2))
            save_trace(path, original)
            loaded = load_trace(path)
            self.assertEqual(loaded, original)
            self.assertEqual(trace_fingerprint(loaded), trace_fingerprint(original))

    def test_invalid_parameters_and_malformed_traces(self):
        invalid = [dict(count=0), dict(seed=True), dict(rate=float('inf')),
                   dict(priority_weights=(0, 0, 0)), dict(priority_weights=(-1, 2, 7)),
                   dict(priority_weights=(1, float('nan'), 7)), dict(uniform_spread=1),
                   dict(burst_start=.8, burst_end=.2), dict(burst_multiplier=.5),
                   dict(service_distribution='exponential', service_time=1e-320)]
        for kwargs in invalid:
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                generate_workload(**kwargs)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'bad.csv'
            header = 'id,arrival,priority,deadline_s,service_time_s\n'
            for text in ['bad,columns\n', header, header+'0,0,0,,\n',
                         header+'0,nan,0,,0.01\n', header+'0,0,0,,0.01\n0,1,0,,0.01\n',
                         header+'0,0,0,,0.01,extra\n']:
                path.write_text(text)
                with self.assertRaises(ValueError):
                    load_trace(path)

    def test_generated_and_replayed_runs_have_identical_results(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            generated, replay = root/'generated', root/'replay'
            subprocess.run([sys.executable, '-m', 'iot_alerts.foundation', '--policy', 'all',
                '--count', '100', '--traffic', 'burst', '--priority-weights', '3', '2', '5',
                '--service-distribution', 'uniform', '--deadlines-ms', '100', '500', '2000',
                '--queue-capacity', '5', '--output', str(generated)], check=True, capture_output=True)
            subprocess.run([sys.executable, '-m', 'iot_alerts.foundation', '--policy', 'all',
                '--trace-input', str(generated/'workload.csv'), '--seed', '999', '--queue-capacity', '5',
                '--output', str(replay)], check=True, capture_output=True)
            self.assertEqual((generated/'summary.json').read_bytes(), (replay/'summary.json').read_bytes())
            self.assertEqual((generated/'workload.csv').read_bytes(), (replay/'workload.csv').read_bytes())
            config = json.loads((replay/'config.json').read_text())
            self.assertEqual(config['input_mode'], 'replay')
            self.assertFalse(config['generation_settings_applied'])
            self.assertEqual(config['input_event_count'], 100)
            for policy in ('fifo', 'priority', 'aging', 'edf'):
                self.assertEqual((generated/policy/'events.csv').read_bytes(), (replay/policy/'events.csv').read_bytes())


if __name__ == '__main__':
    unittest.main()
