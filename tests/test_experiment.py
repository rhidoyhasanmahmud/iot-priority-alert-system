import unittest
from iot_alerts.experiment import Alert, simulate, workload


class SchedulingTests(unittest.TestCase):
    def test_non_preemptive_priority_and_fifo(self):
        events = [Alert(0, 0, 2), Alert(1, .1, 2), Alert(2, .2, 0), Alert(3, .3, 0)]
        fifo = simulate(events, 'fifo', 1)
        priority = simulate(events, 'priority', 1)
        self.assertEqual([r['id'] for r in fifo], [0, 1, 2, 3])
        self.assertEqual([r['id'] for r in priority], [0, 2, 3, 1])
        self.assertEqual(priority[-1]['finish_s'], 4)
        self.assertEqual(priority[1]['wait_s'], .8)

    def test_no_loss_and_service_conservation(self):
        events = workload(500, 120, 42)
        for policy in ('fifo', 'priority'):
            rows = simulate(events, policy, .01)
            self.assertEqual({r['id'] for r in rows}, set(range(500)))
            for row in rows:
                self.assertGreaterEqual(row['wait_s'], 0)
                self.assertAlmostEqual(row['finish_s']-row['start_s'], .01)

    def test_idle_and_empty(self):
        self.assertEqual(simulate([], 'fifo', 1), [])
        rows = simulate([Alert(0, 3, 2), Alert(1, 10, 0)], 'priority', 1)
        self.assertEqual([r['wait_s'] for r in rows], [0, 0])


if __name__ == '__main__':
    unittest.main()
