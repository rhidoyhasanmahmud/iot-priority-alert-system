#!/usr/bin/env python3
"""Stage 9 red-team lifecycle and frozen protocol tests, reserved tuning only."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from stage5k2_workload_fixture import save_fixture
from stage9_frozen_study import load_protocol, plan, PROTOCOL_SHA256
from stage9_independent_audit import audit_run


ROOT = Path(__file__).resolve().parent


class ProtocolFreezeTest(unittest.TestCase):
    def test_pinned_protocol(self) -> None:
        config = load_protocol(ROOT / "stage9_frozen_protocol.json")
        self.assertEqual(config["experimental_runs"], 600)
        self.assertEqual(len(plan(config, pilot=False, pilot_seeds=())), 600)
        self.assertEqual({x[0] for x in plan(config, pilot=False, pilot_seeds=())},
                         set(config["holdout_seeds"]))
        self.assertEqual(len(PROTOCOL_SHA256), 64)

    def test_holdout_cannot_leak_into_pilot(self) -> None:
        config = load_protocol(ROOT / "stage9_frozen_protocol.json")
        with self.assertRaises(ValueError):
            plan(config, pilot=True, pilot_seeds=(220001,))
        with self.assertRaises(ValueError):
            plan(config, pilot=True, pilot_seeds=(8008, 8008))

    def test_mutated_protocol_not_accepted(self) -> None:
        with TemporaryDirectory() as temp:
            p = Path(temp) / "protocol.json"
            p.write_text((ROOT / "stage9_frozen_protocol.json").read_text().replace(
                '"urgent_deadline_ms": 50.0', '"urgent_deadline_ms": 80.0'))
            with self.assertRaises(ValueError):
                load_protocol(p)


class AdversarialEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = TemporaryDirectory()
        root = Path(cls.temp.name)
        cls.fixture = root / "fixture"
        cls.sqlite = root / "run.sqlite"
        cls.ledger = root / "run.jsonl"
        save_fixture(cls.fixture, seed=8009, count=60, urgent_count=15,
                     shape="clustered", dispersion="flat", horizon_ns=1000000000)
        subprocess.run([sys.executable, str(ROOT / "stage9_urgent_pushout.py"),
                        "--fixture-dir", str(cls.fixture), "--transport", "inproc",
                        "--K", "3", "--output", str(cls.ledger),
                        "--sqlite-output", str(cls.sqlite)], check=True, capture_output=True)
        cls.rows = [json.loads(line) for line in cls.ledger.read_text().splitlines()
                    if line.strip()]

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def test_valid_raw_ledger_and_db_pass(self) -> None:
        audited = audit_run(self.rows, self.sqlite, self.fixture)
        self.assertEqual(audited["offered"], 60)
        self.assertEqual(audited["status"],
                         "PASS_STAGE9_INDEPENDENT_PUSHOUT_QUEUE_AND_SQLITE_AUDIT")

    def mutated_row(self, predicate, attribute, value) -> list[dict]:
        rows = copy.deepcopy(self.rows)
        match = next(row for row in rows if predicate(row))
        match[attribute] = value
        return rows

    def test_reject_fabricated_queue_snapshot(self) -> None:
        rows = self.mutated_row(lambda x: x["type"] == "offer", "waiting_at_offer", 999)
        with self.assertRaises((ValueError, AssertionError)):
            audit_run(rows, self.sqlite, self.fixture)

    def test_reject_untrusted_class_relabelling(self) -> None:
        rows = self.mutated_row(lambda x: x["type"] == "offer", "trusted_class", "URGENT_UNKNOWN")
        with self.assertRaises((ValueError, AssertionError)):
            audit_run(rows, self.sqlite, self.fixture)

    def test_reject_eviction_victim_tamper(self) -> None:
        rows = self.mutated_row(lambda x: x["type"] == "offer" and
                               x["admission_action"] == "PUSHOUT_ADMIT",
                               "pushout_victim_id", "fabricated")
        with self.assertRaises((ValueError, AssertionError)):
            audit_run(rows, self.sqlite, self.fixture)

    def test_reject_undisclosed_cancellation(self) -> None:
        rows = self.mutated_row(lambda x: x["type"] == "offer" and
                               x["terminal"] == "CANCELLED", "terminal", "REJECTED")
        with self.assertRaises((ValueError, AssertionError)):
            audit_run(rows, self.sqlite, self.fixture)

    def test_reject_untrue_completion(self) -> None:
        rows = self.mutated_row(lambda x: x["type"] == "offer" and
                               x["terminal"] == "COMPLETED", "synthetic_cpu_iterations", 0)
        with self.assertRaises((ValueError, AssertionError)):
            audit_run(rows, self.sqlite, self.fixture)

    def test_reject_missing_offer(self) -> None:
        rows = copy.deepcopy(self.rows)
        rows.remove(next(x for x in rows if x["type"] == "offer"))
        with self.assertRaises((ValueError, AssertionError)):
            audit_run(rows, self.sqlite, self.fixture)

    def test_reject_modified_sqlite_digest(self) -> None:
        rows = self.mutated_row(lambda x: x["type"] == "manifest",
                                "sqlite_backup_sha256", "0" * 64)
        with self.assertRaises((ValueError, AssertionError)):
            audit_run(rows, self.sqlite, self.fixture)


if __name__ == "__main__":
    unittest.main()
