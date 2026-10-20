import contextlib
import copy
import importlib.util
import io
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from iot_alerts import analysis, study


class IntervalTests(unittest.TestCase):
    def test_paired_offset_avoids_unpaired_variance(self):
        target, reference = [110., 1010., 10010.], [100., 1000., 10000.]
        result = analysis.paired_interval([a-b for a, b in zip(target, reference)], 1000, 7)
        self.assertEqual((result['mean_difference'], result['ci_low'], result['ci_high']), (10., 10., 10.))
        self.assertEqual(result['valid_pairs'], 3)

    def test_bootstrap_exact_two_point_distribution_and_determinism(self):
        result = analysis.paired_interval([-2., 2.], 10000, 19)
        self.assertEqual(result['mean_difference'], 0)
        self.assertEqual((result['ci_low'], result['ci_high']), (-2., 2.))
        self.assertEqual(result, analysis.paired_interval([-2., 2.], 10000, 19))

    def test_missing_pair_never_silently_dropped(self):
        result = analysis.paired_interval([None, -10., -5.], 1000, 1)
        self.assertIsNone(result['mean_difference'])
        self.assertIsNone(result['ci_high'])
        self.assertEqual(result['valid_pairs'], 2)
        self.assertEqual(result['expected_pairs'], 3)
        self.assertEqual(analysis.interval_decision('routine_wait', result, .01), 'not_assessable')
        self.assertEqual(analysis.paired_interval([1.], 100, 1)['interval_status'], 'insufficient_pairs')
        self.assertEqual(analysis.paired_interval([], 100, 1)['interval_status'], 'insufficient_pairs')

    def test_invalid_numbers_and_resamples(self):
        for value in (math.nan, math.inf, True, '1'):
            with self.assertRaises(ValueError):
                analysis.paired_interval([value, 1.], 100, 1)
        for value in (0, -1, True):
            with self.assertRaises(ValueError):
                analysis.paired_interval([1., 2.], value, 1)

    def test_decision_boundaries(self):
        interval = dict(interval_status='available', ci_low=0, ci_high=.01)
        self.assertEqual(analysis.interval_decision('urgent_failure', interval, .01), 'within_budget')
        self.assertEqual(analysis.interval_decision('urgent_failure', interval, 0), 'inconclusive')
        zero = interval | dict(ci_high=0)
        self.assertEqual(analysis.interval_decision('routine_wait', zero, .01), 'no_difference_observed')
        self.assertEqual(analysis.interval_decision('routine_drop', zero, .01), 'no_increase_supported')
        positive = interval | dict(ci_low=.02, ci_high=.03)
        self.assertEqual(analysis.interval_decision('urgent_failure', positive, .01), 'exceeds_budget')
        self.assertEqual(analysis.interval_decision('routine_wait', positive, .01), 'increase_supported')
        negative = interval | dict(ci_low=-2, ci_high=-1)
        self.assertEqual(analysis.interval_decision('routine_wait', negative, .01), 'reduction_supported')

    def test_descriptive_summary_is_mean_of_run_percentiles(self):
        plan = study.make_plan('smoke')
        rows = [dict(scenario_id='s000', policy='fifo', priority=2, **{name: value for name in analysis.METRICS})
                for value in (10., 90.)]
        summary = analysis.summarize_policies(plan, rows)
        self.assertTrue(all(row['mean_of_run_metric'] == 50 for row in summary))
        rows[1]['p95_wait_ms'] = None
        row = next(r for r in analysis.summarize_policies(plan, rows) if r['metric'] == 'p95_wait_ms')
        self.assertEqual(row['mean_of_run_metric'], 10)
        self.assertFalse(row['complete'])
        self.assertEqual(row['defined_runs'], 1)


class AnalysisIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.base = Path(cls.temporary.name)
        cls.input = cls.base/'study'
        with contextlib.redirect_stdout(io.StringIO()):
            study.initialize(cls.input, 'smoke')
            study.run_phase(cls.input, 'tune')
            study.run_phase(cls.input, 'evaluate')
        cls.plan, cls.registration = study.load_registration(cls.input)
        cls.selection = study.read_json(cls.input/'tune/selection.json')
        cls.rows = study.read_json(cls.input/'evaluate/run_metrics.json')

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def validate(self, rows):
        return analysis.validate_rows(self.plan, self.registration, self.selection, rows, self.input)

    def test_complete_grid_paired_seed_paths_and_smoke_label(self):
        lookup = self.validate(self.rows)
        comparisons, pairs, assessments, sensitivity = analysis.compare(self.plan, lookup)
        self.assertEqual(len(comparisons), 8)
        self.assertEqual(len(pairs), 16)
        self.assertEqual(len(sensitivity), 8)
        self.assertTrue(all(r['valid_pairs'] == 2 for r in comparisons))
        self.assertTrue(all(r['inference'] == 'exploratory_unadjusted' for r in comparisons))
        self.assertTrue(all(r['interpretation'] == 'engineering_only_no_research_conclusion' for r in assessments))
        self.assertEqual({r['seed'] for r in pairs}, {4101, 4102})
        self.assertTrue(all(r['retuned'] is False for r in sensitivity))

    def test_missing_duplicate_unexpected_and_tuning_rows_rejected(self):
        for changed in (self.rows[:-1], self.rows+[self.rows[0]],
                        [self.rows[0] | {'seed': 3101}, *self.rows[1:]],
                        [self.rows[0] | {'phase': 'tune'}, *self.rows[1:]],
                        [self.rows[0] | {'setting_id': 'unknown'}, *self.rows[1:]]):
            with self.assertRaises(ValueError):
                self.validate(changed)

    def test_paired_trace_counts_and_summary_links_rejected(self):
        for change in ({'workload_sha256': 'wrong'}, {'generated': 1},
                       {'p95_latency_ms': 123456}, {'p95_wait_ms': math.inf}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.validate([self.rows[0] | change, *self.rows[1:]])

    def test_faster_wait_does_not_hide_increased_loss(self):
        lookup = self.validate(self.rows)
        adjusted = copy.deepcopy(lookup)
        for (scenario, seed, policy, priority), row in adjusted.items():
            if priority == 2:
                if policy == 'adaptive_guarded':
                    row.update(p95_wait_ms=0, drop_fraction=.5, deadline_failure_fraction=.5)
                elif policy == 'fixed_guarded':
                    row.update(p95_wait_ms=100, drop_fraction=0, deadline_failure_fraction=0)
        primary_plan = self.plan | dict(profile='primary')
        comparisons, _, assessments, _ = analysis.compare(primary_plan, adjusted)
        self.assertTrue(all(r['routine_wait'] == 'reduction_supported' for r in assessments))
        self.assertTrue(all(r['routine_drop'] == 'increase_supported' for r in assessments))
        self.assertTrue(all(not r['all_interval_criteria_met'] for r in assessments))
        self.assertTrue(all(r['interpretation'] == 'tradeoff_not_established' for r in assessments))

    def test_analysis_read_only_hashes_repeatable_and_later_source_allowed(self):
        before = study.inventory(self.input)
        source = study.source_identity() | dict(sha256='later-analysis-version')
        with contextlib.redirect_stdout(io.StringIO()), patch.object(study, 'source_identity', return_value=source):
            analysis.run(self.input, self.base/'analysis-a')
            analysis.run(self.input, self.base/'analysis-b')
            with self.assertRaisesRegex(ValueError, 'Source or Python'):
                study.load_registration(self.input)
        for name in ('comparisons.json', 'paired_differences.csv', 'scenario_assessments.json'):
            self.assertEqual(study.file_hash(self.base/'analysis-a'/name), study.file_hash(self.base/'analysis-b'/name))
        self.assertEqual(before, study.inventory(self.input))
        study.verify(self.base/'analysis-a')
        manifest = study.read_json(self.base/'analysis-a/manifest.json')
        self.assertEqual(manifest['simulation_source'], self.registration['provenance']['source'])
        self.assertEqual(manifest['analysis_provenance']['source']['sha256'], 'later-analysis-version')
        self.assertIn('Engineering smoke only', (self.base/'analysis-a/report.md').read_text())
        with self.assertRaises(FileExistsError):
            analysis.run(self.input, self.base/'analysis-a')
        with self.assertRaisesRegex(ValueError, 'outside'):
            analysis.run(self.input, self.input/'analysis')

    def test_incomplete_study_is_rejected_before_output(self):
        path = self.base/'incomplete'
        study.initialize(path, 'smoke')
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(FileNotFoundError):
            analysis.run(path, self.base/'incomplete-analysis')
        self.assertFalse((self.base/'incomplete-analysis').exists())

    @unittest.skipUnless(importlib.util.find_spec('matplotlib'), 'Optional plotting dependency not installed')
    def test_plot_exports_include_png_svg_pdf_and_units(self):
        from iot_alerts import analysis_plots
        render = analysis_plots.render
        lookup = self.validate(self.rows)
        comparisons, _, _, _ = analysis.compare(self.plan, lookup)
        comparisons[0].update(mean_difference=-2, ci_low=-3, ci_high=-1)
        comparisons[1].update(mean_difference=.005, ci_low=.002, ci_high=.015)
        comparisons[-1].update(mean_difference=None, ci_low=None, ci_high=None, interval_status='undefined_metric')
        with patch.object(analysis_plots.plt, 'close', wraps=analysis_plots.plt.close) as close:
            dependencies = render(comparisons, self.plan, self.base/'plot-test')
        figure = close.call_args.args[0]
        urgent_axis = figure.axes[1]
        self.assertTrue(any(list(line.get_xdata()) == [.2, 1.5] for line in urgent_axis.lines))
        self.assertTrue(any(list(line.get_xdata()) == [1., 1.] for line in urgent_axis.lines))
        stem = self.base/'plot-test/burst-uniform-capacity10'
        for extension in ('.png', '.svg', '.pdf'):
            self.assertGreater(stem.with_suffix(extension).stat().st_size, 1000)
        svg = stem.with_suffix('.svg').read_text()
        self.assertIn('percentage points', svg)
        self.assertIn('ENGINEERING SMOKE', svg)
        self.assertIn('Undefined interval', svg)
        self.assertIn('matplotlib', dependencies)
