import math
import unittest
from dataclasses import replace
from iot_alerts.simulator import Alert, run_simulation
from iot_alerts.scheduling import AgingConfig, VARIANTS, select_aging
from iot_alerts.workloads import generate_workload


class CandidateTests(unittest.TestCase):
    def select(self, events, clock=1., capacity=2, variant='adaptive_guarded', config=None):
        return select_aging(events, clock, capacity, variant, config or AgingConfig(.1, .1), .1)

    def test_empty_single_and_saturation(self):
        self.assertEqual(self.select([]), (None, False))
        event = Alert(0, 0, 2)
        self.assertEqual(self.select([event], clock=1e300, config=AgingConfig(1e-300, 1e-300)), (event, False))

    def test_occupancy_changes_promotion(self):
        low, high = Alert(0, 0, 2), Alert(1, .19, 0)
        config = AgingConfig(.1, 1)
        # Empty waiting buffer: long interval keeps original priority.
        self.assertEqual(self.select([low, high], clock=.2, capacity=100, variant='adaptive', config=config)[0], high)
        # Full waiting buffer: low has reached priority zero and wins arrival tie.
        self.assertEqual(self.select([low, high], clock=.2, capacity=1, variant='adaptive', config=config)[0], low)
        # Midpoint gives interval .55; .8 seconds gives only one promotion.
        self.assertEqual(self.select([low, replace(high, arrival=.79)], clock=.8, capacity=2, variant='adaptive', config=config)[0].id, 1)

    def test_deadline_arrival_and_id_ties(self):
        events = [Alert(3, 0, 2), Alert(2, .1, 1, .4), Alert(1, .1, 1, .4)]
        self.assertEqual(self.select(events, variant='adaptive')[0].id, 1)
        events = [Alert(2, .1, 1, .4), Alert(3, 0, 2, .5)]
        self.assertEqual(self.select(events, variant='adaptive')[0].id, 3)

    def test_guard_equality_and_overdue(self):
        low = Alert(0, 0, 2, .125)
        high = Alert(1, .375, 0, .25)  # absolute deadline .625
        config = AgingConfig(.1, .1, .0625)
        self.assertEqual(self.select([low, high], clock=.5, config=config), (low, False))
        self.assertEqual(self.select([low, high], clock=.501, config=config), (high, True))
        self.assertEqual(self.select([low, high], clock=1, config=config), (high, True))
        self.assertEqual(self.select([low, high], clock=1, variant='adaptive', config=config), (low, False))

    def test_guard_uses_earliest_known_urgent(self):
        low = Alert(0, 0, 2, .01)
        events = [low, Alert(1, .8, 0), Alert(2, .8, 0, .21), Alert(3, .8, 0, .22)]
        self.assertEqual(self.select(events)[0].id, 2)
        self.assertFalse(self.select([low, events[1]])[1])
        self.assertFalse(self.select([Alert(0, 0, 0, .1)])[1])

    def test_no_actual_service_oracle(self):
        events = [Alert(0, 0, 2, .01), Alert(1, .8, 0, .21)]
        expected = self.select(events)[0].id
        changed = [replace(e, service_time_s=100 if e.id == 0 else .0001) for e in events]
        self.assertEqual(self.select(changed)[0].id, expected)

    def test_config_validation(self):
        for value in (0, -1, math.inf, math.nan, True):
            for field in ('minimum_s', 'maximum_s', 'service_estimate_s'):
                with self.assertRaises(ValueError):
                    AgingConfig(**{field: value})
        with self.assertRaises(ValueError):
            AgingConfig(1, .1)
        for variant in VARIANTS:
            for capacity in (None, 0, -1, True):
                with self.assertRaises(ValueError):
                    run_simulation([], variant, queue_capacity=capacity)

    def test_matched_equal_intervals_and_accounting(self):
        events = generate_workload(300, 120, 42, traffic='burst', deadlines=(.1, .5, 2), service_distribution='uniform')
        config = AgingConfig(.1, .1)
        results = {p: run_simulation(events, p, queue_capacity=10, aging_config=config) for p in VARIANTS}
        for adaptive, fixed in [('adaptive_guarded', 'fixed_guarded'), ('adaptive', 'fixed_deadline')]:
            self.assertEqual(results[adaptive].completions, results[fixed].completions)
            self.assertEqual(results[adaptive].rejections, results[fixed].rejections)
            self.assertEqual(results[adaptive].guard_activations, results[fixed].guard_activations)
        for result in results.values():
            self.assertEqual(result.completed + result.dropped, len(events))
            self.assertLessEqual(result.max_waiting, 10)
            self.assertTrue(all(a.finish_s <= b.start_s for a, b in zip(result.completions, result.completions[1:])))

    def test_completion_arrival_dispatch_order_and_guard_count(self):
        events = [Alert(0, 0, 0, service_time_s=1), Alert(1, .1, 2, .1), Alert(2, 1, 0, .015)]
        result = run_simulation(events, 'adaptive_guarded', queue_capacity=1)
        self.assertEqual([c.event.id for c in result.completions], [0, 2, 1])
        self.assertEqual(result.guard_activations, 1)
        self.assertEqual(result.dropped, 0)
