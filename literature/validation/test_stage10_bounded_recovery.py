#!/usr/bin/env python3
"""Reserved-development red-team tests; not a Stage 10 held-out study."""
from __future__ import annotations

import copy
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from stage5k2_workload_fixture import save_fixture
from stage10_bounded_recovery import Stage10Gateway, run_case
from stage10_independent_audit import audit_run


class Stage10IndependentAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = TemporaryDirectory(prefix="stage10-red-team-")
        cls.root = Path(cls.temporary.name)
        cls.fixture = cls.root / "fixture"
        save_fixture(cls.fixture, seed=9010, count=60, urgent_count=15,
                     horizon_ns=1_000_000_000, shape="clustered", dispersion="variable")
        cls.worker = cls.root / "worker.sqlite"
        cls.spool = cls.root / "spool.sqlite"
        cls.rows, cls.result = run_case(
            fixture_dir=cls.fixture, policy="pushout_deferred", K=3, B=8,
            iterations_per_unit=10000, urgent_deadline_ms=50.0,
            routine_tau_ms=20.0, sqlite_output=cls.worker,
            spool_output=cls.spool)

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_valid_evidence_passes(self):
        checked = audit_run(self.rows, self.worker, self.spool, self.fixture)
        self.assertEqual(checked["status"],
                         "PASS_STAGE10_INDEPENDENT_K_PLUS_B_SQLITE_QUEUE_AUDIT")
        self.assertEqual(checked["offered"], 60)
        self.assertEqual(checked["C"], self.result["C"])
        self.assertEqual(checked["U"], self.result["U"])

    def mutated(self, predicate, key, value):
        rows = copy.deepcopy(self.rows)
        target = next(x for x in rows if predicate(x))
        target[key] = value
        return rows

    def assert_refused(self, rows, *, worker=None, spool=None):
        with self.assertRaises((ValueError, AssertionError)):
            audit_run(rows, worker or self.worker, spool or self.spool, self.fixture)

    def test_reject_falsified_deferred_capacity_snapshot(self):
        self.assert_refused(self.mutated(lambda x: x["type"] == "offer",
                                        "deferred_at_offer", 1000))

    def test_reject_falsified_admission(self):
        self.assert_refused(self.mutated(
            lambda x: x["type"] == "offer" and
                      x["admission_action"] == "PUSHOUT_DEFER_ADMIT",
            "admission_action", "ADMIT_MAIN"))

    def test_reject_hidden_cancellation(self):
        rows = self.mutated(lambda x: x["type"] == "offer" and
                                     x["terminal"] == "COMPLETED",
                            "terminal", "REJECTED")
        self.assert_refused(rows)

    def test_reject_forged_source_class(self):
        self.assert_refused(self.mutated(lambda x: x["type"] == "offer" and
                                                  x["trusted_class"] == "ROUTINE",
                                        "trusted_class", "URGENT"))

    def test_reject_corrupted_main_sqlite_digest(self):
        self.assert_refused(self.mutated(lambda x: x["type"] == "manifest",
                                        "worker_sqlite_sha256", "0"*64))

    def test_reject_corrupted_spool_sqlite_digest(self):
        self.assert_refused(self.mutated(lambda x: x["type"] == "manifest",
                                        "spool_sqlite_sha256", "0"*64))

    def test_reject_undeclared_buffer(self):
        self.assert_refused(self.mutated(lambda x: x["type"] == "manifest", "B", 0))

    def test_reject_modified_slack_definition(self):
        self.assert_refused(self.mutated(lambda x: x["type"] == "manifest",
                                        "slack_guard_ns", -1))

    def test_reject_missing_offer(self):
        rows = copy.deepcopy(self.rows)
        rows.remove(next(x for x in rows if x["type"] == "offer"))
        self.assert_refused(rows)

    def test_no_extra_capacity_ablation_refuses_B(self):
        with self.assertRaises(ValueError):
            Stage10Gateway(db_path=self.root / "unused.sqlite",
                           spool_path=self.root / "unused_spool.sqlite",
                           run_id="invalid", K=3, B=8, policy="pushout_slack",
                           hidden_work=[], iterations_per_unit=10000,
                           urgent_deadline_ns=50_000_000, routine_tau_ns=20_000_000)

    def test_one_slot_overflow_falls_back_to_accounted_cancellations(self):
        worker = self.root / "bounded_one_worker.sqlite"
        spool = self.root / "bounded_one_spool.sqlite"
        rows, result = run_case(
            fixture_dir=self.fixture, policy="pushout_deferred", K=3, B=1,
            iterations_per_unit=10000, urgent_deadline_ms=50.0,
            routine_tau_ms=20.0, sqlite_output=worker, spool_output=spool)
        audited = audit_run(rows, worker, spool, self.fixture)
        self.assertEqual(audited["spool_peak"], 1)
        self.assertGreater(result["cancelled"], 0)
        self.assertGreater(result["spool_inserted"], 0)

    def test_reserved_capacity_ablation_uses_same_worker_and_spool(self):
        worker = self.root / "reserved_worker.sqlite"
        spool = self.root / "reserved_spool.sqlite"
        rows, result = run_case(
            fixture_dir=self.fixture, policy="pushout_reserved_deferred", K=3, B=8,
            iterations_per_unit=10000, urgent_deadline_ms=50.0,
            routine_tau_ms=20.0, sqlite_output=worker, spool_output=spool)
        audited = audit_run(rows, worker, spool, self.fixture)
        self.assertEqual(audited["offered"], 60)
        self.assertLessEqual(audited["spool_peak"], 8)
        self.assertEqual(audited["C"], result["C"])


if __name__ == "__main__":
    unittest.main()
