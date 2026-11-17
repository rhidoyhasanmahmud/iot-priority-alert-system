#!/usr/bin/env python3
"""Positive/negative real-SQLite but fictional in-process Stage 7 tests."""

from __future__ import annotations

import copy
from collections import deque
import json
from pathlib import Path
import tempfile
import time
import unittest

from stage5d_lifecycle_audit import AuditError
from stage5k2_workload_fixture import save_fixture
from stage7_calibration_audit import CalibrationError, audit as audit_calibration
from stage7_calibration_probe import run_probe
from stage7_controlled_replay import PolicyGateway, run_case
from stage7_independent_replay_audit import audit_run


class Stage7IndependentReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory(prefix="s7-tests-")
        cls.root = Path(cls.temp.name)
        cls.fixture = cls.root / "fixture"
        save_fixture(cls.fixture, seed=71, count=20, urgent_count=5,
                     horizon_ns=100_000_000, shape="clustered", dispersion="variable")
        cls.examples = {}
        for policy in ("fifo", "strict_urgent_first", "routine_wait_guard"):
            db = cls.root / f"{policy}.sqlite"
            records, _ = run_case(fixture_dir=cls.fixture, transport="inproc", policy=policy,
                                  K=2, iterations_per_unit=5000,
                                  urgent_deadline_ms=20, routine_tau_ms=20,
                                  sqlite_output=db, timeout_s=10)
            cls.examples[policy] = (records, db)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def test_fifo_accounting_and_real_sqlite_contents_pass(self) -> None:
        rows, db = self.examples["fifo"]
        found = audit_run(rows, db, self.fixture)
        self.assertEqual(found["offered"], 20)
        self.assertEqual(found["committed"] + found["rejected"], 20)

    def test_strict_priority_accounting_and_sqlite_pass(self) -> None:
        rows, db = self.examples["strict_urgent_first"]
        found = audit_run(rows, db, self.fixture)
        self.assertEqual(found["policy"], "strict_urgent_first")

    def test_guard_candidate_accounting_and_real_sqlite_pass(self) -> None:
        rows, db = self.examples["routine_wait_guard"]
        found = audit_run(rows, db, self.fixture)
        self.assertEqual(found["policy"], "routine_wait_guard")
        self.assertEqual(found["committed"] + found["rejected"], 20)

    def test_routine_wait_guard_is_online_and_uses_elapsed_offer_age_only(self) -> None:
        gateway = object.__new__(PolicyGateway)
        gateway.policy = "routine_wait_guard"
        gateway.tau_ns = 20_000_000
        current = time.monotonic_ns()
        gateway.waiting = deque([
            ({"event_id": "routine", "trusted_class": "ROUTINE",
              "offer_ns": current - 15_000_000}, {}),
            ({"event_id": "urgent", "trusted_class": "URGENT",
              "offer_ns": current - 3_000_000}, {}),
        ])
        chosen, _ = gateway._select_next()
        self.assertEqual(chosen["event_id"], "routine")
        self.assertEqual(len(gateway.waiting), 1)

    def test_guard_misrepresented_rule_is_rejected(self) -> None:
        rows, db = self.examples["routine_wait_guard"]
        forged = copy.deepcopy(rows)
        forged[0]["routine_guard_rule"] = "WE_LOOK_AT_FUTURE_WORK"
        with self.assertRaisesRegex(AuditError, "routine-guard rule"):
            audit_run(forged, db, self.fixture)

    def test_only_executed_jobs_gain_hidden_work_information(self) -> None:
        rows, _ = self.examples["fifo"]
        offers = [row for row in rows if row["type"] == "offer"]
        for row in offers:
            if row["terminal"] == "REJECTED":
                self.assertNotIn("synthetic_work_units_post_dispatch", row)
                self.assertNotIn("dispatch_snapshot", row)
            else:
                self.assertGreater(row["synthetic_work_units_post_dispatch"], 0)

    def test_independent_gate_rejects_inproc_claimed_as_real_mqtt(self) -> None:
        rows, db = self.examples["fifo"]
        with self.assertRaises(AuditError):
            audit_run(rows, db, self.fixture, require_mqtt=True)

    def test_tampered_dispatch_snapshot_is_rejected(self) -> None:
        rows, db = self.examples["strict_urgent_first"]
        forged = copy.deepcopy(rows)
        next(row for row in forged if row.get("dispatch_reason") == "queued_policy_selection")[
            "dispatch_snapshot"] = [{"event_id": "fake", "trusted_class": "URGENT"}]
        with self.assertRaisesRegex(AuditError, "snapshot"):
            audit_run(forged, db, self.fixture)

    def test_future_hidden_work_leak_in_rejected_row_is_rejected(self) -> None:
        rows, db = self.examples["fifo"]
        forged = copy.deepcopy(rows)
        next(row for row in forged if row.get("terminal") == "REJECTED")[
            "synthetic_work_units_post_dispatch"] = 7
        with self.assertRaisesRegex(AuditError, "Rejected"):
            audit_run(forged, db, self.fixture)

    def test_forged_sql_commit_result_is_rejected(self) -> None:
        rows, db = self.examples["fifo"]
        forged = copy.deepcopy(rows)
        next(row for row in forged if row.get("terminal") == "COMPLETED")[
            "db_rule_result"] = "FORGED"
        with self.assertRaises(AuditError):
            audit_run(forged, db, self.fixture)

    def test_corrupted_cpu_work_conversion_is_rejected(self) -> None:
        rows, db = self.examples["fifo"]
        forged = copy.deepcopy(rows)
        next(row for row in forged if row.get("terminal") == "COMPLETED")[
            "synthetic_cpu_iterations"] += 10
        with self.assertRaises(AuditError):
            audit_run(forged, db, self.fixture)

    def test_forged_source_digest_is_rejected(self) -> None:
        rows, db = self.examples["fifo"]
        forged = copy.deepcopy(rows)
        forged[0]["source_sha256"] = "0" * 64
        with self.assertRaises(AuditError):
            audit_run(forged, db, self.fixture)

    def test_forged_provenance_is_rejected(self) -> None:
        rows, db = self.examples["fifo"]
        forged = copy.deepcopy(rows)
        forged[0]["trace_provenance"] = "TRUSTED_REAL_IOT_SLA"
        with self.assertRaisesRegex(AuditError, "fictional workload provenance"):
            audit_run(forged, db, self.fixture)

    def test_missing_offer_fails_independent_population_check(self) -> None:
        rows, db = self.examples["fifo"]
        forged = copy.deepcopy(rows)
        forged.pop(next(i for i, row in enumerate(forged) if row["type"] == "offer"))
        with self.assertRaises(AuditError):
            audit_run(forged, db, self.fixture)

    def test_changed_sqlite_backup_fails_sha_and_row_integrity(self) -> None:
        rows, db = self.examples["fifo"]
        modified = self.root / "modified.sqlite"
        modified.write_bytes(db.read_bytes())
        with modified.open("r+b") as f:
            f.seek(101)
            first = f.read(1)
            f.seek(101)
            f.write(bytes([first[0] ^ 1]))
        with self.assertRaises(AuditError):
            audit_run(rows, modified, self.fixture)

    def test_artificial_calibration_raw_and_sqlite_pass(self) -> None:
        with tempfile.TemporaryDirectory(prefix="s7cal-") as tmp:
            report, db = Path(tmp) / "cal.json", Path(tmp) / "cal.sqlite"
            run_probe(iterations_per_unit=1000, seed=1, repetitions=5,
                      output=report, sqlite_output=db)
            self.assertFalse(audit_calibration(report, db)["field_calibrated"])
            forged = json.loads(report.read_text())
            forged["by_unit"]["4"]["total_median_ns"] += 100
            report.write_text(json.dumps(forged))
            with self.assertRaisesRegex(CalibrationError, "Summary statistics"):
                audit_calibration(report, db)


if __name__ == "__main__":
    unittest.main(verbosity=2)
