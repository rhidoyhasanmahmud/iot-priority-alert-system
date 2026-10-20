import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from iot_alerts import study
from iot_alerts.workloads import load_trace, trace_fingerprint


class StudyTests(unittest.TestCase):
    def initialize(self, path):
        return study.initialize(path, 'smoke')

    def run_phase(self, path, phase):
        with contextlib.redirect_stdout(io.StringIO()):
            return study.run_phase(path, phase)

    def synthetic_rows(self, plan, *, undefined=False, infeasible=False):
        rows = []
        for scenario in study.scenarios(plan):
            for seed in plan['tuning_seeds']:
                rows.append(dict(setting_id='priority', scenario_id=scenario['id'], seed=seed,
                                 priority=0, deadline_failure_fraction=0.))
                for setting in study.tuning_settings(plan):
                    # All settings tie, exposing the numeric parameter tie-break.
                    rows.extend([
                        dict(setting_id=setting['id'], scenario_id=scenario['id'], seed=seed,
                             priority=0, deadline_failure_fraction=.5 if infeasible else 0.),
                        dict(setting_id=setting['id'], scenario_id=scenario['id'], seed=seed,
                             priority=2, p95_wait_ms=None if undefined else 10.)])
        return rows

    def test_primary_matrix_and_seed_split(self):
        plan = study.make_plan()
        self.assertEqual(len(study.scenarios(plan)), 48)
        self.assertEqual(len(study.tuning_settings(plan)), 15)
        self.assertEqual(plan['tuning_seeds'], list(range(1001, 1011)))
        self.assertEqual(plan['evaluation_seeds'], list(range(2001, 2031)))
        self.assertEqual(len(study.scenarios(plan))*len(plan['evaluation_seeds'])*8, 11520)

    def test_overlap_duplicates_and_invalid_capacity_rejected(self):
        for change in ({'evaluation_seeds': [1001]}, {'tuning_seeds': [1001, 1001]},
                       {'tuning_seeds': [1]}, {'capacities': [0]}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                study.validate_plan(study.make_plan() | change)

    def test_plan_exclusive_and_checksum_and_environment(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary)/'study'
            self.initialize(path)
            with self.assertRaises(FileExistsError):
                self.initialize(path)
            with patch.object(study, 'source_identity', return_value={'changed': True}):
                with self.assertRaisesRegex(ValueError, 'Source or Python'):
                    study.load_registration(path)
            plan = study.read_json(path/'plan.json')
            plan['count'] += 1
            study.write_json(path/'plan.json', plan)
            with self.assertRaisesRegex(ValueError, 'plan checksum'):
                study.load_registration(path)

    def test_no_evaluation_or_partial_tuning_before_freeze(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary)/'study'
            self.initialize(path)
            for partial in (False, True):
                if partial:
                    (path/'tune').mkdir()
                    study.write_json(path/'tune/selection.json', {'status': 'ready'})
                with patch.object(study, 'generate_workload', wraps=study.generate_workload) as generate:
                    with self.assertRaises(FileNotFoundError):
                        self.run_phase(path, 'evaluate')
                    self.assertFalse((path/'evaluate').exists())
                    self.assertFalse(any(call.args[2] in (4101, 4102) for call in generate.call_args_list))

    def test_selection_tie_undefined_and_infeasible(self):
        plan = study.make_plan('smoke')
        result = study.select_parameters(plan, self.synthetic_rows(plan))
        self.assertEqual(result['status'], 'ready')
        self.assertEqual(result['selected']['adaptive_guarded']['minimum_s'], 1.)
        self.assertEqual(result['selected']['fixed_guarded']['fixed_interval_s'], 1.)
        for kwargs in ({'undefined': True}, {'infeasible': True}):
            failed = study.select_parameters(plan, self.synthetic_rows(plan, **kwargs))
            self.assertEqual(failed['status'], 'infeasible')
            self.assertTrue(all(value is None for value in failed['selected'].values()))

    def test_scenario_equal_weight_not_pooled_events(self):
        plan = study.make_plan('smoke')
        rows = self.synthetic_rows(plan)
        for row in rows:
            if row['priority'] == 2:
                row['p95_wait_ms'] = 0 if row['scenario_id'] == 's000' else 100
        result = study.select_parameters(plan, rows)
        self.assertTrue(all(score['mean_low_p95_wait_ms'] == 50 for score in result['scores']))
        self.assertEqual(study.paired_upper([0., 0.], 200, 1), 0.)
        self.assertEqual(study.paired_upper([.5, .5], 200, 1), .5)

    def test_smoke_end_to_end_pairing_freeze_and_artifact_verification(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary)/'study'
            registration = self.initialize(path)
            self.assertEqual(registration['tuning_runs'], 20)
            tuning = self.run_phase(path, 'tune')
            self.assertEqual(tuning['run_count'], 20)
            selection_hash = study.file_hash(path/'tune/selection.json')
            evaluation = self.run_phase(path, 'evaluate')
            self.assertEqual(evaluation['run_count'], 32)
            self.assertEqual(evaluation['selection_sha256'], selection_hash)
            self.assertEqual(study.file_hash(path/'tune/selection.json'), selection_hash)
            rows = study.read_json(path/'evaluate/run_metrics.json')
            self.assertEqual({r['seed'] for r in rows}, {4101, 4102})
            for scenario in study.scenarios(study.make_plan('smoke')):
                for seed in (4101, 4102):
                    paired = [r for r in rows if r['scenario_id'] == scenario['id'] and r['seed'] == seed]
                    self.assertEqual(len(paired), 8*4)
                    trace = path/'evaluate'/scenario['id']/str(seed)/'workload.csv'
                    self.assertEqual({r['workload_sha256'] for r in paired}, {trace_fingerprint(load_trace(trace))})
            study.verify(path/'tune')
            study.verify(path/'evaluate')
            study.verify_study(path)
            marker = study.read_json(path/'evaluate/complete.json')
            altered = marker | {'plan_sha256': 'wrong'}
            study.write_json(path/'evaluate/complete.json', altered)
            with self.assertRaisesRegex(ValueError, 'completion marker'):
                study.verify_study(path)
            study.write_json(path/'evaluate/complete.json', marker)
            config_file = next((path/'evaluate').rglob('config.json'))
            config = study.read_json(config_file)
            self.assertEqual(config['evidence_label'], 'engineering-smoke-only-not-paper-evidence')
            self.assertEqual(config['selection_sha256'], selection_hash)
            config['guard_activations'] = -1
            study.write_json(config_file, config)
            with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
                study.verify(path/'evaluate')
            with self.assertRaises(FileExistsError):
                self.run_phase(path, 'tune')

    def test_infeasible_selection_blocks_evaluation(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary)/'study'
            self.initialize(path)
            with patch.object(study, 'select_parameters', return_value={'status': 'infeasible', 'selected': {}, 'scores': []}):
                self.run_phase(path, 'tune')
            with self.assertRaisesRegex(ValueError, 'No feasible tuning'):
                self.run_phase(path, 'evaluate')
            self.assertFalse((path/'evaluate').exists())

    def test_modified_tuning_artifact_blocks_evaluation(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary)/'study'
            self.initialize(path)
            self.run_phase(path, 'tune')
            selection_path = path/'tune/selection.json'
            selection = study.read_json(selection_path)
            selection['status'] = 'infeasible'
            study.write_json(selection_path, selection)
            with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
                self.run_phase(path, 'evaluate')
            self.assertFalse((path/'evaluate').exists())

    def test_source_snapshot_is_preserved_and_checked(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary)/'study'
            self.initialize(path)
            snapshot = path/'source_snapshot/iot_alerts/simulator.py'
            self.assertEqual(study.file_hash(snapshot), study.file_hash(study.ROOT/'iot_alerts/simulator.py'))
            snapshot.write_text('changed')
            with self.assertRaisesRegex(ValueError, 'snapshot checksum'):
                study.load_registration(path)
