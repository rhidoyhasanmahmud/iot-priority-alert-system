#!/usr/bin/env python3
"""Fail-closed pre-holdout checks; uses only reserved tuning seed 7003."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import tempfile
import unittest

from stage8_frozen_study import load_protocol, plan, run_study
from stage8_independent_analysis import StudyAuditError, audit_study, mean_ci


class Stage8ProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parent
        cls.protocol = cls.root / "stage8_frozen_protocol.json"
        cls.config = load_protocol(cls.protocol)
        cls.temp = tempfile.TemporaryDirectory(prefix="stage8-preholdout-tests-")
        cls.study = Path(cls.temp.name) / "pilot"
        run_study(config_path=cls.protocol, output_dir=cls.study, pilot=True,
                  pilot_seeds=(7003,), git_revision="UNCOMMITTED")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def test_immutable_hash_and_exact_holdout_design(self) -> None:
        self.assertEqual(len(plan(self.config, pilot=False)), 450)
        self.assertEqual(len({(s, n, k) for s, n, k, _ in plan(self.config, pilot=False)}), 150)
        self.assertEqual(len(set(self.config["holdout_seeds"])), 30)
        self.assertFalse(set(self.config["holdout_seeds"]) &
                         set(self.config["pilot_only_seeds"]))

    def test_pilot_seeds_cannot_be_substituted_from_holdout(self) -> None:
        with self.assertRaisesRegex(ValueError, "reserved tuning seeds"):
            plan(self.config, pilot=True, pilot_seeds=(210001,))

    def test_altered_protocol_refused_before_execution(self) -> None:
        bad = Path(self.temp.name) / "changed.json"
        changed = copy.deepcopy(self.config)
        changed["urgent_deadline_ms"] = 500
        bad.write_text(json.dumps(changed))
        with self.assertRaisesRegex(ValueError, "protocol has changed"):
            load_protocol(bad)

    def test_full_pilot_independent_sqlite_and_source_audit(self) -> None:
        result = audit_study(self.study, self.protocol, pilot=True)
        self.assertEqual(result["runs_independently_reaudited"], 6)
        self.assertEqual(result["three_policy_matched_blocks"], 2)
        self.assertFalse(result["field_calibrated"])

    def test_cannot_promote_pilot_into_scientific_holdout(self) -> None:
        with self.assertRaises(StudyAuditError):
            audit_study(self.study, self.protocol, pilot=False)

    def test_tampered_summary_count_rejected(self) -> None:
        study = self.study / "study.json"
        original = study.read_text()
        try:
            payload = json.loads(original)
            payload["runs"][0]["committed"] += 1
            study.write_text(json.dumps(payload))
            with self.assertRaisesRegex(StudyAuditError, "Emitter summary"):
                audit_study(self.study, self.protocol, pilot=True)
        finally:
            study.write_text(original)

    def test_tampered_source_hash_rejected(self) -> None:
        study = self.study / "study.json"
        original = study.read_text()
        try:
            payload = json.loads(original)
            payload["runs"][0]["ledger_sha256"] = "0" * 64
            study.write_text(json.dumps(payload))
            with self.assertRaisesRegex(StudyAuditError, "Raw ledger/SQLite file hash"):
                audit_study(self.study, self.protocol, pilot=True)
        finally:
            study.write_text(original)

    def test_run_reorder_is_rejected(self) -> None:
        study = self.study / "study.json"
        original = study.read_text()
        try:
            payload = json.loads(original)
            payload["runs"][0], payload["runs"][1] = payload["runs"][1], payload["runs"][0]
            study.write_text(json.dumps(payload))
            with self.assertRaisesRegex(StudyAuditError, "reordered"):
                audit_study(self.study, self.protocol, pilot=True)
        finally:
            study.write_text(original)

    def test_bootstrap_reproducibility_on_independent_seeds(self) -> None:
        a = mean_ci([0.0, 0.1, -0.1, 0.2], seed=1, repetitions=100)
        b = mean_ci([0.0, 0.1, -0.1, 0.2], seed=1, repetitions=100)
        self.assertEqual(a, b)
        self.assertLessEqual(a["ci95_low"], a["mean"])
        self.assertGreaterEqual(a["ci95_high"], a["mean"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
