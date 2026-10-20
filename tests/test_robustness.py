import contextlib
import copy
import io
import shutil
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from iot_alerts import robustness as robust, study


class EffectTests(unittest.TestCase):
    def fixture(self):
        plan = study.make_plan('smoke')
        lookup = {}
        # Factorial response: fixed=10, occupancy=2, guard=3, interaction=4.
        values = dict(fixed_deadline=10., adaptive=12., fixed_guarded=13., adaptive_guarded=19.)
        for scenario in study.scenarios(plan):
            for seed in plan['evaluation_seeds']:
                for policy, value in values.items():
                    for priority in (0, 2):
                        lookup[(scenario['id'], seed, policy, priority)] = dict(
                            p95_wait_ms=value, deadline_failure_fraction=value/100,
                            drop_fraction=value/100, workload_sha256='same-paired-trace', run_path=policy)
        return plan, lookup

    def test_factorial_signs_and_interaction(self):
        plan, lookup = self.fixture()
        with contextlib.redirect_stdout(io.StringIO()):
            intervals, pairs = robust.effect_tables(plan, plan['evaluation_seeds'], lookup, robust.ABLATIONS)
        expected = dict(occupancy_guarded=6, occupancy_unguarded=2, guard_adaptive=7, guard_fixed=3, interaction=4)
        for row in intervals:
            if row['metric_id'] == 'routine_wait':
                self.assertEqual(row['mean_difference'], expected[row['effect']])
        self.assertEqual(len(intervals), 40)
        self.assertEqual(len(pairs), 80)
        self.assertTrue(all(r['inference'] == 'secondary_exploratory_unadjusted' for r in intervals))

    def test_missing_component_and_unpaired_trace(self):
        plan, lookup = self.fixture()
        lookup[('s000', 4101, 'adaptive_guarded', 2)]['p95_wait_ms'] = None
        with contextlib.redirect_stdout(io.StringIO()):
            intervals, _ = robust.effect_tables(plan, plan['evaluation_seeds'], lookup, robust.ABLATIONS)
        row = next(r for r in intervals if r['scenario_id'] == 's000' and r['effect'] == 'interaction' and r['metric_id'] == 'routine_wait')
        self.assertEqual(row['direction'], 'not_assessable')
        self.assertEqual(row['valid_pairs'], 1)
        lookup[('s000', 4101, 'adaptive_guarded', 2)]['workload_sha256'] = 'different'
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(ValueError):
            robust.effect_tables(plan, plan['evaluation_seeds'], lookup, robust.ABLATIONS)

    def test_one_factor_at_a_time_and_baseline_deduplication(self):
        selection = dict(selected=dict(adaptive_guarded=dict(minimum_s=.1, maximum_s=1.)))
        items = robust.sensitivity_settings(selection, .01, study.read_json(robust.PROTOCOL))
        self.assertEqual(len(items), 5)
        indexed = {item['id']: item for item in items}
        self.assertEqual(indexed['interval-0.5']['minimum_s'], .05)
        self.assertEqual(indexed['interval-0.5']['maximum_s'], .5)
        self.assertEqual(indexed['interval-0.5']['service_estimate_s'], .01)
        self.assertEqual(indexed['estimate-2']['minimum_s'], .1)
        self.assertEqual(indexed['estimate-2']['service_estimate_s'], .02)


class RobustnessIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.base = Path(cls.temporary.name)
        cls.parent = cls.base/'parent'
        with contextlib.redirect_stdout(io.StringIO()):
            study.initialize(cls.parent, 'smoke')
            study.run_phase(cls.parent, 'tune')
            study.run_phase(cls.parent, 'evaluate')

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_ablation_read_only_and_all_contrasts(self):
        before = study.inventory(self.parent)
        with contextlib.redirect_stdout(io.StringIO()):
            count = robust.analyze(self.parent, self.base/'ablation')
        self.assertEqual(count, 40)
        self.assertEqual(before, study.inventory(self.parent))
        manifest = study.read_json(self.base/'ablation/manifest.json')
        self.assertTrue(manifest['no_retuning'])
        self.assertEqual(manifest['effects'], robust.ABLATIONS)
        self.assertIn('Engineering smoke only', (self.base/'ablation/report.md').read_text())
        study.verify(self.base/'ablation')

    def test_sensitivity_lifecycle_and_pairing(self):
        output = self.base/'sensitivity'
        before = study.inventory(self.parent)
        with contextlib.redirect_stdout(io.StringIO()):
            frozen = robust.register(self.parent, output)
            self.assertFalse((output/'runs').exists())
            self.assertEqual(frozen['seeds'], [5101, 5102])
            with self.assertRaises(FileNotFoundError):
                robust.analyze(output, self.base/'premature', kind='sensitivity')
            self.assertFalse((self.base/'premature').exists())
            count = robust.execute(output)
            result = robust.analyze(output, self.base/'sensitivity-analysis', kind='sensitivity')
        self.assertEqual(count, 20)
        self.assertEqual(result, 32)
        frozen, registration = robust.load_sensitivity(output)
        lookup = robust.sensitivity_rows(output, frozen, registration)
        for scenario in study.scenarios(frozen['parent_plan']):
            for seed in frozen['seeds']:
                rows = [r for (sid, s, _, _), r in lookup.items() if sid == scenario['id'] and s == seed]
                self.assertEqual(len({r['workload_sha256'] for r in rows}), 1)
        self.assertEqual(before, study.inventory(self.parent))
        study.verify(self.base/'sensitivity-analysis')
        with self.assertRaises(FileExistsError):
            robust.execute(output)

    def test_seed_overlap_and_changed_engine_block_registration(self):
        protocol = study.read_json(robust.PROTOCOL) | dict(smoke_seeds=[4101, 4102])
        actual = robust.read_json
        def read(path):
            return protocol if Path(path) == robust.PROTOCOL else actual(path)
        with patch.object(robust, 'read_json', side_effect=read), self.assertRaisesRegex(ValueError, 'disjoint'):
            robust.register(self.parent, self.base/'leaking')
        identity = copy.deepcopy(study.source_identity())
        identity['files']['iot_alerts/simulator.py'] = 'changed'
        with patch.object(robust, 'source_identity', return_value=identity), self.assertRaisesRegex(ValueError, 'engine'):
            robust.register(self.parent, self.base/'different-engine')
        self.assertFalse((self.base/'leaking').exists())
        self.assertFalse((self.base/'different-engine').exists())

    def test_modified_plan_source_and_output_boundaries(self):
        output = self.base/'altered-registration'
        robust.register(self.parent, output)
        identity = study.source_identity() | dict(sha256='changed')
        with patch.object(robust, 'source_identity', return_value=identity), self.assertRaisesRegex(ValueError, 'Source/Python'):
            robust.execute(output)
        frozen = study.read_json(output/'plan.json')
        frozen['seeds'] = [1, 2]
        study.write_json(output/'plan.json', frozen)
        with self.assertRaisesRegex(ValueError, 'plan checksum'):
            robust.execute(output)
        with self.assertRaisesRegex(ValueError, 'outside'):
            robust.analyze(self.parent, self.parent/'ablation')
        with self.assertRaises(FileExistsError):
            robust.register(self.parent, output)

    def test_modified_sensitivity_metrics_are_rejected(self):
        output = self.base/'corrupt-results'
        with contextlib.redirect_stdout(io.StringIO()):
            robust.register(self.parent, output)
            robust.execute(output)
        rows = study.read_json(output/'runs/run_metrics.json')
        rows[0]['workload_sha256'] = 'changed'
        study.write_json(output/'runs/run_metrics.json', rows)
        frozen, registration = robust.load_sensitivity(output)
        with self.assertRaisesRegex(ValueError, 'checksum'):
            robust.sensitivity_rows(output, frozen, registration)
        # Even if an inventory is regenerated, semantic cross-links still reject it.
        study.seal(output/'runs', dict(plan_sha256=registration['plan_sha256'], run_count=registration['run_count']))
        with self.assertRaisesRegex(ValueError, 'summary or paired trace'):
            robust.sensitivity_rows(output, frozen, registration)

    def test_relative_parent_reference_survives_joint_archive_move(self):
        package = self.base/'portable'
        package.mkdir()
        shutil.copytree(self.parent, package/'parent')
        frozen = robust.register(package/'parent', package/'extension')
        self.assertFalse(Path(frozen['parent']).is_absolute())
        moved = self.base/'relocated'
        package.rename(moved)
        restored, _ = robust.load_sensitivity(moved/'extension')
        self.assertEqual((moved/'extension'/restored['parent']).resolve(), moved/'parent')
