#!/usr/bin/env python3
"""Conventional *fictional* dispatch correctness, not academic result tests."""

from __future__ import annotations

import unittest

from stage5k2_baseline_sandbox import simulate_contract, verify_simulated_lifecycle
from stage5k2_workload_fixture import build_fixture


def mini_fixture() -> tuple[list[dict], list[dict]]:
    classes = ["routine", "routine", "urgent"]
    units = [10, 1, 1]
    offers = [{"fixture_id": "toy", "event_id": f"synthetic-e{i}",
               "trusted_class": kind, "planned_offer_offset_ns": i}
              for i, kind in enumerate(classes)]
    hidden = [{"event_id": f"synthetic-e{i}", "synthetic_required_work_units": work}
              for i, work in enumerate(units)]
    return offers, hidden


class ConventionalSandboxBaselineTests(unittest.TestCase):
    def test_fifo_is_nonpreemptive_and_respects_offer_order(self) -> None:
        offers, hidden = mini_fixture()
        result = simulate_contract(offers, hidden, policy="fifo", waiting_capacity=2,
                                   illustrative_ns_per_unit=1)
        self.assertEqual([row["start_offset_ns"] for row in result], [0, 10, 11])
        self.assertEqual([row["complete_offset_ns"] for row in result], [10, 11, 12])
        self.assertEqual(verify_simulated_lifecycle(result, waiting_capacity=2)["offered"], 3)

    def test_strict_urgent_first_prioritizes_only_at_next_dispatch(self) -> None:
        offers, hidden = mini_fixture()
        result = simulate_contract(offers, hidden, policy="strict_urgent_first",
                                   waiting_capacity=2, illustrative_ns_per_unit=1)
        self.assertEqual([row["start_offset_ns"] for row in result], [0, 11, 10])
        self.assertEqual([row["complete_offset_ns"] for row in result], [10, 12, 11])
        self.assertEqual(verify_simulated_lifecycle(result, waiting_capacity=2)["offered"], 3)

    def test_zero_waiting_capacity_rejects_while_worker_busy(self) -> None:
        offers, hidden = mini_fixture()
        result = simulate_contract(offers, hidden, policy="fifo", waiting_capacity=0,
                                   illustrative_ns_per_unit=1)
        self.assertEqual([row["status"] for row in result], [
            "completed_synthetic", "rejected_full_synthetic", "rejected_full_synthetic"])
        self.assertEqual(verify_simulated_lifecycle(result, waiting_capacity=0)["rejected_full_synthetic"], 2)

    def test_exact_completion_at_new_offer_precedes_admission(self) -> None:
        offers, hidden = mini_fixture()
        offers = [offers[0], offers[1] | {"planned_offer_offset_ns": 10}]
        hidden = hidden[:2]
        result = simulate_contract(offers, hidden, policy="fifo", waiting_capacity=0,
                                   illustrative_ns_per_unit=1)
        self.assertEqual([row["start_offset_ns"] for row in result], [0, 10])
        self.assertEqual(verify_simulated_lifecycle(result, waiting_capacity=0)["completed_synthetic"], 2)

    def test_both_policies_keep_single_worker_capacity_and_conservation(self) -> None:
        offers, work, _ = build_fixture(seed=1729, count=60, urgent_count=15,
                                         horizon_ns=1_000_000_000,
                                         shape="clustered", dispersion="variable")
        for policy in ("fifo", "strict_urgent_first"):
            result = simulate_contract(offers, work, policy=policy, waiting_capacity=3)
            self.assertEqual(verify_simulated_lifecycle(result, waiting_capacity=3)["offered"], 60)
            self.assertEqual([r["event_id"] for r in result], [r["event_id"] for r in offers])

    def test_undeclared_online_field_is_rejected(self) -> None:
        offers, work = mini_fixture()
        offers[0]["synthetic_required_work_units"] = 10
        with self.assertRaisesRegex(ValueError, "hidden-work leak"):
            simulate_contract(offers, work, policy="fifo", waiting_capacity=2)

    def test_wrong_or_missing_hidden_id_is_rejected(self) -> None:
        offers, work = mini_fixture()
        work[0]["event_id"] = "synthetic-wrong"
        with self.assertRaisesRegex(ValueError, "exact unique"):
            simulate_contract(offers, work, policy="fifo", waiting_capacity=2)

    def test_bad_capacity_policy_and_unit_conversion_are_rejected(self) -> None:
        offers, work = mini_fixture()
        for changes in ({"policy": "oracle"}, {"waiting_capacity": -1},
                        {"illustrative_ns_per_unit": 0}):
            params = {"policy": "fifo", "waiting_capacity": 2} | changes
            with self.assertRaises(ValueError):
                simulate_contract(offers, work, **params)

    def test_independent_lifecycle_verifier_rejects_overlapping_work(self) -> None:
        offers, work = mini_fixture()
        rows = simulate_contract(offers, work, policy="fifo", waiting_capacity=2,
                                 illustrative_ns_per_unit=1)
        rows[1]["start_offset_ns"] = 3
        with self.assertRaisesRegex(AssertionError, "overlap"):
            verify_simulated_lifecycle(rows, waiting_capacity=2)

    def test_independent_lifecycle_verifier_rejects_false_fullness(self) -> None:
        offers, work = mini_fixture()
        rows = simulate_contract(offers, work, policy="fifo", waiting_capacity=0,
                                 illustrative_ns_per_unit=1)
        rows[1]["planned_offer_offset_ns"] = 99
        with self.assertRaisesRegex(AssertionError, "without a full buffer"):
            verify_simulated_lifecycle(rows, waiting_capacity=0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
